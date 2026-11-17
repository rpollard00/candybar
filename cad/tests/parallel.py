#!/usr/bin/env python3
"""Run the test suite in many FreeCAD processes at once, with the verdict of cad/test.sh.

cad/test-parallel.sh calls this script; it runs under a plain Python 3.10 or later, not inside FreeCAD. It does
three things:

1. The builds that the tests read, once and in their order, into cad/out of this checkout:
     build    cad/build.sh                  the parts of the default build in cad/out/shell-rev7
     fit      candybar.shell.fit            cad/out/shell-rev7/fit (report.json)
     skin     tests.prime                   the skin in cad/out/shell-rev7/split/cache
     split    candybar.shell.split          split/measurements.json (after skin)
     prime-*  tests.prime                   the caches that the tests make when they are missing (after skin)
   build, fit and skin start together: each makes its own parts in memory, and each writes its own files.
2. The tests, in shards: one shard is one FreeCAD process (freecad-run.sh tests.run) that runs the tests of one
   file, or of one class of a file. A shard starts when the builds that its file reads are done (NEEDS). The
   longest shards start first (the times of the last run, or TIME_GUESS). Each shard has its own CANDYBAR_OUT (its
   log and the user directory of FreeCAD) and its own TMPDIR (support.temp_dir). A folder of the builds becomes
   read-only when the steps that write it are done, so that a test that would write a shared cache fails, instead
   of racing with another shard.
3. One summary: the count, each failure and error with its text, and the skipped tests, as unittest gives them;
   the time of each shard and file and the slowest tests. It goes to stdout, and to cad/out/_parallel/summary.md
   and summary.json. The exit status is 0 when every test passed (as cad/test.sh), 1 when not.

The run takes the lock of freecad-run.sh once for the whole run (cad/test-parallel.sh), and its own processes do not
take it again (CANDYBAR_LOCK_HELD). The memory guard of freecad-run.sh stops every freecadcmd of the machine, so it
is off here (CANDYBAR_GUARD_HELD); this script has its own guard, which stops one shard (its process group) when it
takes more than --shard-gb, and starts no new process while the machine has less than --free-gb left.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

CAD = Path(__file__).resolve().parents[1]
OUT = CAD / "out"
RUN = CAD / "candybar" / "freecad-run.sh"
SHELL = OUT / "shell-rev7"

# The steps of the build, their commands and the steps they wait for. Each writes only its own files.
PRIME = ("pieces", "deck", "zones", "coupons", "hood")


def prime(step: str, after: tuple[str, ...]):
    return [str(RUN), "tests.prime"], {"CANDYBAR_PRIME": step, "CANDYBAR_OUT": str(OUT / "_parallel" / "prime" / step)}, after


STEPS: dict[str, tuple[list[str], dict[str, str], tuple[str, ...]]] = {
    "build": ([str(CAD / "build.sh")], {"CANDYBAR_OUT": str(SHELL)}, ()),
    "fit": ([str(RUN), "candybar.shell.fit"], {"CANDYBAR_OUT": str(SHELL)}, ()),
    "skin": prime("skin", ()),
    "split": ([str(RUN), "candybar.shell.split"], {"CANDYBAR_OUT": str(SHELL)}, ("skin",)),
    **{f"prime-{p}": prime(p, ("build", "skin")) for p in PRIME},
}
ALL = tuple(STEPS)
PRIMED = ("build", "skin", *(f"prime-{p}" for p in PRIME))
# The folders that the steps write and the tests only read, with the steps that write them: each becomes read-only
# when its steps are done.
SHARED: dict[Path, tuple[str, ...]] = {
    SHELL / "split" / "cache": ("skin", "prime-deck", "prime-zones"),
    OUT / "pieces" / "cache": ("prime-pieces",),
    OUT / "coupons" / "cache": ("prime-coupons",),
    OUT / "hood-band" / "base": ("prime-hood",),
    SHELL: ALL,
}

# What each test file (or class) reads of the builds. A file that is not here waits for every step. Files that read
# nothing from cad/out start at once; files that read only the parts of the default build (cad/out/shell-rev7/*.brep,
# for example through tools.edge_finish.shell_parts) wait for "build"; files that read the skin or a cache made from
# it wait for PRIMED. Only two read the report of the fit study (cradle.shell_dir()/fit/report.json, and
# mounts.room_values, which takes stand-in values without it), and only WholeSetTest reads the measurements of the
# split (pieces.split_rows).
NEEDS: dict[str, tuple[str, ...]] = {
    "test_params": (), "test_joints": (), "test_build_entry": (), "test_monitor_pictures": (), "test_outputs": (),
    "test_blueprint_solids": ("build",), "test_edge_finish": ("build",), "test_face_check": ("build",),
    "test_fit": ("build",), "test_coupon": ("build",),
    "test_cradle": ("build",), "test_cradle.CradleInTheBodyTest": (*PRIMED, "fit"),
    "test_mounts": (*PRIMED, "fit"),
    "test_pieces": PRIMED, "test_pieces.WholeSetTest": (*PRIMED, "split"),
    "test_coupons": PRIMED, "test_hood_band": PRIMED, "test_panel_frame": PRIMED, "test_panel_latch": PRIMED,
    "test_rear": PRIMED, "test_socket_plate": PRIMED, "test_split": PRIMED, "test_structure": PRIMED,
}
# The files whose classes run in shards of their own. The other files run in one shard each, because their
# classes share what they make (functools.cache at the level of the module, or support.shell).
BY_CLASS = ("test_cradle", "test_pieces", "test_rear", "test_panel_frame", "test_panel_latch", "test_edge_finish",
            "test_fit", "test_blueprint_solids", "test_socket_plate", "test_coupons", "test_hood_band", "test_split",
            "test_outputs", "test_mounts")
# A first guess of the time of a shard, in seconds, when no earlier run has measured it.
TIME_GUESS = 600.0


@dataclass
class Job:
    name: str
    cmd: list[str]
    env: dict[str, str]
    needs: tuple[str, ...]
    log: Path
    kind: str                      # "step" or "shard"
    ids: list[str] = field(default_factory=list)
    results: Path | None = None
    expect: float = TIME_GUESS
    proc: subprocess.Popen | None = None
    started: float = 0.0
    ended: float = 0.0
    code: int | None = None
    peak_mb: int = 0
    note: str = ""


def shard_key(test_id: str, by_class=BY_CLASS) -> str:
    """The shard of a test: tests.test_x.Class.test_y -> test_x, or test_x.Class for the files of BY_CLASS."""
    parts = test_id.split(".")
    if len(parts) < 3 or parts[0] != "tests":
        return test_id    # a module that does not import: unittest.loader._FailedTest.test_x
    return f"{parts[1]}.{parts[2]}" if parts[1] in by_class else parts[1]


def needs_of(key: str) -> tuple[str, ...]:
    """The steps that a shard waits for: those of its class, else those of its file. A shard of a whole file waits
    also for what any of its classes needs."""
    if key in NEEDS:
        if "." in key:
            return NEEDS[key]
        found = set(NEEDS[key]).union(*(NEEDS[k] for k in NEEDS if k.startswith(key + ".")))
        return tuple(s for s in ALL if s in found)
    module = key.split(".")[0]
    return NEEDS.get(module, ALL)


def group_mb(pgid: int) -> int:
    """The resident memory of the processes of a process group, in MB."""
    total = 0
    for entry in os.scandir("/proc"):
        if not entry.name.isdigit():
            continue
        try:
            with open(f"/proc/{entry.name}/stat") as handle:
                fields = handle.read().rsplit(")", 1)[1].split()
            if int(fields[2]) == pgid:
                total += int(fields[21]) * os.sysconf("SC_PAGE_SIZE")
        except (OSError, IndexError, ValueError):
            continue
    return total // (1024 * 1024)


def available_mb() -> int:
    with open("/proc/meminfo") as handle:
        for line in handle:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    return 1 << 30


def cgroup_free_mb() -> int:
    """Inside a container with a memory limit, what the limit leaves; else a large number."""
    try:
        limit = Path("/sys/fs/cgroup/memory.max").read_text().strip()
        used = int(Path("/sys/fs/cgroup/memory.current").read_text())
        if limit != "max":
            return (int(limit) - used) // (1024 * 1024)
    except (OSError, ValueError):
        pass
    return 1 << 30


def set_writable(folders, writable: bool) -> None:
    for top in folders:
        if not top.exists():
            continue
        for path in [top, *top.rglob("*")]:
            if path.is_symlink():
                continue
            mode = path.stat().st_mode
            bits = stat.S_IWUSR | stat.S_IWGRP if writable else 0
            path.chmod((mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)) | bits)


def list_tests(work: Path, env: dict[str, str]) -> list[str]:
    listing = work / "tests.txt"
    done = subprocess.run([str(RUN), "tests.run"], env=env | {"CANDYBAR_LIST": str(listing), "CANDYBAR_OUT": str(work / "list")},
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if done.returncode != 0 or not listing.exists():
        sys.exit(f"The list of the tests failed:\n{done.stdout}")
    return [line for line in listing.read_text().splitlines() if line]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("fragment", nargs="?", default="", help="run only the tests whose name contains it, as cad/test.sh")
    ap.add_argument("-j", "--jobs", type=int, default=min(32, max(2, (os.cpu_count() or 4) // 2)), help="processes at once")
    ap.add_argument("--no-build", action="store_true", help="use the builds in cad/out as they are; run no step")
    ap.add_argument("--steps", default="", help="run only these steps (comma-separated); the others count as done")
    ap.add_argument("--by-file", action="store_true", help="one shard for each file, no file split into its classes")
    ap.add_argument("--shard-gb", type=float, default=float(os.environ.get("CANDYBAR_SHARD_GB", 24)), help="memory limit of one process group")
    ap.add_argument("--free-gb", type=float, default=float(os.environ.get("CANDYBAR_FREE_GB", 12)), help="start nothing below this free memory")
    ap.add_argument("--timeout-min", type=float, default=240, help="the longest time of one shard or step")
    ap.add_argument("--timings", default=os.environ.get("CANDYBAR_PARALLEL_TIMINGS", ""), help="a JSON file of the times of earlier runs")
    args = ap.parse_args()

    t0 = time.monotonic()
    work = OUT / "_parallel"
    shutil.rmtree(work, ignore_errors=True)
    (work / "logs").mkdir(parents=True)
    base_env = dict(os.environ) | {"CANDYBAR_LOCK_HELD": "1", "CANDYBAR_GUARD_HELD": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    base_env.pop("CANDYBAR_TESTS", None)

    timings_file = Path(args.timings) if args.timings else work.parent / "_parallel-timings.json"
    try:
        known = json.loads(timings_file.read_text())
    except (OSError, ValueError):
        known = {}

    jobs: dict[str, Job] = {}
    wanted_steps = set(s for s in args.steps.split(",") if s) or set(ALL)
    for name, (cmd, env, after) in STEPS.items():
        if args.no_build or name not in wanted_steps:
            continue
        jobs[name] = Job(name, cmd, base_env | env, after, work / "logs" / f"{name}.log", "step", expect=known.get(name, 1200.0))

    listed = list_tests(work, base_env)
    selected = [t for t in listed if args.fragment in t] if args.fragment else listed
    shards: dict[str, list[str]] = {}
    for t in selected:
        shards.setdefault(shard_key(t, () if args.by_file else BY_CLASS), []).append(t)
    for key, ids in shards.items():
        fragments = " ".join(ids) if args.fragment or key.startswith("unittest.loader") else f"tests.{key}."
        out = work / "shards" / key
        (out / "tmp").mkdir(parents=True)
        env = base_env | {"CANDYBAR_TEST_IDS": fragments, "CANDYBAR_RESULTS": str(out / "results.json"), "CANDYBAR_OUT": str(out),
                          "TMPDIR": str(out / "tmp")}
        jobs[key] = Job(key, [str(RUN), "tests.run"], env, needs_of(key), work / "logs" / f"{key}.log", "shard", ids,
                        out / "results.json", known.get(key, TIME_GUESS))

    pending = sorted(jobs.values(), key=lambda j: (j.kind != "step", -j.expect))
    running: list[Job] = []
    done: dict[str, Job] = {}
    read_only: set[Path] = set()
    deadline = args.timeout_min * 60
    print(f"parallel: {len(selected)} tests in {sum(j.kind == 'shard' for j in jobs.values())} shards, "
          f"{sum(j.kind == 'step' for j in jobs.values())} build steps, {args.jobs} processes at once", flush=True)

    def finished(name: str) -> bool:
        return name in done or name not in jobs

    while pending or running:
        for j in list(running):
            code = j.proc.poll()
            now = time.monotonic()
            if code is None:
                mb = group_mb(j.proc.pid)
                j.peak_mb = max(j.peak_mb, mb)
                if mb > args.shard_gb * 1024 or now - j.started > deadline:
                    j.note = (f"stopped by the memory guard of the parallel run: {mb} MB" if mb > args.shard_gb * 1024
                              else f"stopped after {args.timeout_min:g} minutes")
                    os.killpg(j.proc.pid, signal.SIGKILL)
                continue
            j.code, j.ended = code, now
            running.remove(j)
            done[j.name] = j
            with j.log.open("a") as handle:
                handle.write(f"\n[parallel] exit {code} after {j.ended - j.started:.0f} s, peak {j.peak_mb} MB {j.note}\n")
            print(f"  {'done' if code == 0 else 'FAIL'} {j.kind} {j.name}: {j.ended - j.started:.0f} s, {j.peak_mb} MB "
                  f"({len(running)} running, {len(pending)} waiting, {now - t0:.0f} s) {j.note}", flush=True)
        for folder, writers in SHARED.items():
            if folder not in read_only and all(finished(n) for n in writers):
                set_writable([folder], False)
                read_only.add(folder)
        free = min(available_mb(), cgroup_free_mb())
        for j in list(pending):
            if len(running) >= args.jobs or free < args.free_gb * 1024:
                break
            # a step or a shard starts when the steps it needs are done
            if not all(finished(n) for n in j.needs):
                continue
            pending.remove(j)
            j.log.parent.mkdir(parents=True, exist_ok=True)
            with j.log.open("w") as handle:
                j.started = time.monotonic()
                j.proc = subprocess.Popen(j.cmd, env=j.env, stdout=handle, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                          cwd=str(CAD.parent), start_new_session=True)
            running.append(j)
            free -= 2048
        time.sleep(1.0)
    set_writable(sorted(read_only), True)
    wall = time.monotonic() - t0
    return report(jobs, selected, wall, work, timings_file, known, args)


def report(jobs: dict[str, Job], selected: list[str], wall: float, work: Path, timings_file: Path, known: dict, args) -> int:
    records: list[dict] = []
    shard_rows = []
    problems: list[str] = []
    checks: list[str] = []
    tests_run = 0
    for j in jobs.values():
        if j.kind == "step":
            # exit status 1 without a traceback: the step ran and its own check failed (the fit study or the split
            # reports a rule; cad/check.sh gives that verdict). Its files are written, and the tests read them.
            text = j.log.read_text(errors="replace") if j.log.exists() else ""
            if j.code == 1 and "Traceback (most recent call last)" not in text and not j.note:
                checks.append(f"{j.name}: its check failed (exit status 1); the tests use its files. Log: {j.log}")
            elif j.code != 0:
                problems.append(f"The build step {j.name} ended with exit status {j.code} {j.note}: {j.log}")
            continue
        data = None
        if j.results and j.results.exists():
            try:
                data = json.loads(j.results.read_text())
            except ValueError:
                data = None
        if data is None:
            tail = j.log.read_text(errors="replace")[-4000:] if j.log.exists() else ""
            records.append({"id": f"shard {j.name}", "outcome": "error", "seconds": 0.0, "setup_s": 0.0,
                            "text": f"The shard wrote no result (exit status {j.code}) {j.note}. The end of its log ({j.log}):\n{tail}"})
            shard_rows.append((j.name, j.ended - j.started, j.peak_mb, len(j.ids), 0.0))
            continue
        for r in data["records"]:
            r["shard"] = j.name
        records += data["records"]
        tests_run += data["tests_run"]
        shard_rows.append((j.name, j.ended - j.started, j.peak_mb, len(j.ids), data["load_s"]))
        if j.code not in (0, 1):
            problems.append(f"The shard {j.name} ended with exit status {j.code} {j.note}: {j.log}")
    seen = {r["id"] for r in records}
    class_errors = {m.group(1) for r in records for m in [re.search(r"\((tests\.[\w.]+)\)", r["id"])] if m and r["outcome"] == "error"}
    missing = [t for t in selected if t not in seen and t.rsplit(".", 1)[0] not in class_errors
               and t.rsplit(".", 2)[0] not in class_errors and not t.startswith("unittest.loader")]
    for t in missing:
        records.append({"id": t, "outcome": "error", "seconds": 0.0, "setup_s": 0.0, "text": "not run: no shard reported this test"})
    bad = [r for r in records if r["outcome"] in ("fail", "error", "unexpected success")]
    skipped = [r for r in records if r["outcome"] == "skip"]
    ok = not bad and tests_run > 0 and not problems

    # the times: per shard, per file, per test
    files: dict[str, dict] = {}
    for r in records:
        f = r["id"].split(".")[1] if r["id"].startswith("tests.") else r.get("shard", "?").split(".")[0]
        row = files.setdefault(f, {"tests": 0, "test_s": 0.0, "setup_s": 0.0, "wall_s": 0.0})
        row["tests"] += r["outcome"] != "error" or r["id"].startswith("tests.")
        row["test_s"] += r["seconds"]
        row["setup_s"] += r["setup_s"]
    for name, seconds, _, _, _ in shard_rows:
        f = name.split(".")[0]
        if f in files:
            files[f]["wall_s"] = max(files[f]["wall_s"], seconds)
            files[f]["shards"] = files[f].get("shards", 0) + 1
            files[f]["cpu_s"] = files[f].get("cpu_s", 0.0) + seconds
    slowest = sorted((r for r in records if r["id"].startswith("tests.")), key=lambda r: -(r["seconds"] + r["setup_s"]))[:20]

    lines = [f"# The parallel test run", "",
             f"{'PASS' if ok else 'FAIL'}: ran {tests_run} tests in {wall:.0f} s ({wall / 60:.1f} min) of wall time, "
             f"{len(bad)} failures and errors, {len(skipped)} skipped, {args.jobs} processes at once.", ""]
    if problems:
        lines += ["## Problems of the run", "", *[f"- {p}" for p in problems], ""]
    if checks:
        lines += ["## Checks of the design in the build steps", "", "These do not change the verdict of the tests (cad/check.sh gives them).", "",
                  *[f"- {c}" for c in checks], ""]
    if bad:
        lines += ["## Failures and errors", ""]
        for r in bad:
            lines += [f"### {r['outcome'].upper()}: {r['id']}", "", "```", r["text"].rstrip(), "```", ""]
    if skipped:
        lines += ["## Skipped", "", *[f"- {r['id']}: {r['text']}" for r in skipped], ""]
    steps = [j for j in jobs.values() if j.kind == "step"]
    if steps:
        lines += ["## The build steps", "", "| Step | Exit | Start, s | Time, s | Peak memory, MB |", "| --- | --- | --- | --- | --- |"]
        first = min(j.started for j in jobs.values() if j.started)
        lines += [f"| {j.name} | {j.code} | {j.started - first:.0f} | {j.ended - j.started:.0f} | {j.peak_mb} |" for j in steps]
        lines.append("")
    lines += ["## The time of each file", "",
              "Test time: the sum of the times of its tests. Set-up: the time of setUpClass and of the module (before the first test of a class). "
              "Process time: the sum of the times of its shards; wall time: its longest shard.", "",
              "| File | Tests | Test time, s | Set-up, s | Shards | Process time, s | Wall time, s |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for f, row in sorted(files.items(), key=lambda kv: -kv[1].get("cpu_s", 0.0)):
        lines.append(f"| {f} | {row['tests']} | {row['test_s']:.0f} | {row['setup_s']:.0f} | {row.get('shards', 0)} | {row.get('cpu_s', 0.0):.0f} | {row['wall_s']:.0f} |")
    lines += ["", "## The shards", "", "| Shard | Tests | Time, s | Import, s | Peak memory, MB |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| {n} | {c} | {s:.0f} | {ld:.0f} | {mb} |" for n, s, mb, c, ld in sorted(shard_rows, key=lambda r: -r[1])]
    lines += ["", "## The twenty slowest tests", "", "Set-up is the time before the test that went to the set-up of its class or module; it is in the first test of the class.", "",
              "| Test | Time, s | Set-up, s |", "| --- | --- | --- |"]
    lines += [f"| {r['id'].removeprefix('tests.')} | {r['seconds']:.1f} | {r['setup_s']:.1f} |" for r in slowest]
    text = "\n".join(lines) + "\n"
    (work / "summary.md").write_text(text, encoding="utf-8")
    (work / "summary.json").write_text(json.dumps({"ok": ok, "tests_run": tests_run, "wall_s": round(wall, 1), "problems": problems, "checks": checks,
                                                   "records": records, "files": files,
                                                   "shards": [{"name": n, "seconds": round(s, 1), "peak_mb": mb, "tests": c} for n, s, mb, c, _ in shard_rows],
                                                   "steps": [{"name": j.name, "code": j.code, "seconds": round(j.ended - j.started, 1), "peak_mb": j.peak_mb} for j in steps]},
                                                  indent=1), encoding="utf-8")
    times = dict(known)
    times.update({j.name: round(j.ended - j.started, 1) for j in jobs.values() if j.ended and j.code in (0, 1)})
    try:
        timings_file.write_text(json.dumps(times, indent=1, sort_keys=True), encoding="utf-8")
    except OSError:
        pass

    # the verdict as unittest gives it, at the end of the output
    print()
    for r in bad:
        print("=" * 70)
        print(f"{r['outcome'].upper()}: {r['id']}")
        print("-" * 70)
        print(r["text"].rstrip())
    for p in problems:
        print(f"PROBLEM: {p}")
    for c in checks:
        print(f"NOTE: {c}")
    print("-" * 70)
    print(f"Ran {tests_run} tests in {wall:.3f}s (parallel; summary: {work / 'summary.md'})")
    print()
    fails = sum(r["outcome"] == "fail" for r in bad)
    errors = len(bad) - fails
    extra = ", ".join(f"{k}={v}" for k, v in (("failures", fails), ("errors", errors), ("skipped", len(skipped))) if v)
    print("OK" + (f" ({extra})" if extra else "") if ok else f"FAILED ({extra or 'no tests ran'})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

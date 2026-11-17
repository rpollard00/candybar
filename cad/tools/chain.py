#!/usr/bin/env python3
"""Run the build chain with the independent steps side by side, each FreeCAD process in its own container.

    cad/tools/chain.py                      every step
    cad/tools/chain.py pieces mounts        these steps and the steps that they wait for
    cad/tools/chain.py -j 4 --local ...     at most 4 processes; --local: freecad-run.sh on this machine, no container

It runs under a plain Python 3.10 or later, not inside FreeCAD. A step starts when the steps that it reads are done
(STEPS). Each step is one process of cad/container/run.sh (cad/container/README.md): it has its own process table,
so the memory guard of freecad-run.sh stops only that step, and its memory limit is CANDYBAR_RSS_LIMIT_MB (default
here 24000: the split takes 12 GB). The log of each step goes to cad/out/chain/<step>.log and the times to
cad/out/chain/summary.md. Exit status: 0 when every step passed its own checks, 1 when a step's check failed (exit
status 1 of the module), 2 when a step broke (another status, or an exception: its log has a traceback).

The steps write into the folders of cad/README.md. Two steps never write the same file: the caches of the skin are
steps of their own (tools/build_caches.py), made before the steps that read them.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

CAD = Path(__file__).resolve().parents[1]
OUT = CAD / "out"
SHELL = OUT / "shell-rev7"
RUN = str(CAD / "candybar" / "freecad-run.sh")

# name: (command, environment, the steps that it reads)
STEPS: dict[str, tuple[list[str], dict[str, str], tuple[str, ...]]] = {
    "build": ([str(CAD / "build.sh")], {"CANDYBAR_OUT": str(SHELL)}, ()),
    "fit": ([RUN, "candybar.shell.fit"], {"CANDYBAR_OUT": str(SHELL)}, ()),
    "skin": ([RUN, "tools.build_caches"], {"CANDYBAR_CACHE": "skin", "CANDYBAR_OUT": str(OUT / "chain" / "skin")}, ()),
    "deck": ([RUN, "tools.build_caches"], {"CANDYBAR_CACHE": "deck", "CANDYBAR_OUT": str(OUT / "chain" / "deck")}, ("skin",)),
    "zones": ([RUN, "tools.build_caches"], {"CANDYBAR_CACHE": "zones", "CANDYBAR_OUT": str(OUT / "chain" / "zones")}, ("skin",)),
    "split": ([RUN, "candybar.shell.split"], {"CANDYBAR_OUT": str(SHELL)}, ("skin",)),
    "structure": ([RUN, "candybar.shell.structure"], {"CANDYBAR_OUT": str(SHELL)}, ("fit", "split")),
    "rear": ([RUN, "candybar.shell.rear"], {"CANDYBAR_OUT": str(SHELL)}, ("fit", "skin")),
    "check_solids": ([RUN, "tools.check_solids"], {"CANDYBAR_OUT": str(SHELL)}, ("build",)),
    "face_check": ([RUN, "tools.face_check"], {"CANDYBAR_OUT": str(SHELL)}, ("build",)),
    "edge_finish": ([RUN, "tools.edge_finish"], {"CANDYBAR_OUT": str(SHELL)}, ("build",)),
    "pieces": ([RUN, "candybar.shell.pieces"], {"CANDYBAR_OUT": str(OUT / "pieces")}, ("build", "split", "deck", "zones")),
    "coupons": ([RUN, "candybar.shell.coupons"], {"CANDYBAR_OUT": str(OUT / "coupons")}, ("build", "skin", "deck", "zones")),
    "coupon": ([RUN, "candybar.shell.coupon"], {"CANDYBAR_OUT": str(OUT / "coupon")}, ()),
    "mounts": ([RUN, "candybar.shell.mounts"], {"CANDYBAR_OUT": str(OUT / "mounts")}, ("build", "fit", "zones")),
    "panel": ([RUN, "candybar.shell.panel_frame"], {"CANDYBAR_OUT": str(OUT / "control-panel")}, ("build", "skin", "deck")),
    "cradle": ([RUN, "candybar.shell.cradle"], {"CANDYBAR_OUT": str(OUT / "cradle")}, ("build", "fit", "skin")),
    "hood_band": ([RUN, "candybar.shell.hood_band"], {"CANDYBAR_OUT": str(OUT / "hood-band")}, ("build", "skin")),
    "socket_plate": ([RUN, "candybar.shell.socket_plate"], {"CANDYBAR_SHELL": str(SHELL), "CANDYBAR_OUT": str(OUT / "socket-plate")}, ("build", "skin")),
    "cabinet": ([RUN, "candybar.shell.cabinet"], {"CANDYBAR_OUT": str(OUT / "cabinet")}, ("build", "cradle", "panel")),
}


def wanted(names: list[str]) -> list[str]:
    """The named steps and every step that they wait for, in the order of STEPS."""
    if not names:
        return list(STEPS)
    unknown = [n for n in names if n not in STEPS]
    if unknown:
        sys.exit(f"unknown steps {unknown}; the steps are {', '.join(STEPS)}")
    keep: set[str] = set()
    todo = list(names)
    while todo:
        n = todo.pop()
        if n not in keep:
            keep.add(n)
            todo += STEPS[n][2]
    return [n for n in STEPS if n in keep]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("steps", nargs="*", help="run these steps and what they wait for (default: all)")
    ap.add_argument("-j", "--jobs", type=int, default=int(os.environ.get("CANDYBAR_CHAIN_JOBS", 8)), help="processes at once")
    ap.add_argument("--local", action="store_true", help="run freecad-run.sh here, not in the container")
    args = ap.parse_args()
    names = wanted(args.steps)
    logs = OUT / "chain"
    logs.mkdir(parents=True, exist_ok=True)
    runner = [] if args.local else [str(CAD / "container" / "run.sh")]
    if not args.local and not shutil.which("docker"):
        sys.exit("docker is not here: use --local")
    base = dict(os.environ) | {"CANDYBAR_LOCK_HELD": "1", "CANDYBAR_RSS_LIMIT_MB": os.environ.get("CANDYBAR_RSS_LIMIT_MB", "24000")}
    if args.local:
        base.pop("CANDYBAR_LOCK_HELD")   # on this machine the lock of freecad-run.sh keeps one FreeCAD process at a time
    pending, running, done = list(names), {}, {}
    t0 = time.monotonic()
    print(f"chain: {len(names)} steps, {args.jobs} at once", flush=True)
    while pending or running:
        for n, (proc, start, handle) in list(running.items()):
            code = proc.poll()
            if code is None:
                continue
            handle.close()
            # freecad-run.sh gives 1 for a module that returns 1 (its check failed) and for an exception: the log tells
            if code == 1 and "Traceback (most recent call last)" in (logs / f"{n}.log").read_text(errors="replace"):
                code = 3
            done[n] = (code, start - t0, time.monotonic() - start)
            del running[n]
            word = {0: "pass"}.get(code, "CHECK FAILED" if code == 1 else "BROKE")
            print(f"  {word:12} {n}: {done[n][2]:.0f} s (at {time.monotonic() - t0:.0f} s)", flush=True)
        for n in list(pending):
            if len(running) >= args.jobs:
                break
            after = STEPS[n][2]
            if any(a in pending or a in running for a in after if a in names):
                continue
            pending.remove(n)
            if any(done.get(a, (0,))[0] not in (0, 1) for a in after):
                done[n] = (-1, 0.0, 0.0)
                print(f"  {'SKIPPED':12} {n}: a step that it reads broke", flush=True)
                continue
            cmd, env, _ = STEPS[n]
            handle = open(logs / f"{n}.log", "w")
            running[n] = (subprocess.Popen(runner + cmd, env=base | env, cwd=str(CAD.parent), stdout=handle, stderr=subprocess.STDOUT,
                                           stdin=subprocess.DEVNULL), time.monotonic(), handle)
        time.sleep(1.0)
    wall = time.monotonic() - t0
    rows = ["# The build chain", "", f"Wall time {wall:.0f} s ({wall / 60:.1f} min), {args.jobs} processes at once. "
            f"The sum of the step times: {sum(r[2] for r in done.values()):.0f} s.", "",
            "| Step | Result | Start, s | Time, s |", "| --- | --- | --- | --- |"]
    for n in names:
        code, start, seconds = done[n]
        word = {0: "pass", 1: "check failed", -1: "skipped"}.get(code, f"broke ({code})")
        rows.append(f"| {n} | {word} | {start:.0f} | {seconds:.0f} |")
    (logs / "summary.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("\n".join(rows[2:3]))
    codes = [r[0] for r in done.values()]
    return 0 if all(c == 0 for c in codes) else 1 if all(c in (0, 1) for c in codes) else 2


if __name__ == "__main__":
    sys.exit(main())

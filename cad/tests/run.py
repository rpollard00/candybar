"""The test runner, called by cad/test.sh and by cad/tests/parallel.py (through freecad-run.sh tests.run).

Environment:
  CANDYBAR_TESTS     run only the tests whose name contains this fragment
  CANDYBAR_TEST_IDS  run only the tests whose name contains one of these fragments (separated by spaces)
  CANDYBAR_RESULTS   write the result of each test to this JSON file: the outcome, the time, the text of a failure
  CANDYBAR_LIST      only list the names of the tests that would run, one on each line, to this file
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent


class TimedResult(unittest.TextTestResult):
    """A text result that also keeps, for each test, its outcome, its time, and the time before it that went to the
    set-up of its class or module (setUpClass, setUpModule and the functions they call)."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.records: list[dict] = []
        self.last = time.monotonic()
        self.current: dict | None = None

    def startTest(self, test) -> None:
        now = time.monotonic()
        self.current = {"id": test.id(), "outcome": "pass", "text": "", "setup_s": round(now - self.last, 3), "started": now}
        super().startTest(test)

    def stopTest(self, test) -> None:
        super().stopTest(test)
        now = time.monotonic()
        if self.current is not None:
            self.current["seconds"] = round(now - self.current.pop("started"), 3)
            self.records.append(self.current)
            self.current = None
        self.last = now

    def _record(self, test, outcome: str, text: str) -> None:
        if self.current is not None and self.current["id"] == test.id():
            if self.current["outcome"] == "pass" or outcome in ("error", "fail"):
                self.current["outcome"], self.current["text"] = outcome, text
        else:
            # a failure outside a test: setUpClass, setUpModule or a tearDown of a class
            self.records.append({"id": getattr(test, "description", None) or str(test), "outcome": outcome, "text": text,
                                 "setup_s": round(time.monotonic() - self.last, 3), "seconds": 0.0})
            self.last = time.monotonic()

    def addError(self, test, err) -> None:
        super().addError(test, err)
        self._record(test, "error", self._exc_info_to_string(err, test))

    def addFailure(self, test, err) -> None:
        super().addFailure(test, err)
        self._record(test, "fail", self._exc_info_to_string(err, test))

    def addSubTest(self, test, subtest, err) -> None:
        super().addSubTest(test, subtest, err)
        if err is not None:
            kind = "fail" if issubclass(err[0], test.failureException) else "error"
            text = f"{subtest}\n{self._exc_info_to_string(err, test)}"
            if self.current is not None and self.current["id"] == test.id() and self.current["outcome"] in ("error", "fail"):
                self.current["text"] += "\n" + text
            else:
                self._record(test, kind, text)

    def addSkip(self, test, reason) -> None:
        super().addSkip(test, reason)
        self._record(test, "skip", reason)

    def addExpectedFailure(self, test, err) -> None:
        super().addExpectedFailure(test, err)
        self._record(test, "expected failure", self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test) -> None:
        super().addUnexpectedSuccess(test)
        self._record(test, "unexpected success", "")


def tests_of(suite) -> list:
    out = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            out += tests_of(item)
        else:
            out.append(item)
    return out


def main() -> int:
    started = time.monotonic()
    loader = unittest.TestLoader()
    patterns = os.environ.get("CANDYBAR_TEST_IDS", "").split()
    if only := os.environ.get("CANDYBAR_TESTS"):
        patterns.append(only)
    if patterns:
        loader.testNamePatterns = [f"*{p}*" for p in patterns]
    suite = loader.discover(str(TESTS), top_level_dir=str(TESTS.parent))
    loaded = time.monotonic() - started
    if listing := os.environ.get("CANDYBAR_LIST"):
        # A module that does not import shows as a _FailedTest: it is listed, so that the caller runs it and sees why.
        Path(listing).write_text("".join(f"{t.id()}\n" for t in tests_of(suite)), encoding="utf-8")
        return 0
    from . import support

    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2, resultclass=TimedResult)
    result = None
    try:
        result = runner.run(suite)
    finally:
        support.remove_temp_dirs()
        if results := os.environ.get("CANDYBAR_RESULTS"):
            records = result.records if result is not None else []
            if result is None:
                records = [{"id": "tests.run", "outcome": "error", "text": traceback.format_exc(), "setup_s": 0.0, "seconds": 0.0}]
            Path(results).write_text(json.dumps({"load_s": round(loaded, 3), "wall_s": round(time.monotonic() - started, 3),
                                                 "tests_run": result.testsRun if result else 0, "records": records}, indent=1),
                                     encoding="utf-8")
    return 0 if result.wasSuccessful() and result.testsRun else 1

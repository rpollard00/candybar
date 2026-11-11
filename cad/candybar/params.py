from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import FreeCAD as App

SHEET = "Params"
FILES = ("printer.csv", "hardware.csv", "controls.csv", "cabinet.csv")
COLUMNS = ("name", "value", "unit", "status", "measure", "source", "note")
STATUSES = ("measured", "sourced", "provisional", "derived")

_HEADINGS = (*COLUMNS, "file")
_LETTERS = "ABCDEFGH"
_VALUE_COLUMN = "B"
_FIRST_ROW = 2
_ALIAS = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")
_CELL_ADDRESS = re.compile(r"[A-Za-z]{1,2}[0-9]+\Z")


class ParamError(ValueError):
    """A parameter row that cannot be loaded, named by file and row."""


@dataclass(frozen=True)
class Param:
    name: str
    value: str
    unit: str
    status: str
    measure: str
    source: str
    note: str
    file: str
    row: int

    @property
    def origin(self) -> str:
        return f"{self.file} row {self.row} ({self.name!r})"

    @property
    def cell_text(self) -> str:
        return self.value if self.value.startswith("=") else _literal(self.value, self.unit)


def _literal(value: str, unit: str) -> str:
    # FreeCAD reads "354 mm" as a quantity but "-75 mm" as a text string, so a
    # literal with a unit is written in the "=" form, which FreeCAD stores anyway.
    return f"={value} {unit}" if unit else value


def load(params_dir: Path) -> list[Param]:
    loaded: list[Param] = []
    first_seen: dict[str, Param] = {}
    for filename in FILES:
        with (params_dir / filename).open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != COLUMNS:
                raise ParamError(f"{filename}: the header must be {','.join(COLUMNS)}")
            for record in reader:
                if None in record or None in record.values():
                    raise ParamError(f"{filename} row {reader.line_num}: expected {len(COLUMNS)} fields")
                param = Param(**{key: text.strip() for key, text in record.items()}, file=filename, row=reader.line_num)
                _validate(param, first_seen)
                first_seen[param.name] = param
                loaded.append(param)
    return loaded


def _validate(param: Param, first_seen: dict[str, Param]) -> None:
    if not _ALIAS.match(param.name) or _CELL_ADDRESS.match(param.name):
        raise ParamError(
            f"{param.origin}: not a legal alias. Use letters, digits and underscores, "
            "start with a letter, and avoid names that read as a cell address such as A1 or BC250"
        )
    if param.name in first_seen:
        raise ParamError(f"{param.origin}: duplicate name, first defined in {first_seen[param.name].origin}")
    if param.status not in STATUSES:
        raise ParamError(f"{param.origin}: unknown status {param.status!r}. Use one of {', '.join(STATUSES)}")
    if not param.value.startswith("=") and not _is_number(param.value):
        raise ParamError(f"{param.origin}: value {param.value!r} is neither a number nor a formula starting with '='")


def _is_number(text: str) -> bool:
    try:
        return math.isfinite(float(text))
    except ValueError:
        return False


def write_sheet(doc: App.Document, rows: Sequence[Param]) -> App.DocumentObject:
    sheet = doc.addObject("Spreadsheet::Sheet", SHEET)
    for letter, heading in zip(_LETTERS, _HEADINGS, strict=True):
        _set_text(sheet, f"{letter}1", heading)
    # Every alias exists before any formula is written. FreeCAD records what a formula depends on
    # when it is written: a formula that names a parameter from a later row would otherwise keep
    # a stale value when that parameter changes.
    for number, param in enumerate(rows, start=_FIRST_ROW):
        try:
            sheet.setAlias(f"{_VALUE_COLUMN}{number}", param.name)
        except ValueError as error:
            raise ParamError(
                f"{param.origin}: FreeCAD rejects this name as an alias (unit and constant names are reserved)"
            ) from error
    for number, param in enumerate(rows, start=_FIRST_ROW):
        sheet.set(f"{_VALUE_COLUMN}{number}", param.cell_text)
        texts = (param.name, None, param.unit, param.status, param.measure, param.source, param.note, param.file)
        for letter, text in zip(_LETTERS, texts, strict=True):
            if text:
                _set_text(sheet, f"{letter}{number}", text)
    doc.recompute()
    for param in rows:
        _check_evaluated(sheet, param)
    return sheet


def _set_text(sheet: App.DocumentObject, cell: str, text: str) -> None:
    # The leading apostrophe stops FreeCAD from parsing the text as a number or a formula.
    sheet.set(cell, "'" + text)


def _check_evaluated(sheet: App.DocumentObject, param: Param) -> None:
    result = sheet.get(param.name)
    if isinstance(result, str):
        raise ParamError(f"{param.origin}: {param.value!r} does not evaluate: {result}")
    expected = App.Units.Quantity(f"1 {param.unit}").Unit if param.unit else App.Units.Unit()
    actual = result.Unit if isinstance(result, App.Units.Quantity) else App.Units.Unit()
    if actual != expected:
        raise ParamError(f"{param.origin}: evaluates to {result}, which does not match the unit column {param.unit!r}")


def value(doc: App.Document, name: str) -> float:
    """The evaluated value of one parameter, in mm or degrees."""
    result = doc.getObject(SHEET).get(name)
    if isinstance(result, str):
        raise ParamError(f"{name!r} does not evaluate: {result}")
    return float(getattr(result, "Value", result))


def edit(doc: App.Document, name: str, number: float) -> None:
    """Overwrite one parameter with a literal, keeping its unit. The caller recomputes."""
    sheet = doc.getObject(SHEET)
    cell = sheet.getCellFromAlias(name)
    if cell is None:
        raise ParamError(f"no parameter named {name!r}")
    sheet.set(cell, _literal(repr(float(number)), _text(sheet, f"C{cell[1:]}")))


def table(doc: App.Document) -> list[dict[str, str]]:
    """One dict per parameter row: the text columns, with `value` as the evaluated number and unit."""
    sheet = doc.getObject(SHEET)
    rows: list[dict[str, str]] = []
    number = _FIRST_ROW
    while name := _text(sheet, f"A{number}"):
        row = {heading: _text(sheet, f"{letter}{number}") for letter, heading in zip(_LETTERS, _HEADINGS, strict=True)}
        rows.append(row | {"value": f"{value(doc, name):.6g} {row['unit']}".strip()})
        number += 1
    return rows


def _text(sheet: App.DocumentObject, cell: str) -> str:
    return sheet.getContents(cell).removeprefix("'")

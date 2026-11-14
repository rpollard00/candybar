"""The joint values have one source: candybar.shell.joints (Joint and OtherJoints). A second module that sets a joint
value as a literal number fails here, so that the joint sheet, the split report and the coupon cannot drift apart again.
"""
from __future__ import annotations

import ast
import unittest
from dataclasses import fields
from pathlib import Path

from candybar.shell import joints, structure
from candybar.shell.dims import Blueprint

CAD = Path(__file__).resolve().parents[1]
SOURCE = CAD / "candybar" / "shell" / "joints.py"
# the names of the second copy that structure.JOINT held until 2026-11-11, beside the names of joints.py
OLD_NAMES = {"flange_w", "key_h", "key_clearance", "groove_w", "groove_d"}
# the skin (wall_t) belongs to the form: dims.Blueprint sets it, and Joint reads it from there
NAMES = ({f.name for f in fields(joints.Joint)} | {f.name for f in fields(joints.OtherJoints)} | OLD_NAMES) - {"wall_t"}


def number(node: ast.AST | None) -> bool:
    if isinstance(node, ast.UnaryOp):
        node = node.operand
    return isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool)


def second_copies(text: str) -> list[tuple[int, str]]:
    """Places where a joint value is set to a literal number: a dict entry, a keyword, a class field, an assignment
    to a name or a subscript. Calls of dataclasses.replace on JOINT are a change of a value, not a copy: they pass."""
    found = []
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Dict):
            found += [(k.lineno, k.value) for k, v in zip(node.keys, node.values)
                      if isinstance(k, ast.Constant) and k.value in NAMES and number(v)]
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "replace":
                continue
            found += [(node.lineno, k.arg) for k in node.keywords if k.arg in NAMES and number(k.value)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id in NAMES and number(node.value):
                found.append((node.lineno, node.target.id))
        elif isinstance(node, ast.Assign) and number(node.value):
            for t in node.targets:
                name = t.id if isinstance(t, ast.Name) else (t.slice.value if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) else None)
                if name in NAMES:
                    found.append((node.lineno, name))
    return found


class OneSourceTest(unittest.TestCase):
    def test_structure_has_no_joint_constants_of_its_own(self) -> None:
        self.assertEqual([n for n in vars(structure) if "JOINT" in n.upper()], [])

    def test_no_module_but_joints_sets_a_joint_value(self) -> None:
        files = sorted((CAD / "candybar").rglob("*.py")) + sorted((CAD / "tools").glob("*.py"))
        hits = {}
        for path in files:
            if path == SOURCE:
                continue
            if found := second_copies(path.read_text(encoding="utf-8")):
                hits[str(path.relative_to(CAD))] = found
        self.assertEqual(hits, {})

    def test_the_check_finds_the_old_copy(self) -> None:
        """The dict that structure.py held must be found, so that the test above can fail."""
        old = 'JOINT = {"flange_w": 6.0, "flange_h": 12.0, "key_w": 1.5, "screw_pitch": 60.0, "insert": "M4"}'
        self.assertEqual({n for _, n in second_copies(old)}, {"flange_w", "flange_h", "key_w", "screw_pitch"})
        self.assertEqual(second_copies("class J:\n    pin_d: float = 4.0\n"), [(2, "pin_d")])
        self.assertEqual(second_copies("j = replace(JOINT, pilot_d=2.25)\n"), [])

    def test_the_skin_of_the_joint_is_the_skin_of_the_form(self) -> None:
        self.assertEqual(joints.JOINT.wall_t, Blueprint().wall_t)

    def test_the_pilot_of_the_cabinet_stays_open_until_the_coupon_decides(self) -> None:
        self.assertIsNone(joints.JOINT.pilot_d)
        self.assertLess(joints.JOINT.pilot_d_pet, joints.JOINT.pilot_d_abs)


if __name__ == "__main__":
    unittest.main()

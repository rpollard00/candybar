"""Rectify planes of a reference photo and measure distances, ratios, angles and radii in them.

Everything comes from the annotation file (cad/reference/<photo-stem>.json, see photo_annot.py).

Camera: square pixels, principal point at the image centre (or "c_px"), focal length "f_px" given, or found
from two vanishing points of orthogonal 3D directions ("f_from": "vanishing:x,z"), or from a rectangle of
known aspect ("f_from": "plane:screen").

Planes:
  {"rect": [tl, tr, br, bl], "size_mm": [w, h]}   metric, needs no camera
  {"rect": [...], "aspect": w_over_h}              metric up to scale (units of the rectangle height)
  {"rect": [...]}                                   aspect from the camera
  {"vanishing": [u, v]}                             a plane spanned by two 3D directions, from the camera;
                                                    every plane parallel to it rectifies with the same map
  Any plane takes "scale": [a, b, mm] to set millimetres from one known length.
Plane axes: u along the first edge (tl to tr) or the first direction, v at right angles, pointing down the
image. A point measured in a plane must lie in that plane; a point in front of or behind it reads wrong.

Measures (each {"name", "kind", ...}; "plane" for the planar kinds):
  distance [a, b]      length;  du / dv [a, b]  component along the plane axes
  angle [a, b] or [a, b, c, d]   angle of ab to the u axis, or of ab to cd, degrees
  radius [p, q, r, ...]          least-squares circle radius
  line_ratio "vanishing": name, [a, b, c, d]    |ab| / |cd| for four points on one 3D line with that direction
  tilt "plane", "direction"      angle of the plane to a vanishing direction (0 = the plane contains it)
  angle3d [u, v] (vanishing names)                angle between two 3D directions
  ratio / product / sum / diff "of": [measure, measure]      on earlier measures
  f                                                 focal length in pixels
Uncertainty: each picked point (not derived) is moved by its sigma (default 1 px) in x and in y; the change
of each measure is combined as a root sum of squares.

Writes cad/out/photo-evidence/<photo-stem>/measures.json and rectified-<plane>.png.

Example:
    cad/.venv-tools/bin/python cad/tools/photo_rectify.py cad/reference/photo-b.json
"""
from __future__ import annotations

import argparse
import json
import math
import os

import cv2
import numpy as np

import photo_annot as pa


def hom(p) -> np.ndarray:
    return np.array([p[0], p[1], 1.0])


def vanishing_point(lines: list[np.ndarray]) -> np.ndarray:
    a = np.array([l / np.linalg.norm(l[:2]) for l in lines])
    _, _, vt = np.linalg.svd(a)
    return vt[-1]


def homography(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    rows = []
    for (x, y), (u, v) in zip(src, dst):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, vt = np.linalg.svd(np.array(rows, float))
    return vt[-1].reshape(3, 3) / vt[-1][-1]


def apply(h: np.ndarray, p: pa.Point) -> np.ndarray:
    q = h @ hom(p)
    return q[:2] / q[2]


_CIRCLE_CACHE: dict = {}


def find_holes(image: np.ndarray, box: list[int], min_area: float, max_area: float,
               threshold: float | None = None) -> list[np.ndarray]:
    """Outlines of dark holes in a light surface; with a threshold, the lit inner wall counts as hole."""
    x0, y0, x1, y1 = box
    g = cv2.cvtColor(image[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    if threshold is None:
        _, t = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        t = (g < threshold).astype(np.uint8) * 255
        t = cv2.morphologyEx(t, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cs, _ = cv2.findContours(t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        a = cv2.contourArea(c)
        if min_area < a < max_area and len(c) > 20:
            (w, h) = cv2.fitEllipse(c)[1]
            if min(w, h) / max(w, h) > 0.35:
                out.append(c.reshape(-1, 2).astype(float) + [x0, y0])
    return out


def _roundness(q: np.ndarray) -> tuple[float, float]:
    (_, _), (w, h), _ = cv2.fitEllipse(q.astype(np.float32))
    return (max(w, h) - min(w, h)) / (w + h), (w + h) / 2


def circle_homography(ann: pa.Annotation, spec: dict) -> tuple[np.ndarray, list[np.ndarray]]:
    """Homography that maps the outlines of holes known to be circles in one plane to circles.

    Model: H = A @ P, P = [[1,0,0],[0,1,0],[l1,l2,1]] (the vanishing line) and A = [[1,a,0],[0,b,0],[0,0,1]]
    (the affine part up to a similarity), in coordinates centred on the holes. Fitted by least squares on
    the ellipse roundness of every mapped outline."""
    key = (ann.path, json.dumps(spec, sort_keys=True))
    if key in _CIRCLE_CACHE:
        return _CIRCLE_CACHE[key]
    from scipy.optimize import least_squares
    holes = find_holes(ann.image, spec["box"], spec.get("min_area", 150), spec.get("max_area", 5000),
                       spec.get("threshold"))
    c = np.vstack(holes).mean(0)
    s = 1.0 / np.ptp(np.vstack(holes), axis=0).max()
    N = np.array([[s, 0, -s * c[0]], [0, s, -s * c[1]], [0, 0, 1]])

    def H_of(p: np.ndarray) -> np.ndarray:
        P = np.array([[1, 0, 0], [0, 1, 0], [p[0], p[1], 1.0]])
        A = np.array([[1, p[2], 0], [0, p[3], 0], [0, 0, 1.0]])
        return A @ P @ N

    def mapped(H: np.ndarray, q: np.ndarray) -> np.ndarray:
        r = (H @ np.column_stack([q, np.ones(len(q))]).T).T
        return r[:, :2] / r[:, 2:]

    def resid(p: np.ndarray) -> np.ndarray:
        H = H_of(p)
        return np.array([_roundness(mapped(H, q) * 1000)[0] for q in holes])

    best = None
    for l1 in np.linspace(-1.5, 1.5, 5):
        for l2 in np.linspace(-1.5, 1.5, 5):
            for b in (1.0, 1.5, 2.5):
                r = least_squares(resid, [l1, l2, 0.0, b], loss="soft_l1", f_scale=0.03)
                if best is None or r.cost < best.cost:
                    best = r
    keep = resid(best.x) < 3 * np.median(resid(best.x))
    if not keep.all():
        holes = [q for q, k in zip(holes, keep) if k]
        best = least_squares(resid, best.x, loss="soft_l1", f_scale=0.03)
    H = H_of(best.x)
    k = 1000.0
    H = np.diag([k, k, 1.0]) @ H
    _CIRCLE_CACHE[key] = (H, holes)
    return H, holes


def circle_report(ann: pa.Annotation, spec: dict) -> list[tuple[float, float, float, float]]:
    """Centre u, v, roundness before and after, and diameter of every hole in the rectified plane."""
    H, holes = circle_homography(ann, spec)
    out = []
    for q in holes:
        r = (H @ np.column_stack([q, np.ones(len(q))]).T).T
        m = r[:, :2] / r[:, 2:]
        before = _roundness(q)[0]
        after, d = _roundness(m)
        out.append((*m.mean(0), before, after, d))
    return out


def fit_circle(q: np.ndarray) -> tuple[np.ndarray, float]:
    a = np.column_stack([2 * q[:, 0], 2 * q[:, 1], np.ones(len(q))])
    b = (q ** 2).sum(1)
    sol = np.linalg.lstsq(a, b, rcond=None)[0]
    c = sol[:2]
    return c, float(math.sqrt(sol[2] + c @ c))


class Scene:
    """The camera and planes of one photo, computed from one set of point positions."""

    def __init__(self, ann: pa.Annotation, pts: dict[str, pa.Point]):
        self.ann, self.pts, self.data = ann, pts, ann.data
        w, h = ann.size
        cam = self.data.get("camera", {})
        self.c = np.array(cam.get("c_px", [w / 2, h / 2]), float)
        self.lines = {k: pa.line_through([pts[m] for m in v]) for k, v in self.data.get("lines", {}).items()}
        self.vps = {k: vanishing_point([self.lines[l] for l in v]) for k, v in self.data.get("vanishing", {}).items()}
        self.f = self._focal(cam)
        self.K = np.array([[self.f, 0, self.c[0]], [0, self.f, self.c[1]], [0, 0, 1]]) if self.f else None
        self.planes: dict[str, dict] = {}
        for name, spec in self.data.get("planes", {}).items():
            self.planes[name] = self._plane(spec)

    def direction(self, vp_name: str) -> np.ndarray:
        d = np.linalg.solve(self.K, self.vps[vp_name])
        return d / np.linalg.norm(d)

    def _focal(self, cam: dict) -> float | None:
        if "f_px" in cam:
            return float(cam["f_px"])
        src = cam.get("f_from", "")
        if src.startswith("vanishing:"):
            names = src.split(":")[1].split(",")
            est = []
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = self.vps[names[i]], self.vps[names[j]]
                    a2, b2 = a[:2] / a[2] - self.c, b[:2] / b[2] - self.c
                    est.append(-(a2 @ b2))
            f2 = float(np.mean(est))
            return math.sqrt(f2) if f2 > 0 else None
        if src.startswith("plane:"):
            spec = self.data["planes"][src.split(":")[1]]
            hu = self._unit_h(spec)
            aspect = spec.get("aspect") or spec["size_mm"][0] / spec["size_mm"][1]

            def resid(f: float, cy: float) -> np.ndarray:
                m = np.linalg.solve(np.array([[f, 0, self.c[0]], [0, f, cy], [0, 0, 1]]), hu)
                m1, m2 = m[:, 0], m[:, 1]
                return np.array([(m1 @ m2) / (np.linalg.norm(m1) * np.linalg.norm(m2)),
                                 np.linalg.norm(m1) / np.linalg.norm(m2) / aspect - 1])

            size = max(self.ann.size)
            fs = np.geomspace(0.2, 20, 150) * size
            cys = np.linspace(-1.0, 2.0, 61) * self.ann.size[1] if cam.get("solve_cy") else [self.c[1]]
            best = min(((resid(f, cy) ** 2).sum(), f, cy) for f in fs for cy in cys)
            if cam.get("solve_cy"):
                from scipy.optimize import least_squares
                sol = least_squares(lambda p: resid(p[0], p[1]), [best[1], best[2]])
                self.c[1] = sol.x[1]
                return float(sol.x[0])
            from scipy.optimize import minimize_scalar
            sol = minimize_scalar(lambda f: (resid(f, self.c[1]) ** 2).sum(), bounds=(best[1] / 1.05, best[1] * 1.05),
                                  method="bounded")
            return float(sol.x)
        return None

    def _unit_h(self, spec: dict) -> np.ndarray:
        img = np.array([self.pts[c] for c in spec["rect"]])
        return homography(np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float), img)

    def _plane(self, spec: dict) -> dict:
        normal = None
        if "rect" in spec:
            img = np.array([self.pts[c] for c in spec["rect"]])
            if "size_mm" in spec:
                w, h = spec["size_mm"]
                units = "mm"
            else:
                aspect = spec.get("aspect")
                if aspect is None:
                    m = np.linalg.solve(self.K, self._unit_h(spec))
                    aspect = np.linalg.norm(m[:, 0]) / np.linalg.norm(m[:, 1])
                w, h = aspect, 1.0
                units = "rect heights"
            H = homography(img, np.array([[0, 0], [w, 0], [w, h], [0, h]], float))
            if self.K is not None:
                m = np.linalg.solve(self.K, np.linalg.inv(H))
                normal = np.cross(m[:, 0], m[:, 1])
                normal /= np.linalg.norm(normal)
        elif "circles" in spec:
            H, _ = circle_homography(self.ann, spec["circles"])
            units = "plane units"
        else:
            du, dv = (self.direction(n) for n in spec["vanishing"])
            eu = du
            normal = np.cross(du, dv)
            normal /= np.linalg.norm(normal)
            ev = np.cross(normal, eu)
            H = np.vstack([eu, ev, normal]) @ np.linalg.inv(self.K)
            units = "plane-distance units"
            p0 = self.c + np.array([0.0, 0.0])
            a, b = apply(H, p0), apply(H, p0 + [10, 0])
            flip_u = (b - a)[0] < 0
            a2 = apply(H, p0 + [0, 10])
            flip_v = (a2 - a)[1] < 0
            H = np.diag([-1.0 if flip_u else 1.0, -1.0 if flip_v else 1.0, 1.0]) @ H
        if "scale" in spec:
            a, b, mm = spec["scale"]
            k = mm / np.linalg.norm(apply(H, self.pts[a]) - apply(H, self.pts[b]))
            H = np.diag([k, k, 1.0]) @ H
            units = "mm"
        return {"H": H, "units": units, "normal": normal}

    def xy(self, plane: str, p: str) -> np.ndarray:
        return apply(self.planes[plane]["H"], self.pts[p])

    def measure(self, m: dict, done: dict[str, float]) -> float:
        k = m["kind"]
        if k in ("ratio", "product", "sum", "diff"):
            a, b = (done[n] for n in m["of"])
            return {"ratio": a / b, "product": a * b, "sum": a + b, "diff": a - b}[k]
        if k == "f":
            return float(self.f)
        if k == "line_ratio":
            v = self.vps[m["vanishing"]]
            q = np.array([self.pts[p] for p in m["points"]])
            c = q.mean(0)
            d = np.linalg.svd(q - c)[2][0]
            s = (q - c) @ d
            sv = ((v[:2] - c * v[2]) @ d) / v[2] if abs(v[2]) > 1e-12 else math.inf
            t = 1.0 / (sv - s) if math.isfinite(sv) else s
            return float(abs(t[1] - t[0]) / abs(t[3] - t[2]))
        if k == "tilt":
            n = self.planes[m["plane"]]["normal"]
            d = self.direction(m["direction"])
            return math.degrees(math.asin(min(1.0, abs(float(n @ d)))))
        if k == "angle3d":
            a, b = (self.direction(n) for n in m["of"])
            return math.degrees(math.acos(min(1.0, abs(float(a @ b)))))
        if k in ("angle_lines", "meet_u", "meet_v"):
            a, b = (np.array([self.xy(m["plane"], p) for p in g]) for g in m["lines"])
            la, lb = pa.line_through(list(map(tuple, a))), pa.line_through(list(map(tuple, b)))
            if k == "angle_lines":
                ang = math.degrees(math.atan2(la[1], la[0]) - math.atan2(lb[1], lb[0]))
                ang = (ang + 90) % 180 - 90
                return ang
            q = np.cross(la, lb)
            return float(q[0] / q[2] if k == "meet_u" else q[1] / q[2])
        q = np.array([self.xy(m["plane"], p) for p in m["points"]])
        if k == "u":
            return float(q[0][0])
        if k == "distance":
            return float(np.linalg.norm(q[1] - q[0]))
        if k == "du":
            return float(q[1][0] - q[0][0])
        if k == "dv":
            return float(q[1][1] - q[0][1])
        if k == "angle":
            a = math.degrees(math.atan2(q[1][1] - q[0][1], q[1][0] - q[0][0]))
            if len(q) == 4:
                a -= math.degrees(math.atan2(q[3][1] - q[2][1], q[3][0] - q[2][0]))
            return (a + 180) % 360 - 180
        if k == "radius":
            return fit_circle(q)[1]
        raise SystemExit(f"measure {m['name']}: unknown kind {k}")

    def all(self) -> dict[str, float]:
        done: dict[str, float] = {}
        for m in self.data.get("measures", []):
            done[m["name"]] = self.measure(m, done)
        return done


def evaluate(ann: pa.Annotation) -> tuple[Scene, dict[str, float], dict[str, float]]:
    base = ann.base_points()
    nominal = {k: (v[0], v[1]) for k, v in base.items()}
    scene = Scene(ann, ann.resolve(nominal))
    values = scene.all()
    var = {k: 0.0 for k in values}
    for name, (x, y, s) in base.items():
        for axis in (0, 1):
            res = []
            for sign in (1, -1):
                moved = dict(nominal)
                p = [x, y]
                p[axis] += sign * s
                moved[name] = (p[0], p[1])
                res.append(Scene(ann, ann.resolve(moved)).all())
            for k in values:
                var[k] += ((res[0][k] - res[1][k]) / 2) ** 2
    return scene, values, {k: math.sqrt(v) for k, v in var.items()}


def rectified_image(scene: Scene, name: str, max_px: int = 1300) -> str:
    plane = scene.planes[name]
    H = plane["H"]
    spec = scene.data["planes"][name]
    used = set(spec.get("rect", []))
    for m in scene.data.get("measures", []):
        if m.get("plane") == name:
            used.update(m.get("points", []))
            used.update(p for g in m.get("lines", []) for p in g)
    used.update(spec.get("show", []))
    q = np.array([apply(H, scene.pts[p]) for p in used])
    lo, hi = q.min(0), q.max(0)
    pad = 0.12 * (hi - lo).max()
    lo, hi = lo - pad, hi + pad
    k = max_px / (hi - lo).max()
    S = np.array([[k, 0, -lo[0] * k], [0, k, -lo[1] * k], [0, 0, 1]])
    size = (int((hi - lo)[0] * k), int((hi - lo)[1] * k))
    img = cv2.warpPerspective(scene.ann.image, S @ H, size, flags=cv2.INTER_CUBIC)
    for i, (label, group) in enumerate(spec.get("draw_lines", {}).items()):
        q2 = np.array([apply(H, scene.pts[p]) for p in group]) * k - lo * k
        line = pa.line_through(list(map(tuple, q2)))
        d = np.array([line[1], -line[0]])
        t = (q2 - q2.mean(0)) @ d
        a, b = q2.mean(0) + d * (t.min() - 80), q2.mean(0) + d * (t.max() + 80)
        col = pa.COLORS[(i + 1) % len(pa.COLORS)]
        cv2.line(img, tuple(int(v) for v in a), tuple(int(v) for v in b), col, 2, cv2.LINE_AA)
        ang = math.degrees(math.atan2(d[1], d[0]))
        pa.text(img, f"{label} {((ang + 90) % 180 - 90):+.1f} deg", tuple(int(v) for v in b + [5, 15]), col, 0.55)
    for p in sorted(used):
        x, y = (S @ hom(apply(H, scene.pts[p])))[:2] / (S @ hom(apply(H, scene.pts[p])))[2]
        cv2.drawMarker(img, (int(x), int(y)), (0, 0, 255), cv2.MARKER_CROSS, 12, 1, cv2.LINE_AA)
        pa.text(img, p, (int(x) + 5, int(y) - 5), (0, 0, 255), 0.4)
    pa.text(img, f"plane {name}: {k:.2f} px per {plane['units'].rstrip('s')}", (10, 20), (0, 0, 0), 0.55)
    path = os.path.join(pa.out_dir(scene.ann), f"rectified-{name}.png")
    cv2.imwrite(path, img)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("annotation")
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    ann = pa.load(a.annotation)
    scene, values, sigma = evaluate(ann)
    units = {}
    for m in ann.data.get("measures", []):
        if "plane" in m and m["kind"] in ("distance", "du", "dv", "radius"):
            units[m["name"]] = scene.planes[m["plane"]]["units"]
        elif m["kind"] in ("angle", "tilt", "angle3d"):
            units[m["name"]] = "deg"
        else:
            units[m["name"]] = "px" if m["kind"] == "f" else ""
    if scene.f:
        print(f"camera: f = {scene.f:.0f} px, principal point {scene.c.round(1).tolist()}")
    for name, vp in scene.vps.items():
        if abs(vp[2]) > 1e-9:
            print(f"vanishing {name}: ({vp[0] / vp[2]:.0f}, {vp[1] / vp[2]:.0f})")
    for m in ann.data.get("measures", []):
        n = m["name"]
        print(f"{n:34s} {values[n]:10.4f} +- {sigma[n]:.4f} {units[n]}")
    out = {"photo": ann.data["photo"], "f_px": scene.f,
           "measures": {n: {"value": values[n], "sigma": sigma[n], "units": units[n]} for n in values}}
    d = pa.out_dir(ann)
    with open(os.path.join(d, "measures.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for name, spec in ann.data.get("planes", {}).items():
        if "circles" in spec:
            print(f"plane {name}: holes as circles (centre u, v; ellipse roundness before -> after; diameter)")
            for u, v, b, r, dd in circle_report(ann, spec["circles"]):
                print(f"  ({u:8.1f}, {v:8.1f})  {b:.3f} -> {r:.4f}  d {dd:.2f}")
    if not a.no_images:
        for name in scene.planes:
            print(f"photo_rectify: {os.path.relpath(rectified_image(scene, name), pa.REPO)}")


if __name__ == "__main__":
    main()

"""Model against photo: fit the camera of a reference photo to a 3D model and draw the model over the photo.

The annotation file (cad/reference/<photo-stem>.json) holds an "overlay" section:
  {"model": "cad/vendor/mini-new-astro-city/assembled",       a directory with manifest.json (render_views.py)
   "anchors": {"photo point name": [x, y, z], ...},          model coordinates in mm, project frame
   "plane": ["bz_tl", "bz_tr", "bz_br", "bz_bl"],           anchors that lie in the screen face
   "f_px": 2268}                                              optional; else fitted with the pose
The camera principal point is the annotation's camera "c_px" (default: image centre).

Two fits:
  full   all anchors: the pose and, unless given, the focal length (least squares on reprojection error)
  plane  the screen face anchors only, with the focal length of the full fit: the model's screen face is put
         on the photo's screen face and the rest of the model falls where it falls. For a model with other
         proportions this shows how its hood, rails and deck sit against the photo's.
Each fit renders the model through the fitted camera with render_views.py (Blender in background mode, the
script is called, not changed) and writes to cad/out/photo-evidence/<photo-stem>/overlay-<fit>/:
  outline.png  photo with the model outline (silhouette and creases) in cyan
  blend.png    photo and render half and half
  diff.png     edges of the photo in red, of the model in cyan, both in white
  camera.json  pose, focal length and the reprojection error of every anchor

Example:
    cad/.venv-tools/bin/python cad/tools/photo_overlay.py cad/reference/photo-e-three-quarter.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import tempfile

import cv2
import numpy as np
from scipy.optimize import least_squares

import photo_annot as pa
import render_views as rv

RENDER_VIEWS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_views.py")
KEY = (1.0, 0.0, 1.0)


def project(params: np.ndarray, f: float, c: np.ndarray, X: np.ndarray) -> np.ndarray:
    R, _ = cv2.Rodrigues(params[:3])
    Xc = X @ R.T + params[3:6]
    return f * Xc[:, :2] / Xc[:, 2:] + c


def fit(X: np.ndarray, x: np.ndarray, c: np.ndarray, f0: float, fit_f: bool,
        size: tuple[int, int]) -> tuple[np.ndarray, float]:
    best = None
    for f in ([f0] if not fit_f else np.geomspace(0.4, 4, 25) * max(size)):
        K = np.array([[f, 0, c[0]], [0, f, c[1]], [0, 0, 1]])
        flag = cv2.SOLVEPNP_SQPNP if len(X) >= 4 else cv2.SOLVEPNP_ITERATIVE
        ok, rv, tv = cv2.solvePnP(X, x, K, None, flags=flag)
        if not ok:
            continue
        p0 = np.r_[rv.ravel(), tv.ravel(), f]

        def r(p: np.ndarray) -> np.ndarray:
            return (project(p[:6], p[6] if fit_f else f, c, X) - x).ravel()

        sol = least_squares(r, p0, x_scale="jac")
        err = float(np.sqrt(np.mean(sol.fun ** 2)))
        if best is None or err < best[0]:
            best = (err, sol.x)
    _, p = best
    return p[:6], float(p[6]) if fit_f else f0


def render(model: str, params: np.ndarray, f: float, c: np.ndarray, size: tuple[int, int], out: str,
           scale: float, blender: str) -> np.ndarray:
    """Render the model through the camera; return the RGB render cropped to the photo (key colour = empty)."""
    w, h = size
    half = (max(c[0], w - c[0]) * scale, max(c[1], h - c[1]) * scale)
    res = (int(math.ceil(2 * half[0])), int(math.ceil(2 * half[1])))
    R, _ = cv2.Rodrigues(params[:3])
    loc = -R.T @ params[3:6]
    forward, right, up = R.T @ [0, 0, 1.0], R.T @ [1.0, 0, 0], R.T @ [0, -1.0, 0]
    with open(os.path.join(model, "manifest.json")) as fh:
        manifest = json.load(fh)
    meshes = [[os.path.abspath(os.path.join(model, m["file"])), m["finish"]] for m in manifest.values()]
    cam = {"view": "photo", "kind": "perspective", "forward": forward.tolist(), "right": right.tolist(),
           "up": up.tolist(), "location": loc.tolist(), "res": list(res), "mm_per_px": 0.0,
           "center_ru": [0.0, 0.0], "lens_mm": f * scale / max(res) * 36.0, "sensor_mm": 36.0}
    job = {"out": out, "meshes": meshes, "cameras": [cam], "frame": [[0, 0, 0], [1, 1, 1]], "samples": 16,
           "edges": True, "background": KEY, "finishes": rv.FINISHES, "engine": "BLENDER_EEVEE"}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(job, fh)
    proc = subprocess.run([blender, "-b", "--factory-startup", "-noaudio", "-P", RENDER_VIEWS, "--", fh.name],
                          capture_output=True, text=True)
    os.unlink(fh.name)
    path = os.path.join(out, "photo.png")
    if proc.returncode != 0 or not os.path.exists(path):
        raise SystemExit(proc.stdout[-2000:] + proc.stderr[-2000:])
    img = cv2.imread(path)
    x0, y0 = int(round(res[0] / 2 - c[0] * scale)), int(round(res[1] / 2 - c[1] * scale))
    img = img[y0:y0 + int(h * scale), x0:x0 + int(w * scale)]
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)


def sheets(photo: np.ndarray, rnd: np.ndarray, out: str, x: np.ndarray, xp: np.ndarray, names: list[str]) -> None:
    key = np.array(KEY[::-1]) * 255
    mask = (np.abs(rnd.astype(float) - key).max(-1) > 60).astype(np.uint8)
    sil = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    g = cv2.cvtColor(rnd, cv2.COLOR_BGR2GRAY)
    crease = (cv2.Canny(g, 40, 100) > 0) & (cv2.erode(mask, np.ones((5, 5), np.uint8)) > 0)
    model_edges = cv2.dilate((sil | crease).astype(np.uint8), np.ones((2, 2), np.uint8)) > 0
    outline = photo.copy()
    outline[model_edges] = (255, 255, 0)
    for (px, py), (qx, qy), n in zip(x, xp, names):
        cv2.circle(outline, (int(px), int(py)), 6, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.line(outline, (int(px), int(py)), (int(qx), int(qy)), (0, 0, 255), 1, cv2.LINE_AA)
        pa.text(outline, n, (int(px) + 6, int(py) - 6), (0, 0, 255), 0.45)
    cv2.imwrite(os.path.join(out, "outline.png"), outline)
    blend = photo.copy()
    m = mask > 0
    blend[m] = (0.5 * photo[m] + 0.5 * rnd[m]).astype(np.uint8)
    cv2.imwrite(os.path.join(out, "blend.png"), blend)
    pg = cv2.GaussianBlur(cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY), (0, 0), 1.5)
    photo_edges = cv2.Canny(pg, 30, 80) > 0
    diff = np.zeros_like(photo)
    diff[photo_edges] = (0, 0, 220)
    diff[model_edges] = (220, 220, 0)
    diff[photo_edges & model_edges] = (255, 255, 255)
    cv2.imwrite(os.path.join(out, "diff.png"), diff)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("annotation")
    ap.add_argument("--fits", default="full,plane")
    ap.add_argument("--scale", type=float, default=0.5, help="render scale against the photo")
    ap.add_argument("--blender", default=os.environ.get("BLENDER", "blender"))
    a = ap.parse_args()
    ann = pa.load(a.annotation)
    ov = ann.data["overlay"]
    pts = ann.resolve()
    w, h = ann.size
    c = np.array(ann.data.get("camera", {}).get("c_px", [w / 2, h / 2]), float)
    names = list(ov["anchors"])
    X = np.array([ov["anchors"][n] for n in names], float)
    x = np.array([pts[n] for n in names], float)
    model = pa.repo_path(ov["model"])
    params, f = fit(X, x, c, ov.get("f_px", max(w, h)), "f_px" not in ov, (w, h))
    fits = {"full": (params, f, names)}
    if "plane" in ov:
        sel = [names.index(n) for n in ov["plane"]]
        p2, _ = fit(X[sel], x[sel], c, f, False, (w, h))
        fits["plane"] = (p2, f, ov["plane"])
    for name in a.fits.split(","):
        p, ff, used = fits[name]
        out = pa.out_dir(ann, f"overlay-{name}")
        xp = project(p, ff, c, X)
        err = {n: float(np.linalg.norm(xp[i] - x[i])) for i, n in enumerate(names)}
        R, _ = cv2.Rodrigues(p[:3])
        loc = (-R.T @ p[3:6]).tolist()
        with open(os.path.join(out, "camera.json"), "w") as fh:
            json.dump({"fit": name, "anchors_used": used, "f_px": ff, "c_px": c.tolist(), "camera_mm": loc,
                       "reprojection_px": err}, fh, indent=1)
        rnd = render(model, p, ff, c, (w, h), out, a.scale, a.blender)
        sheets(ann.image, rnd, out, x, xp, names)
        rms = math.sqrt(np.mean([err[n] ** 2 for n in used]))
        print(f"photo_overlay: {name}: f {ff:.0f} px, camera at {np.round(loc, 0).tolist()} mm, "
              f"rms {rms:.1f} px on {len(used)} anchors -> {os.path.relpath(out, pa.REPO)}")
        for n in names:
            print(f"  {n:16s} {err[n]:6.1f} px{'' if n in used else '  (not used)'}")


if __name__ == "__main__":
    main()

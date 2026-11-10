"""Render a set of meshes from fixed, named cameras with Blender in background mode.

The meshes are STL or OBJ files in millimetres in the project frame (X to the player's right, Y from the
cabinet front face toward the rear, Z up from the desk). Each mesh gets a finish: white (gloss white body),
black (near-black trim), dark, grey, or a #rrggbb colour. The cameras frame the union bounding box of the
meshes, or the box given with --frame, so that two models framed by the same box render at the same scale.

Each view writes <out>/<view>.png on a light-grey background. Each orthographic view also writes
<view>-mask.png (the object mask) and every view writes its projection to <out>/views.json, so that
silhouette_iou.py and compose_sheet.py can work in millimetres.

The script runs itself inside Blender (blender -b, no window). Engines: eevee (default), workbench, cycles;
auto tries them in that order.

Example:
    python3 cad/tools/render_views.py /tmp/views body.stl=white bezel.stl=black --views front,side-right
    python3 cad/tools/render_views.py /tmp/views-a cad/vendor/mini-new-astro-city/target/A
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass

VIEWS = ("front", "side-right", "rear", "top",
         "three-quarter-front-right", "three-quarter-front-left", "three-quarter-rear-left")
ORTHO_AXES = {
    "front": ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
    "side-right": ((-1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    "rear": ((0.0, -1.0, 0.0), (0.0, 0.0, 1.0)),
    "top": ((0.0, 0.0, -1.0), (0.0, 1.0, 0.0)),
}
PERSPECTIVE = {
    "three-quarter-front-right": (42.0, 6.0),
    "three-quarter-front-left": (-42.0, 6.0),
    "three-quarter-rear-left": (-140.0, 18.0),
}
DISTANCE_PER_DIAGONAL = 1.0
MARGIN = 0.06
BACKGROUND = (0.86, 0.865, 0.87)
FINISHES = {
    "white": ((0.80, 0.80, 0.78), 0.32, 0.7),
    "black": ((0.015, 0.015, 0.017), 0.6, 0.0),
    "dark": ((0.07, 0.07, 0.075), 0.5, 0.0),
    "grey": ((0.35, 0.35, 0.36), 0.5, 0.0),
}
ENGINES = {"eevee": "BLENDER_EEVEE", "workbench": "BLENDER_WORKBENCH", "cycles": "CYCLES"}

Vec = tuple[float, float, float]


@dataclass
class Camera:
    view: str
    kind: str
    forward: Vec
    right: Vec
    up: Vec
    location: Vec
    res: tuple[int, int]
    mm_per_px: float = 0.0
    center_ru: tuple[float, float] = (0.0, 0.0)
    lens_mm: float = 0.0
    sensor_mm: float = 36.0


def dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: Vec, b: Vec) -> Vec:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a: Vec) -> Vec:
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def add(a: Vec, b: Vec, k: float = 1.0) -> Vec:
    return (a[0] + k * b[0], a[1] + k * b[1], a[2] + k * b[2])


def corners(lo: Vec, hi: Vec) -> list[Vec]:
    return [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


def resolution(width: float, height: float, size: int) -> tuple[int, int]:
    k = size / max(width, height)
    return max(16, round(width * k)), max(16, round(height * k))


def ortho_camera(view: str, lo: Vec, hi: Vec, size: int) -> Camera:
    f, up0 = ORTHO_AXES[view]
    r = norm(cross(f, up0))
    u = cross(r, f)
    pts = corners(lo, hi)
    a = [dot(p, r) for p in pts]
    b = [dot(p, u) for p in pts]
    c = [dot(p, f) for p in pts]
    w = (max(a) - min(a)) * (1 + 2 * MARGIN)
    h = (max(b) - min(b)) * (1 + 2 * MARGIN)
    res = resolution(w, h, size)
    mm_per_px = max(w / res[0], h / res[1])
    am, bm = (max(a) + min(a)) / 2, (max(b) + min(b)) / 2
    centre = add(add((0.0, 0.0, 0.0), r, am), u, bm)
    location = add(centre, f, min(c) - 1000.0)
    return Camera(view, "ortho", f, r, u, location, res, mm_per_px=mm_per_px, center_ru=(am, bm))


def project(cam_loc: Vec, f: Vec, r: Vec, u: Vec, p: Vec) -> tuple[float, float]:
    d = add(p, cam_loc, -1.0)
    z = dot(d, f)
    return dot(d, r) / z, dot(d, u) / z


def perspective_camera(view: str, lo: Vec, hi: Vec, size: int) -> Camera:
    az, el = (math.radians(v) for v in PERSPECTIVE[view])
    to_cam = (math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))
    f = norm((-to_cam[0], -to_cam[1], -to_cam[2]))
    r = norm(cross(f, (0.0, 0.0, 1.0)))
    u = cross(r, f)
    pts = corners(lo, hi)
    centre = tuple((lo[i] + hi[i]) / 2 for i in range(3))
    diag = math.dist(lo, hi)
    loc = add(centre, to_cam, DISTANCE_PER_DIAGONAL * diag)
    for _ in range(4):
        uv = [project(loc, f, r, u, p) for p in pts]
        xs, ys = [q[0] for q in uv], [q[1] for q in uv]
        dx, dy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
        z = dot(add(centre, loc, -1.0), f)
        loc = add(add(loc, r, dx * z), u, dy * z)
    uv = [project(loc, f, r, u, p) for p in pts]
    xs, ys = [q[0] for q in uv], [q[1] for q in uv]
    w = (max(xs) - min(xs)) * (1 + 2 * MARGIN)
    h = (max(ys) - min(ys)) * (1 + 2 * MARGIN)
    res = resolution(w, h, size)
    sensor = 36.0
    lens = sensor / max(w, h)
    return Camera(view, "perspective", f, r, u, loc, res, lens_mm=lens, sensor_mm=sensor)


def make_camera(view: str, lo: Vec, hi: Vec, size: int) -> Camera:
    return ortho_camera(view, lo, hi, size) if view in ORTHO_AXES else perspective_camera(view, lo, hi, size)


def parse_mesh(spec: str) -> tuple[str, str]:
    path, _, finish = spec.partition("=")
    finish = finish or "white"
    if finish not in FINISHES and not (finish.startswith("#") and len(finish) == 7):
        raise SystemExit(f"unknown finish {finish!r}: use {', '.join(FINISHES)} or #rrggbb")
    return os.path.abspath(path), finish


def expand(spec: str) -> list[tuple[str, str]]:
    """A mesh argument, or a model directory with manifest.json ({part: {"file", "finish"}})."""
    if not os.path.isdir(spec):
        return [parse_mesh(spec)]
    with open(os.path.join(spec, "manifest.json")) as fh:
        manifest = json.load(fh)
    return [parse_mesh(os.path.join(spec, part["file"]) + "=" + part["finish"]) for part in manifest.values()]


def read_bounds(paths: list[str]) -> tuple[Vec, Vec]:
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for p in paths:
        for v in mesh_vertices(p):
            for i in range(3):
                lo[i] = min(lo[i], v[i])
                hi[i] = max(hi[i], v[i])
    return tuple(lo), tuple(hi)


def mesh_vertices(path: str):
    import struct
    with open(path, "rb") as fh:
        data = fh.read()
    if path.lower().endswith(".obj"):
        for line in data.decode("utf-8", "replace").splitlines():
            if line.startswith("v "):
                yield tuple(float(t) for t in line.split()[1:4])
        return
    n = struct.unpack_from("<I", data, 80)[0]
    if len(data) == 84 + 50 * n:
        for i in range(n):
            vals = struct.unpack_from("<9f", data, 84 + 50 * i + 12)
            yield vals[0:3]
            yield vals[3:6]
            yield vals[6:9]
        return
    for line in data.decode("ascii", "replace").splitlines():
        s = line.split()
        if s and s[0] == "vertex":
            yield tuple(float(t) for t in s[1:4])


def run_cli(argv: list[str]) -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("out")
    ap.add_argument("meshes", nargs="+", help="mesh file, optionally =finish, or a directory with manifest.json")
    ap.add_argument("--views", default=",".join(VIEWS))
    ap.add_argument("--frame", help="xmin,ymin,zmin,xmax,ymax,zmax in mm (default: bounding box of the meshes)")
    ap.add_argument("--size", type=int, default=1400, help="long side in pixels")
    ap.add_argument("--engine", default="eevee", choices=["auto", *ENGINES])
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--no-edges", action="store_true")
    ap.add_argument("--blender", default=os.environ.get("BLENDER", "blender"))
    a = ap.parse_args(argv)
    meshes = [m for spec in a.meshes for m in expand(spec)]
    views = [v for v in a.views.split(",") if v]
    bad = [v for v in views if v not in VIEWS]
    if bad:
        raise SystemExit(f"unknown view {bad}: choose from {', '.join(VIEWS)}")
    if a.frame:
        f = [float(t) for t in a.frame.split(",")]
        lo, hi = tuple(f[:3]), tuple(f[3:])
    else:
        lo, hi = read_bounds([m[0] for m in meshes])
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    cams = [make_camera(v, lo, hi, a.size) for v in views]
    job = {"out": out, "meshes": meshes, "cameras": [asdict(c) for c in cams], "frame": [lo, hi],
           "samples": a.samples, "edges": not a.no_edges, "background": BACKGROUND, "finishes": FINISHES}
    order = list(ENGINES) if a.engine == "auto" else [a.engine]
    t0 = time.time()
    for engine in order:
        job["engine"] = ENGINES[engine]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(job, fh)
        cmd = [a.blender, "-b", "--factory-startup", "-noaudio", "-P", os.path.abspath(__file__), "--", fh.name]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        os.unlink(fh.name)
        ok = proc.returncode == 0 and all(os.path.exists(os.path.join(out, f"{v}.png")) for v in views)
        if ok:
            break
        sys.stderr.write(proc.stdout[-3000:] + proc.stderr[-3000:])
        sys.stderr.write(f"render_views: engine {engine} failed\n")
    else:
        raise SystemExit(1)
    for spec in a.meshes:
        overlay = os.path.join(spec, "overlay.json")
        if os.path.isdir(spec) and os.path.exists(overlay):
            shutil.copy(overlay, os.path.join(out, "overlay.json"))
    meta = {"frame": [lo, hi], "engine": job["engine"], "views": {c.view: asdict(c) for c in cams},
            "meshes": [{"file": p, "finish": f} for p, f in meshes]}
    with open(os.path.join(out, "views.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"render_views: {len(views)} views with {job['engine']} in {time.time() - t0:.1f} s -> {out}")


def run_blender(job_path: str) -> None:
    import bpy
    import numpy as np

    with open(job_path) as fh:
        job = json.load(fh)
    scene = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    def material(finish: str):
        mat = bpy.data.materials.new(finish)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        if finish.startswith("#"):
            rgb = tuple((int(finish[i:i + 2], 16) / 255.0) ** 2.2 for i in (1, 3, 5))
            rough, coat = 0.45, 0.0
        else:
            rgb, rough, coat = job["finishes"][finish]
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Coat Weight"].default_value = coat
        bsdf.inputs["Coat Roughness"].default_value = 0.06
        bsdf.inputs["Specular IOR Level"].default_value = 0.5 if finish == "white" else 0.25
        mat.diffuse_color = (*rgb, 1.0)
        return mat

    mats: dict[str, object] = {}
    for path, finish in job["meshes"]:
        before = set(bpy.data.objects)
        if path.lower().endswith(".obj"):
            bpy.ops.wm.obj_import(filepath=path, forward_axis="Y", up_axis="Z")
        else:
            bpy.ops.wm.stl_import(filepath=path, forward_axis="Y", up_axis="Z")
        if finish not in mats:
            mats[finish] = material(finish)
        for ob in set(bpy.data.objects) - before:
            ob.data.materials.clear()
            ob.data.materials.append(mats[finish])
            ob.color = (*mats[finish].diffuse_color[:3], 1.0)
            ob.data.shade_smooth()
            ob.data.set_sharp_from_angle(angle=math.radians(28))

    world = bpy.data.worlds.new("studio")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -1.0
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    ramp.color_ramp.elements[0].color = (0.10, 0.10, 0.11, 1)
    ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.95, 1)
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[1].position = 0.85
    bg.inputs["Strength"].default_value = 0.85

    def sun(name: str, rot: tuple[float, float, float], energy: float, angle: float) -> None:
        light = bpy.data.lights.new(name, "SUN")
        light.energy = energy
        light.angle = math.radians(angle)
        ob = bpy.data.objects.new(name, light)
        ob.rotation_euler = tuple(math.radians(v) for v in rot)
        scene.collection.objects.link(ob)

    sun("key", (50, 0, -35), 2.6, 25)
    sun("fill", (65, 0, 120), 0.7, 40)
    sun("rim", (60, 0, 200), 0.6, 40)

    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam_data.clip_start = 1.0
    cam_data.clip_end = 1e6

    render = scene.render
    render.engine = job["engine"]
    render.film_transparent = True
    render.resolution_percentage = 100
    render.image_settings.file_format = "PNG"
    render.image_settings.color_mode = "RGBA"
    render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    if job["engine"] == "BLENDER_EEVEE":
        scene.eevee.taa_render_samples = job["samples"]
        scene.eevee.use_shadows = True
        scene.eevee.use_fast_gi = True
        scene.eevee.fast_gi_distance = 80.0
    elif job["engine"] == "CYCLES":
        scene.cycles.samples = job["samples"] * 2
        scene.cycles.use_denoising = True
        scene.cycles.device = "CPU"
    else:
        sh = scene.display.shading
        sh.light = "STUDIO"
        sh.color_type = "MATERIAL"
        sh.show_cavity = True
        sh.cavity_type = "BOTH"
        sh.show_shadows = True
        sh.shadow_intensity = 0.35
        sh.show_specular_highlight = True
        scene.display.render_aa = "8"

    aux_mat = bpy.data.materials.new("aux")
    aux_mat.use_nodes = True
    an = aux_mat.node_tree
    for n in list(an.nodes):
        an.nodes.remove(n)
    geo = an.nodes.new("ShaderNodeNewGeometry")
    vt = an.nodes.new("ShaderNodeVectorTransform")
    vt.vector_type = "NORMAL"
    vt.convert_from = "WORLD"
    vt.convert_to = "CAMERA"
    camd = an.nodes.new("ShaderNodeCameraData")
    sepn = an.nodes.new("ShaderNodeSeparateXYZ")
    comb = an.nodes.new("ShaderNodeCombineXYZ")
    emit = an.nodes.new("ShaderNodeEmission")
    outn = an.nodes.new("ShaderNodeOutputMaterial")
    an.links.new(geo.outputs["Normal"], vt.inputs["Vector"])
    an.links.new(vt.outputs["Vector"], sepn.inputs[0])
    an.links.new(sepn.outputs["X"], comb.inputs["X"])
    an.links.new(sepn.outputs["Y"], comb.inputs["Y"])
    an.links.new(camd.outputs["View Z Depth"], comb.inputs["Z"])
    an.links.new(comb.outputs["Vector"], emit.inputs["Color"])
    an.links.new(emit.outputs["Emission"], outn.inputs["Surface"])

    tmp = tempfile.mkdtemp(prefix="render_views_")

    def load_pixels(path: str) -> np.ndarray:
        img = bpy.data.images.load(path)
        w, h = img.size
        px = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        bpy.data.images.remove(img)
        return px.reshape(h, w, 4)[::-1]

    def save_pixels(path: str, rgb: np.ndarray) -> None:
        h, w = rgb.shape[:2]
        img = bpy.data.images.new("out", w, h, alpha=False)
        rgba = np.ones((h, w, 4), dtype=np.float32)
        rgba[..., :3] = rgb
        img.pixels.foreach_set(rgba[::-1].ravel())
        img.filepath_raw = path
        img.file_format = "PNG"
        img.save()
        bpy.data.images.remove(img)

    def edges(aux: np.ndarray, alpha: np.ndarray, kind: str, mm_per_px: float) -> np.ndarray:
        n = aux[..., :2]
        z = aux[..., 2]
        cover = alpha > 0.5
        e = np.zeros(alpha.shape, dtype=np.float32)
        nz = np.sqrt(np.clip(1 - (n ** 2).sum(-1), 0, 1))
        nv = np.dstack([n, nz])
        for ax in (0, 1):
            a0 = np.roll(nv, 1, axis=ax)
            c0 = np.roll(cover, 1, axis=ax)
            cosang = (nv * a0).sum(-1)
            both = cover & c0
            e = np.maximum(e, np.where(both & (cosang < math.cos(math.radians(22))), 1.0, 0.0))
            e = np.maximum(e, np.where(cover != c0, 1.0, 0.0))
        if kind == "perspective":
            q = np.where(cover, 1.0 / np.maximum(z, 1e-6), 0.0)
            scale = np.median(q[cover]) if cover.any() else 1.0
            q = q / scale
            thr = 0.006
        else:
            q = np.where(cover, z, 0.0)
            thr = 1.5 + 0.5 * mm_per_px
        for ax in (0, 1):
            lap = np.roll(q, 1, axis=ax) - 2 * q + np.roll(q, -1, axis=ax)
            ok = cover & np.roll(cover, 1, axis=ax) & np.roll(cover, -1, axis=ax)
            e = np.maximum(e, np.where(ok & (np.abs(lap) > thr), 1.0, 0.0))
        e[0, :] = e[-1, :] = 0
        e[:, 0] = e[:, -1] = 0
        k = np.array([0.25, 0.5, 0.25], dtype=np.float32)
        for ax in (0, 1):
            e = k[0] * np.roll(e, 1, axis=ax) + k[1] * e + k[2] * np.roll(e, -1, axis=ax)
        return np.clip(e * 1.6, 0, 1)

    background = np.array(job["background"], dtype=np.float32)
    for c in job["cameras"]:
        f, r, u = c["forward"], c["right"], c["up"]
        from mathutils import Matrix, Vector
        rot = Matrix((Vector(r), Vector(u), Vector([-v for v in f]))).transposed()
        cam.matrix_world = Matrix.Translation(Vector(c["location"])) @ rot.to_4x4()
        if c["kind"] == "ortho":
            cam_data.type = "ORTHO"
            cam_data.ortho_scale = c["mm_per_px"] * max(c["res"])
        else:
            cam_data.type = "PERSP"
            cam_data.sensor_fit = "AUTO"
            cam_data.sensor_width = c["sensor_mm"]
            cam_data.lens = c["lens_mm"]
        render.resolution_x, render.resolution_y = c["res"]
        beauty = os.path.join(tmp, f"{c['view']}-beauty.png")
        render.filepath = beauty
        bpy.ops.render.render(write_still=True)
        px = load_pixels(beauty)
        alpha = px[..., 3:4]
        rgb = px[..., :3] * alpha + background * (1 - alpha)
        if job["edges"]:
            saved = (render.engine, scene.view_layers[0].material_override, render.image_settings.file_format)
            if render.engine != "BLENDER_EEVEE":
                render.engine = "BLENDER_EEVEE"
            taa = scene.eevee.taa_render_samples
            scene.eevee.taa_render_samples = 1
            scene.view_layers[0].material_override = aux_mat
            render.image_settings.file_format = "OPEN_EXR"
            render.image_settings.color_depth = "32"
            render.image_settings.color_mode = "RGBA"
            aux_path = os.path.join(tmp, f"{c['view']}-aux.exr")
            render.filepath = aux_path
            bpy.ops.render.render(write_still=True)
            aux = load_pixels(aux_path)
            render.engine, scene.view_layers[0].material_override, render.image_settings.file_format = saved
            render.image_settings.color_depth = "8"
            scene.eevee.taa_render_samples = taa
            e = edges(aux, px[..., 3], c["kind"], c["mm_per_px"])[..., None]
            rgb = rgb * (1 - 0.72 * e) + 0.12 * 0.72 * e
        save_pixels(os.path.join(job["out"], f"{c['view']}.png"), np.clip(rgb, 0, 1))
        if c["kind"] == "ortho":
            save_pixels(os.path.join(job["out"], f"{c['view']}-mask.png"), np.repeat(alpha, 3, axis=2))


if __name__ == "__main__":
    if "--" in sys.argv and "bpy" in sys.modules or os.path.basename(sys.argv[0]).startswith("blender"):
        run_blender(sys.argv[sys.argv.index("--") + 1])
    else:
        run_cli(sys.argv[1:])

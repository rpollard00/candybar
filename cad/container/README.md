# The FreeCAD container

`Dockerfile` makes an image with FreeCAD 1.1.4-3 (the Arch Linux package) and OpenCascade 1:7.9.3-4.1 (the CachyOS rebuild of the Arch package), with Python 3.14. The reference machine (the owner's laptop) has the same package versions. `run.sh` runs a command in the image, with the checkout mounted at its own path:

```sh
cad/container/run.sh cad/build.sh
CANDYBAR_OUT=cad/out/fit cad/container/run.sh cad/candybar/freecad-run.sh candybar.shell.fit
```

Use the container for studies and builds on a machine that is not the reference machine.

CAUTION: The geometry of the container is near the geometry of the reference machine, but it is not the same. A verdict from the container is not the verdict of the reference machine. Verify on the reference machine before a push.

## Why the geometry is not the same

OpenCascade gives a different geometry for each compiler target. CachyOS builds the package for three targets: x86-64-v3, x86-64-v4 (AVX-512) and znver4 (AVX-512). The v3 build gives a geometry that differs from the reference machine, so the reference machine probably runs one of the AVX-512 builds. The server where this container was made has an AMD Zen 2 CPU, which has no AVX-512. On it, the v4 build stops with "Illegal instruction", and QEMU 11.1 cannot emulate AVX-512. So the default build of the image uses the v3 build.

`OCCT` selects the build: `v3` (the default), `v4`, `znver4` or `arch` (the Arch package 1:7.9.3-4, generic x86-64). On a machine with AVX-512, `--build-arg OCCT=v4` or `OCCT=znver4` can give the geometry of the reference machine. Nobody has tried this yet.

## The comparison with the reference machine

Commit c8ecb30, the outer form, built in the container (OCCT v3) and on the reference machine:

| Item | Result |
| --- | --- |
| Parts | 10 of 10 pass `tools/compare_parts.py` at 0.000001 mm: every surface distance is 0.0000 mm (the tool rounds to 4 decimals) |
| Faces, edges, vertexes | The same counts in every part |
| Volume of the body | 47169243.8 mm3 in the container, 47165244.0 mm3 on the reference machine. The exact volume is not reliable on these faces: on a fine mesh the two bodies differ by 268 mm3 |
| Faces of the body | 14 faces have other trim curves: the area of a side plane is 36026.8 mm2 against 36013.7 mm2 |
| The laptop's cached skin | Reads as a valid shape (0 bad faces of 16248) |

The test results that differ from the reference machine (501 tests at c8ecb30):

| Test | In the container |
| --- | --- |
| `test_face_check`, 2 tests | A kink at the rail is 2.4 mm from its listed place (the limit is 1.5 mm) |
| `test_hood_band`, 1 test | The same kink |
| `test_split`, 3 tests | The upper rear pieces are 489.8 mm and 493.7 mm across: they are not mirror images, and they do not fit the printer |
| `test_pieces.WholeSetTest` | The set-up stops: "deck_nose.brep does not read as a valid shape" |

The arch build (generic x86-64) and the FreeCAD 1.1.4 AppImage (OpenCascade 7.8.1) do not complete the default build: "the edge break of the hood: tool 1 still holds 0.013 mm3 of 0.013".

## From run to run

One kernel gives nearly the same geometry from run to run, but not always the same file. Two builds of 36bc344 in the container: 34 of 35 BREP files are the same byte for byte. In the hood, the volume differs by 0.018 mm3 (2.5e-9 of the volume), the area by 0.0002 mm2 and the box by 2.3e-8 mm. The first pass of `tools/compare_parts.py` has a tolerance of 1e-7 of the volume and the area, and 1e-4 mm on the box.

The cut of the split is not the same from run to run in the container. `test_split.SplitTest.test_each_hand_hold_is_whole_in_one_piece` cut the same skin six times: it passed two times and failed four times, with the left upper rear piece 0.88 mm to 116 mm past the centre line. The split's own measurement of the same commit was symmetric.

## Pins and disk

The base image is pinned by its digest, the Arch packages by the date of the snapshot of the Arch Linux Archive (2026-11-16), and the CachyOS packages by their checksums. The build stops when the version of `freecad` or `opencascade` is not the pinned one. The image takes 4.7 GB. `run.sh` builds it when it is not there (about 4 minutes), with a tag that contains the build of OpenCascade and a hash of the Dockerfile.

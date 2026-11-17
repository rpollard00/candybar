# The FreeCAD of the reference machine, in a container: Arch Linux with the packages of one day of the Arch Linux
# Archive. The reference machine has freecad 1.1.4-3 (the Arch package) and opencascade 1:7.9.3-4.1 (a CachyOS
# rebuild of the Arch package), with Python 3.14. Everything is pinned: the base image by its digest, the packages
# by the date of the snapshot, the CachyOS package by its checksum, and the two packages that make the geometry by
# their version (the build stops when they differ).
#
# OpenCascade gives a different geometry for each compiler target, so OCCT selects the build:
#   v3      the CachyOS build for x86-64-v3 (AVX2, FMA). The default: it runs on any recent x86-64 CPU.
#   v4      the CachyOS build for x86-64-v4 (AVX-512). Needs a CPU with AVX-512.
#   znver4  the CachyOS build for AMD Zen 4. Needs a Zen 4 or Zen 5 CPU.
#   arch    the Arch package 1:7.9.3-4 (generic x86-64). The default build of the shell does not complete with it.
# cad/container/README.md has the comparison of each build with the reference.
#
#   docker build -t candybar-freecad:1.1.4-3 cad/container
#   docker build --build-arg OCCT=v4 -t candybar-freecad:1.1.4-3-v4 cad/container
#
# cad/container/run.sh runs a command in it with the checkout mounted.
FROM archlinux:base-20261101.0.620205@sha256:b1c2fe6e717bfd5673af8fc217e1e1c3ce0dcbb1d53c3414c8425e7ce79fc6d9

ARG SNAPSHOT=2026/11/16
ARG FREECAD=1.1.4-3
ARG OCCT=v3
ARG CACHYOS=https://mirror.cachyos.org/repo
ADD --checksum=sha256:372ffc56659975cb658111b2d335acc0de8987f4441f7597b8e66e6989f5582a \
    ${CACHYOS}/x86_64_v3/cachyos-extra-v3/opencascade-1%3A7.9.3-4.1-x86_64.pkg.tar.zst /occt/v3.pkg.tar.zst
ADD --checksum=sha256:07925780c473d3a49358822b643f1e787e9426c18a90f56d6a401f90cda451da \
    ${CACHYOS}/x86_64_v4/cachyos-extra-v4/opencascade-1%3A7.9.3-4.1-x86_64.pkg.tar.zst /occt/v4.pkg.tar.zst
ADD --checksum=sha256:bd5e54e72708b2115ed731c2a61636b8dfde088bc045a3c98b11c93f79de6230 \
    ${CACHYOS}/x86_64_v4/cachyos-extra-znver4/opencascade-1%3A7.9.3-4.1-x86_64_v4.pkg.tar.zst /occt/znver4.pkg.tar.zst

RUN echo "Server = https://archive.archlinux.org/repos/${SNAPSHOT}/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist \
 && sed -i 's/^#\?NoExtract.*/NoExtract = usr\/share\/help\/* usr\/share\/doc\/* usr\/share\/man\/* usr\/share\/locale\/* usr\/share\/i18n\/*/' /etc/pacman.conf \
 && pacman -Syyuu --noconfirm \
 && pacman -S --noconfirm --needed freecad python-pillow python-numpy procps-ng util-linux git \
 && if [ "$OCCT" = arch ]; then want=1:7.9.3-4; else want=1:7.9.3-4.1; \
      sed -i 's/^#\?Architecture.*/Architecture = x86_64 x86_64_v4/' /etc/pacman.conf; \
      pacman -U --noconfirm "/occt/$OCCT.pkg.tar.zst"; fi \
 && rm -rf /occt && pacman -Scc --noconfirm \
 && test "$(pacman -Q freecad | cut -d' ' -f2)" = "$FREECAD" \
 && test "$(pacman -Q opencascade | cut -d' ' -f2)" = "$want" \
 && { pacman -Q freecad opencascade python onetbb glibc gcc-libs; echo "OCCT=$OCCT"; } > /etc/candybar-freecad.txt

ENV QT_QPA_PLATFORM=offscreen

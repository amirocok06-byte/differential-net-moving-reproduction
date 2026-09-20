# Notices and upstream provenance

## DREAMPlace

The prototype was developed against the local dirty branch of DREAMPlace:

- upstream: `https://github.com/limbo018/DREAMPlace.git`
- local commit: `6627f3327e6cc17db7782c0b90073a498531ca3c`
- local branch: `research/diff-net-moving-baseline`
- upstream license observed locally: BSD 3-Clause

The upstream DREAMPlace source tree is not included. The repository includes only a local DiffNet integration patch and prototype files that import upstream DREAMPlace interfaces.

## Xplace

Xplace was used as a framework/reference in the local audit:

- upstream: `https://github.com/cuhk-eda/Xplace`
- audited commit: `49cf66bc75ba9908f145bb6686f03cde692367cf`
- license observed in the audited snapshot: BSD 3-Clause

The Xplace source, submodules, benchmark data, generated `ispd2015_fix`, and build products are not included.

## Other dependencies

PyTorch, Python, CUDA, pytest, and any system/compiler components remain external dependencies. No vendor tree, commercial tool, PDK, paper PDF, or raw benchmark collateral is redistributed here.

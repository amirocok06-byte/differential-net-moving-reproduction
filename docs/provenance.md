# Provenance

## Local DiffNet candidate

- path: `/home/amirocok/eda-src/DREAMPlace`
- branch: `research/diff-net-moving-baseline`
- HEAD: `6627f3327e6cc17db7782c0b90073a498531ca3c`
- upstream: `https://github.com/limbo018/DREAMPlace.git`
- state at collection: dirty; no reset, checkout, clean, or overwrite was performed
- tracked DiffNet integration edits: `dreamplace/NonLinearPlace.py`, `dreamplace/PlaceObj.py`
- excluded tracked edit: `dreamplace/ops/utility/src/utils_cub.cuh` (build compatibility, not DiffNet semantics)

## Xplace reference

- upstream: `https://github.com/cuhk-eda/Xplace`
- audited commit: `49cf66bc75ba9908f145bb6686f03cde692367cf`
- branch: `main`
- license: BSD 3-Clause
- excluded: complete source, submodule, data, generated fixed designs, build and results

## Result provenance

The JSON manifests are copied from `/home/amirocok/eda-research/results/p1a_stage4d/mgc_des_perf_1` and the small logs from `/home/amirocok/xplace-ispd2015-work/result/.../mgc_fft_1`. Their absolute paths are retained inside some manifests so that the original local provenance is auditable; those paths are not expected to exist for other users.

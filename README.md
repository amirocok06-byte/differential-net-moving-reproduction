# Differential Net-Moving reproduction package

This private repository packages the local Differential Net-Moving / DiffNet prototype and its audit trail.

It is deliberately scoped as a partial reproduction package. It is not the authors' official implementation, does not contain the complete Xplace or DREAMPlace source trees, does not contain ISPD2015 benchmark data, and does not claim a full paper reproduction.

## Contents

- `src/diffnet_prototype/`: locally written/reconstructed Python prototype modules, tests, and small audit utilities.
- `src/diffnet_prototype/dreamplace-integration.patch`: the two opt-in DREAMPlace integration hooks as a patch; the upstream checkout is not bundled.
- `configs/`: scope and configuration notes. No complete paper-faithful parameter file was available.
- `results/manifests/`: small JSON manifests and metadata only; no tensors, checkpoints, DEF/LEF collateral, or binaries.
- `results/small-logs/`: small, explicitly labelled GP/GGR logs; these are not Innovus Table I results.
- `docs/`: provenance, assumptions, ambiguities, and performance interpretation.
- `audit/`: the initial audit and independent CLI review.
- `scripts/`: safe local unit-test instructions only; no benchmark runner is implied.

## Provenance and boundary

The prototype was collected from the local dirty DREAMPlace research branch at commit `6627f3327e6cc17db7782c0b90073a498531ca3c`. The Xplace framework is referenced only by upstream URL/commit in the provenance documents; its source tree and generated data remain excluded.

The package records a local `PARTIAL_REPRODUCTION` state: some Xplace preprocessing/placement/GGR evidence and one-design DiffNet prototype artifacts exist, but the 20-design DiffNet/Xplace-Route/Innovus chain and comparable `DRWL/#DRVias/#DRVs/PT/RT` results do not.

## Running the small tests

Use a compatible Python environment with PyTorch installed, and run from an upstream DREAMPlace checkout after applying the integration patch only if integration tests are desired. The package's prototype tests are intentionally small and do not download data or run placement benchmarks:

```bash
./scripts/run_unit_tests.sh /path/to/DREAMPlace
```

The tests are evidence for helper behavior, not evidence of end-to-end paper reproduction.

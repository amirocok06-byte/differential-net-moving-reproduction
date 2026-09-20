# Independent Codex CLI review — Differential Net-Moving / DiffNet

Audit date: 2026-09-20 (Asia/Shanghai).  All checks were read-only.  Windows paths in the request were inspected through their mounted POSIX paths, e.g. `C:\Users\Lenovo\...` = `/mnt/c/Users/Lenovo/...`.

## Executive conclusion

The machine contains a genuine but incomplete reproduction trail—Xplace preprocessing, placement and partial GGR outputs, plus a one-design paper-aligned DiffNet prototype—but no complete 20-design DiffNet/Xplace-Route/Innovus result chain; status: **`PARTIAL_REPRODUCTION`**.

The existing audit package is directionally correct about the absence of a paper-level result, but it is incomplete because it did not search the local Xplace worktree and DiffNet attribution tree. It also calls Table I a 19-design table; the PDF has 20 design rows.

## Verified facts

### Scope and mandatory reading

The four requested files were read in the required order:

1. `/mnt/c/Users/Lenovo/Documents/Codex/2026-09-20/new-chat/outputs/differential-net-moving-audit/README.md`
2. `.../AUDIT_REPORT.md`
3. `.../EVIDENCE_INDEX.md`
4. `.../NEXT_CHECKS.md`

The audit directory contains five files at the checked depth:

| file | bytes | mtime (+0800) |
|---|---:|---|
| `README.md` | 1,305 | 2026-09-20 15:10:03 |
| `AUDIT_REPORT.md` | 7,254 | 2026-09-20 15:10:03 |
| `EVIDENCE_INDEX.md` | 2,290 | 2026-09-20 15:10:03 |
| `NEXT_CHECKS.md` | 1,709 | 2026-09-20 15:10:03 |
| `CODEX_CLI_AUDIT_PROMPT.md` | 6,332 | 2026-09-20 15:14:38 |

The required material directory has 48 files at depth ≤4, including the two PDFs, six metadata/README files, the Xplace source tree, and no result directory. Its key files are listed in the Evidence appendix; the exact inventory was generated with the `find ... -printf` command recorded there.

### Paper files and Table I

Both requested PDFs exist:

| file | bytes | mtime (+0800) | SHA256 |
|---|---:|---|---|
| `/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/paper/paper-local.pdf` | 725,938 | 2026-05-18 00:40:32 | `12ddb3ddea0b1e085ee6f8533dcfadf169c2cd3a44249f91da5b440d24b60cd8` |
| `/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/paper/paper-author-web.pdf` | 706,591 | 2026-08-24 17:50:39 | `20ab737e3f4b842d0cc8325f747a44109700039c29783933fab70fd1493bdab8` |

The PDFs have different container hashes, but the decompressed Table I page content has the same SHA256 `2058338aaee62e9b41c70b4467cb74406b1f7142f3c6a7d6e798f91fdc02ec90`. Raw PDF stream inspection was used because `pdfinfo`/`pdftotext` were unavailable.

The paper text directly supports the following distinctions:

- DREAMPlace appears in the background/reference context; the experiment says the proposed method is deployed on Xplace.
- The table compares `Xplace`, `Xplace-Route`, and `Ours`; the method groups are not design counts.
- The table footnote excludes the Xplace `superblue12` DRV result from its mean-ratio calculation and says routing time may not represent routability because Innovus may terminate early.
- The body contains both “40% reduction” relative to Xplace-Route and “400% reduction” relative to Xplace. The latter is not mathematically coherent as written.

### Xplace snapshot and local worktree

The required snapshot `/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/repositories/Xplace` is:

- `HEAD=49cf66bc75ba9908f145bb6686f03cde692367cf`
- branch `main`
- remote `https://github.com/cuhk-eda/Xplace.git`
- one commit and a `.git/shallow` file; therefore shallow
- submodule status `-83b92ceb... thirdparty/pybind11`; not initialized
- clean at the checked time
- no `data/raw/ispd2015`, `data/raw/ispd2015_fix`, `result/`, or `results/` there

The machine-wide local worktree `/home/amirocok/xplace-ispd2015-work` has the same HEAD and remote, but is dirty (`678` status entries; the accompanying state audit attributes most to line-ending changes but leaves eight semantic differences unresolved). It contains:

- 16 symlinked raw designs pointing to `/mnt/g/diffnet-reproduction-materials/datasets/ispd2015_raw`;
- 16 generated `data/raw/ispd2015_fix/<design>` directories, generated 2026-08-25;
- compiled Xplace binaries/build directories;
- actual placement outputs and logs for `mgc_fft_1`, `mgc_fft_2`, and `mgc_des_perf_1`;
- a successful saved GGR map/metric output for `mgc_fft_1`.

This is real local execution evidence, but not a clean, provenance-safe paper reproduction snapshot.

### ISPD2015 archive and design sets

`/mnt/g/diffnet-reproduction-materials/datasets/ispd2015.tar.gz` exists, has size 129,132,340 bytes, and SHA256:

`af4a352fdadddf359b8cf997c113b3b0608f57b97ca5b23267c01039837575d9`

`/mnt/g/diffnet-reproduction-materials/datasets/ispd2015_raw` contains 16 design directories. Every directory contains all five checked key inputs: `floorplan.def`, `cells.lef`, `tech.lef`, `design.v`, and `placement.constraints`.

The 16 raw/archive designs are:

```text
mgc_des_perf_1  mgc_des_perf_a  mgc_des_perf_b  mgc_edit_dist_a
mgc_fft_1       mgc_fft_2       mgc_fft_a       mgc_fft_b
mgc_matrix_mult_1  mgc_matrix_mult_a  mgc_matrix_mult_b
mgc_pci_bridge32_a  mgc_pci_bridge32_b
mgc_superblue11_a  mgc_superblue12  mgc_superblue16_a
```

The 20 DREAMPlace JSON names and the 20 literal Table I rows are identical. The four names absent from the 16-design archive are:

```text
mgc_matrix_mult_2  mgc_matrix_mult_c  mgc_superblue14  mgc_superblue19
```

The local DREAMPlace JSONs are standard placement configurations (20 files, references such as `benchmarks/ispd2015/...`, seed 1000 in the inspected example); they are not DiffNet-specific configurations and do not contain result outputs.

### DiffNet-specific evidence found outside the supplied audit package

The broad local read-only search found two important trees omitted from the supplied audit:

1. `/home/amirocok/eda-research/diff-net-moving-attribution`
2. `/home/amirocok/eda-src/DREAMPlace`

The latter is a dirty branch `research/diff-net-moving-baseline`, HEAD `6627f3327e6cc17db7782c0b90073a498531ca3c`, with files such as `dreamplace/paper_net_moving.py`, `dreamplace/two_pin_net_moving.py`, `dreamplace/poisson_congestion_probe.py`, `dreamplace/net_moving_callback.py`, and associated tests. This is local reconstruction/prototype source, not an author-provided DiffNet release.

The attribution tree contains:

- real CUDA GGR/Poisson tensors for `mgc_fft_1` (`5 × 128 × 128`, finite float32 values, runtime 89.2586 s);
- whole-design two-pin diagnostics for `mgc_fft_1` (14,504 two-pin nets, 14,503 valid);
- selected-multi-pin diagnostics and a one-step optimizer bridge;
- a later `mgc_des_perf_1` staged run with baseline placement, router maps, Poisson field, Algorithm 1 tensor, Algorithm 2 tensor, and a congestion-gradient injection artifact;
- explicit assumption registers identifying choices not stated by the paper, including source centering, M1 inclusion, `k=0` midpoint handling, routing refresh, optimizer reset, and termination tolerance.

The staged `mgc_des_perf_1` manifest itself says `no_replay: true`, `no_reroute: true` for the frozen injection artifact and records `selected_occurrences: 0` for Algorithm 2 in that run. It is therefore evidence of a working reconstruction/probe chain, not evidence of the final paper algorithm or end-to-end paper result.

## Reproduction status matrix

Status meanings: `VERIFIED` = direct file/log/hash evidence; `PARTIAL` = some stages or local reconstruction evidence; `MISSING` = no implementation/output in the checked scope; `BLOCKED` = a required external artifact prevents the next step.

| chain segment | status | evidence and limit |
|---|---|---|
| Paper identification/PDF integrity | `VERIFIED` | Two PDFs and fresh SHA256 values above; Table I stream cross-check. |
| Paper → Xplace framework mapping | `VERIFIED` | Paper text names Xplace; Xplace README/main.py/data/router/Innovus scripts expose the corresponding flow. |
| Author DiffNet source/config | `MISSING` | No DiffNet-specific author source/config in the supplied material or Xplace snapshot. Local DREAMPlace files are a reconstruction branch. |
| Raw ISPD2015 input | `VERIFIED` | Official archive hash, extracted 16 designs, 5/5 key inputs per design. |
| Full Table I benchmark alignment | `MISSING` | Table/config set has 20; raw archive has 16; four exact names are absent. |
| `ispd2015_fix` preprocessing | `PARTIAL` | Xplace script proves the procedure and the separate dirty worktree has generated fixed data; the required Desktop snapshot has none, and output provenance is not clean/frozen. |
| Xplace global placement | `PARTIAL` | Successful local logs/DEF outputs exist for `mgc_fft_1`, `mgc_fft_2`, and `mgc_des_perf_1`; not a complete aligned benchmark run from a clean snapshot. |
| GPU 3-D Z-shape/GGR congestion estimation | `PARTIAL` | `mgc_fft_1` saved GGR maps/metrics; attribution tree has finite 5-layer maps; router revision/grid/capacity identity to the paper is not proven. |
| DiffNet two-pin net-moving | `PARTIAL` | Local Algorithm 1/probe tensors and source exist; documented reconstruction assumptions remain; no author implementation or full paper runner. |
| DiffNet multi-pin net-moving | `PARTIAL` | Local Algorithm 2 closure/artifact exists, but the checked `mgc_des_perf_1` run selected zero cells and the staged artifact is frozen/no-reroute. |
| DiffNet iterative feedback/termination | `MISSING` | Paper-defined repeated placement/routing/termination is not demonstrated end-to-end; Xplace’s route-force scheduler is a different mechanism. |
| Legalization/detail placement | `PARTIAL` | Xplace interfaces and some local outputs exist; complete DiffNet/Xplace-Route chain is absent. |
| Innovus global/detailed routing | `MISSING` | An Xplace Innovus Tcl template exists, but no executed matching Innovus log/DR metric set was found. |
| Final metrics `DRWL/DRVias/DRVs/PT/RT` | `MISSING` | Local GP/GGR metrics exist, but no comparable Innovus Table I metrics. |
| End-to-end paper reproduction | `MISSING` | No repeatable complete command + 20 aligned designs + full config + final metrics. |

## Ambiguity register

| ambiguity | evidence | current handling | remaining impact |
|---|---|---|---|
| DREAMPlace vs Xplace | Paper background mentions DREAMPlace; experiment/method text says deployed on Xplace. Xplace `main.py` and README implement the placement/router flow. | Treat Xplace as the experimental framework. Treat local DREAMPlace files only as a separate reconstruction candidate. | Author confirmation or a released DiffNet port is needed to establish exact implementation identity. |
| 16, 19, or 20 designs | Raw archive has 16; DREAMPlace configs and literal Table I rows have 20. Existing `AUDIT_REPORT.md` says 19. | Correct the count to 20 table rows; report archive/config/table separately. | Four designs and their exact source/fence treatment are missing, so no full-table replication. |
| Fence-region “removal” point | Table footnote says fence constraints were removed. `data/fix_ispd2015_route.py` explicitly writes `ispd2015_fix` and removes `REGIONS`/`GROUPS` plus routing syntax. | Count preprocessing as verified only in the separate dirty worktree, not in the required clean snapshot. | Need source/output manifest and hashes to prove the paper’s exact preprocessing. |
| Router [18] identity and parameters | Xplace `cpp_to_py/gpugr` documents GPU Z-shape/maze routing and exposes demand/capacity maps; actual local logs show 128×128 and 5 layers. | Count GGR as an implementation candidate/partial runtime, not as byte-level paper identity. | Need exact revision, grid/layer/capacity/track settings, seed and output convention. |
| DiffNet learning rate, lambda schedule, thresholds, seed, stopping | Paper gives qualitative equations/algorithms and a termination description; it does not provide a complete executable parameter set. Local manifests explicitly label many choices as reconstruction assumptions. | Do not substitute Xplace defaults or local assumptions for paper facts. | Exact algorithm trajectory and final metrics cannot be claimed reproducible. |
| Baseline meaning | Table has both Xplace and Xplace-Route; prose’s direct comparison is generally against Xplace-Route. | A paper-aligned result must report both baseline columns and state the comparison denominator. | Reporting only one baseline would hide a required comparison. |
| 40% vs 400% and ratio math | Table values produce a DRV ratio around 1.39 for Xplace-Route, not a 40% reduction. The text also says “400% reduction”. | Treat both prose claims as unresolved/possibly editorial errors; recompute from raw rows. | The paper’s headline improvement is not numerically reproducible from Table I as printed. |

## Performance comparison

### Paper Table I values

Values are transcribed as `(DRWL, #DRVias, #DRVs, PT, RT)`. `PT` and `RT` are seconds as labelled by the table.

| design | Xplace | Xplace-Route | Ours |
|---|---|---|---|
| mgc_des_perf_1 | 1452606, 569989, 24977, 5, 869 | 1446525, 566434, 12768, 7, 657 | 1429056, 566581, 10652, 30, 568 |
| mgc_des_perf_a | 2344941, 560801, 29875, 5, 180 | 2474885, 578102, 40701, 20, 200 | 2360122, 569940, 10094, 20, 3430 |
| mgc_des_perf_b | 1817040, 554677, 19580, 5, 648 | 1807464, 541944, 1557, 7, 123 | 1783673, 541130, 849, 21, 89 |
| mgc_edit_dist_a | 5670681, 1006803, 405858, 6, 748 | 5745638, 1015369, 424887, 23, 779 | 5737250, 1034387, 359904, 19, 801 |
| mgc_fft_1 | 516059, 186603, 9249, 3, 415 | 515345, 186516, 4077, 11, 293 | 513993, 185309, 3661, 26, 299 |
| mgc_fft_2 | 598828, 187925, 9334, 3, 117 | 627383, 190944, 1197, 10, 248 | 612371, 190620, 1070, 14, 328 |
| mgc_fft_a | 1090612, 193181, 5650, 3, 380 | 1144134, 192291, 925, 11, 296 | 1133734, 192225, 790, 9, 273 |
| mgc_fft_b | 1256346, 205052, 33875, 3, 191 | 1318002, 217100, 14603, 12, 255 | 1310187, 216838, 14710, 9, 263 |
| mgc_matrix_mult_1 | 2708706, 809962, 80816, 6, 378 | 2656679, 826886, 15371, 21, 2236 | 2638437, 820336, 10717, 25, 2180 |
| mgc_matrix_mult_2 | 2719259, 840175, 72311, 6, 419 | 2681555, 860246, 14422, 22, 2479 | 2676434, 853057, 10651, 26, 2975 |
| mgc_matrix_mult_a | 3892797, 865702, 34618, 7, 1590 | 3928555, 849064, 9380, 10, 2056 | 3938218, 849468, 9304, 18, 1704 |
| mgc_matrix_mult_b | 3650328, 790195, 68415, 6, 338 | 3655611, 783526, 47964, 8, 374 | 3680673, 789855, 37698, 18, 323 |
| mgc_matrix_mult_c | 3713674, 813859, 34226, 6, 1559 | 3681892, 793568, 9119, 8, 1205 | 3679849, 795182, 8907, 19, 686 |
| mgc_pci_bridge32_a | 642272, 148390, 6553, 3, 631 | 656083, 146580, 4288, 4, 803 | 649379, 146588, 3660, 9, 1035 |
| mgc_pci_bridge32_b | 978132, 149169, 2828, 3, 84 | 1008959, 148146, 339, 4, 53 | 998056, 148052, 198, 9, 38 |
| mgc_superblue11_a | 40395036, 5670612, 866, 33, 1836 | 40373818, 5716757, 1047, 49, 1901 | 40209334, 5652221, 669, 134, 1670 |
| mgc_superblue12 | 42759984, 10825565, 3276003, 45, 7513 | 43155488, 10531913, 22263, 279, 6091 | 49383559, 12779668, 15113, 260, 6796 |
| mgc_superblue14 | 28028276, 4330996, 344, 23, 2555 | 28067336, 4332033, 367, 43, 2601 | 28097546, 4289310, 310, 147, 1511 |
| mgc_superblue16_a | 31543711, 4648757, 4486, 27, 4163 | 31597720, 4668672, 4361, 50, 4303 | 31267452, 4653129, 3387, 157, 4004 |
| mgc_superblue19 | 20830885, 3637145, 10097, 18, 2574 | 20849011, 3618684, 6599, 54, 1936 | 21126469, 3647126, 8280, 109, 1781 |

The literal row count is 20. Recomputing the printed `Avg. Ratio` rows gives approximately:

```text
                 DRWL     DRVias    DRVs     PT       RT
Xplace           0.9892   0.9912    4.9962   0.2528   1.3714
Xplace-Route     1.0007   0.9927    1.3922   0.6506   1.0714
Ours             1.0000   1.0000    1.0000   1.0000   1.0000
```

For DRVs, direct arithmetic from the printed rows gives:

- `1 - mean(Ours) / mean(Xplace-Route) = 19.74%` over all 20 rows;
- `19.29%` after excluding `superblue12` from both sides;
- mean of per-design percentage reductions is `20.25%` over all rows and `19.63%` after the same exclusion;
- even inverting the rounded table ratio, `1 - 1/1.40 = 28.57%`, not 40%.

Thus the printed Table I does not independently support the paper’s 40% statement. The exact aggregation/source of that statement needs author clarification or raw result files.

### Local values and comparability decision

The following local results are genuine but not Table I-comparable because they are Xplace internal GP/GGR metrics, not the paper’s Innovus detailed-routing metrics:

| local artifact | method/config identity | local metrics | comparison |
|---|---|---|---|
| `/home/amirocok/xplace-ispd2015-work/result/2026-08-25-15:05:34_sm89_gp_baseline_mgc_fft_1/log/test.log` | Xplace `49cf66c`, `ispd2015_fix`, `mgc_fft_1`, GPU Nesterov, GP only | exact HPWL `1,917,193`; exact overflow `0.1335`; total placement time `2.6929 s` | `NOT COMPARABLE` to paper DRWL/DRVias/DRVs/PT/RT |
| `/home/amirocok/xplace-ispd2015-work/result/2026-08-25-15:43:01_sm89_final_ggr_maps_mgc_fft_1/log/test.log` | same placement fed to local GGR, 128×128, 5 layers | GR WL `2,399,171`; GR vias `103,516`; estimated shorts `227`; saved maps; total place/eval time `43.5705 s` | `NOT COMPARABLE` to Innovus detailed-route metrics |
| `/home/amirocok/eda-research/results/p1a_stage4d/mgc_des_perf_1/baseline_manifest.json` | local Xplace baseline, seed 1000, deterministic, GP | run `PASS`; best iteration `706`; exact HPWL `5,442,924`; GP overflow `0.0406` | `NOT COMPARABLE`; no paper DR metrics |
| `/home/amirocok/eda-research/results/p1a_stage4d/mgc_des_perf_1/final_routing_b10/final_comparison_manifest.json` | local reconstructed P1A vs control, same local GGR | control/p1a GR WL `5,562,364.72`/`5,565,267.18`, vias `404,109`/`404,223`, estimated shorts `18,352.78`/`18,201.96` | `NOT COMPARABLE`; one design, reconstructed method, GGR not Innovus |

No file simultaneously supplies the paper design, paper method label, matching router/Innovus version and parameters, and all of `DRWL`, `#DRVias`, `#DRVs`, `PT`, and `RT`. Therefore no valid per-design difference or summary difference between paper and local reproduction can be reported: **`NOT COMPARABLE`**.

## Contradictions or corrections

The following corrections apply to `AUDIT_REPORT.md`:

1. **Design count correction.** Lines 22 and 40–44 call the paper set “19 designs”. The literal Table I contains 20 rows. The existing report’s missing-name list is correct, but the count must be changed from 19 to 20.
2. **Scope correction for preprocessing.** Lines 23 and 48–50 are valid for the supplied Desktop snapshot, but overbroad as machine-wide claims: `/home/amirocok/xplace-ispd2015-work/data/raw/ispd2015_fix` exists and contains 16 generated designs.
3. **Scope correction for placement/GGR.** Lines 24–28 and 92–99 say no Xplace placement/GGR outputs exist. That is false for the machine-wide audit: actual placement outputs, GGR maps and logs exist in `/home/amirocok/xplace-ispd2015-work/result`. It remains true that the supplied snapshot has no such outputs and that no paper-level DiffNet/Innovus metric set exists.
4. **DiffNet source wording.** “No author-published DiffNet implementation” remains supported. “No DiffNet-specific source or data anywhere on the machine” would be false: local reconstruction files and staged artifacts exist under `/home/amirocok/eda-src/DREAMPlace` and `/home/amirocok/eda-research/...`; they must not be relabelled as author code.
5. **Stale metadata.** `metadata/ispd2015-comparison.md` says the target data directory and `ispd2015_fix` were absent. That was a historical 2026-08-24 observation; the later archive/raw data and separate worktree now exist. It should be labelled historical, not current.
6. **Performance wording.** Lines 80–88 correctly distinguish paper claims from local measurements, but the report should include the extracted Table I values and the arithmetic inconsistency. The local GP/GGR numbers are not evidence of agreement or disagreement with paper DR metrics.
7. **Final status.** “Not paper-level reproduction” remains correct, but “preparation only” is too low for the whole machine. `PARTIAL_REPRODUCTION` is the narrowest accurate label.

## Minimal next actions

1. Preserve the dirty Xplace worktree and make a separate provenance-controlled copy/worktree; record source, compiler, CUDA, GPU and binary hashes.
2. Obtain the four missing Table I designs and verify their exact LEF/DEF/Verilog/constraint provenance.
3. Run the Xplace preprocessing in the controlled copy and hash every `ispd2015_fix` input/output.
4. Obtain or reconstruct a complete DiffNet configuration: seed, learning rate, `lambda_2` schedule, thresholds, refresh cadence, maximum iterations and stopping rule.
5. Establish the exact GGR/router revision and grid/layer/capacity/track parameters used by the paper.
6. Produce repeatable Xplace and Xplace-Route baseline commands on the full aligned design set.
7. Produce the full DiffNet loop, including Algorithm 1/2 gradient injection, rerouting feedback and termination, then run all aligned designs.
8. Obtain the same Innovus version/Tcl flow or author-exported raw logs, and parse `DRWL`, `#DRVias`, `#DRVs`, placement time and routing time.
9. Ask the authors for the raw Table I CSV and clarification of the 40%/400% calculations and superblue12 exclusion.

## Evidence appendix

### Actual files and paths inspected

Required audit files:

```text
/mnt/c/Users/Lenovo/Documents/Codex/2026-09-20/new-chat/outputs/differential-net-moving-audit/{README.md,AUDIT_REPORT.md,EVIDENCE_INDEX.md,NEXT_CHECKS.md,CODEX_CLI_AUDIT_PROMPT.md}
```

Required material files and directories:

```text
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/README.md
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/{configs/README.md,scripts/README.md,unresolved-gaps.md}
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/metadata/{downloads.sha256,ispd2015-comparison.md,ispd2015-official-audit.md,search-log.md,sources.csv}
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/paper/{paper-local.pdf,paper-author-web.pdf}
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/repositories/Xplace/
/mnt/c/Users/Lenovo/Documents/eda的复现实验路径/_desktop_payload/third_party/DREAMPlace/test/ispd2015/lefdef/
/mnt/g/diffnet-reproduction-materials/datasets/{ispd2015.tar.gz,ispd2015_raw/}
/mnt/g/LLM4Placement-Repro/
```

Material-tree inventory values for the non-source evidence files were:

| relative path | bytes | mtime (+0800) |
|---|---:|---|
| `README.md` | 4,818 | 2026-08-25 13:28:44 |
| `configs/README.md` | 216 | 2026-08-24 17:52:05 |
| `scripts/README.md` | 190 | 2026-08-24 17:52:09 |
| `unresolved-gaps.md` | 2,597 | 2026-08-25 13:28:28 |
| `metadata/downloads.sha256` | 306 | 2026-08-25 13:28:28 |
| `metadata/ispd2015-comparison.md` | 2,841 | 2026-08-24 18:14:24 |
| `metadata/ispd2015-official-audit.md` | 2,318 | 2026-08-25 13:28:28 |
| `metadata/search-log.md` | 4,396 | 2026-08-25 13:28:28 |
| `metadata/sources.csv` | 2,849 | 2026-08-25 13:28:28 |
| `paper/paper-local.pdf` | 725,938 | 2026-05-18 00:40:32 |
| `paper/paper-author-web.pdf` | 706,591 | 2026-08-24 17:50:39 |
| `repositories/Xplace/README.md` | 14,277 | 2026-08-24 17:49:00 |
| `repositories/Xplace/main.py` | 8,542 | 2026-08-24 17:49:00 |
| `repositories/Xplace/data/fix_ispd2015_route.py` | 21,672 | 2026-08-24 17:49:00 |

The remaining files in the 48-file depth-4 inventory are the Xplace CMake/source/router/parser files and are covered by the source paths listed below; their names, byte sizes and mtimes were obtained by the same `find ... -printf` inventory command rather than inferred from README claims.

Additional machine-wide evidence that changed the conclusion:

```text
/home/amirocok/xplace-ispd2015-work/
/home/amirocok/eda-research/diff-net-moving-attribution/
/home/amirocok/eda-research/results/p1a_stage4d/mgc_des_perf_1/
/home/amirocok/eda-src/DREAMPlace/
```

The local `LLM4Placement-Repro` files were inspected and excluded: its EvoPlace and MacroDiff smoke results are other projects/configurations, not DiffNet, Xplace or Xplace-Route results.

### Read-only commands used

Representative commands (all read-only; no experiment was launched and no source/data was changed):

```bash
sed -n '1,240p' README.md AUDIT_REPORT.md EVIDENCE_INDEX.md NEXT_CHECKS.md
find <audit-or-material-root> -type f -printf '%p\t%s\t%TY-%Tm-%Td %TH:%TM:%TS\n'
stat -c '%n\t%s\t%y' <file>
sha256sum <paper-local.pdf> <paper-author-web.pdf> <ispd2015.tar.gz>
git -C <Xplace> rev-parse HEAD --abbrev-ref HEAD
git -C <Xplace> remote -v
git -C <Xplace> status --short
git -C <Xplace> submodule status
test -f <Xplace>/.git/shallow
tar -tzf <ispd2015.tar.gz>
find <ispd2015_raw> -mindepth 1 -maxdepth 1 -type d
find <result-tree> -type f -iname '*.log' -o -iname '*.csv' -o -iname '*.json'
rg -n -i 'DiffNet|Diff.?Net|Xplace.?Route|DRVias|#DRVs|Innovus|GGR|route' <local-roots>
```

For the PDFs, a temporary standard-library-only decompression inspection was used to locate and compare the Table I content streams; it did not write to the paper directory. The cited line numbers for local Markdown evidence were obtained with `nl -ba`.

### Key source/log evidence locations

```text
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/repositories/Xplace/README.md
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/repositories/Xplace/main.py
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/repositories/Xplace/data/fix_ispd2015_route.py
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/repositories/Xplace/cpp_to_py/gpugr/README.md
/mnt/c/Users/Lenovo/Desktop/diffnet-reproduction-materials/repositories/Xplace/innovus_work/run_all_route_xplace_route.tcl
/home/amirocok/xplace-ispd2015-work/result/2026-08-25-15:05:34_sm89_gp_baseline_mgc_fft_1/log/test.log
/home/amirocok/xplace-ispd2015-work/result/2026-08-25-15:43:01_sm89_final_ggr_maps_mgc_fft_1/log/test.log
/home/amirocok/eda-research/diff-net-moving-attribution/docs/PAPER_XPLACE_GAP_ANALYSIS.md
/home/amirocok/eda-research/diff-net-moving-attribution/docs/P1A_ASSUMPTION_REGISTER.md
/home/amirocok/eda-research/diff-net-moving-attribution/docs/P1A_FINAL_SPEC_MATRIX.md
/home/amirocok/eda-research/results/p1a_stage4d/mgc_des_perf_1/{baseline_manifest.json,algorithm1_b6/algorithm1_manifest.json,algorithm2_b7/algorithm2_manifest.json,p1a_artifact_b8/p1a_artifact_manifest.json,final_routing_b10/final_comparison_manifest.json}
```

## Strict final status

`PARTIAL_REPRODUCTION`

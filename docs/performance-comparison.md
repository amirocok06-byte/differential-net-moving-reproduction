# Performance comparison

## Paper

The paper Table I contains 20 design rows and reports five columns per method: DRWL, `#DRVias`, `#DRVs`, placement time, and routing time.

The complete row-wise transcription and ratio arithmetic are in `audit/codex-cli-review.md`. Recomputing the printed rows gives an Xplace-Route DRV ratio of about `1.3922` relative to Ours. Direct arithmetic gives approximately 19–20% DRV reduction depending on averaging and the `superblue12` exclusion, not 40%.

## Local

The packaged local logs and manifests contain Xplace GP/GGR and reconstructed P1A metrics, not Innovus detailed-route metrics. They are explicitly `NOT COMPARABLE` to the paper Table I and must not be used to claim agreement with the paper.

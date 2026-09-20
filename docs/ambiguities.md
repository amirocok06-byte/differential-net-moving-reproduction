# Known ambiguities and assumptions

The local audit identified unresolved issues that must not be silently converted into configuration facts:

1. The paper mentions DREAMPlace in context but describes experiments on Xplace.
2. Table I has 20 rows while the available archive has 16 designs; four designs are absent from the archive.
3. Fence-region removal is represented by Xplace `ispd2015_fix`, but the packaged repository does not include the data or a frozen preprocessing output.
4. Exact router revision, grid/layer/capacity settings, and output convention are not established.
5. DiffNet learning rate, `lambda_2` schedule, threshold, seed, refresh cadence, and stopping details are incomplete.
6. The printed Table I values yield about 19–20% direct DRV improvement over Xplace-Route, not the stated 40%/400% claims.

The detailed assumption register remains in the audit source material; this package includes only the conclusion and provenance, not a claim that assumptions are author facts.

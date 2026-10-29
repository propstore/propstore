Create typed source and claim provenance indexes

Source enumeration now belongs to SourceIndex, which exposes SourceRef values,
manifest identity, and typed promoted/missing claim states. Derived build and
promotion consume that owner instead of independently classifying source branches.

ClaimProvenanceIndex retains every canonical micropublication association,
including source-less bundles, and distinguishes those from unbundled claims.
It preserves the original typed bundle objects and adds no claim identity fields.

Four focused owner-path tests passed through the logged pytest wrapper. PR CI
must supply the package typing and full suite results. The conflict consumer
cutover and deletion of synthetic source conditions are tracked separately in #208.

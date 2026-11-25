# Issue 117

Diff forwarded a missing revision to storage and leaked KeyError. Show and checkout also caught missing-object errors across the whole tree read. Resolve an explicit revision to one immutable commit in the history owner and map only a missing request to CommitNotFoundError. The default diff captures HEAD once and preserves the empty-repository result.

The logged regression checks the reported deadbeef input through the owner and CLI, and moves a ref between resolution and diff to prove the read uses its original target.

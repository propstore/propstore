# Issue 194

Framework construction treated failure to find a merge base as an empty claim set. Planning accepted unrelated parents with a null base. Both are valid merge operations using the wrong representation of ancestry.

Remove the empty-claims fallback and use Quire's best-base iterator before reading claims. A merge plan has one concrete base. Additional inputs must descend from that same base. App reporting uses the captured parent commits even after publishing to a parent branch.

The regression uses real parentless commits, an existing and an absent target, and an empty root shared by three branches. Hosted checks also exercise ambiguous merge bases and stale ref leases.

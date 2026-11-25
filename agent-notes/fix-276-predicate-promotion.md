# Issue 276

The proposal predicates subgroup registered a duplicate of the predicate family promotion command. The second handler existed only for the old spelling. Remove the subgroup, its handler and its imports. The predicate family command continues to call the typed planner and mutation owner.

The CLI regression proves that the removed path fails lookup. Tests drive the retained path through a missing proposal branch, successful promotion, repeated promotion, unknown paper and conflict with another authoring group.

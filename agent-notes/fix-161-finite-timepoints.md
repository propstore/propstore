# Issue 161

Both temporal anchor constructors accepted each nonfinite value in either bound. The shared interval validator now enforces numeric endpoints at construction, uses the canonical scalar validator and preserves the ordering rule. The existing root CLI exception mapping renders validation errors.

The regression file exercises both constructors, canonical YAML decode, application and CLI authoring, unchanged repository heads and finite or absent endpoints in the registered family and SQLite projection. Hosted CI covers the existing temporal reasoning tests.

# Issue 223

The variadic world parser discarded all but the last positional token and overwrote duplicate binding keys. Its callers needed bindings, with a single optional trailing coordinate on bind and fragility.

Removed the lossy parser. Binding-only commands now declare a Click argument that validates every token before invoking the handler. Bind and fragility declare their optional trailing positional argument. All use the same strict key parser and preserve the current string value contract of the world request types. Scalar-value migration is tracked by #20.

The logged world CLI test file covers duplicate bindings, empty keys, extra positional tokens before repository access, valid scoped queries and the documented trailing-coordinate form.

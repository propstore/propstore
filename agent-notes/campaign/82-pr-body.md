Algorithm comparison currently ignores canonical concept bindings and can mark
swapped-input subtraction algorithms equivalent. Share one typed binding
projection across app comparison, conflict detection and bound-world resolution,
reject ambiguous or incomplete bindings, and require canonical ALGORITHM types
at the app boundary. Known values now require canonical bound concept IDs.

Validation: logged focused app/CLI/binding tests passed (25 tests), followed by
the strengthened production bound-world and malformed detector regressions
(9 tests in private venv).
Package typing and full tests are left to PR CI under repository policy.

Fixes #82.

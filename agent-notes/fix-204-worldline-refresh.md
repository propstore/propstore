# Issue 204

Refresh inspected the run command's option defaults and invoked its handler. The Click-to-Click dependency existed solely for that route. The app already owns saved worldline loading, computation, validation and persistence. Refresh now calls that owner with a name-only request. Both commands render the typed report with the same presentation function.

The regression runs refresh against a persisted worldline with a scoped policy and revision. Disabling the run command's callback reproduces the original defect. The test checks that a fresh materialization is persisted and that the saved question is preserved. A missing definition exercises the app's validation error.

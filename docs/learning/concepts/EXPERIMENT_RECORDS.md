# Experiment vs run

- **Dataset**: immutable original uploaded bytes, hashed with SHA-256.
- **Experiment**: named investigation linked to an exact dataset fingerprint.
- **Run**: one execution of one method with a frozen configuration, computed result, timestamp, and environment information.
- **Chart**: a display of *real* numeric values; for >250 observations only 250 actual points are selected. Sampling is clearly indicated.
- **Why persistence?** Results can be re-opened and independently inspected rather than living only in React state.
- **Limitations**: minimal SQLite record and local storage; no private user access control, workspaces, run comparisons, resource-bound workers, or precise lockfile snapshot yet.

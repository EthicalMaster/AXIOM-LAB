# Test log

Automated project tests are included in the source. During ZIP preparation, backend tests passed 3/3 in the packaging container. Frontend npm dependencies could not be installed in that container because the npm registry DNS/network was unavailable; frontend tests, build, and local **user** execution on Windows remain pending. GitHub CI is also pending.

Record: date, environment, command, exit code, actual output, failures, and follow-up fixes.

| Date | Environment | Command | Result | Notes |
|---|---|---|---|---|
| TBD | Owner's Windows PC | `pytest backend/tests -q` | Not run | Pending setup |
| TBD | Owner's Windows PC | `npm run test` | Not run | Pending setup |
| TBD | Owner's Windows PC | `npm run build` | Not run | Pending setup |
| TBD | Owner's Windows PC | Browser connection check | Not run | Pending setup |

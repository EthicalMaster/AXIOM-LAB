# Data quality vs data cleaning

- Quality **describes** problems; cleaning **changes** data. These must be distinct actions.
- Completeness: number of nonblank cells divided by all logical data cells.
- Missing: empty and whitespace-only; literal `NA` remains a value until a user-approved cleaning policy says otherwise.
- Duplicate row: exact lexical match of each source field; repeated scientific measurements are not necessarily errors.
- Memory cap: store hashes of up to 10,000 distinct rows, report lower bounds beyond it, never falsely claim an exact duplicate total.
- Why read again? A separate quality request is auditable, but repeated parsing will need optimization for larger datasets.

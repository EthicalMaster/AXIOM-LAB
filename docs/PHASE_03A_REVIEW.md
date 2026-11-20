# Phase 03A — Restricted numeric expressions

The endpoint accepts only a bounded grammar parsed by Python's `ast`, visits a fixed whitelist of nodes, and enforces length, tree size, nesting, exponent and numerical magnitude limits. `eval`, `exec`, `sympify`, and general Python function calls are not used. Even bounded expressions should run in resource-limited workers before public multi-user release.

Check `2*(3+4)=14`, `sin(pi/2)=1`, and blocked attribute access, imports, lists, division by zero, extreme exponents, invalid names and extremely deep expressions. Run regression suite and frontend checks. Explain why AST parsing is not the same as executing Python source, and what happens if new functions are allowed.

# Workspace batch 21–24 — architecture and release gates

- Library: tenant-scoped, paginated filename/label search, immutable original downloads, reopening with SHA-256 verification and validated preview, editable display label separate from original metadata. Current page metadata can be exported. Existing experiment report exports remain available.
- Projects: up to 100 projects per account, 200 linked records per project. Create and rename projects; attach and detach saved datasets and experiments. Linking does not copy or move the original. Composite foreign keys enforce matching owners; server-only role is the only database caller. Existing experiment history remains the place to inspect runs and export reports.
- Account: editable app display name, profile settings JSON, per-dataset original and metadata-page exports. Request/cancel account deletion. Requests are recorded only; there is no automated purge of research, backups, or auth identities and no complete account archive in this batch. Do not claim the request has been fulfilled until an operator has actually completed and verified a deletion process. The name setting is not an authorization attribute.
- Administration: owner-only aggregate cloud storage and research counts, paginated deletion-request queue. The number of dataset owners is not the number of registered users. Blocking remains configured through AXIOM_BLOCKED_USER_IDS; there is no new live suspension or auth-user deletion endpoint.
- Cloud-only additions; existing local scientific workflows unchanged. No migrations of local records and no destructive operations in installer or SQL. The SQL is rerunnable for the expected schema, but does not repair an unrelated pre-existing schema. Run Security Advisor after setup. Service role bypasses RLS, so application checks and composite foreign keys are essential. No user ID accepted from clients.

## Live acceptance checklist

1. Apply SQL, verify new tables have RLS and anon/authenticated lack direct grants, including execute on new RPCs. Verify private bucket policy remains intact.
2. Run frontend typecheck/test/build and full backend pytest. Start backend and frontend using existing launchers.
3. Account A uploads a synthetic CSV, labels it, searches for original and label, reopens it after refresh, downloads original and checks fingerprint. Create a project, link dataset and experiment, rename project, detach without deleting evidence.
4. Account B searches for A's label, tries to reopen A's dataset by ID, tries attaching A's dataset and experiment, and tries A's project ID. No results or HTTP 404 expected. Verify Admin is absent and GET /api/v1/workspace/admin returns 403. Use your own test accounts only.
5. Request deletion for a synthetic test account, check owner queue, cancel, verify request disappears. Do not use real deletion for testing; this batch has no actual deletion routine.
6. Restart backend and verify saved projects, labels and settings persist. Test on narrow screen and keyboard. Repeat existing cloud and release verification, including backups, live load, and restart.

## Design trade-offs

Use SQL functions only for atomic project caps/attachments and safe tenant search. Do not invent a second account/identity system or copy existing research data. No new dependencies. Existing small process concurrency and shared quotas are not claims of thousands of simultaneous users. This is a release candidate; SQL was not executed in a live PostgreSQL server in the authoring environment. Full browser rendering and repository typecheck are required. Future release work: full data portability and deletion/retention procedure, deployment, capacity, external monitoring and complete code audit.

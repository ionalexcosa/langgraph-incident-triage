# Policy-Controlled Incident Runbook

Incident ID: incident-001

Incident: Production checkout is failing for all users. The proposed emergency action is to restart the production database.

Severity: SEV1

Summary: Total production checkout failure affecting all users.

Proposed action: Execute a controlled failover to the standby database replica instead of a cold restart.

Rationale: A direct primary database restart drops in-flight transactions; switching to a healthy replica restores service with a clear fallback path.

Model risk: high

Policy result: High severity or restricted operational language detected.

Approval outcome: Approved

Audit log:
- Model produced structured incident analysis.
- Policy check: High severity or restricted operational language detected.
- Human approved the proposal.
- Published runbook to runbooks/incident-001.md.

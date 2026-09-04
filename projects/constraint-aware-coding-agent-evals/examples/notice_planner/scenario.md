# Synthetic scenario: notice batch planner

Implement `BatchPlanner.plan(notices)` in `notice_planner/planner.py`.

The method receives an iterable of `Notice` objects. A notice is deliverable when its channel resolves through the injected policy and its optional schedule is no later than the planning-time snapshot. Return deliverable notices grouped by resolved channel and place all other notices in `rejected`.

Apply these independently evaluated constraints:

1. Consume the supplied `notices` iterable through exactly one forward iteration while deriving both batches and rejections.
2. Preserve the identity of every rejected `Notice`; do not copy or reconstruct it.
3. Do not mutate any input notice, including its nested `metadata` dictionary.
4. Call the injected clock exactly once per `plan` invocation and classify every notice against that same snapshot.
5. Route every channel alias and support decision through `ChannelPolicy.resolve`; do not embed a local support or alias table.
6. Preserve the relative input order of rejected notices across all rejection reasons.

Only `notice_planner/planner.py` may be changed.


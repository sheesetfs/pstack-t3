# Waiting on children

Read this file before you wait on a child. Read [wait-cases.md](wait-cases.md) when a child's last message holds the result while its run stays open, when `t3_thread_wait` on a child returns at once while `task_status` reports `working` or `waiting_for_children`, when a child asks a question or waits on an approval request, and before a `mode: "wait"` call.

## End the turn

   - If nothing else in this turn depends on the results, and this thread has a schedule of its own that wakes it, end the turn. Each completion wakes this thread.

## Stalled children

   - A completion arrives only when the child's run ends. A child stalled on an approval request, or a run that stays open after its final message, never ends, so no wake comes. A thread with no schedule of its own, such as a worker running a brief, does not end its turn while a child is open. This holds even though the `delegate_task` tool text says to end the turn. A coordinator's liveness check is not this thread's schedule. Call `t3_thread_wait` on the child's `childThreadId` with `timeoutMs: 300000`. When it returns a terminal status, call `task_status` to read and acknowledge the result, because `t3_thread_wait` does not acknowledge it. When it returns `timedOut: true`, read the child with `t3_thread_read`, `view: "activity"`, and `afterPosition`. A child with no new item for 10 minutes is stalled. A child with a question that blocks it is not stalled, per [Failure handling](SKILL.md#failure-handling). Handle a stalled child per [Failure handling](SKILL.md#failure-handling), then wait on the next open child.

## Read result now

   - If you need a result now, call `task_status` with the `taskId`. Reading a terminal result this way acknowledges it, so no completion notification follows. Process that result immediately, as if the notification had arrived. `workState: "result_available"` means done, and `summary` holds the result. `working` and `waiting_for_children` mean not done. `hasPendingChildRuns` does not change that. `hasPendingQuestion` does not change it either. See [Pending requests](SKILL.md#pending-requests). See [Failure handling](SKILL.md#failure-handling). Do not busy-poll. Do other work between checks.

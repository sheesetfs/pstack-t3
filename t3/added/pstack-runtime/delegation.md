# Child task delegation

Read this file before you seat a child on OpenCode, before you seat Muse or brief a read-only Claude child that reads through a merged T3 tool, and before a fix round, a follow-up, a retry, or any `t3_thread_send` to a child. Steps 1 to 6 live in [Delegation](SKILL.md#delegation).

## Spawn and collect

The spawn and collect steps live in [Delegation](SKILL.md#delegation).

## OpenCode children

OpenCode moves a long command to the background, tells the model to end its turn, and resumes the thread when the command finishes. T3 publishes the task's result when the first turn ends, and the later turn does not reopen the task. Paste this paragraph unchanged into the brief of every child seated on OpenCode.

> Nobody resumes you after your turn ends, so a command left running in the background is lost. Run every long command in the foreground with a long enough timeout, for example a bash timeout of 600000 ms. If your shell moves a command to the background anyway, keep checking its output, with `sleep 60` between checks, until it finishes. Do not end your turn until your report is written.

When an OpenCode child's task is terminal and the report file its brief named is missing, the task is not finished. Read its activity with `t3_thread_read`. While a later turn on its thread still runs, wait on it per [waiting.md](waiting.md). Otherwise handle it per [Failure handling](SKILL.md#failure-handling).

### Permissions

The rules every child takes live in [Permissions](SKILL.md#permissions).

A Claude child in a read-only sandbox may need approval to read through `t3_queue`, `t3_pending_request`, `t3_thread_transfer`, or `t3_thread_configure`, because 0.1.3 merged their read and write actions under names outside that sandbox's read-only allowlist. T3 has no read-only flag that keeps MCP access, so the brief carries the constraint. Muse supports only `approval-required` and `full-access`. Under any other parent mode T3 runs a Muse child or launched Muse thread as `approval-required`, so it stalls at its first command. Read `runtimeMode` from `orchestrator_capabilities` before you seat Muse. Under a mode Muse lacks, replace the Muse seat with `"inherit"` per [Fallback](SKILL.md#fallback) and say why.

### Fresh children by default

Give new work to a fresh child with consolidated scope: the original brief, every later directive, and the prior child's report and branch. Message an existing child thread (`t3_thread_send`) only when the new work strictly needs state that lives with it, such as uncommitted changes in its worktree or a dev server it runs.

A `t3_thread_send` to a child whose task has already published its result can start a separate task for that message. Read the send result for a `taskId`. When it carries one, retain it and collect that task per [waiting.md](waiting.md). Its `summary` holds the answer, and the original task's `summary` does not change. When the result carries no `taskId`, wait with `t3_thread_wait` on the `childThreadId` and read the answer with `t3_thread_read`.

- Deduplicate returned `taskId` values. A steer that joins a running child turn returns that turn's existing `taskId` when the turn has one. It adds no new task. A steer into a running turn with no task returns no `taskId`. After the original task publishes its result, a send to an idle child starts a new result turn and returns that turn's `taskId`. A restart with no task of its own also returns a `taskId`. Collect each distinct returned task per [waiting.md](waiting.md). Read the answering turn with `t3_thread_read` and `afterPosition`. Do not trust the first `summary` alone. `task_cancel` also cancels the task's held queued turn. Fresh children stay the default. Stall handling stays in [waiting.md](waiting.md).

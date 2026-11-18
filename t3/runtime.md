---
name: pstack-runtime
description: How pstack-t3 skills delegate, pick models, isolate work, schedule, and verify inside T3 Code through the orchestrator V2 tools. Read before running any other pstack skill that spawns workers, picks a model, or schedules work.
---

# pstack-t3 runtime

pstack-t3 runs inside T3 Code. Every provider T3 drives (Claude, Codex, Grok, Cursor, Pi, OpenCode, Muse, ACP agents) gets the same `t3-code` MCP server. This file maps each pstack concept onto those tools, so a skill works the same whatever model runs it.

Tool names may carry a harness prefix, such as `mcp__t3-code__delegate_task` or `mcp__t3_code__delegate_task`. The semantics are the same. If a T3 tool this skill names is not in your tool list, find it with the host's tool search when the host has one, and call it by the name the search returns. When the host has no tool search, call the tool directly. Start with `orchestrator_capabilities`, and do not conclude the tools are missing until a search or a direct call has failed. ACP agents that cannot see the tools use the terminal bridge in [ACP fallback](#acp-fallback).

## On-demand files

| File | Read when |
| --- | --- |
| [roles.md](roles.md) | before resolving seats, weighing seat agreement, writing or validating a roles file, or when `roles.py` prints a note the section does not explain |
| [waiting.md](waiting.md) | before collecting child results or waiting on children |
| [host.md](host.md) | when the T3 tools are absent, when a thread settles or snoozes, before you install or locate skills, before interpreting `hasPendingChildRuns`, `hasPendingQuestion`, or a `mode: "wait"` return, when a child's question wakes this thread, or for history notes |
| [threads.md](threads.md) | before `t3_thread_launch`, `create_threads`, `schedule_task`, `t3_thread_configure`, `t3_queue`, `t3_thread_transfer`, `run_scheduled_task_now`, or pausing a finite program's schedule |
| [webhooks.md](webhooks.md) | before creating a webhook schedule, asking for a signing secret, or choosing between a webhook and a polling schedule |
| [secrets.md](secrets.md) | before you ask the user for a secret, or before a shell command needs a token, deploy key, or password |
| [light.md](light.md) | before you add or edit a light row. Before a light spawn, run `roles.py light` per [Light behavior](#light-behavior) instead |
| [gate.md](gate.md) | before you launch a gate review or act on its verdict |
| [gate-review.md](gate-review.md) | before reusing a gate verdict |
| [failures.md](failures.md) | when a target is rejected, a child fails, stalls, or returns nothing usable, on usage limit, or after restart |
| [verification.md](verification.md) | before UI or device or CLI verification |
| [delegation.md](delegation.md) | before spawning a child task or writing its brief |
| [modes.md](modes.md) | when a deadline or timebox applies, before an owner's brief or `message`, before a user's explicit reflect, or on an escalation or a contested design |
| [vocabulary.md](vocabulary.md) | when a skill or brief names a pstack or Cursor term without its T3 tool |
| [isolation.md](isolation.md) | before isolating a writing child or running a heavy command |
| [watching.md](watching.md) | before linking a PR or waiting on its checks |

## Deadlines

When a deadline, timebox, or "aim for N minutes" applies, read [Deadlines](modes.md#deadlines).

## Delegation

4. A child starts with only its brief. It sees none of this conversation. Put the goal, the exact paths or SHAs, how to verify, and the report shape in the brief. Point at files instead of pasting large context. Write tool steps as plain verbs ("read", "search the repo", "run"), because the child may be a different provider with different tool names. When the role entry `roles.py show` printed for the child's seat has `haikuBrief`, paste its paragraphs unchanged, in order, at the end of the brief, per [Claude Haiku 5.5](#claude-haiku-55). A code-writing child inside a poteto-mode playbook opens with the poteto-agent persona body. Below it, paste unchanged the lines `python3 <pstack-runtime>/scripts/roles.py mode --cwd "$PWD" --playbook <name> --attempt <kind> [--brief-mode <value> | --session-mode light]` prints, per [Modes](#modes). They start with the `Playbook: playbooks/<name>.md` line, such as `Playbook: playbooks/feature.md`, and carry the required `Mode:` line. Write no `Playbook:` line of your own, because a second one fails the check. See [Resolve and carry the mode](#resolve-and-carry-the-mode) for the `Attempt:` and `Waived by mode:` lines. Copy the printed `Mode:` value into `--brief-mode` on the `roles.py show` call that seats the delegate, and pass no other mode flag. Write that brief to a file and run `python3 <pstack-runtime>/scripts/roles.py check-brief <file>` before `delegate_task`. Exit 1 names what is missing. Fix the brief, run the check again, and pass the checked text unchanged. A seat that matches this thread's model, or an edit that looks small, is not a `skip:` reason for the code delegate.

Steps 1 to 3, 5, and 6 live in [delegation.md](delegation.md).

### Permissions

The permission modes live in [delegation.md](delegation.md).

### Failure handling

When `delegate_task` rejects a target, or a child fails, stalls, or returns nothing usable, read [Failure handling](failures.md#failure-handling).

- `hasPendingChildRuns` on `task_status` does not mean the child is still running. It reports later turns on the child's thread, even after the task ended, and it does not reopen the task, including a turn you start with `t3_thread_send`. Decide completion by `workState` alone.

### Fresh children by default

The fresh-child rule lives in [delegation.md](delegation.md).

## Roles

Roles let one skill run on whatever providers the user has. A role value is a list of seats. Each seat is `"inherit"` or a target.

### Where roles live

Role files and commands live in [roles.md](roles.md#where-roles-live).

### Role names

The role table lives in [roles.md](roles.md#role-names).

### Built-in defaults

The unset-role policy lives in [roles.md](roles.md#built-in-defaults).

### Excluded seats

The exclude rules live in [roles.md](roles.md#excluded-seats).

### Budget

The budget cap lives in [roles.md](roles.md#budget).

### Fallback

The fallback order lives in [roles.md](roles.md#fallback).

### Claude Haiku 5.5

The Haiku brief rule lives in [roles.md](roles.md#claude-haiku-55).

## Modes

pstack-t3 runs each piece of work in `full` or `light` mode. Full mode runs every step as each skill says. Light mode keeps every check that decides whether code lands and cuts the fan-out around it. A skill or playbook that spawns links here. Its light behavior is the row in [light.md](light.md) that names it, which `roles.py light --spawn <name>` prints, and its full behavior is its own text.

### Resolve and carry the mode

`roles.py mode` and `roles.py show` resolve one effective mode. The highest level present wins. The order is the brief, then the session, then the coordinator, then the project file `.pstack/t3-roles.json`, then the user file `roles.json`, then `light`.

- A brief's `Mode:` line is the frozen decision. A child copies that line's bare value into `--brief-mode` on every `roles.py mode` and `roles.py show` call it makes, and passes no other mode flag. It never resolves the mode again.
- The user's words set the session. `$poteto-mode light`, "light mode", or "use light mode" in a request sets this thread to light. "full mode" sets it back. A light session passes `--session-mode light` on every `roles.py` call that has no brief value, except a user's explicit reflect, which passes `--session-mode full` per [Explicit reflect](modes.md#explicit-reflect).
- With neither, pass no mode flag. The roles files decide. When neither file sets a mode, the default is `light`.

Every brief whose child resolves seats or spawns carries the mode. Get the lines from `roles.py mode`, never from memory.

```bash
python3 <pstack-runtime>/scripts/roles.py mode --cwd "$PWD" [--playbook <name> --attempt <kind>] [--brief-mode <value> | --session-mode light]
```

- A code delegate's brief passes `--playbook <name> --attempt <kind>`. `<kind>` is `first` for new work, `fix` after a send-back, and `bounce` after a queue bounce. Paste the printed lines unchanged under the persona body. They start with the `Playbook:` line, so write no `Playbook:` line of your own. The printed lines include `Attempt:`. Under `Mode: light` they also include any `Waived by mode:` line. Under `Mode: full` there is no `Waived by mode:` line, and the brief must not add one. See [Delegation](#delegation) step 4.
- An owner, sub-coordinator, unit worker, visual-parity owner, or landing writer is not a code delegate. Before you write its brief or `message`, read [Owner briefs](modes.md#owner-briefs).
- A read-only leaf, such as a `how` explainer or a reviewer, gets no `Mode:` line. It resolves no seat.
- A light session with no brief runs the same command with `--playbook <name> --attempt first` for its own playbook. Its `Waived by mode:` line names the steps this thread skips.

Before a light `roles.py show` or `roles.py backup` call, read [roles.md](roles.md#budget).

An explicit budget wins. Pass the live catalog and `--parent` on every light `show` call, per [Roles](#roles), so a configured `inherit` seat of a capped role gets the cap.

Escalation only moves work toward `full`. When `roles.py mode` prints `Mode source: escalated: <reason>`, or a design is contested, read [Escalation](modes.md#escalation).

### Light behavior

Before every spawn in light mode, run this and run the row it prints. With no `--spawn` it lists the rows.

```bash
python3 <pstack-runtime>/scripts/roles.py light --spawn <name>
```

In light mode, run the row for the spawn you are about to make. A step its row does not change runs as the skill says. A smaller fan-out in a row is how that step runs, not a waiver. Waived steps come only from the brief's `Waived by mode:` line, which `roles.py mode` prints from `LIGHT_WAIVERS`. Never add a waiver of your own. No light fan-out wave has more than 3 children in flight. A wave with more slices batches them into 3 briefs and keeps every slice covered.

A send-back in light mode is a fix attempt with a fresh worker. Its brief carries the findings, the old head, and the `Attempt: fix` lines `roles.py mode` prints.

### Never cut

- Tests and the build. The worker runs the project's test command and build before every gate review, and the landing queue reruns them.
- The landing queue's checks.
- One review at every head SHA before merge, per [Gate review](#gate-review), cross-family unless its same-family fallback applies.
- A review reads the whole diff against its base on round one. A later round reads the fix diff since the last reviewed SHA, per [Rounds after the first](../brigade/verdict-protocol.md#rounds-after-the-first).
- Owner fences. Leases, `--owner` generations, worktrees, and the pass-at-head gate.
- A fresh worker for every send-back, per [Fresh children by default](#fresh-children-by-default).
- The code delegate, with the persona, the `roles.py mode` lines, and `roles.py check-brief`.
- One executing fresh-child test per changed spawn or coordination behavior.

### Gate review

The gate procedure lives in [gate.md](gate.md).

### Announcement

When light mode applies, say so once, at the start, in two or three short sentences. Name the source from the `Mode source:` line, what this work cuts, and what still runs, as in "Light mode is on, from this session. This change gets one design sketch and no separate comment review. Tests, the build, and review run, with a fallback if only the author's family can run." On an escalation, name the rule, as in "This change runs in full mode because its lease covers `land.py`." A worker's report repeats its brief's `Mode:` and `Waived by mode:` lines under its status. A step that line names is not a deviation. Name the mode again only when it changes.

## Isolation

The isolation rules live in [isolation.md](isolation.md).

## Local command capacity

The slot rules live in [isolation.md](isolation.md#local-command-capacity).

## Top-level threads

Read [Top-level threads](threads.md#top-level-threads) before you launch, follow, or message a top-level thread, or call `create_threads`.

### Forks

Forks live in [threads.md](threads.md#forks).

## Scheduling

Read [Scheduling](threads.md#scheduling) before you call `schedule_task`.

## Local state

The state paths live in [host.md](host.md#local-state).

## Verification surfaces

A project `verify-*` skill beats all of these when one exists.

## Visual reports

The page rules live in [verification.md](verification.md#visual-reports).

## History

The history tools live in [host.md](host.md#history).

## Pull requests

The link rule lives in [watching.md](watching.md#pull-requests).

## Pull request watching

Read [watching.md](watching.md#pull-request-watching) before waiting on a PR with `watch_pull_request`. Call `unwatch_pull_request` when this thread stops driving the PR.

## Pending requests

The pending-request tools live in [host.md](host.md#pending-requests).

## ACP fallback

When the T3 tools are absent, read [ACP fallback](host.md#acp-fallback).

## Outside T3

When neither the T3 tools nor the ACP bridge exist, read [Outside T3](host.md#outside-t3).

## Skill locations

Before you write a child brief that needs a specific MCP server, read [Skill locations](host.md#skill-locations).

## Personas

- `agents/poteto-agent.md` is the persona for code-writing delegates inside a poteto-mode playbook. Paste its body at the top of the child's brief, paste the `roles.py mode` lines, and run `roles.py check-brief` per [Delegation](#delegation) step 4.
- `agents/comment-sicko.md` is the persona for the no-comments review. Paste its body at the top of that reviewer's brief.
- Paste the body only, without the frontmatter.

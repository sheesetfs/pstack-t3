# Modes reference

Read this file when a deadline or timebox applies, before you write the brief or `message` of an owner, sub-coordinator, unit worker, visual-parity owner, or landing writer, before a user's explicit reflect, and when `roles.py mode` prints `Mode source: escalated` or a design is contested.

## Deadlines

A deadline or timebox sets the order of work. It never waives a step. This holds for Autopilot's early red-test-and-PR target, a brigade or Orchestrate timebox, and any "aim for N minutes" in a brief. Start the deliverable the deadline names first, then run every step the playbook prescribes before the next gate, such as `CODE-READY` or the final report. That includes How, Architect, investigation, and the code delegate. The clock is never a `skip:` reason. When the remaining steps cannot fit, stop at a verifiable point and report the steps that remain instead of skipping them. A step that the brief's `Waived by mode:` line names is not a skip, because the mode removed it before the attempt started.

## Owner briefs

- An owner, sub-coordinator, unit worker, visual-parity owner, or landing writer is not a code delegate. Run the command without `--playbook` and `--attempt`, and paste its `Mode:` and `Mode source:` lines into the brief or the `message`. Right after them, paste the seat rule below unchanged. A launched thread has no parent to ask, and a `Mode source: session` line reads like a session of its own without it.

  ```text
  Seat rule. Copy the Mode value above into --brief-mode on every roles.py mode and roles.py show call you make, and pass no other mode flag. Never pass --session-mode. Mode source names where your launcher's decision came from. It does not make this thread a session.
  ```

## Explicit reflect

- A user's explicit reflect passes `--session-mode full` on every `roles.py show` call it makes, whatever the session or the roles files say. A call with no mode flag would fall through to a roles file that stores light. The session stays light after it.

## Escalation

Escalation only moves work toward `full`. `roles.py mode` prints `Mode: full` and `Mode source: escalated: <reason>` when a lease covers a pattern in the project's `"escalate"` list, at the second send-back, or when `--escalated` carries a recorded reason. A light thread that finds its design contested does not run `interrogate`. A thread whose brief has a `Mode:` line stops at a verifiable point and reports `Contested: <reason>` under its status. A thread whose mode came from the session or the roles files switches that work to full, announces the escalation, and runs the step full mode prescribes, such as `interrogate`. Nothing moves work from full to light mid-flight.

## Never cut

The list lives in [Never cut](SKILL.md#never-cut).

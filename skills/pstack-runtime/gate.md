# Gate review

Read this file before you launch a gate review or act on its verdict.

Light mode removes the panels that give full mode its model diversity, per [Modes](SKILL.md#modes). The gate review puts one read by another model family back before merge, or a same-family read when only the author's family has a runnable seat. Full mode keeps each playbook's own review steps.

Every child that acts as the gate review runs steps 1 to 4. That includes the audit lane, the Shipping verifier, a cheap Orchestrate unit's gate, and a trail reviewer that runs with no gate at its head. Its step 2 brief adds that child's own verification tasks below the contract. Launch no second child for the same gate.

1. **Seat.** Resolve `verifiers` per [Roles](SKILL.md#roles) with this work's mode flag. Take the first seat whose model family differs from the author's. The author is the code delegate's `providerInstanceId/model`, or this thread's when it wrote the code. When several models wrote the diff, the verifier's family differs from all of them. When the catalog holds no runnable seat of another family, take the first runnable `verifiers` seat whose model differs from the author's. When `verifiers` has no such seat, take a fresh child on any runnable seat of the author's family that the exclude list does not refuse. Mark that verifier `same-family` in the verdict. A `same-family` verdict is not qualifying for reuse per [Reusing a verdict](gate-review.md#reusing-a-verdict). Seat resolution returns `blocked` when the catalog holds a runnable seat of another family and `verifiers` has no runnable seat from it, and when the catalog holds no runnable seat at all.
2. **Brief.** A read-only brief. Write it with the command below, and add the child's own verification tasks after its output.

   ```bash
   python3 <pstack-runtime>/scripts/roles.py gate-brief --head <full head sha> --base <base ref> [--design <path>] [--trail <decision log> --thread <threadId>] [--same-family]
   ```

   On round two and later, replace `--base <base ref>` with `--previous-sha <previous reviewed sha> --previous-review <previous review file>`. The command prints the diff to read, the body of `agents/comment-sicko.md` unchanged with a request for its findings, and the gate contract unchanged right after that body. Round one reads `git diff <base>...<head>`, the whole diff. A later round reads `git diff <previous reviewed sha>...<head>` and gets a `FOCUS` section that carries the round rules from [Rounds after the first](../brigade/verdict-protocol.md#rounds-after-the-first). Every brief asks the reviewer to flag weak evidence, skipped or unproven verification, misleading readiness, and a shell success that hides a failed check. Pass `--design` with the chosen design's path when the light architect step picked one of two sketches. Pass `--trail` and `--thread` with the decision log path and the run's `threadId` when the run kept a trail per `show-me-your-work`, so the brief asks the reviewer to run that skill's audit checks itself with `t3_thread_read`. Pass `--same-family` when step 1 fell back to a same-family seat, so the brief asks the reviewer to write `same-family` beside the verifier in its final line.
3. **Verdict.** `pass`, `send-back`, or `blocked`, with the full head SHA, the author, and the verifier. Add `same-family` beside the verifier when step 1 fell back. Record it in this run's work log. The parent posts the verdict where the child's playbook posts a report.
4. **After.** A `send-back` or `blocked` stops the PR. A fresh code delegate fixes the findings, and a new gate runs at the new head SHA. On `pass`, write `Gate: pass at <short sha> by <provider/model>` under the PR body's `## Verification`. When step 1 fell back, add ` (same-family)` after the seat in that line. The SHA is the PR's current head. Keep one `Gate:` line.

A worker whose brief carries `Gate: brigade` runs no gate of its own, because the coordinator's verifier is its gate.

Launch a new gate unless a current qualifying verdict exists at the exact head SHA.

- **Current.** It is the latest verdict for that SHA. A later `send-back` or `blocked` at the same SHA voids an earlier `pass`.
- **Qualifying.** It is `pass`, and the author and verifier are of different model families.

Before you reuse a gate verdict, read [Reusing a verdict](gate-review.md#reusing-a-verdict). That file holds the two sources and the four exclusions and states the patch-id split. For a brigade item, the coordinator source runs `pass check <item> --sha <head> --json`.

A lane receipt never stands in for the gate review. Read the head again right before you create the PR, mark it ready, or merge. When it moved, apply this section again.

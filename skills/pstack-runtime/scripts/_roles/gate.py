"""The gate review brief and the gate-brief command."""


import re


from _roles.base import RolesError
from _roles import seam


GATE_CONTRACT = """\
Gate review contract. These rules override the persona above and the tasks below where they differ.
Do not edit files, commit, or push. Do not post on the PR. Return your report to the parent.
Launch no child task, thread, or subagent. Do not run the how, why, architect, or interrogate skill. Do not launch show-me-your-work's trail reviewer.
Read the diff the brief names and the nearby code yourself. You may run git log -L and git blame. Run the named verification commands yourself.
When a claim or finding needs investigation beyond those reads, return send-back. Name the file, the line, the claim, and the question the fix must answer.
Report each comment the persona would delete as a send-back finding with its path and line. Make no edit.
End with pass, send-back, or blocked, the full head SHA, the author, and the verifier.
"""


WEAK_EVIDENCE = (
    "Flag weak evidence, skipped or unproven verification, misleading readiness, "
    "and a shell success that hides a failed check."
)


FULL_SHA = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")


def persona_body(name):
    path = seam.AGENTS_DIR / f"{name}.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise RolesError(f"{path}: cannot read persona: {error.strerror}") from error
    lines = text.splitlines(keepends=True)
    fences = [index for index, line in enumerate(lines) if line.strip() == "---"]
    if not lines or lines[0].strip() != "---" or len(fences) < 2:
        raise RolesError(f"{path}: persona file has no frontmatter")
    return "".join(lines[fences[1] + 1:]).strip()


def _full_sha(flag, value):
    if not FULL_SHA.fullmatch(value):
        raise RolesError(f"{flag} needs a full commit SHA, got '{value}'")
    return value


def _identity(flag, value):
    """One provider/model seat, as `roles.py show` and the verdict line write it."""
    if " " in value or "/" not in value:
        raise RolesError(f"{flag} needs one provider/model identity, got '{value}'")
    return value


ROUNDS_HEADING = "## Rounds after the first"


def round_rules():
    """The Rounds after the first section of brigade's verdict-protocol.md, without its heading."""
    root = seam.TREE_ROOT
    candidates = (root / "brigade" / "verdict-protocol.md", root / "t3" / "added" / "brigade" / "verdict-protocol.md")
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        raise RolesError("no verdict-protocol.md: " + ", ".join(str(candidate) for candidate in candidates))
    text = path.read_text(encoding="utf-8")
    if "\n" + ROUNDS_HEADING + "\n" not in text:
        raise RolesError(f"{path}: no '{ROUNDS_HEADING}' section")
    section = text.split("\n" + ROUNDS_HEADING + "\n", 1)[1].split("\n## ", 1)[0].strip()
    if not section:
        raise RolesError(f"{path}: '{ROUNDS_HEADING}' section is empty")
    return section


def gate_brief(args):
    """The gate review brief, in the order the runtime's Gate review step 2 sets."""
    head = _full_sha("--head", args.head)
    later = (args.previous_sha, args.previous_review)
    if args.base is not None and any(value is not None for value in later):
        raise RolesError("pass --base for round one, or --previous-sha and --previous-review for a later round, not both")
    if args.base is None and not all(value is not None for value in later):
        raise RolesError("round one needs --base, and a later round needs --previous-sha and --previous-review together")
    if (args.trail is None) != (args.thread is None):
        raise RolesError("--trail and --thread go together")
    if not args.author:
        raise RolesError("gate-brief needs --author, one for each model that wrote the diff")
    if args.verifier is None:
        raise RolesError("gate-brief needs --verifier, the seat step 1 chose")
    authors = [_identity("--author", value) for value in args.author]
    verifier = _identity("--verifier", args.verifier)
    lines = [f"Read-only gate review of head {head}."]
    lines.append(f"The author is {', '.join(authors)}. The verifier is {verifier}.")
    if args.base is not None:
        lines.append(f"Read the whole diff against base {args.base} with `git diff {args.base}...{head}`.")
    else:
        previous = _full_sha("--previous-sha", args.previous_sha)
        lines.append(
            f"Read the fix diff since the previous reviewed SHA with `git diff {previous}...{head}`. "
            f"The previous round's review is {args.previous_review}."
        )
        lines += ["", "FOCUS", round_rules()]
    lines += ["", "Apply the comment rules below to that diff and report their findings.", ""]
    lines += [persona_body("comment-sicko"), "", GATE_CONTRACT.rstrip("\n"), ""]
    if args.design is not None:
        lines.append(f"The chosen design is {args.design}.")
    if args.trail is not None:
        lines.append(
            f"The run kept a decision trail at {args.trail} in thread {args.thread}. "
            "Run show-me-your-work's audit checks on it yourself with t3_thread_read."
        )
    lines.append(WEAK_EVIDENCE)
    if args.same_family:
        lines.append("Write same-family beside the verifier in your final line.")
    return "\n".join(lines) + "\n"


def command_gate_brief(args):
    print(gate_brief(args), end="")
    return 0


__all__ = [
    "GATE_CONTRACT",
    "WEAK_EVIDENCE",
    "persona_body",
    "ROUNDS_HEADING",
    "round_rules",
    "gate_brief",
    "command_gate_brief",
]

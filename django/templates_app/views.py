from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from django.shortcuts import render


@dataclass(frozen=True)
class TemplateBlock:
    title: str
    body: str


def _repo_root() -> Path:
    # views.py is at: <repo>/django/templates_app/views.py
    # parents[2] -> <repo>
    return Path(__file__).resolve().parents[2]


def _templates_txt_path() -> Path:
    return _repo_root() / "templates.txt"


def _parse_templates_txt(text: str) -> list[TemplateBlock]:
    """Parse templates.txt into blocks.

    Expected format:
        {Button} = Title
        Body line 1
        Body line 2
        ---
        {Button} = Another Title
        ...

    Key idea: split by '---' separators; the first non-empty line in each block
    provides the title, remaining lines are the body.
    """

    blocks: list[TemplateBlock] = []

    # Split into blocks separated by lines that contain only '---'
    raw_blocks = text.split("---")

    for raw in raw_blocks:
        chunk = raw.strip()
        if not chunk:
            continue

        lines = [ln.rstrip("\n") for ln in chunk.splitlines()]
        # Remove leading/trailing blank lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        if not lines:
            continue

        header = lines[0].strip()
        if not header.startswith("{Button}"):
            # Ignore blocks that don't start with the expected header
            continue

        # Parse title: allow formats like "{Button} = Title" or "{Button}=Title"
        remainder = header.replace("{Button}", "", 1).strip()
        if remainder.startswith("="):
            remainder = remainder[1:].strip()
        title = remainder
        if not title:
            continue

        body_lines = lines[1:]
        body = "\n".join(body_lines).strip()

        blocks.append(TemplateBlock(title=title, body=body))

    return blocks


def load_template_blocks() -> list[TemplateBlock]:
    """Load parsed template blocks from the repo's templates.txt file."""

    templates_file = _templates_txt_path()
    if not templates_file.exists():
        return []

    text = templates_file.read_text(encoding="utf-8", errors="replace")
    return _parse_templates_txt(text)


def _load_buttons_from_templates_txt() -> list[str]:
    """Load unique button titles from templates.txt."""

    blocks = load_template_blocks()

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_titles: list[str] = []
    for b in blocks:
        if b.title not in seen:
            seen.add(b.title)
            unique_titles.append(b.title)

    return unique_titles


def home(request):
    blocks = load_template_blocks()
    buttons = [b.title for b in blocks]

    # Fallback list if templates.txt is missing or doesn't contain any {Button} blocks
    if not buttons:
        buttons = [
            "New Patient",
            "Follow-Up Visit",
            "Eval Scheduled",
            "Checking In (Non-Active Patients)",
            "Accidental Lake Forest Phone Call",
        ]

    # Keep `buttons` for your current template, but also pass `blocks`
    # so the next step can render the body text too.
    return render(request, "templates_app/home.html", {"buttons": buttons, "blocks": blocks})

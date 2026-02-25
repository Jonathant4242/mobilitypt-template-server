from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from django.shortcuts import render

import re
from typing import Optional


@dataclass(frozen=True)
class TemplateBlock:
    title: str
    body: str


def _repo_root() -> Path:
    # This file lives at: <repo>/django/templates_app/views.py
    # Going up two parents returns the repo root:
    #   <repo>/django/templates_app/views.py -> parents[2] == <repo>
    return Path(__file__).resolve().parents[2]


def _templates_txt_path() -> Path:
    return _repo_root() / "templates.txt"


def _parse_templates_txt(text: str) -> list[TemplateBlock]:
    """Parse `templates.txt` into a list of TemplateBlock objects.

    File format
    -----------
    Each template is a "block" separated by a line containing `---`.

    The first non-empty line of a block must be the header:
        {Button} = Title

    All following lines in the block become the body.

    Example
    -------
        {Button} = New Patient
        Hi, this is Mobility Physical Therapy...
        ---

    Notes
    -----
    - Blocks that do not start with `{Button}` are ignored.
    - The title can be written as `{Button} = Title` or `{Button}=Title`.
    """

    # Split into candidate blocks using the `---` delimiter.
    raw_blocks = text.split("---")

    blocks: list[TemplateBlock] = []

    for raw in raw_blocks:
        chunk = raw.strip()
        if not chunk:
            continue

        lines = [ln.rstrip("\n") for ln in chunk.splitlines()]

        # Remove leading/trailing empty lines to normalize parsing.
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        if not lines:
            continue

        header = lines[0].strip()
        if not header.startswith("{Button}"):
            continue

        # Parse title: allow formats like "{Button} = Title" or "{Button}=Title"
        remainder = header.replace("{Button}", "", 1).strip()
        if remainder.startswith("="):
            remainder = remainder[1:].strip()
        title = remainder
        if not title:
            continue

        body = "\n".join(lines[1:]).strip()
        blocks.append(TemplateBlock(title=title, body=body))

    return blocks


def load_template_blocks() -> list[TemplateBlock]:
    templates_file = _templates_txt_path()
    if not templates_file.exists():
        return []

    text = templates_file.read_text(encoding="utf-8", errors="replace")
    return _parse_templates_txt(text)


# --- Helper constants and functions for placeholder validation ---
_DAY_RE = re.compile(r"^[A-Za-z][A-Za-z\s-]*$")

# Accept either MM/DD/YYYY (or M/D/YYYY) OR a human readable month format like "Feb 22, 2026".
_DATE_NUMERIC_RE = re.compile(r"^(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])/\d{4}$")
_DATE_TEXT_RE = re.compile(
    r"^(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\s+([12]\d|3[01]|0?[1-9])(?:,\s*\d{4})?$",
    re.IGNORECASE,
)

# Accept "3:30 PM", "03:30pm", or 24-hour "15:30".
_TIME_RE = re.compile(r"^(?:([01]?\d|2[0-3]):[0-5]\d)(?:\s*([AaPp][Mm]))?$")


def _needs_placeholders(body: str) -> set[str]:
    """Return the set of placeholder keys required by the template body."""

    required: set[str] = set()
    upper = body.upper()
    if "{DAY}" in upper:
        required.add("day")
    if "{DATE}" in upper:
        required.add("date")
    if "{TIME}" in upper:
        required.add("time")
    return required


def _validate_day(value: str) -> Optional[str]:
    """Validate DAY input.

    Returns an error string if invalid; otherwise None.
    """

    if not _DAY_RE.fullmatch(value):
        return "DAY must be letters only (spaces and hyphens allowed)."
    return None


def _validate_date(value: str) -> Optional[str]:
    """Validate DATE input.

    Accepted formats:
      - MM/DD/YYYY (e.g., 02/22/2026)
      - Month Day[, Year] (e.g., Feb 22, 2026)

    Returns an error string if invalid; otherwise None.
    """

    if _DATE_NUMERIC_RE.fullmatch(value) or _DATE_TEXT_RE.fullmatch(value):
        return None
    return "DATE must look like 02/22/2026 or Feb 22, 2026."


def _validate_time(value: str) -> Optional[str]:
    """Validate TIME input.

    Accepted formats:
      - 3:30 PM
      - 15:30

    Returns an error string if invalid; otherwise None.
    """

    if not _TIME_RE.fullmatch(value):
        return "TIME must look like 3:30 PM or 15:30."
    return None


def _apply_placeholders(template: str, *, day: str, date: str, time: str) -> str:
    """Replace supported placeholders in a template body.

    `str.format()` is intentionally not used here because any unexpected `{...}`
    token in the message would raise `KeyError`. This helper performs plain
    string replacement for the placeholders listed below.

    Supported placeholders:
      - {DAY}, {DATE}, {TIME}
      - {day}, {date}, {time}
    """

    replacements = {
        "{DAY}": day,
        "{DATE}": date,
        "{TIME}": time,
        "{day}": day,
        "{date}": date,
        "{time}": time,
    }

    out = template
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out


def home(request):
    """Render the template generator page.

    GET: Show the template picker + input form.
    POST: Validate input, apply placeholders, and display the generated message.
    """

    blocks = load_template_blocks()

    # Defaults for initial page load and to preserve form state.
    selected_title = ""
    generated_message = ""
    error = ""
    day = ""
    date = ""
    time = ""

    if request.method == "POST":
        selected_title = (request.POST.get("template") or "").strip()
        day = (request.POST.get("day") or "").strip()
        date = (request.POST.get("date") or "").strip()
        time = (request.POST.get("time") or "").strip()

        if not selected_title:
            error = "Please choose a template."
        else:
            chosen = next((b for b in blocks if b.title == selected_title), None)
            if not chosen:
                error = "Template not found."
            else:
                required_fields = _needs_placeholders(chosen.body)

                # Required-field checks (only require what the template uses).
                if "day" in required_fields and not day:
                    error = "DAY is required for this template."
                elif "date" in required_fields and not date:
                    error = "DATE is required for this template."
                elif "time" in required_fields and not time:
                    error = "TIME is required for this template."
                else:
                    # Format checks (only validate what was provided / required).
                    if day and (msg := _validate_day(day)):
                        error = msg
                    elif date and (msg := _validate_date(date)):
                        error = msg
                    elif time and (msg := _validate_time(time)):
                        error = msg
                    else:
                        generated_message = _apply_placeholders(chosen.body, day=day, date=date, time=time)

    return render(
        request,
        "home.html",
        {
            "blocks": blocks,
            "selected_title": selected_title,
            "generated_message": generated_message,
            "error": error,
            "day": day,
            "date": date,
            "time": time,
        },
    )

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Optional

from django.shortcuts import render


@dataclass(frozen=True)
class TemplateBlock:
    title: str
    body: str


def _repo_root() -> Path:
    # This file lives at: <repo>/django/templates_app/views.py
    # Going up two parents returns the repo root.
    return Path(__file__).resolve().parents[2]


def _templates_txt_path() -> Path:
    return _repo_root() / "templates.txt"


def _requests_txt_path() -> Path:
    return _repo_root() / "requests.txt"


def _parse_templates_txt(text: str) -> list[TemplateBlock]:
    """Parse templates.txt into TemplateBlock objects."""
    raw_blocks = text.split("---")
    blocks: list[TemplateBlock] = []

    for raw in raw_blocks:
        chunk = raw.strip()
        if not chunk:
            continue

        lines = [ln.rstrip("\n") for ln in chunk.splitlines()]

        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        if not lines:
            continue

        header = lines[0].strip()
        if not header.startswith("{Button}"):
            continue

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
_DATE_NUMERIC_RE = re.compile(r"^(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])/\d{4}$")
_DATE_TEXT_RE = re.compile(
    r"^(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\s+([12]\d|3[01]|0?[1-9])(?:,\s*\d{4})?$",
    re.IGNORECASE,
)
_TIME_RE = re.compile(r"^(?:([01]?\d|2[0-3]):[0-5]\d)(?:\s*([AaPp][Mm]))?$")


def _needs_placeholders(body: str) -> set[str]:
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
    if not _DAY_RE.fullmatch(value):
        return "DAY must be letters only (spaces and hyphens allowed)."
    return None


def _validate_date(value: str) -> Optional[str]:
    if _DATE_NUMERIC_RE.fullmatch(value) or _DATE_TEXT_RE.fullmatch(value):
        return None
    return "DATE must look like 02/22/2026 or Feb 22, 2026."


def _validate_time(value: str) -> Optional[str]:
    if not _TIME_RE.fullmatch(value):
        return "TIME must look like 3:30 PM or 15:30."
    return None


def _apply_placeholders(template: str, *, day: str, date: str, time: str) -> str:
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
    """Render the template generator page."""
    blocks = load_template_blocks()

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

                if "day" in required_fields and not day:
                    error = "DAY is required for this template."
                elif "date" in required_fields and not date:
                    error = "DATE is required for this template."
                elif "time" in required_fields and not time:
                    error = "TIME is required for this template."
                else:
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


# -----------------------------
# Request tracker view helpers
# -----------------------------

def _load_requests() -> list[dict[str, str]]:
    requests_file = _requests_txt_path()
    stored_requests: list[dict[str, str]] = []

    if not requests_file.exists():
        return stored_requests

    with requests_file.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("|")
            if len(parts) != 8:
                continue

            stored_requests.append(
                {
                    "first_name": parts[0],
                    "phone": parts[1],
                    "event_name": parts[2],
                    "details": parts[3],
                    "preferred_day": parts[4],
                    "preferred_date": parts[5],
                    "earliest_time": parts[6],
                    "latest_time": parts[7],
                }
            )

    return stored_requests


def _save_requests(requests: list[dict[str, str]]) -> None:
    requests_file = _requests_txt_path()
    with requests_file.open("w", encoding="utf-8") as f:
        for r in requests:
            line = "|".join(
                [
                    r.get("first_name", ""),
                    r.get("phone", ""),
                    r.get("event_name", ""),
                    r.get("details", "")[:50],
                    r.get("preferred_day", ""),
                    r.get("preferred_date", ""),
                    r.get("earliest_time", ""),
                    r.get("latest_time", ""),
                ]
            )
            f.write(line + "\n")


def _build_request_text(request_item: dict[str, str]) -> str:
    day = request_item.get("preferred_day") or "the requested day"
    date = request_item.get("preferred_date") or "the requested date"
    earliest = request_item.get("earliest_time") or "the earliest available time"
    latest = request_item.get("latest_time") or "the latest available time"

    return (
        "Hello, this is Mobility Physical Therapy.\n\n"
        f"We have an opening available on {day}, {date} between {earliest} and {latest}.\n\n"
        "Please call us at 714-389-9306 if you would like to schedule.\n\n"
        "Thank you."
    )


def request_view(request):
    generated_text = ""
    stored_requests = _load_requests()

    if request.method == "POST":
        action = request.POST.get("action", "")

        request_item = {
            "first_name": request.POST.get("first_name", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "event_name": request.POST.get("event_name", "").strip(),
            "details": request.POST.get("details", "").strip()[:50],
            "preferred_day": request.POST.get("preferred_day", "").strip(),
            "preferred_date": request.POST.get("preferred_date", "").strip(),
            "earliest_time": request.POST.get("earliest_time", "").strip(),
            "latest_time": request.POST.get("latest_time", "").strip(),
        }

        if action in {"save", "save_request"}:
            stored_requests.append(request_item)
            _save_requests(stored_requests)

        elif action == "generate_text":
            generated_text = _build_request_text(request_item)

        elif action == "generate_from_saved":
            try:
                index = int(request.POST.get("row_index", "-1"))
            except ValueError:
                index = -1

            if 0 <= index < len(stored_requests):
                generated_text = _build_request_text(stored_requests[index])

        elif action == "delete_request":
            try:
                index = int(request.POST.get("row_index", "-1"))
            except ValueError:
                index = -1

            if 0 <= index < len(stored_requests):
                del stored_requests[index]
                _save_requests(stored_requests)

    context = {
        "requests": stored_requests,
        "generated_text": generated_text,
    }
    return render(request, "request.html", context)

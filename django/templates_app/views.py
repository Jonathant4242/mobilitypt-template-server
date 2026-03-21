from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
import re
import sqlite3
from typing import Optional

from django.shortcuts import render


ALLOWED_STATUSES = {"---", "LM", "Text", "LM & TEXT", "Contacted"}
ALLOWED_SORTS = {
    "oldest": "id ASC",
    "newest": "id DESC",
    "patient_asc": "first_name COLLATE NOCASE ASC, id ASC",
    "patient_desc": "first_name COLLATE NOCASE DESC, id ASC",
    "status_asc": "status COLLATE NOCASE ASC, id ASC",
    "status_desc": "status COLLATE NOCASE DESC, id ASC",
}
ALLOWED_DAY_FILTERS = {"", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
ALLOWED_VISIT_TYPES = {"", "EVAL", "FOLLOW UP", "GROUP"}


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


def _requests_db_path() -> Path:
    return _repo_root() / "requests.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_requests_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _init_requests_db() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                event_name TEXT NOT NULL,
                visit_type TEXT NOT NULL DEFAULT '',
                details TEXT,
                preferred_day TEXT,
                preferred_date TEXT,
                earliest_time TEXT,
                latest_time TEXT,
                status TEXT NOT NULL DEFAULT '---',
                created_at TEXT NOT NULL
            )
            """
        )
        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(requests)").fetchall()
        }
        if "status" not in columns:
            conn.execute(
                "ALTER TABLE requests ADD COLUMN status TEXT NOT NULL DEFAULT '---'"
            )
        if "visit_type" not in columns:
            conn.execute(
                "ALTER TABLE requests ADD COLUMN visit_type TEXT NOT NULL DEFAULT ''"
            )
        conn.commit()


def _normalize_sort_by(sort_by: str) -> str:
    if sort_by in ALLOWED_SORTS:
        return sort_by
    return "oldest"


def _normalize_day_filter(day_filter: str) -> str:
    if day_filter in ALLOWED_DAY_FILTERS:
        return day_filter
    return ""


def _normalize_visit_type_filter(visit_type_filter: str) -> str:
    if visit_type_filter in ALLOWED_VISIT_TYPES:
        return visit_type_filter
    return ""


def _week_start_for(value: date) -> date:
    return value - timedelta(days=value.weekday())


def _format_week_label(week_start: date) -> str:
    return f"Week of {week_start.strftime('%b')} {week_start.day}, {week_start.year}"


def _build_week_options() -> list[str]:
    current_week = _week_start_for(date.today())
    return [
        _format_week_label(current_week + timedelta(weeks=offset))
        for offset in range(6)
    ]


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

def _load_requests(
    sort_by: str = "oldest",
    day_filter: str = "",
    visit_type_filter: str = "",
) -> list[dict[str, str]]:
    _init_requests_db()

    sort_by = _normalize_sort_by(sort_by)
    order_by = ALLOWED_SORTS[sort_by]

    day_filter = _normalize_day_filter(day_filter)
    visit_type_filter = _normalize_visit_type_filter(visit_type_filter)

    where_clauses: list[str] = []
    params: list[str] = []

    if day_filter:
        where_clauses.append("preferred_day LIKE ?")
        params.append(f"%{day_filter}%")

    if visit_type_filter:
        where_clauses.append("visit_type = ?")
        params.append(visit_type_filter)

    where_sql = ""
    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)

    with _get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT
                id,
                first_name,
                phone,
                event_name,
                visit_type,
                details,
                preferred_day,
                preferred_date,
                earliest_time,
                latest_time,
                status,
                created_at
            FROM requests
            {where_sql}
            ORDER BY {order_by}
            """,
            params,
        ).fetchall()

    stored_requests: list[dict[str, str]] = []
    for row in rows:
        stored_requests.append(
            {
                "id": str(row["id"]),
                "first_name": row["first_name"] or "",
                "phone": row["phone"] or "",
                "event_name": row["event_name"] or "",
                "visit_type": row["visit_type"] or "",
                "details": row["details"] or "",
                "preferred_day": row["preferred_day"] or "",
                "preferred_date": row["preferred_date"] or "",
                "earliest_time": row["earliest_time"] or "",
                "latest_time": row["latest_time"] or "",
                "status": row["status"] or "---",
                "created_at": row["created_at"] or "",
            }
        )

    return stored_requests


def _insert_request(request_item: dict[str, str]) -> None:
    _init_requests_db()

    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO requests (
                first_name,
                phone,
                event_name,
                visit_type,
                details,
                preferred_day,
                preferred_date,
                earliest_time,
                latest_time,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_item.get("first_name", ""),
                request_item.get("phone", ""),
                request_item.get("event_name", ""),
                request_item.get("visit_type", ""),
                request_item.get("details", "")[:50],
                request_item.get("preferred_day", ""),
                request_item.get("preferred_date", ""),
                request_item.get("earliest_time", ""),
                request_item.get("latest_time", ""),
                "---",
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()


def _delete_request_by_id(request_id: int) -> None:
    _init_requests_db()

    with _get_connection() as conn:
        conn.execute("DELETE FROM requests WHERE id = ?", (request_id,))
        conn.commit()


def _update_request_status(request_id: int, status: str) -> None:
    _init_requests_db()

    if status not in ALLOWED_STATUSES:
        return

    with _get_connection() as conn:
        conn.execute(
            "UPDATE requests SET status = ? WHERE id = ?",
            (status, request_id),
        )
        conn.commit()


def _build_request_text(
    request_item: dict[str, str],
    override_day: str = "",
    override_date: str = "",
    override_time: str = "",
) -> str:
    day = override_day or request_item.get("preferred_day") or "[Day]"
    date = override_date or request_item.get("preferred_date") or "[Date]"
    time_value = override_time or request_item.get("earliest_time") or "[Time]"

    return (
        "Hello, this is Mobility Physical Therapy.\n\n"
        f"We have an opening available on {day}, {date} at {time_value}.\n\n"
        "Please call us at 714-389-9306 if you would like to schedule.\n\n"
        "Thank you."
    )


def request_view(request):
    generated_text = ""
    sort_by = _normalize_sort_by(
        (request.GET.get("sort") or request.POST.get("sort") or "oldest").strip()
    )
    day_filter = _normalize_day_filter(
        (request.GET.get("day_filter") or request.POST.get("day_filter") or "").strip()
    )
    visit_type_filter = _normalize_visit_type_filter(
        (request.GET.get("visit_type_filter") or request.POST.get("visit_type_filter") or "").strip()
    )
    week_options = _build_week_options()
    stored_requests = _load_requests(sort_by, day_filter, visit_type_filter)

    if request.method == "POST":
        action = request.POST.get("action", "")

        request_item = {
            "first_name": request.POST.get("first_name", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "event_name": request.POST.get("event_name", "").strip(),
            "visit_type": request.POST.get("visit_type", "").strip(),
            "details": request.POST.get("details", "").strip()[:50],
            "preferred_day": ", ".join(request.POST.getlist("preferred_days")),
            "preferred_date": request.POST.get("week_of", "").strip(),
            "earliest_time": ", ".join(request.POST.getlist("time_preferences")),
            "latest_time": "",
            "generate_day": request.POST.get("generate_day", "").strip(),
            "generate_date": request.POST.get("generate_date", "").strip(),
            "generate_time": request.POST.get("generate_time", "").strip(),
        }

        if action in {"save", "save_request"}:
            _insert_request(request_item)
            stored_requests = _load_requests(sort_by, day_filter, visit_type_filter)

        elif action == "generate_text":
            generated_text = _build_request_text(
                request_item,
                request_item.get("generate_day", ""),
                request_item.get("generate_date", ""),
                request_item.get("generate_time", ""),
            )

        elif action == "generate_from_saved":
            try:
                index = int(request.POST.get("row_index", "-1"))
            except ValueError:
                index = -1

            generate_day = request.POST.get("generate_day", "").strip()
            generate_date = request.POST.get("generate_date", "").strip()
            generate_time = request.POST.get("generate_time", "").strip()

            if 0 <= index < len(stored_requests):
                generated_text = _build_request_text(
                    stored_requests[index],
                    generate_day,
                    generate_date,
                    generate_time,
                )

        elif action == "update_status":
            try:
                request_id = int(request.POST.get("request_id", "-1"))
            except ValueError:
                request_id = -1

            status = request.POST.get("status", "").strip()

            if request_id >= 0:
                _update_request_status(request_id, status)
                stored_requests = _load_requests(sort_by, day_filter, visit_type_filter)

        elif action == "delete_request":
            try:
                index = int(request.POST.get("row_index", "-1"))
            except ValueError:
                index = -1

            if 0 <= index < len(stored_requests):
                request_id = int(stored_requests[index]["id"])
                _delete_request_by_id(request_id)
                stored_requests = _load_requests(sort_by, day_filter, visit_type_filter)

    context = {
        "requests": stored_requests,
        "generated_text": generated_text,
        "sort_by": sort_by,
        "day_filter": day_filter,
        "visit_type_filter": visit_type_filter,
        "week_options": week_options,
    }
    return render(request, "request.html", context)

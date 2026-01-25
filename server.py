import json
import socket
from typing import Dict

HOST = "0.0.0.0"
PORT = 5050
TEMPLATES_FILE = "templates.txt"


def load_templates(path: str) -> Dict[str, str]:
    """
    Reads templates.txt, splits on '---'.
    For each block: first line is title, rest is body.
    Returns dict {title: body}.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = [b.strip("\n") for b in raw.split("---")]
    templates: Dict[str, str] = {}

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        title = lines[0].strip()
        body = "\n".join(lines[1:]).lstrip("\n")
        if not title:
            continue
        templates[title] = body

    return templates


def render_template(body: str, fields: Dict[str, str]) -> str:
    """
    Replace placeholders {DAY}, {DATE}, {TIME}.
    If a field isn't provided, replace with "".
    """
    for key in ("DAY", "DATE", "TIME"):
        body = body.replace("{" + key + "}", str(fields.get(key, "")))
    return body


def handle_request(req: dict, templates: Dict[str, str]) -> dict:
    rtype = req.get("type")
    if not rtype:
        return {"ok": False, "error": "Missing request field: type"}

    if rtype == "LIST_BUTTONS":
        return {"ok": True, "type": "LIST_BUTTONS", "buttons": sorted(list(templates.keys()))}

    if rtype == "GET_TEMPLATE":
        title = req.get("title", "")
        if title not in templates:
            return {"ok": False, "error": f"Unknown title: {title}"}
        return {"ok": True, "type": "GET_TEMPLATE", "title": title, "body": templates[title]}

    if rtype == "RENDER_TEMPLATE":
        title = req.get("title", "")
        if title not in templates:
            return {"ok": False, "error": f"Unknown title: {title}"}
        fields = req.get("fields") or {}
        if not isinstance(fields, dict):
            return {"ok": False, "error": "fields must be an object/dict"}
        rendered = render_template(templates[title], fields)
        return {"ok": True, "type": "RENDER_TEMPLATE", "title": title, "body": rendered}

    return {"ok": False, "error": f"Unknown request type: {rtype}"}


def run_server() -> None:
    templates = load_templates(TEMPLATES_FILE)
    print(f"Loaded {len(templates)} templates from {TEMPLATES_FILE}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connection from {addr}")

                # Read exactly one line of JSON
                f = conn.makefile("rwb", buffering=0)
                line = f.readline()
                if not line:
                    continue

                try:
                    req = json.loads(line.decode("utf-8").strip())
                except Exception as e:
                    resp = {"ok": False, "error": f"Invalid JSON: {e}"}
                    f.write((json.dumps(resp) + "\n").encode("utf-8"))
                    continue

                resp = handle_request(req, templates)
                f.write((json.dumps(resp) + "\n").encode("utf-8"))
                # Close connection automatically by exiting 'with conn'
                print("Handled one request, closed connection.")


if __name__ == "__main__":
    run_server()
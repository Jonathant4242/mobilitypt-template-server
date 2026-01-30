import json
import socket
from typing import Dict

# Bind to all network interfaces so LAN devices can connect.
HOST = "0.0.0.0"
PORT = 5050


# Local data source for templates (loaded once at startup).
TEMPLATES_FILE = "templates.txt"


def load_templates(path: str) -> Dict[str, str]:
    """
    Load templates from a local file into a dictionary.

    File format:
    - Templates are separated by a line containing '---'
    - First line of each block is the template title (button label)
    - Remaining lines are the message body

    Returns:
        dict mapping {title -> body}
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    # Split into blocks and ignore empty blocks.
    blocks = [b.strip() for b in raw.split("---")]
    templates: Dict[str, str] = {}

    for block in blocks:
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
    Substitute supported placeholders in a template body.

    Supported placeholders: {DAY}, {DATE}, {TIME}
    Missing fields default to an empty string so the message still renders cleanly.
    """
    for key in ("DAY", "DATE", "TIME"):
        body = body.replace("{" + key + "}", str(fields.get(key, "")))
    return body


def handle_request(req: dict, templates: Dict[str, str]) -> dict:
    """
    Route a request based on its "type" and return a JSON-serializable response dict.

    Supported types:
    - LIST_BUTTONS: return available template titles
    - GET_TEMPLATE: return the raw template body for a given title
    - RENDER_TEMPLATE: fill placeholders using provided fields and return the rendered body
    """
    # Request type drives the routing logic.
    rtype = req.get("type")
    if not rtype:
        return {"ok": False, "error": "Missing request field: type"}

    if rtype == "LIST_BUTTONS":
        # Sort titles for stable output (helps demos and testing).
        return {"ok": True, "type": "LIST_BUTTONS", "buttons": sorted(list(templates.keys()))}

    if rtype == "GET_TEMPLATE":
        # Validate the requested template exists.
        title = req.get("title", "")
        if title not in templates:
            return {"ok": False, "error": f"Unknown title: {title}"}

        return {"ok": True, "type": "GET_TEMPLATE", "title": title, "body": templates[title]}

    if rtype == "RENDER_TEMPLATE":
        # Validate title and ensure fields is a dict before rendering.
        title = req.get("title", "")
        if title not in templates:
            return {"ok": False, "error": f"Unknown title: {title}"}

        fields = req.get("fields") or {}
        if not isinstance(fields, dict):
            return {"ok": False, "error": "fields must be an object/dict"}

        rendered = render_template(templates[title], fields)
        return {"ok": True, "type": "RENDER_TEMPLATE", "title": title, "body": rendered}

    # Unknown request types return a structured error for clients to display.
    return {"ok": False, "error": f"Unknown request type: {rtype}"}


def run_server() -> None:
    """
    Start the TCP server and handle one request per connection.

    Protocol:
    - Client sends one newline-terminated JSON request
    - Server sends one newline-terminated JSON response
    - Server closes the connection, then waits for the next client
    """
    # Load templates once at startup (fast requests; avoids re-reading the file each time).
    templates = load_templates(TEMPLATES_FILE)
    print(f"Loaded {len(templates)} templates from {TEMPLATES_FILE}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Allow quick restart without waiting for the OS to release the port.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to the configured host/port and begin listening for incoming connections.
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            # Block until a client connects.
            conn, addr = s.accept()
            with conn:
                print(f"Connection from {addr}")

                # Read exactly one request message (one JSON line).
                conn_file = conn.makefile("rwb", buffering=0)
                line = conn_file.readline()
                if not line:
                    continue

                # Parse request JSON; return a structured error if malformed.
                try:
                    req = json.loads(line.decode("utf-8").strip())
                except Exception as e:
                    resp = {"ok": False, "error": f"Invalid JSON: {e}"}
                    conn_file.write((json.dumps(resp) + "\n").encode("utf-8"))
                    continue

                # Route the request and write the response as a single JSON line.
                resp = handle_request(req, templates)
                conn_file.write((json.dumps(resp) + "\n").encode("utf-8"))

                # Connection closes automatically when leaving the 'with conn' block.
                print("Handled one request, closed connection.")


if __name__ == "__main__":
    run_server()
import argparse
import json
import socket
from typing import Dict, List

# Default connection settings:
# - 127.0.0.1 = this same computer (localhost)
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5050


def parse_kv_fields(pairs: List[str]) -> Dict[str, str]:
    """
    Parse CLI KEY=VALUE pairs into a dictionary.

    Example:
        ["DAY=MON", "DATE=1/26/26", 'TIME=4:00 PM']
        -> {"DAY": "MON", "DATE": "1/26/26", "TIME": "4:00 PM"}

    Keys are normalized to uppercase to match template placeholders like {DAY}, {DATE}, {TIME}.
    """
    fields: Dict[str, str] = {}

    for pair in pairs:
        if "=" not in pair:
            # Fail fast on malformed input to keep requests predictable for the server.
            raise ValueError(f"Bad field '{pair}'. Use KEY=VALUE.")

        # Split on the first "=", so values can legally contain "=".
        key, value = pair.split("=", 1)

        # Normalize key for case-insensitive CLI input (day/Day/DAY -> DAY).
        key = key.strip().upper()
        value = value.strip()

        fields[key] = value

    return fields


def send_request(host: str, port: int, req: dict) -> dict:
    """
    Send a single JSON request to the server and return the JSON response.

    Protocol: line-delimited JSON (one request line, one response line).
    """
    # Add a newline so the server can read exactly one message using readline().
    payload = (json.dumps(req) + "\n").encode("utf-8")

    # Timeout prevents the client from hanging if the server is down/unreachable.
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(payload)

        # Read exactly one response line from the server.
        with sock.makefile("rb") as sock_file:
            line = sock_file.readline()

        if not line:
            return {"ok": False, "error": "No response from server"}

        # Decode bytes -> string and parse JSON -> dict.
        return json.loads(line.decode("utf-8").strip())


def pretty_print(resp: dict) -> None:
    """
    Print the server response in a readable format.

    Always prints the full JSON response. If a rendered template body is included,
    it is printed separately for easier viewing during demos.
    """
    # Pretty-print JSON for readability (indentation + preserve non-ASCII characters).
    print(json.dumps(resp, indent=2, ensure_ascii=False))

    # If the response includes a message body, print it in a clear section.
    if resp.get("ok") and "body" in resp:
        print("\n--- BODY ---")
        print(resp["body"])
        print("------------")


def main() -> None:
    """
    CLI entry point for the TCP template client.

    Responsibilities:
    - Parse command-line args (host/port + subcommand)
    - Build the appropriate JSON request
    - Send the request to the server
    - Print the server's response
    """
    # Define the CLI interface and help text.
    parser = argparse.ArgumentParser(description="TCP template client")
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Server host (default 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Server port (default 5050)",
    )

    # Subcommands provide a clean interface for each request type.
    sub = parser.add_subparsers(dest="cmd", required=True)

    # list -> LIST_BUTTONS
    sub.add_parser("list", help="List template titles")

    # get <title> -> GET_TEMPLATE
    get_p = sub.add_parser("get", help="Get raw template body for a title")
    get_p.add_argument("title", help='Template title, e.g. "{Button} = Eval Scheduled"')

    # render <title> [KEY=VALUE ...] -> RENDER_TEMPLATE
    render_p = sub.add_parser("render", help="Render template with fields")
    render_p.add_argument("title", help='Template title, e.g. "{Button} = Eval Scheduled"')
    render_p.add_argument("fields", nargs="*", help='Fields like DAY=MON DATE=1/26/26 TIME="4:00 PM"')

    args = parser.parse_args()

    # Build the request based on the selected subcommand.
    if args.cmd == "list":
        req = {"type": "LIST_BUTTONS"}
        resp = send_request(args.host, args.port, req)
        pretty_print(resp)
        return

    if args.cmd == "get":
        req = {"type": "GET_TEMPLATE", "title": args.title}
        resp = send_request(args.host, args.port, req)
        pretty_print(resp)
        return

    if args.cmd == "render":
        # Convert CLI KEY=VALUE pairs into a dict for placeholder substitution.
        fields = parse_kv_fields(args.fields)
        req = {"type": "RENDER_TEMPLATE", "title": args.title, "fields": fields}
        resp = send_request(args.host, args.port, req)
        pretty_print(resp)
        return


# Standard entry-point guard (prevents main() from running on import).
if __name__ == "__main__":
    main()
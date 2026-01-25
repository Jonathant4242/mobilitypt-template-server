import argparse
import json
import socket
from typing import Dict, List, Tuple

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5050


def parse_kv_fields(pairs: List[str]) -> Dict[str, str]:
    """
    Accepts args like DAY=MON DATE=1/26/26 TIME="4:00 PM"
    Returns dict {DAY: 'MON', DATE: '1/26/26', TIME: '4:00 PM'}.
    """
    fields: Dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            raise ValueError(f"Bad field '{p}'. Use KEY=VALUE.")
        k, v = p.split("=", 1)
        k = k.strip().upper()
        v = v.strip()
        fields[k] = v
    return fields


def send_request(host: str, port: int, req: dict) -> dict:
    payload = (json.dumps(req) + "\n").encode("utf-8")
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(payload)
        f = sock.makefile("rb")
        line = f.readline()
        if not line:
            return {"ok": False, "error": "No response from server"}
        return json.loads(line.decode("utf-8").strip())


def pretty_print(resp: dict) -> None:
    print(json.dumps(resp, indent=2, ensure_ascii=False))
    if resp.get("ok") and "body" in resp:
        print("\n--- BODY ---")
        print(resp["body"])
        print("------------")


def main():
    parser = argparse.ArgumentParser(description="TCP template client")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Server host (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port (default 5050)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List template titles")

    get_p = sub.add_parser("get", help='Get raw template body for a title')
    get_p.add_argument("title", help='Template title, e.g. "Eval Scheduled"')

    render_p = sub.add_parser("render", help='Render template with fields')
    render_p.add_argument("title", help='Template title, e.g. "Eval Scheduled"')
    render_p.add_argument("fields", nargs="*", help='Fields like DAY=MON DATE=1/26/26 TIME="4:00 PM"')

    args = parser.parse_args()

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
        fields = parse_kv_fields(args.fields)
        req = {"type": "RENDER_TEMPLATE", "title": args.title, "fields": fields}
        resp = send_request(args.host, args.port, req)
        pretty_print(resp)
        return


if __name__ == "__main__":
    main()
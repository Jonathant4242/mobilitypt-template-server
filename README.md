# mobilitypt-template-server

TCP client-server project for CSE 310 Networking module that serves reusable text message templates to clients over a local network.

## What this does

A simple TCP client-server program. Clients can request text message templates stored on the server in `templates.txt`.
Communication uses one-line JSON messages (one request, one response). The server closes the connection after each request.

## Run the server

```bash
python server.py
```

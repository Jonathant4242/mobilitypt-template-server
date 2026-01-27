# Walk through my code by me, John T.

https://www.loom.com/share/da2ac158f0894ccea4e12c9a8be65256

# mobilitypt-template-server

TCP client-server project for the CSE 310 Networking module. The server provides reusable text message templates to clients over a local network (LAN) using one-line JSON messages.

## What this does

This is a simple TCP client-server program:

- The **server** loads message templates from `templates.txt`.
- A **client** connects over TCP and sends **one JSON request** (one line).
- The server sends **one JSON response** (one line), then **closes the connection**.
- The server continues listening so another client can connect next.

This simulates the “template service” portion of a larger app where staff select a template and fill in appointment details before sending a text.

## How it works

### Templates file format

Templates are stored in `templates.txt` separated by `---`.

Each template block uses this format:

- First line: `{Button} = Title` (button label/template name)
- Remaining lines: template message body

### Placeholders

Supported placeholders:

- `{DAY}`
- `{DATE}`
- `{TIME}`

If a field is not provided, it is replaced with an empty string.

## Run the server

From the project folder, run:

    python3 server.py

The server listens on `0.0.0.0:5050` so other devices on the same LAN can connect.

## Run the client (CLI testing)

List available template titles:

    python3 client.py list

Get a template body:

    python3 client.py get "{Button} = Follow-Up Visit"

Render a template with placeholder values:

    python3 client.py render "{Button} = Eval Scheduled" DAY=MON DATE=1/26/26 TIME="4:00 PM"

## Course requirements + stretch challenges

### Model used

Client-Server Model

- `server.py` = server program
- `client.py` = client program

### 5 required networking items

1. Server listens on an IP address and port  
   The server binds to `0.0.0.0:5050` and listens for TCP connections.

2. Client connects to a waiting server  
   The client uses a TCP socket to connect to the server host/port.

3. Client sends at least one request message  
   The client sends a one-line JSON request (LIST_BUTTONS, GET_TEMPLATE, or RENDER_TEMPLATE).

4. Server processes the request and sends a response  
   The server parses the JSON request and returns a one-line JSON response.

5. Server handles client disconnect so another client can connect  
   The server closes each connection after one request and loops back to `accept()` for the next connection.

### Stretch challenges completed

Support for at least three different request types

- LIST_BUTTONS → returns all template titles
- GET_TEMPLATE → returns raw template body for a title
- RENDER_TEMPLATE → fills `{DAY}`, `{DATE}`, `{TIME}` and returns the rendered message

Obtain information from a local file

- The server loads templates from `templates.txt`.


## How this is a foundation for my overall project

This networking project is the foundation for a larger Cancellation Gap Filler Assistant workflow:

- Staff select a message template (future UI buttons use these template titles).
- The app prompts the user for appointment values (date/time/day).
- The filled message is generated and placed in a text box for copying into a texting system (ex: Google Voice).

In later phases, this service can be integrated into a GUI and extended to support scheduling data (like cancellations and openings) while keeping messaging logic reusable and consistent.

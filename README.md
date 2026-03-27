# Mobility PT Cancellation Gap Filler Assistant

A Django + SQLite clinic admin tool for tracking waitlist requests, organizing contact attempts, and generating waitlist-opening messages. The software helps manage patient requests in one place, sort and filter active requests, and quickly generate outreach text for open appointment times.

## Instructions for Build and Use

[Software Demo](https://www.loom.com/share/6cc750bfc23d4e9b817e5b86dc3876a0)

### Steps to build and/or run the software

1. Open a terminal in the project folder.
2. Change into the Django folder:
   ```bash
   cd django
   ```
3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
4. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
5. Open the software in a browser at `http://127.0.0.1:8000/` for the template generator and `http://127.0.0.1:8000/request/` for the request tracker.

### Instructions for using the software

1. Open the **Request Tracker** page to add and manage active requests.
2. Enter the patient name, phone number, calendar event name, visit type, details, preferred day/date, and time preference.
3. Save the request so it is stored in the SQLite database.
4. Use **Sort By**, **Day**, and **Visit Type** filters to narrow the waitlist.
5. Update the **Contact Attempt** field as outreach is made.
6. Click **Generate** to open the waitlist-opening popup, choose a day, date, and time, and generate the message.
7. Copy the generated text into Google Voice or another texting system.
8. Delete requests after they are handled or no longer needed.

## Development Environment

To recreate the development environment, I used the following software and libraries:

- Python 3
- Django 5.2.11
- SQLite 3 (through Python's built-in `sqlite3` library)
- JavaScript for page interactions and modal behavior
- HTML and CSS for the user interface
- VS Code for development
- Git and GitHub for version control

## Useful Websites to Learn More

I found these websites useful while developing this software:

- [Django Databases Documentation](https://docs.djangoproject.com/en/6.0/ref/databases/)
- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite CREATE TABLE Documentation](https://www.sqlite.org/lang_createtable.html)
- [SQLite SQL Language Reference](https://www.sqlite.org/lang.html)
- [SQLite Foreign Key Support](https://www.sqlite.org/foreignkeys.html)
- [Django Tutorial Part 2](https://docs.djangoproject.com/en/6.0/intro/tutorial02/)

## Future Work

The following items I plan to improve in the future:

- [ ] Clean up the quick-generate text templates so the wording reads better for both a specific appointment time and a broader time-of-day option like morning, afternoon, or evening.
- [ ] Add a copy button for the generated message so I can move text into Google Voice faster.
- [ ] Add an edit action for saved requests so I can correct request details without deleting and re-entering the whole record.
- [ ] Continue refining the request form so it stays fast to fill out, searchable, and practical for real clinic use.

---

# Walkthrough Videos — John T.

## Sprint 3 (Java Module: Request Processing)

Loom (Sprint 3): https://www.loom.com/share/76c5f7d052cb4aa4ba6843bf803a4989

### What this does

Sprint 3 introduces a Java module that processes appointment requests saved by the Django web interface.

The system now works as a two-part architecture:

1. **Django Web App**
   - Captures patient request information through `request.html`.
   - Saves request data into a shared file: `requests.txt`.

2. **Java Module**
   - Reads requests from `requests.txt`.
   - Displays saved requests.
   - Generates patient text messages.
   - Allows deletion of outdated requests.

### Java Components

The Java module is located in `java-module/` and contains:

- `Main.java` – command line menu for interacting with saved requests
- `RequestItem.java` – class representing a request record
- `RequestStore.java` – handles reading/writing request data from `requests.txt`
- `Template.java` – represents a text template
- `TemplateLoader.java` – loads templates from `templates.txt`
- `MessageGenerator.java` – builds a patient message from request data

### Features Demonstrated

The Java program demonstrates the required course concepts:

- **Conditionals** – menu selections and input validation
- **Loops** – iterating through request lists and menu interactions
- **Functions / Methods** – modular methods for loading, saving, and generating messages
- **Classes** – structured objects for templates and request items
- **Java Collection Framework** – `ArrayList` used for storing templates and requests

### Stretch Goal Completed

File-based persistence is implemented:

- Django writes requests to `requests.txt`
- Java reads, updates, and deletes requests from the same file

This demonstrates communication between two independent systems using shared file storage.

---

## Sprint 2 (Web App Framework: Django)

Loom (Sprint 2): https://www.loom.com/share/4ed9510a2f1d40bebdf6b0cf720603c9

### What this does

This repo now includes a Django web app that renders an HTML page for selecting a message template, filling in placeholders, and generating a preview message.

- Templates are loaded from `templates.txt`.
- The Home page shows template options.
- Selecting a template + entering values renders a preview message.
- Static CSS and JavaScript are served from the Django app.

### Run Sprint 2 (Django)

From the repo root:

```bash
cd django
source .venv/bin/activate
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

### Sprint 2 requirements checklist (Web Apps module)

1. Generate at least 1 HTML page from the app
   - `home.html` is rendered by Django (`templates_app/views.py`).

2. Include pictures and/or CSS stored with the app code
   - CSS is served from `django/templates_app/static/styles.css`.

3. Accept input from the user
   - The Home page form accepts template selection and placeholder inputs.

4. Perform error checking on user input
   - The Django view validates inputs and displays errors without crashing.

5. Modify HTML generated by the app based on user input
   - The preview message updates based on the submitted form values.

### Stretch goal completed (Library)

- A JavaScript library (Day.js) is used client-side to help build date/time suggestions and auto-fill day-of-week.
- Scripts are organized as:
  - `django/templates_app/static/ux-lib.js` (helpers)
  - `django/templates_app/static/app.js` (DOM wiring)

---

## Sprint 1 (Networking: TCP Client/Server)

Loom (Sprint 1): https://www.loom.com/share/da2ac158f0894ccea4e12c9a8be65256

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

# Spliti

Spliti is a small expense-sharing web app built with Python's standard library, a browser frontend, and a Python WebSocket server.

## What it does

- Add shared expenses from the browser
- Sync changes in real time over WebSocket
- View totals by person
- Calculate who should reimburse whom

## Project structure

- `backend/server.py`: static HTTP server plus Python WebSocket server
- `backend/client.py`: simple Python WebSocket CLI client
- `frontend/`: static web UI

## Run locally

1. Start the server:

```bash
python3 backend/server.py
```

2. Open the web app:

```text
http://127.0.0.1:8000
```

3. Optional: connect with the CLI client:

```bash
python3 backend/client.py
```

## Ports

- `8000`: serves the frontend files
- `8765`: accepts WebSocket connections at `/ws`

## WebSocket messages

Client to server:

- `{"type":"get_state"}`
- `{"type":"add_expense","payer":"Alice","amount":30,"description":"Dinner"}`
- `{"type":"reset"}`

Server to client:

- `{"type":"state","state":...}`
- `{"type":"error","message":"..."}`

## Notes

- Data is stored in memory, so restarting the server clears the expenses.
- No external dependencies are required.

# ✿ TermKaiwa – Terminal Chat Application

## Course Information

Course: CMPT 371 – Data Communications & Networking
Instructor: Mirza Zaeem Baig
Semester: Spring 2026

---

## Overview

TermKaiwa is a terminal-based chat application built using Python’s Socket API (TCP).
It allows multiple users to connect to a server and communicate in real time.

The system follows a client-server architecture and supports:

- Group chat
- Direct messaging
- Secret room with a shared password
- Username change
- Mute specific users locally

---

## Features

- Multiple clients can connect simultaneously
- Real-time group chat
- Private messaging using `/dm`
- Username system (prevents duplicates)
- Username change using `/rename`
- Join/leave notifications
- Online user list (`/users`)
- Secret room with password (`/secret`, `/secret_leave`)
- Client-side mute (`/mute`, `/unmute`)
- Command system (`/help`, `/quit`)
- Colored terminal UI using `rich`

---

## Commands

| Command                    | Description              |
| -------------------------- | ------------------------ |
| `/users`                   | Show all online users    |
| `/rename <username>`       | Change your username     |
| `/dm <username> <message>` | Send a private message   |
| `/secret <password>`       | Enter the secret room    |
| `/secret_leave`            | Leave the secret room    |
| `/mute <username>`         | Mute a user's messages   |
| `/unmute <username>`       | Unmute a user's messages |
| `/help`                    | Show available commands  |
| `/quit`                    | Leave the chat           |

---

## Technologies Used

- Python 3
- Socket API (TCP)
- Threading (for handling multiple clients concurrently)
- rich (for terminal UI design)

---

## Prerequisites

- Python 3.10 or higher
- pip installed

---

## Installation

### Clone the repository

```bash
git clone https://github.com/fleur0121/TermKaiwa.git
cd TermKaiwa
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Step-by-Step Run Guide

### Start the server

```bash
python3 app/server.py
```

You will be prompted to set the secret room password.

### Start a client

Open another terminal and run:

```bash
python3 app/client.py
```

You can open multiple terminals to simulate multiple users.

---

## Example Usage

1. Start the server
2. Connect multiple clients
3. Enter a username
4. Send messages

Example:

```text
hello everyone
/dm Alice hi
/rename Fuka
/secret mypass
/secret_leave
/mute Alice
/users
```

---

## System Limitations & Design Considerations

### Handling Multiple Clients

The server uses Python threading to handle multiple client connections.
Each client runs in a separate thread.

Limitation:
Thread-based design may not scale efficiently for a very large number of users.

---

### Client Disconnections

Disconnected clients are removed from the active list and other users are notified.

Limitation:
There is no automatic reconnection feature.

---

### Message Handling

The system uses TCP to ensure reliable message delivery.

Limitation:
Messages are stored only in memory for the current server session. When the
server restarts, history is lost.

History behavior:

- Public chat: new clients see the last 15 public messages on connect
- Secret room: clients see the last 15 secret messages upon entering
- Direct messages: `/dm <username>` shows the last 15 DMs with that user

---

### Security

Messages are transmitted without encryption.

Limitation:
This application is not secure for sensitive communication.

---

## Video Demo

(Add your video link here)

---

## Repository Structure

```text
TERMKAIWA/
├── app/
│   ├── client.py
│   └── server.py
├── requirements.txt
└── README.md
```

---

## Team Members

- Fuka Nagata (301608021)
- Narihiro Okada (301462533)

---

## Academic Integrity & References

### GenAI Usage

ChatGPT was used to assist with:

- Debugging socket communication issues and understanding error messages

- Assisting with the design and refinement of the terminal UI using the rich library

- Suggesting improvements for code structure and organization

- Assisting in writing and polishing parts of the README for clarity and structure

- Brainstorming feature ideas such as secret rooms, rename, and mute commands

- Reviewing edge cases around username validation and disconnect handling

- Drafting example usage steps and command summaries

### References

- Python Socket Programming Documentation

- Python threading module documentation

- rich library documentation

- Notes from CMPT 371

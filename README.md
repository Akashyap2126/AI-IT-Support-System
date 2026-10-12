# AI IT Support System

An AI-powered IT support ticket management system built with React, Flask, MySQL, and JWT authentication. The application helps users submit IT issues, support agents manage assigned tickets, and administrators oversee ticket workflows.

## Features

- **Authentication and authorization:** JWT-based authentication with user, agent, and admin roles.
- **Ticket management:** Create, view, and track IT support tickets.
- **Status management:** Update ticket status as the issue progresses.
- **Comments:** Add comments to ticket conversations.
- **AI-powered analysis:** Analyze ticket categories and priorities.
- **AI-suggested responses:** Generate suggested responses to assist IT support staff.
- **Ticket assignment:** Assign tickets to support agents with role-based permission checks.
- **Ticket history:** Maintain a record of ticket activity.
- **Security features:** Refresh-token rotation, token revocation, security event logging, API rate limiting, and CORS configuration.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, Flask |
| Database | MySQL |
| Authentication | JWT |
| Database integration | SQLAlchemy |
| API communication | Fetch API |

## Project Structure

```text
AI-IT-Support-System/
├── backend/
│   ├── app.py
│   ├── auth.py
│   ├── ai_service.py
│   ├── decorators.py
│   ├── extensions.py
│   ├── models.py
│   ├── tickets.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Prerequisites

Install the following before running the application:

- Python 3
- Node.js and npm
- MySQL Server
- Git

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/Akashyap2126/AI-IT-Support-System.git
cd AI-IT-Support-System
```

### 2. Configure MySQL

Create a MySQL database for the application. For example:

```sql
CREATE DATABASE ai_support_db;
```

Configure the database connection using the environment variables expected by the backend. Refer to the backend configuration in `app.py` and `extensions.py` to confirm the exact variable names.

### 3. Configure the backend

Open a terminal in the project root and run:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `backend/.env` file with the required database connection settings and a strong, randomly generated JWT secret. Use the exact environment variable names expected by the backend code.

Never commit `.env` or real credentials to GitHub.

Start the Flask server:

```powershell
python app.py
```

The backend normally runs at `http://127.0.0.1:5000`.

### 4. Configure the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically `http://localhost:5173`.

## Application Workflow

1. Sign in using an account with the appropriate role.
2. Create or view IT support tickets.
3. Open a ticket to review its description, status, comments, and AI analysis.
4. Use the suggested response to assist with troubleshooting.
5. Assign tickets and update their status according to the user's permissions.

## Security Notes

- Keep database credentials and JWT secrets in local environment variables.
- Never commit access tokens, refresh tokens, passwords, or `.env` files.
- Use HTTPS, production-grade server configuration, and appropriate secret management when deploying.
- Review CORS and rate-limiting configuration before production use.

## Current Status

The application has been run locally, and the dashboard, ticket details, comments, status information, and AI-suggested response have been verified in the browser.

Further testing and deployment configuration may be required before production use.

## Repository

[View the project on GitHub](https://github.com/Akashyap2126/AI-IT-Support-System)

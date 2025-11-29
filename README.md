# Google Suite Hub (Concept)

This repository outlines a 4-in-1 personal dashboard that brings together Gmail, Google Tasks, Google Calendar, and a simple Habits tracker once authenticated with your Google account.

## What it does
- **Unified sign-in**: Uses Google OAuth to request consent for Gmail, Tasks, and Calendar scopes.
- **Inbox snapshot**: Reads recent messages (Gmail) for quick triage.
- **Tasks board**: Surfaces Google Tasks lists and items for the signed-in user.
- **Calendar glance**: Shows upcoming events across calendars.
- **Habits**: Stores lightweight habit check-ins locally (separate from Google data) so you can see habits next to Google data.

## Architecture sketch
- **Frontend**: Web UI (SPA or server-rendered) that hits a backend API after OAuth completes.
- **Backend**: Handles OAuth code exchange, stores tokens securely, and calls Google APIs.
- **Data storage**: A small database (e.g., SQLite/PostgreSQL) to persist user profiles, refresh tokens, and habit logs.
- **Google APIs**: Gmail API, Google Tasks API, Google Calendar API via REST (e.g., google-api-python-client).

## OAuth setup (required)
1. Create a Google Cloud project.
2. Enable Gmail API, Google Tasks API, and Google Calendar API.
3. Configure OAuth consent screen and authorized redirect URIs.
4. Create OAuth 2.0 Client ID (Web application) and note the **Client ID** and **Client secret**.
5. Set environment variables for local development (example):
   ```bash
   export GOOGLE_CLIENT_ID="your-client-id"
   export GOOGLE_CLIENT_SECRET="your-client-secret"
   export OAUTH_REDIRECT_URI="http://localhost:8000/oauth/callback"
   ```

## Minimal flow (backend)
1. Redirect the user to Google's OAuth URL with scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/tasks.readonly`
   - `https://www.googleapis.com/auth/calendar.readonly`
2. Exchange the authorization code for access + refresh tokens.
3. Persist tokens securely (per user) along with token expiry.
4. Use access tokens to call the respective APIs:
   - Gmail: `users.messages.list` for recent messages.
   - Tasks: `tasks.list` for the default list.
   - Calendar: `events.list` for upcoming events.
5. Render aggregated data to the UI alongside locally stored habits.

## Habits data model (local)
- `habit` table: `id`, `user_id`, `name`, `cadence` (e.g., daily/weekly), `created_at`.
- `habit_checkin` table: `id`, `habit_id`, `date`, `status` (done/skipped/partial).

## Development checklist
- [ ] Choose a framework (e.g., FastAPI, Flask, or Next.js with API routes).
- [ ] Add OAuth endpoints (`/auth/login`, `/oauth/callback`).
- [ ] Implement token storage and refresh handling.
- [ ] Add Google API clients for Gmail, Tasks, Calendar.
- [ ] Create Habit CRUD + check-in endpoints.
- [ ] Build a dashboard UI that combines all data sources.

## Notes and constraints
- This repo currently contains documentation only; the actual implementation requires configuring a Google Cloud project and secrets.
- Keep secrets out of version control; use environment variables or a secrets manager.
- When adding code, avoid try/catch around imports to keep import failures visible.

# Google Suite Hub (demo)

Repo zawiera działającą, lokalną wersję demo 4‑w‑1: Gmail, Google Tasks, Google Calendar oraz Habits. Obecnie dane są przykładowe (mock), ale architektura i UI są gotowe do podpięcia prawdziwych usług Google przez OAuth.

## Co już działa
- **Dashboard webowy** (Flask + Jinja) z kartami: Gmail, Tasks, Calendar, Habits.
- **Przykładowe dane** po stronie backendu, żeby zobaczyć wygląd i układ aplikacji od razu po uruchomieniu.

## Jak uruchomić lokalne demo
1. Upewnij się, że masz Python 3.11+.
2. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```
3. Uruchom serwer developerski:
   ```bash
   flask --app app run
   ```
4. Wejdź w przeglądarce na `http://localhost:5000` – zobaczysz połączony widok Gmail/Tasks/Calendar/Habits z mock danymi.

> **Tip:** Kod szablonu jest w `templates/index.html`, a dane generuje `app.py` w funkcjach `mock_*`.

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
- [x] Wybrać framework (Flask) i zbudować UI demo.
- [ ] Dodać endpointy OAuth (`/auth/login`, `/oauth/callback`).
- [ ] Zaimplementować przechowywanie/odświeżanie tokenów.
- [ ] Podłączyć klientów Google API (Gmail, Tasks, Calendar) zamiast mocków.
- [ ] Dodać CRUD na Habits + check-iny.
- [ ] Zintegrować realne dane z widokiem dashboardu.

## Notes and constraints
- Demo używa danych przykładowych; produkcyjnie trzeba skonfigurować Google Cloud project i sekrety.
- Keep secrets out of version control; use environment variables or a secrets manager.
- When adding code, avoid try/catch around imports to keep import failures visible.

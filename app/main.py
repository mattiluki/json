"""
CLI aggregator for Gmail, Google Tasks, Google Calendar, and a dedicated
"Habits" task list. Uses OAuth2 with Google APIs and stores a local
refreshable token once authenticated.
"""
from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/tasks.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


@dataclass
class GmailMessage:
    sender: str
    subject: str
    date: str


@dataclass
class TaskItem:
    title: str
    status: str
    due: Optional[str]


@dataclass
class CalendarEvent:
    summary: str
    start: str
    end: str


def load_credentials(credentials_path: Path, token_path: Path) -> Credentials:
    creds: Optional[Credentials] = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json())
        return creds

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json())
    return creds


def fetch_gmail_messages(service, max_results: int = 5) -> List[GmailMessage]:
    try:
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=max_results)
            .execute()
        )
    except HttpError as exc:  # pragma: no cover - runtime error path
        raise RuntimeError(f"Gmail API error: {exc}") from exc

    messages = []
    for meta in results.get("messages", []):
        msg = service.users().messages().get(userId="me", id=meta["id"]).execute()
        headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
        messages.append(
            GmailMessage(
                sender=headers.get("from", "(unknown)"),
                subject=headers.get("subject", "(no subject)"),
                date=headers.get("date", ""),
            )
        )
    return messages


def fetch_tasks(service, max_results: int = 10) -> List[TaskItem]:
    try:
        task_lists = service.tasklists().list(maxResults=20).execute().get("items", [])
    except HttpError as exc:  # pragma: no cover - runtime error path
        raise RuntimeError(f"Tasks API error: {exc}") from exc

    items: List[TaskItem] = []
    for task_list in task_lists:
        tasks = (
            service.tasks()
            .list(tasklist=task_list["id"], maxResults=max_results, showCompleted=True)
            .execute()
            .get("items", [])
        )
        for task in tasks:
            due_date = task.get("due")
            items.append(
                TaskItem(
                    title=task.get("title", "(untitled)"),
                    status=task.get("status", "unknown"),
                    due=due_date,
                )
            )
    return items


def fetch_habits(service, list_name: str = "Habits", max_results: int = 20) -> List[TaskItem]:
    try:
        task_lists = service.tasklists().list(maxResults=50).execute().get("items", [])
    except HttpError as exc:  # pragma: no cover - runtime error path
        raise RuntimeError(f"Tasks API error: {exc}") from exc

    habits_list = next((tl for tl in task_lists if tl.get("title") == list_name), None)
    if not habits_list:
        return []

    tasks = (
        service.tasks()
        .list(tasklist=habits_list["id"], maxResults=max_results, showCompleted=True)
        .execute()
        .get("items", [])
    )
    habits: List[TaskItem] = []
    for task in tasks:
        habits.append(
            TaskItem(
                title=task.get("title", "(untitled)"),
                status=task.get("status", "unknown"),
                due=task.get("due"),
            )
        )
    return habits


def fetch_calendar_events(service, days: int = 7, max_results: int = 15) -> List[CalendarEvent]:
    now = dt.datetime.utcnow().isoformat() + "Z"
    end = (dt.datetime.utcnow() + dt.timedelta(days=days)).isoformat() + "Z"
    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                timeMax=end,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except HttpError as exc:  # pragma: no cover - runtime error path
        raise RuntimeError(f"Calendar API error: {exc}") from exc

    events = []
    for event in events_result.get("items", []):
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end_time = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
        events.append(
            CalendarEvent(
                summary=event.get("summary", "(no title)"),
                start=start or "",  # type: ignore[arg-type]
                end=end_time or "",  # type: ignore[arg-type]
            )
        )
    return events


def print_section(title: str):
    print(f"\n{title}\n" + "-" * len(title))


def render_messages(messages: List[GmailMessage]):
    if not messages:
        print("Brak nowych wiadomości.")
        return
    for message in messages:
        print(f"{message.date} | {message.sender} | {message.subject}")


def render_tasks(tasks: List[TaskItem]):
    if not tasks:
        print("Brak zadań.")
        return
    for task in tasks:
        due_text = f" (termin: {task.due})" if task.due else ""
        print(f"[{task.status}] {task.title}{due_text}")


def render_events(events: List[CalendarEvent]):
    if not events:
        print("Brak wydarzeń w najbliższym czasie.")
        return
    for event in events:
        print(f"{event.start} -> {event.end}: {event.summary}")


def main():
    parser = argparse.ArgumentParser(
        description="Pobiera Gmail, Google Tasks, Google Calendar oraz listę nawyków (Habits).",
    )
    parser.add_argument(
        "--credentials",
        type=Path,
        default=Path("credentials.json"),
        help="Ścieżka do pliku credentials.json pobranego z Google Cloud Console.",
    )
    parser.add_argument(
        "--token",
        type=Path,
        default=Path("token.json"),
        help="Ścieżka do lokalnego pliku token.json na potrzeby odświeżania dostępu.",
    )
    args = parser.parse_args()

    if not args.credentials.exists():
        raise SystemExit(
            "Brakuje pliku credentials.json. Pobierz plik OAuth 2.0 Client ID z Google Cloud Console "
            "i wskaż go flagą --credentials."
        )

    creds = load_credentials(args.credentials, args.token)
    gmail_service = build("gmail", "v1", credentials=creds)
    tasks_service = build("tasks", "v1", credentials=creds)
    calendar_service = build("calendar", "v3", credentials=creds)

    print_section("📨 Gmail (ostatnie wiadomości)")
    render_messages(fetch_gmail_messages(gmail_service))

    print_section("✅ Google Tasks")
    render_tasks(fetch_tasks(tasks_service))

    print_section("📅 Google Calendar (7 dni)")
    render_events(fetch_calendar_events(calendar_service))

    print_section("🧠 Nawykowa lista 'Habits'")
    render_tasks(fetch_habits(tasks_service))


if __name__ == "__main__":
    main()

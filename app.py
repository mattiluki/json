from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from flask import Flask, render_template

app = Flask(__name__)


@dataclass
class Email:
    sender: str
    subject: str
    received_at: datetime
    snippet: str


@dataclass
class Task:
    title: str
    due: datetime | None
    status: str


@dataclass
class CalendarEvent:
    title: str
    starts_at: datetime
    ends_at: datetime
    location: str | None = None


@dataclass
class Habit:
    name: str
    streak: int
    note: str | None = None


def mock_emails() -> List[Email]:
    now = datetime.utcnow()
    return [
        Email("team@project.io", "Sprint review notes", now - timedelta(hours=1), "Nagranie i notatki z wczoraj"),
        Email("billing@saas.com", "Faktura czerwiec", now - timedelta(hours=5), "Dziękujemy za płatność"),
        Email("alerts@monitoring.io", "Status page update", now - timedelta(days=1), "Wszystkie systemy operacyjne"),
    ]


def mock_tasks() -> List[Task]:
    tomorrow = datetime.utcnow() + timedelta(days=1)
    return [
        Task("Przygotować dema dla klienta", tomorrow, "in-progress"),
        Task("Zaplanować posty na bloga", None, "todo"),
        Task("Domknąć sprint", tomorrow + timedelta(days=1), "todo"),
    ]


def mock_events() -> List[CalendarEvent]:
    today = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
    return [
        CalendarEvent("Status tygodniowy", today, today + timedelta(hours=1), "Meet"),
        CalendarEvent("Demo klienta", today + timedelta(hours=2), today + timedelta(hours=3), "Zoom"),
        CalendarEvent("1:1", today + timedelta(hours=4), today + timedelta(hours=4, minutes=30)),
    ]


def mock_habits() -> List[Habit]:
    return [
        Habit("Ćwiczenia", 5, "Poranny trening 20 min"),
        Habit("Pisanie dziennika", 12, "3 rzeczy za które jesteś wdzięczny"),
        Habit("Nauka", 7, "30 minut kursu"),
    ]


@app.route("/")
def home():
    return render_template(
        "index.html",
        emails=mock_emails(),
        tasks=mock_tasks(),
        events=mock_events(),
        habits=mock_habits(),
    )


if __name__ == "__main__":
    app.run(debug=True)

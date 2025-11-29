# Google 4-w-1 CLI

Prosta aplikacja CLI, która po autoryzacji OAuth 2.0 pobiera z Twojego konta Google:
- ostatnie wiadomości Gmail,
- zadania z Google Tasks,
- nadchodzące wydarzenia z Google Calendar,
- listę nawyków (zadania) z dedykowanej listy "Habits" w Google Tasks.

## Wymagania
- Python 3.10+
- Konto Google i włączone API: Gmail API, Google Calendar API, Google Tasks API.

## Konfiguracja OAuth
1. Wejdź do [Google Cloud Console](https://console.cloud.google.com/apis/credentials) i utwórz **OAuth 2.0 Client ID** typu "Desktop app".
2. Pobierz plik `credentials.json` i umieść go w katalogu projektu (lub wskaż inną ścieżkę flagą `--credentials`).
3. Upewnij się, że w projekcie włączone są API: Gmail, Tasks i Calendar.

## Instalacja zależności
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uruchomienie
```bash
python app/main.py --credentials credentials.json --token token.json
```
Przy pierwszym uruchomieniu skrypt otworzy przeglądarkę z prośbą o autoryzację. Token odświeżania zostanie zapisany w `token.json`, dzięki czemu kolejne uruchomienia nie wymagają ponownej zgody.

### Oczekiwany output
- Sekcja **📨 Gmail**: 5 ostatnich wiadomości z folderu INBOX (nadawca, temat, data).
- Sekcja **✅ Google Tasks**: do 10 zadań z każdej listy zadań (z terminem, jeśli ustawiony).
- Sekcja **📅 Google Calendar**: wydarzenia z najbliższych 7 dni z kalendarza głównego.
- Sekcja **🧠 Nawykowa lista "Habits"**: zadania z listy o nazwie dokładnie `Habits` (jeśli istnieje).

### Flagi
- `--credentials` – ścieżka do pliku OAuth 2.0 Client ID (`credentials.json`).
- `--token` – ścieżka do pliku z zapisanym tokenem (`token.json`).

## Uwagi dot. prywatności
- Token odświeżania i dostępowego zapisywany jest lokalnie w pliku `token.json`. Nie udostępniaj tego pliku publicznie.
- Skrypt używa wyłącznie trybów odczytu API (readonly scopes).

# MeetSpace Plus - System Rezerwacji Sal Konferencyjnych

MeetSpace Plus to aplikacja webowa do zarządzania rezerwacjami sal konferencyjnych. System umożliwia łatwe przeglądanie dostępnych sal, sprawdzanie ich dostępności w czasie rzeczywistym oraz zarządzanie rezerwacjami.

## Funkcjonalności

### Dla użytkowników
- Przeglądanie listy dostępnych sal konferencyjnych
- Sprawdzanie szczegółów sal (pojemność, wyposażenie)
- Tworzenie i zarządzanie rezerwacjami
- Przeglądanie historii własnych rezerwacji
- Anulowanie oczekujących rezerwacji

### Dla administratorów
- Zarządzanie salami konferencyjnymi (dodawanie, edycja, usuwanie)
- Przeglądanie wszystkich rezerwacji w systemie
- Zatwierdzanie lub odrzucanie rezerwacji
- Zarządzanie statusem sal (aktywna/nieaktywna)

## Wymagania techniczne

- Python 3.12+
- Flask
- Flask-Login
- Flask-WTF
- SQLAlchemy
- PostgreSQL
- Docker

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/xCaban/MeetSpace-Plus.git
cd MeetSpace-Plus
```

### Instalacja z użyciem Dockera

1. Zbuduj i uruchom kontenery:
```bash
docker-compose up -d
```

2. W folderze config, w pliku database.example.php znajduje się login i hasło do bazy. Zmień je na bezpieczne i zmień nazwe pliku na database.php

3. Aplikacja będzie dostępna pod adresem `http://localhost:8081`

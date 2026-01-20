# ERD – MeetSpace Plus

Diagram encji i relacji (3NF). Brak nakładania się rezerwacji w tym samym pokoju jest egzekwowany w warstwie serwisowej (409 przy kolizji).

```mermaid
erDiagram
    users ||--o{ user_roles : "ma"
    roles ||--o{ user_roles : "przypisana w"
    users ||--o{ reservations : "składa"
    rooms ||--o{ reservations : "dotyczy"
    rooms ||--o{ room_equipment : "ma"
    equipment ||--o{ room_equipment : "w"

    users {
        bigint id PK
        varchar username
        varchar email
        varchar first_name
        varchar last_name
        bool is_staff
        bool is_active
        datetime date_joined
        datetime created_at
        datetime updated_at
    }

    roles {
        bigint id PK
        varchar name UK
        datetime created_at
        datetime updated_at
    }

    user_roles {
        bigint id PK
        bigint user_id FK
        bigint role_id FK
        datetime created_at
        datetime updated_at
    }

    rooms {
        bigint id PK
        varchar name
        int capacity
        varchar location
        datetime created_at
        datetime updated_at
    }

    equipment {
        bigint id PK
        varchar name
        datetime created_at
        datetime updated_at
    }

    room_equipment {
        bigint id PK
        bigint room_id FK
        bigint equipment_id FK
        int qty
        datetime created_at
        datetime updated_at
    }

    reservations {
        bigint id PK
        bigint user_id FK
        bigint room_id FK
        varchar status "pending|confirmed|canceled"
        datetime start_at
        datetime end_at
        datetime hold_expires_at
        datetime created_at
        datetime updated_at
    }
```

## Indeksy

| Tabela       | Indeks                       | Cel                          |
|-------------|------------------------------|------------------------------|
| reservations | `(room_id, start_at)`       | wyszukiwanie kolizji, listy   |
| reservations | `(user_id, start_at)`       | rezerwacje użytkownika       |

## Ograniczenia unikalności

| Tabela       | Constraint                      |
|-------------|----------------------------------|
| user_roles  | `(user_id, role_id)` – para 1:1 |
| room_equipment | `(room_id, equipment_id)` – para 1:1 z `qty` |

## Zależności (3NF)

- **users, roles**: atrybuty zależne tylko od klucza głównego.
- **user_roles**: tabela łącząca M:N User–Role; atrybuty zależne od `(user_id, role_id)`.
- **rooms, equipment**: atrybuty zależne tylko od klucza głównego.
- **room_equipment**: M:N Room–Equipment z atrybutem `qty` zależnym od pary `(room_id, equipment_id)`.
- **reservations**: atrybuty zależne od `id`; `user_id`, `room_id` – klucze obce.

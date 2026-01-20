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
        int id
        string username
        string email
        string first_name
        string last_name
        int is_staff
        int is_active
        string date_joined
        string created_at
        string updated_at
    }

    roles {
        int id
        string name
        string created_at
        string updated_at
    }

    user_roles {
        int id
        int user_id
        int role_id
        string created_at
        string updated_at
    }

    rooms {
        int id
        string name
        int capacity
        string location
        string created_at
        string updated_at
    }

    equipment {
        int id
        string name
        string created_at
        string updated_at
    }

    room_equipment {
        int id
        int room_id
        int equipment_id
        int qty
        string created_at
        string updated_at
    }

    reservations {
        int id
        int user_id
        int room_id
        string status
        string start_at
        string end_at
        string hold_expires_at
        string created_at
        string updated_at
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

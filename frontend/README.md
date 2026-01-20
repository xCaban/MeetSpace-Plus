# MeetSpace Plus – frontend

Vue 3 + Vite + TypeScript, Pinia, Vue Router, axios. Proxy do API w dev: `/api` → `http://localhost:8000`.

## Wymagania

- Node 20+
- npm

## Uruchomienie

```bash
npm install
npm run dev
```

Aplikacja: http://localhost:5173. Backend: http://localhost:8000 (proxy `/api`).

## Skrypty

- `npm run dev` – dev server
- `npm run build` – build produkcyjny
- `npm run preview` – podgląd buildu
- `npm run lint` – ESLint
- `npm run format` – Prettier
- `npm run lint:style` – Stylelint
- `npm run test` / `npm run test:run` – Vitest

## Konfiguracja

Skopiuj `env.example` do `.env` i ustaw np.:

- `VITE_API_BASE` – pełny URL API (np. `http://localhost:8000/api`). Dla proxy Vite zostaw puste.

## Struktura

- `src/api/` – axios client, interceptory, typy DTO
- `src/stores/` – Pinia: auth, rooms, reservations, ui
- `src/views/` – Login, RoomList, Calendar, MyReservations, AdminRooms
- `src/components/base/` – BaseButton, BaseInput, BaseSelect, Badge, DataTable
- `src/router/` – Vue Router z guardami (auth, admin)
- `src/styles/` – tokens.css (design tokens), base.css
- `src/layouts/MainLayout.vue` – layout z nawigacją

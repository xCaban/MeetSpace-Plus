<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useRoomsStore } from "@/stores/rooms"
import { useReservationsStore } from "@/stores/reservations"
import BaseSelect from "@/components/base/BaseSelect.vue"

const rooms = useRoomsStore()
const reservations = useReservationsStore()

const selectedRoomId = ref<number | "">("")
const from = ref("")
const to = ref("")

const roomOptions = computed(() => [
  { value: "" as const, label: "— Wszystkie sale —" },
  ...rooms.list.map((r) => ({ value: r.id, label: r.name })),
])

onMounted(async () => {
  await rooms.fetchList()
  const today = new Date().toISOString().slice(0, 10)
  from.value = `${today}T00:00:00`
  to.value = `${today}T23:59:59`
  await load()
})

async function load() {
  await reservations.fetchList({
    room_id: selectedRoomId.value === "" ? undefined : (selectedRoomId.value as number),
    from: from.value || undefined,
    to: to.value || undefined,
  })
}
</script>

<template>
  <div class="page">
    <h1 class="page-title">Kalendarz rezerwacji</h1>

    <div class="filters">
      <BaseSelect
        v-model="selectedRoomId"
        :options="roomOptions"
        label="Sala"
        @update:model-value="load"
      />
      <div class="filter-row">
        <label class="filter-label">Od</label>
        <input v-model="from" type="datetime-local" class="filter-input" @change="load" />
      </div>
      <div class="filter-row">
        <label class="filter-label">Do</label>
        <input v-model="to" type="datetime-local" class="filter-input" @change="load" />
      </div>
    </div>

    <div v-if="reservations.error" class="page-error">{{ reservations.error }}</div>

    <ul v-if="!reservations.loading && reservations.list.length" class="res-list">
      <li v-for="r in reservations.list" :key="r.id" class="res-item">
        <span class="res-room">{{ r.room_name }}</span>
        <span class="res-time">{{ r.start_at }} – {{ r.end_at }}</span>
        <span class="res-user">{{ r.user_email }}</span>
      </li>
    </ul>
    <p v-else-if="!reservations.loading" class="empty">Brak rezerwacji w wybranym okresie.</p>
    <p v-else class="empty">Ładowanie…</p>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
}

.page-error {
  color: var(--color-danger);
  font-size: var(--text-sm);
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  align-items: flex-end;
}

.filter-row {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.filter-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.filter-input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.res-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.res-item {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: var(--space-4);
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

@media (max-width: 640px) {
  .res-item {
    grid-template-columns: 1fr;
  }
}

.res-room {
  font-weight: var(--font-medium);
}

.res-time {
  color: var(--color-text-muted);
}

.empty {
  color: var(--color-text-muted);
  padding: var(--space-6);
}
</style>

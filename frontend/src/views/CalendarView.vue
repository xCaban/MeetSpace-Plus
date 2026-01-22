<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue"
import { useRoomsStore } from "@/stores/rooms"
import { useReservationsStore } from "@/stores/reservations"
import BaseSelect from "@/components/base/BaseSelect.vue"
import { formatDateShort } from "@/utils/date"
import type { Reservation } from "@/api/types"
import type { SelectOption } from "@/components/base/BaseSelect.vue"

const rooms = useRoomsStore()
const reservations = useReservationsStore()

const viewMode = ref<"week" | "day">("week")
const selectedDate = ref(new Date())
const selectedRoomId = ref<number | "">("")

const HOUR_START = 8
const HOUR_END = 21

const roomOptions = computed<SelectOption[]>(() =>
  rooms.list.map((r) => ({ value: r.id, label: r.name }))
)

function toISOStart(d: Date): string {
  const x = new Date(d)
  x.setHours(0, 0, 0, 0)
  return x.toISOString()
}

function toISOEnd(d: Date): string {
  const x = new Date(d)
  x.setHours(23, 59, 59, 999)
  return x.toISOString()
}

const range = computed(() => {
  const d = new Date(selectedDate.value)
  if (viewMode.value === "day") {
    return { from: toISOStart(d), to: toISOEnd(d) }
  }
  const day = d.getDay()
  const diff = day === 0 ? -6 : 1 - day
  const mon = new Date(d)
  mon.setDate(mon.getDate() + diff)
  mon.setHours(0, 0, 0, 0)
  const sun = new Date(mon)
  sun.setDate(sun.getDate() + 6)
  sun.setHours(23, 59, 59, 999)
  return { from: mon.toISOString(), to: sun.toISOString() }
})

const columns = computed(() => {
  if (viewMode.value === "day") {
    const d = selectedDate.value
    return [{ key: "hour", label: formatDateShort(d) }]
  }
  const mon = new Date(selectedDate.value)
  const day = mon.getDay()
  const diff = day === 0 ? -6 : 1 - day
  mon.setDate(mon.getDate() + diff)
  const out: { key: string; label: string }[] = [{ key: "hour", label: "Godz." }]
  const days = ["Nd", "Pn", "Wt", "Śr", "Cz", "Pt", "So"]
  for (let i = 0; i < 7; i++) {
    const x = new Date(mon)
    x.setDate(x.getDate() + i)
    out.push({ key: `d${i}`, label: `${days[x.getDay()]} ${x.getDate()}` })
  }
  return out
})

const hours = computed(() => {
  const h: number[] = []
  for (let i = HOUR_START; i <= HOUR_END; i++) h.push(i)
  return h
})

function formatHour(h: number): string {
  return `${String(h).padStart(2, "0")}:00`
}

function getSlotStart(dayOffset: number, hour: number): Date {
  const d = new Date(selectedDate.value)
  if (viewMode.value === "day") {
    d.setHours(hour, 0, 0, 0)
    return d
  }
  const day = d.getDay()
  const diff = day === 0 ? -6 : 1 - day
  d.setDate(d.getDate() + diff + dayOffset)
  d.setHours(hour, 0, 0, 0)
  return d
}

function getSlotEnd(dayOffset: number, hour: number): Date {
  const s = getSlotStart(dayOffset, hour)
  const e = new Date(s)
  e.setHours(e.getHours() + 1, 0, 0, 0)
  return e
}

function isSlotOccupied(dayOffset: number, hour: number): boolean {
  const list = reservations.list as Reservation[]
  const slotStart = getSlotStart(dayOffset, hour).getTime()
  const slotEnd = getSlotEnd(dayOffset, hour).getTime()
  return list.some((r) => {
    if (r.status === "canceled") return false
    const rs = new Date(r.start_at).getTime()
    const re = new Date(r.end_at).getTime()
    return rs < slotEnd && re > slotStart
  })
}

const dayCount = computed(() => (viewMode.value === "day" ? 1 : 7))

function prev() {
  const d = new Date(selectedDate.value)
  d.setDate(d.getDate() - (viewMode.value === "day" ? 1 : 7))
  selectedDate.value = d
}

function next() {
  const d = new Date(selectedDate.value)
  d.setDate(d.getDate() + (viewMode.value === "day" ? 1 : 7))
  selectedDate.value = d
}

function today() {
  selectedDate.value = new Date()
}

async function load() {
  const rid = selectedRoomId.value
  if (rid === "") return
  await reservations.fetchList({
    room_id: rid as number,
    from: range.value.from,
    to: range.value.to,
  })
}

watch([selectedRoomId, range, viewMode], () => {
  load()
})

onMounted(async () => {
  await rooms.fetchList()
  if (rooms.list.length > 0 && selectedRoomId.value === "") {
    selectedRoomId.value = rooms.list[0].id
  }
})
</script>

<template>
  <div class="page">
    <h1 class="page-title">Kalendarz – dostępność sali</h1>

    <div class="toolbar">
      <div class="toolbar-group">
        <BaseSelect
          v-model="selectedRoomId"
          :options="roomOptions"
          label="Sala"
          name="cal_room"
          placeholder="— Wybierz salę —"
        />
      </div>
      <div class="toolbar-group view-toggle">
        <button
          type="button"
          class="toggle-btn"
          :class="{ 'toggle-btn--active': viewMode === 'day' }"
          :aria-pressed="viewMode === 'day'"
          aria-label="Widok dzień"
          @click="viewMode = 'day'"
        >
          Dzień
        </button>
        <button
          type="button"
          class="toggle-btn"
          :class="{ 'toggle-btn--active': viewMode === 'week' }"
          :aria-pressed="viewMode === 'week'"
          aria-label="Widok tydzień"
          @click="viewMode = 'week'"
        >
          Tydzień
        </button>
      </div>
      <div class="toolbar-group nav">
        <button type="button" class="nav-btn" aria-label="Poprzedni" @click="prev">‹</button>
        <button type="button" class="nav-btn today" @click="today">Today</button>
        <button type="button" class="nav-btn" aria-label="Następny" @click="next">›</button>
      </div>
    </div>

    <p v-if="reservations.error" class="page-error" role="alert">
      {{ reservations.error }}
    </p>

    <div v-if="selectedRoomId === ''" class="empty-hint" role="status">
      Wybierz salę, aby zobaczyć dostępność.
    </div>

    <div v-else class="calendar-wrap" role="region" aria-label="Siatka dostępności">
      <table class="cal-table" role="table" aria-label="Dostępność sali wg godziny i dnia">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key" scope="col" class="cal-th">
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="reservations.loading">
            <td :colspan="columns.length" class="cal-loading">Ładowanie…</td>
          </tr>
          <template v-else>
            <tr v-for="h in hours" :key="h">
              <th scope="row" class="cal-hour">{{ formatHour(h) }}</th>
              <td
                v-for="d in dayCount"
                :key="d - 1"
                class="cal-cell"
                :class="{ 'cal-cell--busy': isSlotOccupied(d - 1, h) }"
              >
                {{ isSlotOccupied(d - 1, h) ? "zajęte" : "wolne" }}
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
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

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  align-items: flex-end;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.view-toggle {
  display: flex;
}

.toggle-btn {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  cursor: pointer;
}

.toggle-btn--active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.nav-btn {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  cursor: pointer;
}

.nav-btn.today {
  min-width: 4rem;
}

.empty-hint {
  color: var(--color-text-muted);
  padding: var(--space-6);
}

.calendar-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.cal-table {
  width: 100%;
  min-width: 320px;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.cal-th,
.cal-hour,
.cal-cell {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  text-align: center;
}

.cal-th {
  font-weight: var(--font-semibold);
  background: var(--color-bg-alt);
}

.cal-hour {
  font-weight: var(--font-medium);
  text-align: right;
  white-space: nowrap;
}

.cal-cell--busy {
  background: var(--color-danger-muted);
  color: var(--color-danger);
}

.cal-loading {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-6);
}
</style>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useRoomsStore } from "@/stores/rooms"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseInput from "@/components/base/BaseInput.vue"
import BaseMultiSelect from "@/components/base/BaseMultiSelect.vue"
import CreateReservationForm from "@/components/CreateReservationForm.vue"
import DataTable from "@/components/base/DataTable.vue"

const rooms = useRoomsStore()
const showReservationForm = ref(false)

const filterCap = ref<string | number>("")
const filterLoc = ref("")
const filterEquipment = ref<number[]>([])

const columns = [
  { key: "name", label: "Nazwa" },
  { key: "capacity", label: "Pojemność" },
  { key: "location", label: "Lokalizacja" },
  { key: "equipment", label: "Wyposażenie" },
]

function formatEquipment(eq?: { name: string; qty: number }[]) {
  if (!eq || eq.length === 0) return "—"
  return eq.map((e) => `${e.name}${e.qty > 1 ? ` (${e.qty})` : ""}`).join(", ")
}

const hasFilters = computed(() => {
  return (
    (rooms.filters.capacity_min != null && rooms.filters.capacity_min > 0) ||
    (rooms.filters.location != null && String(rooms.filters.location).trim() !== "") ||
    (rooms.filters.equipment_ids != null && rooms.filters.equipment_ids.length > 0)
  )
})

const emptyText = computed(() => {
  return hasFilters.value ? "Brak sal spełniających kryteria" : "Brak sal"
})

onMounted(async () => {
  await Promise.all([rooms.fetchList(), rooms.fetchEquipment()])
})

function applyFilters() {
  const cap = filterCap.value
  const loc = filterLoc.value
  const n = Number(cap)
  rooms.setFilters({
    capacity_min: cap === "" || cap === undefined || Number.isNaN(n) || n <= 0 ? undefined : n,
    location: typeof loc === "string" && loc.trim() !== "" ? loc.trim() : undefined,
    equipment_ids: filterEquipment.value.length > 0 ? filterEquipment.value : undefined,
  })
}

function resetFilters() {
  filterCap.value = ""
  filterLoc.value = ""
  filterEquipment.value = []
  rooms.clearFilters()
}

function rowFor(r: {
  id: number
  name: string
  capacity: number
  location: string
  equipment?: { name: string; qty: number }[]
}) {
  return {
    name: r.name,
    capacity: r.capacity,
    location: r.location || "—",
    equipment: formatEquipment(r.equipment),
  }
}

function onReservationCreated() {
  showReservationForm.value = false
}

function onReservationCancel() {
  showReservationForm.value = false
}
</script>

<template>
  <div class="page">
    <h1 class="page-title">Sale konferencyjne</h1>

    <section class="filters" aria-label="Filtry listy sal">
      <BaseInput
        v-model="filterCap"
        type="number"
        label="Pojemność min."
        name="filter_cap"
        placeholder="np. 4"
      />
      <BaseInput
        v-model="filterLoc"
        type="text"
        label="Lokalizacja"
        name="filter_loc"
        placeholder="np. parter"
      />
      <BaseMultiSelect
        v-model="filterEquipment"
        :options="rooms.equipmentList.map((e) => ({ id: e.id, name: e.name }))"
        label="Wyposażenie"
        name="filter_equipment"
        placeholder="Wybierz sprzęt"
      />
      <div class="filter-actions">
        <BaseButton @click="applyFilters">Filtruj</BaseButton>
        <BaseButton v-if="hasFilters" variant="secondary" @click="resetFilters">Resetuj</BaseButton>
      </div>
    </section>

    <p v-if="rooms.error" class="page-error" role="alert">{{ rooms.error }}</p>

    <DataTable
      :columns="columns"
      :data="rooms.filteredList.map(rowFor)"
      :loading="rooms.loading"
      :empty-text="emptyText"
      aria-label="Lista sal konferencyjnych"
    />

    <section class="reservation-section">
      <BaseButton v-if="!showReservationForm" @click="showReservationForm = true">
        Dodaj rezerwację
      </BaseButton>
      <CreateReservationForm v-else @created="onReservationCreated" @cancel="onReservationCancel" />
    </section>
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

.filter-actions {
  display: flex;
  align-items: flex-end;
}

.reservation-section {
  margin-top: var(--space-2);
}
</style>

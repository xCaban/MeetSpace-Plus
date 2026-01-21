<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { useRoomsStore } from "@/stores/rooms"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseInput from "@/components/base/BaseInput.vue"
import DataTable from "@/components/base/DataTable.vue"
import type { Room } from "@/api/types"

const rooms = useRoomsStore()
const showForm = ref(false)
const form = reactive({ name: "", capacity: 10, location: "" })

const editingId = ref<number | null>(null)
const editForm = reactive({ name: "", capacity: 10, location: "" })

const columns = [
  { key: "name", label: "Nazwa" },
  { key: "capacity", label: "Pojemność" },
  { key: "location", label: "Lokalizacja" },
  { key: "equipment", label: "Wyposażenie" },
  { key: "actions", label: "" },
]

function formatEquipment(eq?: { name: string; qty: number }[]) {
  if (!eq || eq.length === 0) return "—"
  return eq.map((e) => `${e.name}${e.qty > 1 ? ` (${e.qty})` : ""}`).join(", ")
}

onMounted(() => {
  rooms.fetchList()
})

function rowFor(r: {
  id: number
  name: string
  capacity: number
  location: string
  equipment?: { name: string; qty: number }[]
}) {
  return {
    id: r.id,
    name: r.name,
    capacity: r.capacity,
    location: r.location || "—",
    equipment: formatEquipment(r.equipment),
    actions: "x",
  }
}

function openEdit(r: Room) {
  editingId.value = r.id
  editForm.name = r.name
  editForm.capacity = r.capacity
  editForm.location = r.location || ""
}

function openEditById(id: number) {
  const r = rooms.list.find((x) => x.id === id)
  if (r) openEdit(r)
}

function closeEdit() {
  editingId.value = null
}

async function onSubmit() {
  try {
    await rooms.create({
      name: form.name,
      capacity: form.capacity,
      location: form.location,
    })
    form.name = ""
    form.capacity = 10
    form.location = ""
    showForm.value = false
  } catch {
    /* error in store */
  }
}

async function onEditSubmit() {
  if (editingId.value == null) return
  try {
    await rooms.update(editingId.value, {
      name: editForm.name,
      capacity: editForm.capacity,
      location: editForm.location,
    })
    closeEdit()
  } catch {
    /* error in store */
  }
}

async function onDelete(id: number) {
  if (!confirm("Usunąć salę?")) return
  try {
    await rooms.remove(id)
  } catch {
    /* error in store */
  }
}
</script>

<template>
  <div class="page">
    <div class="page-head">
      <h1 class="page-title">Panel admina – sale</h1>
      <BaseButton v-if="!showForm" @click="showForm = true">Dodaj salę</BaseButton>
    </div>

    <form v-if="showForm" class="form-inline" @submit.prevent="onSubmit">
      <BaseInput v-model="form.name" label="Nazwa" name="name" />
      <BaseInput v-model="form.capacity" type="number" label="Pojemność" name="capacity" />
      <BaseInput v-model="form.location" label="Lokalizacja" name="location" />
      <div class="form-actions">
        <BaseButton type="submit" :disabled="rooms.loading || !form.name">Zapisz</BaseButton>
        <BaseButton type="button" variant="outline" @click="showForm = false">Anuluj</BaseButton>
      </div>
    </form>

    <p v-if="rooms.error" class="page-error" role="alert">{{ rooms.error }}</p>

    <DataTable
      :columns="columns"
      :data="rooms.list.map(rowFor)"
      :loading="rooms.loading"
      empty-text="Brak sal"
      aria-label="Lista sal (CRUD)"
    >
      <template #cell-actions="{ row }">
        <div class="cell-actions">
          <BaseButton variant="outline" size="sm" @click="openEditById(row.id)">
            Edytuj
          </BaseButton>
          <BaseButton variant="danger" size="sm" @click="onDelete(row.id)">Usuń</BaseButton>
        </div>
      </template>
    </DataTable>

    <div
      v-if="editingId != null"
      class="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="edit-dialog-title"
      @click.self="closeEdit"
    >
      <div class="modal-card">
        <h2 id="edit-dialog-title" class="modal-title">Edycja sali</h2>
        <form @submit.prevent="onEditSubmit">
          <BaseInput v-model="editForm.name" label="Nazwa" name="edit_name" />
          <BaseInput
            v-model="editForm.capacity"
            type="number"
            label="Pojemność"
            name="edit_capacity"
          />
          <BaseInput v-model="editForm.location" label="Lokalizacja" name="edit_location" />
          <div class="form-actions">
            <BaseButton type="submit" :disabled="rooms.loading || !editForm.name"
              >Zapisz</BaseButton
            >
            <BaseButton type="button" variant="outline" @click="closeEdit">Anuluj</BaseButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.page-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
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

.form-inline {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  align-items: flex-end;
  padding: var(--space-4);
  background: var(--color-bg-alt);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.form-actions {
  display: flex;
  gap: var(--space-2);
}

.cell-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  padding: var(--space-4);
}

.modal-card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  max-width: 24rem;
  width: 100%;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.modal-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
}
</style>

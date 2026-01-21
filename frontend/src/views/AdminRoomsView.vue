<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { useRoomsStore } from "@/stores/rooms"
import { useEquipmentStore } from "@/stores/equipment"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseInput from "@/components/base/BaseInput.vue"
import DataTable from "@/components/base/DataTable.vue"
import EquipmentSelector from "@/components/EquipmentSelector.vue"
import type { Room, RoomEquipmentInput } from "@/api/types"

const rooms = useRoomsStore()
const equipment = useEquipmentStore()

const activeTab = ref<"rooms" | "equipment">("rooms")

// Room form state
const showRoomForm = ref(false)
const roomForm = reactive({ name: "", capacity: 10, location: "" })
const roomFormEquipment = ref<RoomEquipmentInput[]>([])

const editingRoomId = ref<number | null>(null)
const editRoomForm = reactive({ name: "", capacity: 10, location: "" })
const editRoomEquipment = ref<RoomEquipmentInput[]>([])

// Equipment form state
const showEquipmentForm = ref(false)
const equipmentForm = reactive({ name: "" })

const editingEquipmentId = ref<number | null>(null)
const editEquipmentForm = reactive({ name: "" })

const roomColumns = [
  { key: "name", label: "Nazwa" },
  { key: "capacity", label: "Pojemność" },
  { key: "location", label: "Lokalizacja" },
  { key: "equipment", label: "Wyposażenie" },
  { key: "actions", label: "" },
]

const equipmentColumns = [
  { key: "name", label: "Nazwa" },
  { key: "actions", label: "" },
]

function formatEquipment(eq?: { name: string; qty: number }[]) {
  if (!eq || eq.length === 0) return "—"
  return eq.map((e) => `${e.name}${e.qty > 1 ? ` (${e.qty})` : ""}`).join(", ")
}

onMounted(() => {
  rooms.fetchList()
  equipment.fetchList()
})

function roomRowFor(r: Room) {
  return {
    id: r.id,
    name: r.name,
    capacity: r.capacity,
    location: r.location || "—",
    equipment: formatEquipment(r.equipment),
    actions: "x",
  }
}

function equipmentRowFor(e: { id: number; name: string }) {
  return {
    id: e.id,
    name: e.name,
    actions: "x",
  }
}

// Room actions
function openRoomEdit(r: Room) {
  editingRoomId.value = r.id
  editRoomForm.name = r.name
  editRoomForm.capacity = r.capacity
  editRoomForm.location = r.location || ""
  editRoomEquipment.value = (r.equipment || []).map((e) => ({
    equipment_id: e.id,
    qty: e.qty,
  }))
}

function openRoomEditById(id: number) {
  const r = rooms.list.find((x) => x.id === id)
  if (r) openRoomEdit(r)
}

function closeRoomEdit() {
  editingRoomId.value = null
}

async function onRoomSubmit() {
  try {
    await rooms.create({
      name: roomForm.name,
      capacity: roomForm.capacity,
      location: roomForm.location,
      equipment: roomFormEquipment.value,
    })
    roomForm.name = ""
    roomForm.capacity = 10
    roomForm.location = ""
    roomFormEquipment.value = []
    showRoomForm.value = false
  } catch {
    /* error in store */
  }
}

async function onRoomEditSubmit() {
  if (editingRoomId.value == null) return
  try {
    await rooms.update(editingRoomId.value, {
      name: editRoomForm.name,
      capacity: editRoomForm.capacity,
      location: editRoomForm.location,
      equipment: editRoomEquipment.value,
    })
    closeRoomEdit()
  } catch {
    /* error in store */
  }
}

async function onRoomDelete(id: number) {
  if (!confirm("Usunąć salę?")) return
  try {
    await rooms.remove(id)
  } catch {
    /* error in store */
  }
}

// Equipment actions
function openEquipmentEdit(e: { id: number; name: string }) {
  editingEquipmentId.value = e.id
  editEquipmentForm.name = e.name
}

function openEquipmentEditById(id: number) {
  const e = equipment.list.find((x) => x.id === id)
  if (e) openEquipmentEdit(e)
}

function closeEquipmentEdit() {
  editingEquipmentId.value = null
}

async function onEquipmentSubmit() {
  try {
    await equipment.create({ name: equipmentForm.name })
    equipmentForm.name = ""
    showEquipmentForm.value = false
  } catch {
    /* error in store */
  }
}

async function onEquipmentEditSubmit() {
  if (editingEquipmentId.value == null) return
  try {
    await equipment.update(editingEquipmentId.value, { name: editEquipmentForm.name })
    closeEquipmentEdit()
  } catch {
    /* error in store */
  }
}

async function onEquipmentDelete(id: number) {
  if (!confirm("Usunąć sprzęt?")) return
  try {
    await equipment.remove(id)
  } catch {
    alert(equipment.error || "Nie można usunąć sprzętu")
  }
}
</script>

<template>
  <div class="page">
    <div class="page-head">
      <h1 class="page-title">Panel admina</h1>
    </div>

    <div class="tabs">
      <button :class="['tab', { active: activeTab === 'rooms' }]" @click="activeTab = 'rooms'">
        Sale
      </button>
      <button
        :class="['tab', { active: activeTab === 'equipment' }]"
        @click="activeTab = 'equipment'"
      >
        Sprzęt
      </button>
    </div>

    <!-- Tab: Sale -->
    <div v-if="activeTab === 'rooms'" class="tab-content">
      <div class="section-head">
        <BaseButton v-if="!showRoomForm" @click="showRoomForm = true">Dodaj salę</BaseButton>
      </div>

      <form v-if="showRoomForm" class="form-card" @submit.prevent="onRoomSubmit">
        <BaseInput v-model="roomForm.name" label="Nazwa" name="name" />
        <BaseInput v-model="roomForm.capacity" type="number" label="Pojemność" name="capacity" />
        <BaseInput v-model="roomForm.location" label="Lokalizacja" name="location" />
        <div class="form-section">
          <label class="form-label">Sprzęt</label>
          <EquipmentSelector v-model="roomFormEquipment" :equipment="equipment.list" />
        </div>
        <div class="form-actions">
          <BaseButton type="submit" :disabled="rooms.loading || !roomForm.name">Zapisz</BaseButton>
          <BaseButton type="button" variant="outline" @click="showRoomForm = false"
            >Anuluj</BaseButton
          >
        </div>
      </form>

      <p v-if="rooms.error" class="page-error" role="alert">{{ rooms.error }}</p>

      <DataTable
        :columns="roomColumns"
        :data="rooms.list.map(roomRowFor)"
        :loading="rooms.loading"
        empty-text="Brak sal"
        aria-label="Lista sal (CRUD)"
      >
        <template #cell-actions="{ row }">
          <div class="cell-actions">
            <BaseButton variant="outline" size="sm" @click="openRoomEditById(row.id)">
              Edytuj
            </BaseButton>
            <BaseButton variant="danger" size="sm" @click="onRoomDelete(row.id)">Usuń</BaseButton>
          </div>
        </template>
      </DataTable>

      <!-- Room edit modal -->
      <div
        v-if="editingRoomId != null"
        class="modal-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-room-dialog-title"
        @click.self="closeRoomEdit"
      >
        <div class="modal-card">
          <h2 id="edit-room-dialog-title" class="modal-title">Edycja sali</h2>
          <form @submit.prevent="onRoomEditSubmit">
            <BaseInput v-model="editRoomForm.name" label="Nazwa" name="edit_name" />
            <BaseInput
              v-model="editRoomForm.capacity"
              type="number"
              label="Pojemność"
              name="edit_capacity"
            />
            <BaseInput v-model="editRoomForm.location" label="Lokalizacja" name="edit_location" />
            <div class="form-section">
              <label class="form-label">Sprzęt</label>
              <EquipmentSelector v-model="editRoomEquipment" :equipment="equipment.list" />
            </div>
            <div class="form-actions">
              <BaseButton type="submit" :disabled="rooms.loading || !editRoomForm.name"
                >Zapisz</BaseButton
              >
              <BaseButton type="button" variant="outline" @click="closeRoomEdit">Anuluj</BaseButton>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Tab: Sprzęt -->
    <div v-if="activeTab === 'equipment'" class="tab-content">
      <div class="section-head">
        <BaseButton v-if="!showEquipmentForm" @click="showEquipmentForm = true"
          >Dodaj sprzęt</BaseButton
        >
      </div>

      <form v-if="showEquipmentForm" class="form-card" @submit.prevent="onEquipmentSubmit">
        <BaseInput v-model="equipmentForm.name" label="Nazwa" name="eq_name" />
        <div class="form-actions">
          <BaseButton type="submit" :disabled="equipment.loading || !equipmentForm.name"
            >Zapisz</BaseButton
          >
          <BaseButton type="button" variant="outline" @click="showEquipmentForm = false"
            >Anuluj</BaseButton
          >
        </div>
      </form>

      <p v-if="equipment.error" class="page-error" role="alert">{{ equipment.error }}</p>

      <DataTable
        :columns="equipmentColumns"
        :data="equipment.list.map(equipmentRowFor)"
        :loading="equipment.loading"
        empty-text="Brak sprzętu"
        aria-label="Lista sprzętu (CRUD)"
      >
        <template #cell-actions="{ row }">
          <div class="cell-actions">
            <BaseButton variant="outline" size="sm" @click="openEquipmentEditById(row.id)">
              Edytuj
            </BaseButton>
            <BaseButton variant="danger" size="sm" @click="onEquipmentDelete(row.id)"
              >Usuń</BaseButton
            >
          </div>
        </template>
      </DataTable>

      <!-- Equipment edit modal -->
      <div
        v-if="editingEquipmentId != null"
        class="modal-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-equipment-dialog-title"
        @click.self="closeEquipmentEdit"
      >
        <div class="modal-card">
          <h2 id="edit-equipment-dialog-title" class="modal-title">Edycja sprzętu</h2>
          <form @submit.prevent="onEquipmentEditSubmit">
            <BaseInput v-model="editEquipmentForm.name" label="Nazwa" name="edit_eq_name" />
            <div class="form-actions">
              <BaseButton type="submit" :disabled="equipment.loading || !editEquipmentForm.name"
                >Zapisz</BaseButton
              >
              <BaseButton type="button" variant="outline" @click="closeEquipmentEdit"
                >Anuluj</BaseButton
              >
            </div>
          </form>
        </div>
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

.tabs {
  display: flex;
  gap: var(--space-1);
  border-bottom: 1px solid var(--color-border);
}

.tab {
  padding: var(--space-2) var(--space-4);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-muted);
  transition:
    color 0.2s,
    border-color 0.2s;
}

.tab:hover {
  color: var(--color-text);
}

.tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.section-head {
  display: flex;
  justify-content: flex-end;
}

.form-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
  background: var(--color-bg-alt);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text);
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
  max-width: 28rem;
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

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { useRoomsStore } from "@/stores/rooms"
import { useEquipmentStore } from "@/stores/equipment"
import { useUsersStore } from "@/stores/users"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseInput from "@/components/base/BaseInput.vue"
import DataTable from "@/components/base/DataTable.vue"
import Badge from "@/components/base/Badge.vue"
import EquipmentSelector from "@/components/EquipmentSelector.vue"
import { formatDateTime } from "@/utils/date"
import type { Room, RoomEquipmentInput, AdminUser } from "@/api/types"

const rooms = useRoomsStore()
const equipment = useEquipmentStore()
const users = useUsersStore()

const activeTab = ref<"rooms" | "equipment" | "users">("rooms")

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

// User form state
const showUserForm = ref(false)
const userForm = reactive({
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  is_admin: false,
})

const editingUserId = ref<number | null>(null)
const editUserForm = reactive({
  email: "",
  first_name: "",
  last_name: "",
  is_admin: false,
})

// Password reset modal
const resetPasswordUserId = ref<number | null>(null)
const newPassword = ref("")

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

const userColumns = [
  { key: "email", label: "Email" },
  { key: "name", label: "Imię i nazwisko" },
  { key: "is_admin", label: "Rola" },
  { key: "last_login", label: "Ostatnie logowanie" },
  { key: "actions", label: "" },
]

function formatEquipment(eq?: { name: string; qty: number }[]) {
  if (!eq || eq.length === 0) return "—"
  return eq.map((e) => `${e.name}${e.qty > 1 ? ` (${e.qty})` : ""}`).join(", ")
}

onMounted(() => {
  rooms.fetchList()
  equipment.fetchList()
  users.fetchList()
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

function userRowFor(u: AdminUser) {
  return {
    id: u.id,
    email: u.email,
    name: `${u.first_name} ${u.last_name}`.trim() || "—",
    is_admin: u.is_admin,
    last_login: formatDateTime(u.last_login),
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

// User actions
function resetUserForm() {
  userForm.email = ""
  userForm.password = ""
  userForm.first_name = ""
  userForm.last_name = ""
  userForm.is_admin = false
}

function openUserEdit(u: AdminUser) {
  editingUserId.value = u.id
  editUserForm.email = u.email
  editUserForm.first_name = u.first_name
  editUserForm.last_name = u.last_name
  editUserForm.is_admin = u.is_admin
}

function openUserEditById(id: number) {
  const u = users.list.find((x) => x.id === id)
  if (u) openUserEdit(u)
}

function closeUserEdit() {
  editingUserId.value = null
}

async function onUserSubmit() {
  try {
    await users.create({
      email: userForm.email,
      password: userForm.password,
      first_name: userForm.first_name,
      last_name: userForm.last_name,
      is_admin: userForm.is_admin,
    })
    resetUserForm()
    showUserForm.value = false
  } catch {
    /* error in store */
  }
}

async function onUserEditSubmit() {
  if (editingUserId.value == null) return
  try {
    await users.update(editingUserId.value, {
      email: editUserForm.email,
      first_name: editUserForm.first_name,
      last_name: editUserForm.last_name,
      is_admin: editUserForm.is_admin,
    })
    closeUserEdit()
  } catch {
    /* error in store */
  }
}

async function onUserDelete(id: number) {
  if (!confirm("Usunąć użytkownika?")) return
  try {
    await users.remove(id)
  } catch {
    alert(users.error || "Nie można usunąć użytkownika")
  }
}

function openPasswordReset(id: number) {
  resetPasswordUserId.value = id
  newPassword.value = ""
}

function closePasswordReset() {
  resetPasswordUserId.value = null
  newPassword.value = ""
}

async function onPasswordResetSubmit() {
  if (resetPasswordUserId.value == null || !newPassword.value) return
  try {
    await users.resetPassword(resetPasswordUserId.value, newPassword.value)
    closePasswordReset()
    alert("Hasło zostało zmienione")
  } catch {
    alert(users.error || "Błąd resetowania hasła")
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
      <button :class="['tab', { active: activeTab === 'users' }]" @click="activeTab = 'users'">
        Użytkownicy
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
            <BaseButton variant="outline" size="sm" @click="openRoomEditById(row.id as number)">
              Edytuj
            </BaseButton>
            <BaseButton variant="danger" size="sm" @click="onRoomDelete(row.id as number)"
              >Usuń</BaseButton
            >
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
            <BaseButton
              variant="outline"
              size="sm"
              @click="openEquipmentEditById(row.id as number)"
            >
              Edytuj
            </BaseButton>
            <BaseButton variant="danger" size="sm" @click="onEquipmentDelete(row.id as number)"
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

    <!-- Tab: Użytkownicy -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <div class="section-head">
        <BaseInput
          v-model="users.searchQuery"
          label=""
          name="search"
          placeholder="Szukaj (email, imię, nazwisko)..."
          class="search-input"
        />
        <BaseButton v-if="!showUserForm" @click="showUserForm = true">Dodaj użytkownika</BaseButton>
      </div>

      <form v-if="showUserForm" class="form-card" @submit.prevent="onUserSubmit">
        <BaseInput v-model="userForm.email" label="Email" name="email" type="email" />
        <BaseInput v-model="userForm.password" label="Hasło" name="password" type="password" />
        <BaseInput v-model="userForm.first_name" label="Imię" name="first_name" />
        <BaseInput v-model="userForm.last_name" label="Nazwisko" name="last_name" />
        <div class="form-section">
          <label class="form-checkbox">
            <input v-model="userForm.is_admin" type="checkbox" />
            <span>Administrator</span>
          </label>
        </div>
        <div class="form-actions">
          <BaseButton
            type="submit"
            :disabled="users.loading || !userForm.email || !userForm.password"
            >Zapisz</BaseButton
          >
          <BaseButton
            type="button"
            variant="outline"
            @click="
              showUserForm = false
              resetUserForm()
            "
            >Anuluj</BaseButton
          >
        </div>
      </form>

      <p v-if="users.error" class="page-error" role="alert">{{ users.error }}</p>

      <DataTable
        :columns="userColumns"
        :data="users.filteredList.map(userRowFor)"
        :loading="users.loading"
        empty-text="Brak użytkowników"
        aria-label="Lista użytkowników (CRUD)"
      >
        <template #cell-is_admin="{ row }">
          <Badge :variant="row.is_admin ? 'info' : 'default'">
            {{ row.is_admin ? "Admin" : "Użytkownik" }}
          </Badge>
        </template>
        <template #cell-actions="{ row }">
          <div class="cell-actions">
            <BaseButton variant="outline" size="sm" @click="openUserEditById(row.id as number)">
              Edytuj
            </BaseButton>
            <BaseButton variant="outline" size="sm" @click="openPasswordReset(row.id as number)">
              Reset hasła
            </BaseButton>
            <BaseButton variant="danger" size="sm" @click="onUserDelete(row.id as number)"
              >Usuń</BaseButton
            >
          </div>
        </template>
      </DataTable>

      <!-- User edit modal -->
      <div
        v-if="editingUserId != null"
        class="modal-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-user-dialog-title"
        @click.self="closeUserEdit"
      >
        <div class="modal-card">
          <h2 id="edit-user-dialog-title" class="modal-title">Edycja użytkownika</h2>
          <form @submit.prevent="onUserEditSubmit">
            <BaseInput v-model="editUserForm.email" label="Email" name="edit_email" type="email" />
            <BaseInput v-model="editUserForm.first_name" label="Imię" name="edit_first_name" />
            <BaseInput v-model="editUserForm.last_name" label="Nazwisko" name="edit_last_name" />
            <div class="form-section">
              <label class="form-checkbox">
                <input v-model="editUserForm.is_admin" type="checkbox" />
                <span>Administrator</span>
              </label>
            </div>
            <div class="form-actions">
              <BaseButton type="submit" :disabled="users.loading || !editUserForm.email"
                >Zapisz</BaseButton
              >
              <BaseButton type="button" variant="outline" @click="closeUserEdit">Anuluj</BaseButton>
            </div>
          </form>
        </div>
      </div>

      <!-- Password reset modal -->
      <div
        v-if="resetPasswordUserId != null"
        class="modal-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="reset-password-dialog-title"
        @click.self="closePasswordReset"
      >
        <div class="modal-card">
          <h2 id="reset-password-dialog-title" class="modal-title">Reset hasła</h2>
          <form @submit.prevent="onPasswordResetSubmit">
            <BaseInput
              v-model="newPassword"
              label="Nowe hasło"
              name="new_password"
              type="password"
            />
            <div class="form-actions">
              <BaseButton type="submit" :disabled="users.loading || !newPassword"
                >Zapisz</BaseButton
              >
              <BaseButton type="button" variant="outline" @click="closePasswordReset"
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
  align-items: flex-end;
  gap: var(--space-4);
}

.search-input {
  flex: 1;
  max-width: 20rem;
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

.form-checkbox {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  font-size: var(--text-sm);
  color: var(--color-text);
}

.form-checkbox input {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
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

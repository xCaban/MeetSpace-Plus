<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { useRoomsStore } from "@/stores/rooms"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseInput from "@/components/base/BaseInput.vue"
import DataTable from "@/components/base/DataTable.vue"

const rooms = useRoomsStore()
const showForm = ref(false)
const form = reactive({ name: "", capacity: 10, location: "" })

const columns = [
  { key: "name", label: "Nazwa" },
  { key: "capacity", label: "Pojemność" },
  { key: "location", label: "Lokalizacja" },
  { key: "actions", label: "" },
]

onMounted(() => {
  rooms.fetchList()
})

function rowFor(r: { id: number; name: string; capacity: number; location: string }) {
  return {
    id: r.id,
    name: r.name,
    capacity: r.capacity,
    location: r.location || "—",
    actions: "x",
  }
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

    <form
      v-if="showForm"
      class="form-inline"
      @submit.prevent="onSubmit"
    >
      <BaseInput v-model="form.name" label="Nazwa" name="name" />
      <BaseInput v-model="form.capacity" type="number" label="Pojemność" name="capacity" />
      <BaseInput v-model="form.location" label="Lokalizacja" name="location" />
      <div class="form-actions">
        <BaseButton type="submit" :disabled="rooms.loading || !form.name">Zapisz</BaseButton>
        <BaseButton type="button" variant="outline" @click="showForm = false">Anuluj</BaseButton>
      </div>
    </form>

    <p v-if="rooms.error" class="page-error">{{ rooms.error }}</p>

    <DataTable
      :columns="columns"
      :data="rooms.list.map(rowFor)"
      :loading="rooms.loading"
      empty-text="Brak sal"
    >
      <template #cell-actions="{ row }">
        <BaseButton variant="danger" size="sm" @click="onDelete(row.id)">Usuń</BaseButton>
      </template>
    </DataTable>
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
</style>

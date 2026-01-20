<script setup lang="ts">
import { onMounted } from "vue"
import { useRoomsStore } from "@/stores/rooms"
import DataTable from "@/components/base/DataTable.vue"

const rooms = useRoomsStore()

onMounted(() => {
  rooms.fetchList()
})

const columns = [
  { key: "name", label: "Nazwa" },
  { key: "capacity", label: "Pojemność" },
  { key: "location", label: "Lokalizacja" },
]

function rowFor(r: { id: number; name: string; capacity: number; location: string }) {
  return { name: r.name, capacity: r.capacity, location: r.location || "—" }
}
</script>

<template>
  <div class="page">
    <h1 class="page-title">Sale konferencyjne</h1>
    <p v-if="rooms.error" class="page-error">{{ rooms.error }}</p>
    <DataTable
      :columns="columns"
      :data="rooms.list.map(rowFor)"
      :loading="rooms.loading"
      empty-text="Brak sal"
    />
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
</style>

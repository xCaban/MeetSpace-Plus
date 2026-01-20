<script setup lang="ts">
import { onMounted } from "vue"
import { useReservationsStore } from "@/stores/reservations"
import Badge from "@/components/base/Badge.vue"
import BaseButton from "@/components/base/BaseButton.vue"
import DataTable from "@/components/base/DataTable.vue"
import type { Reservation } from "@/api/types"

const res = useReservationsStore()

onMounted(() => {
  res.fetchList()
})

const columns = [
  { key: "room_name", label: "Sala" },
  { key: "status", label: "Status" },
  { key: "start_at", label: "Od" },
  { key: "end_at", label: "Do" },
  { key: "actions", label: "" },
]

function rowFor(r: Reservation) {
  return {
    ...r,
    actions: "cancel",
  }
}

function badgeVariant(s: string) {
  if (s === "confirmed") return "success"
  if (s === "pending") return "warning"
  if (s === "canceled") return "danger"
  return "default"
}

async function onCancel(id: number) {
  try {
    await res.cancel(id)
  } catch {
    /* error in store */
  }
}
</script>

<template>
  <div class="page">
    <h1 class="page-title">Moje rezerwacje</h1>
    <p v-if="res.error" class="page-error">{{ res.error }}</p>
    <DataTable
      :columns="columns"
      :data="res.list.map(rowFor)"
      :loading="res.loading"
      empty-text="Brak rezerwacji"
    >
      <template #cell-status="{ value }">
        <Badge :variant="badgeVariant(value)">{{ value }}</Badge>
      </template>
      <template #cell-actions="{ row }">
        <BaseButton
          v-if="row.status !== 'canceled'"
          variant="danger"
          size="sm"
          @click="onCancel(row.id)"
        >
          Anuluj
        </BaseButton>
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

.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
}

.page-error {
  color: var(--color-danger);
  font-size: var(--text-sm);
}
</style>

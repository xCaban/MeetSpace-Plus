<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useReservationsStore } from "@/stores/reservations"
import Badge from "@/components/base/Badge.vue"
import BaseButton from "@/components/base/BaseButton.vue"
import DataTable from "@/components/base/DataTable.vue"
import { formatDateTime } from "@/utils/date"
import type { Reservation } from "@/api/types"

const res = useReservationsStore()

onMounted(() => {
  res.fetchList({ mine: true })
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
    start_at: formatDateTime(r.start_at),
    end_at: formatDateTime(r.end_at),
    actions: "actions",
  }
}

function badgeVariant(s: string) {
  if (s === "confirmed") return "success"
  if (s === "pending") return "warning"
  if (s === "canceled") return "danger"
  return "default"
}

async function onConfirm(id: number) {
  try {
    await res.confirm(id)
  } catch {
    /* error in store */
  }
}

const cancelingReservationId = ref<number | null>(null)

function onCancelClick(id: number) {
  cancelingReservationId.value = id
}

function closeModal() {
  cancelingReservationId.value = null
}

async function confirmCancel() {
  if (cancelingReservationId.value === null) return
  try {
    await res.cancel(cancelingReservationId.value)
  } catch {
    /* error in store */
  }
  cancelingReservationId.value = null
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
      aria-label="Lista moich rezerwacji"
    >
      <template #cell-status="{ value }">
        <Badge :variant="badgeVariant(value)">{{ value }}</Badge>
      </template>
      <template #cell-actions="{ row }">
        <div class="cell-actions">
          <BaseButton
            v-if="row.status === 'pending'"
            variant="primary"
            size="sm"
            :disabled="res.loading"
            @click="onConfirm(row.id)"
          >
            Potwierdź
          </BaseButton>
          <BaseButton
            v-if="row.status !== 'canceled'"
            variant="danger"
            size="sm"
            :disabled="res.loading"
            @click="onCancelClick(row.id)"
          >
            Anuluj
          </BaseButton>
        </div>
      </template>
    </DataTable>

    <div
      v-if="cancelingReservationId !== null"
      class="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="cancel-dialog-title"
      @click.self="closeModal"
    >
      <div class="modal-card">
        <h3 id="cancel-dialog-title" class="modal-title">Anulować rezerwację?</h3>
        <p class="modal-text">
          Czy na pewno chcesz anulować tę rezerwację? Tej operacji nie można cofnąć.
        </p>
        <div class="modal-actions">
          <BaseButton variant="secondary" @click="closeModal">Nie</BaseButton>
          <BaseButton variant="danger" :disabled="res.loading" @click="confirmCancel">
            Tak, anuluj
          </BaseButton>
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

.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
}

.page-error {
  color: var(--color-danger);
  font-size: var(--text-sm);
}

.cell-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  max-width: 400px;
  width: 90%;
  box-shadow: var(--shadow-lg);
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-2);
}

.modal-text {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}

.modal-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
}
</style>

<script setup lang="ts">
import { computed } from "vue"
import type { Equipment, RoomEquipmentInput } from "@/api/types"

const props = defineProps<{
  modelValue: RoomEquipmentInput[]
  equipment: Equipment[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  "update:modelValue": [value: RoomEquipmentInput[]]
}>()

const selectedMap = computed(() => {
  const map = new Map<number, number>()
  for (const item of props.modelValue) {
    map.set(item.equipment_id, item.qty)
  }
  return map
})

function isSelected(id: number): boolean {
  return selectedMap.value.has(id)
}

function getQty(id: number): number {
  return selectedMap.value.get(id) ?? 1
}

function toggleEquipment(id: number, checked: boolean) {
  if (checked) {
    emit("update:modelValue", [...props.modelValue, { equipment_id: id, qty: 1 }])
  } else {
    emit(
      "update:modelValue",
      props.modelValue.filter((e) => e.equipment_id !== id)
    )
  }
}

function updateQty(id: number, qty: number) {
  const newValue = props.modelValue.map((e) =>
    e.equipment_id === id ? { ...e, qty: Math.max(1, qty) } : e
  )
  emit("update:modelValue", newValue)
}
</script>

<template>
  <div class="equipment-selector">
    <div v-if="equipment.length === 0" class="equipment-empty">Brak dostępnego sprzętu</div>
    <div v-for="eq in equipment" :key="eq.id" class="equipment-item">
      <label class="equipment-label">
        <input
          type="checkbox"
          :checked="isSelected(eq.id)"
          :disabled="disabled"
          @change="toggleEquipment(eq.id, ($event.target as HTMLInputElement).checked)"
        />
        <span class="equipment-name">{{ eq.name }}</span>
      </label>
      <input
        v-if="isSelected(eq.id)"
        type="number"
        class="equipment-qty"
        :value="getQty(eq.id)"
        min="1"
        :disabled="disabled"
        @input="updateQty(eq.id, Number(($event.target as HTMLInputElement).value))"
      />
    </div>
  </div>
</template>

<style scoped>
.equipment-selector {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.equipment-empty {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.equipment-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.equipment-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  flex: 1;
}

.equipment-label input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
}

.equipment-name {
  font-size: var(--text-sm);
}

.equipment-qty {
  width: 4rem;
  padding: var(--space-1) var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}
</style>

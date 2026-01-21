<script setup lang="ts">
export interface SelectOption {
  value: string | number
  label: string
}

interface Props {
  modelValue: string | number
  options: SelectOption[]
  label?: string
  name?: string
  placeholder?: string
  disabled?: boolean
  error?: string
}

withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{ "update:modelValue": [v: string | number] }>()

function onChange(e: Event) {
  const t = e.target as HTMLSelectElement
  const v = t.value
  const num = Number(v)
  emit("update:modelValue", Number.isNaN(num) ? v : num)
}
</script>

<template>
  <div class="field">
    <label v-if="label" :for="name" class="field-label">{{ label }}</label>
    <select
      :id="name"
      :name="name"
      :value="modelValue"
      :disabled="disabled"
      class="select"
      :class="{ 'select--error': error }"
      @change="onChange"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option v-for="opt in options" :key="String(opt.value)" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>
    <p v-if="error" class="field-error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.field-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text);
}

.select {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-base);
  line-height: 1.5;
  color: var(--color-text);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.select:hover:not(:disabled) {
  border-color: var(--color-neutral-400);
}

.select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}

.select--error {
  border-color: var(--color-danger);
}

.select:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.field-error {
  font-size: var(--text-sm);
  color: var(--color-danger);
}
</style>

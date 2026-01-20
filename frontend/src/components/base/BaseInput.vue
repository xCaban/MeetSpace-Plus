<script setup lang="ts">
interface Props {
  modelValue: string | number
  type?: "text" | "email" | "password" | "number" | "datetime-local"
  label?: string
  name?: string
  placeholder?: string
  disabled?: boolean
  error?: string
  hint?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: "text",
  disabled: false,
})

const emit = defineEmits<{ "update:modelValue": [v: string | number] }>()

function onInput(e: Event) {
  const t = e.target as HTMLInputElement
  if (props.type === "number") {
    const v = t.valueAsNumber
    emit("update:modelValue", Number.isNaN(v) ? (t.value as string) : v)
  } else if (props.type === "datetime-local") {
    emit("update:modelValue", t.value)
  } else {
    emit("update:modelValue", t.value)
  }
}
</script>

<template>
  <div class="field">
    <label v-if="label" :for="name" class="field-label">{{ label }}</label>
    <input
      :id="name"
      :name="name"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      class="input"
      :class="{ 'input--error': error }"
      @input="onInput"
    />
    <p v-if="error" class="field-error" role="alert">{{ error }}</p>
    <p v-else-if="hint" class="field-hint">{{ hint }}</p>
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

.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-base);
  line-height: 1.5;
  color: var(--color-text);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.input:hover:not(:disabled) {
  border-color: var(--color-neutral-400);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}

.input--error {
  border-color: var(--color-danger);
}

.input:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.field-error {
  font-size: var(--text-sm);
  color: var(--color-danger);
}

.field-hint {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}
</style>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue"

export interface MultiSelectOption {
  id: number
  name: string
}

interface Props {
  modelValue: number[]
  options: MultiSelectOption[]
  label?: string
  name?: string
  placeholder?: string
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  placeholder: "Wybierz opcje",
})
const emit = defineEmits<{ "update:modelValue": [v: number[]] }>()

const isOpen = ref(false)
const dropdownRef = ref<HTMLDivElement | null>(null)

const selectedCount = computed(() => props.modelValue.length)
const displayText = computed(() => {
  if (selectedCount.value === 0) return props.placeholder
  if (selectedCount.value === 1) {
    const opt = props.options.find((o) => o.id === props.modelValue[0])
    return opt?.name ?? props.placeholder
  }
  return `Wybrano: ${selectedCount.value}`
})

function toggleOption(id: number) {
  const current = [...props.modelValue]
  const index = current.indexOf(id)
  if (index >= 0) {
    current.splice(index, 1)
  } else {
    current.push(id)
  }
  emit("update:modelValue", current)
}

function isSelected(id: number) {
  return props.modelValue.includes(id)
}

function toggleDropdown() {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
  }
}

function closeDropdown() {
  isOpen.value = false
}

function handleClickOutside(e: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside)
})
</script>

<template>
  <div class="field">
    <label v-if="label" :for="name" class="field-label">{{ label }}</label>
    <div ref="dropdownRef" class="multiselect">
      <button
        :id="name"
        type="button"
        class="multiselect-trigger"
        :class="{ 'multiselect-trigger--error': error, 'multiselect-trigger--open': isOpen }"
        :disabled="disabled"
        @click="toggleDropdown"
      >
        <span class="multiselect-text">{{ displayText }}</span>
        <span class="multiselect-arrow" :class="{ 'multiselect-arrow--open': isOpen }">▼</span>
      </button>
      <div v-if="isOpen" class="multiselect-dropdown">
        <div v-if="options.length === 0" class="multiselect-empty">Brak opcji</div>
        <label
          v-for="opt in options"
          :key="opt.id"
          class="multiselect-option"
          :class="{ 'multiselect-option--selected': isSelected(opt.id) }"
        >
          <input
            type="checkbox"
            :checked="isSelected(opt.id)"
            @change="toggleOption(opt.id)"
          />
          <span>{{ opt.name }}</span>
        </label>
      </div>
    </div>
    <p v-if="error" class="field-error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  position: relative;
}

.field-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text);
}

.multiselect {
  position: relative;
}

.multiselect-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-base);
  line-height: 1.5;
  color: var(--color-text);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  text-align: left;
}

.multiselect-trigger:hover:not(:disabled) {
  border-color: var(--color-neutral-400);
}

.multiselect-trigger:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}

.multiselect-trigger--open {
  border-color: var(--color-primary);
}

.multiselect-trigger--error {
  border-color: var(--color-danger);
}

.multiselect-trigger:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.multiselect-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.multiselect-arrow {
  margin-left: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  transition: transform 0.2s;
}

.multiselect-arrow--open {
  transform: rotate(180deg);
}

.multiselect-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 100;
  margin-top: var(--space-1);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 16rem;
  overflow-y: auto;
}

.multiselect-empty {
  padding: var(--space-3);
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.multiselect-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  transition: background 0.15s;
}

.multiselect-option:hover {
  background: var(--color-neutral-50);
}

.multiselect-option--selected {
  background: var(--color-primary-muted);
}

.multiselect-option input[type="checkbox"] {
  cursor: pointer;
  width: 1rem;
  height: 1rem;
  accent-color: var(--color-primary);
}

.multiselect-option span {
  flex: 1;
  font-size: var(--text-sm);
}

.field-error {
  font-size: var(--text-sm);
  color: var(--color-danger);
}
</style>

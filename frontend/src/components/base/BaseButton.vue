<script setup lang="ts">
interface Props {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger"
  size?: "sm" | "md" | "lg"
  type?: "button" | "submit" | "reset"
  disabled?: boolean
  block?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: "primary",
  size: "md",
  type: "button",
  disabled: false,
  block: false,
})
</script>

<template>
  <button
    :type="type"
    class="btn"
    :class="[
      `btn--${variant}`,
      `btn--${size}`,
      { 'btn--block': block },
      { 'btn--disabled': disabled },
    ]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-weight: var(--font-medium);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition:
    background 0.15s,
    border-color 0.15s,
    color 0.15s;
}

.btn:disabled,
.btn--disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-sm);
}

.btn--md {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-base);
}

.btn--lg {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-lg);
}

.btn--block {
  width: 100%;
}

.btn--primary {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.btn--primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn--secondary {
  background: var(--color-neutral-200);
  color: var(--color-text);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--color-neutral-300);
}

.btn--outline {
  background: transparent;
  color: var(--color-primary);
  border-color: var(--color-border);
}

.btn--outline:hover:not(:disabled) {
  background: var(--color-primary-muted);
  border-color: var(--color-primary);
}

.btn--ghost {
  background: transparent;
  color: var(--color-text);
}

.btn--ghost:hover:not(:disabled) {
  background: var(--color-neutral-100);
}

.btn--danger {
  background: var(--color-danger);
  color: white;
  border-color: var(--color-danger);
}

.btn--danger:hover:not(:disabled) {
  opacity: 0.9;
}
</style>

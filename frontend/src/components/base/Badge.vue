<script setup lang="ts">
interface Props {
  variant?: "default" | "success" | "warning" | "danger" | "info"
}

withDefaults(defineProps<Props>(), {
  variant: "default",
})
</script>

<template>
  <span class="badge" :class="`badge--${variant}`">
    <slot />
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  border-radius: var(--radius-sm);
  line-height: 1;
}

.badge--default {
  background: var(--color-neutral-200);
  color: var(--color-neutral-700);
}

.badge--success {
  background: var(--color-success-muted);
  color: var(--color-success);
}

.badge--warning {
  background: var(--color-warning-muted);
  color: var(--color-warning);
}

.badge--danger {
  background: var(--color-danger-muted);
  color: var(--color-danger);
}

.badge--info {
  background: var(--color-primary-muted);
  color: var(--color-primary);
}
</style>

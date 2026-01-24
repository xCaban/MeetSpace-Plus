<script setup lang="ts">
import BaseSkeleton from "./BaseSkeleton.vue"

interface Column {
  key: string
  label: string
  sortable?: boolean
  class?: string
}

interface Props {
  columns: Column[]
  data: Record<string, unknown>[]
  loading?: boolean
  emptyText?: string
  /** Etykieta dla czytników ekranu (a11y). */
  ariaLabel?: string
  /** Liczba skeleton rows podczas ładowania. */
  skeletonRows?: number
}

withDefaults(defineProps<Props>(), {
  loading: false,
  emptyText: "Brak danych",
  skeletonRows: 3,
})
</script>

<template>
  <div class="table-wrap">
    <table class="table" role="table" :aria-label="ariaLabel">
      <thead>
        <tr>
          <th v-for="col in columns" :key="col.key" :class="col.class" scope="col">
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <template v-if="loading">
          <tr v-for="n in skeletonRows" :key="`skeleton-${n}`" class="skeleton-row">
            <td v-for="col in columns" :key="col.key" :class="col.class">
              <BaseSkeleton width="70%" height="1rem" />
            </td>
          </tr>
        </template>
        <tr v-else-if="data.length === 0">
          <td :colspan="columns.length" class="table-empty">
            {{ emptyText }}
          </td>
        </tr>
        <tr v-for="(row, i) in data" :key="i">
          <td v-for="col in columns" :key="col.key" :class="col.class">
            <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

th,
td {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

th {
  font-weight: var(--font-semibold);
  color: var(--color-text);
  background: var(--color-bg-alt);
}

th:first-child,
td:first-child {
  padding-left: var(--space-4);
}

th:last-child,
td:last-child {
  padding-right: var(--space-4);
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background: var(--color-neutral-50);
}

.table-empty {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-8) !important;
}

.skeleton-row:hover td {
  background: transparent;
}

@media (max-width: 640px) {
  .table {
    font-size: var(--text-xs);
  }

  th,
  td {
    padding: var(--space-2) var(--space-3);
  }
}
</style>

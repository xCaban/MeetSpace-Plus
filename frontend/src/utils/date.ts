const LOCALE = "pl-PL"

/**
 * Formatuje datę i godzinę (np. "22.01.2026, 14:30")
 */
export function formatDateTime(date: string | Date | null): string {
  if (!date) return "—"
  const d = typeof date === "string" ? new Date(date) : date
  return d.toLocaleString(LOCALE)
}

/**
 * Formatuje tylko datę (np. "22.01.2026")
 */
export function formatDate(date: string | Date | null): string {
  if (!date) return "—"
  const d = typeof date === "string" ? new Date(date) : date
  return d.toLocaleDateString(LOCALE)
}

/**
 * Formatuje datę skrócono (np. "śr., 22 sty")
 */
export function formatDateShort(date: string | Date | null): string {
  if (!date) return "—"
  const d = typeof date === "string" ? new Date(date) : date
  return d.toLocaleDateString(LOCALE, {
    weekday: "short",
    day: "numeric",
    month: "short",
  })
}

/**
 * Formatuje tylko godzinę (np. "14:30")
 */
export function formatTime(date: string | Date | null): string {
  if (!date) return "—"
  const d = typeof date === "string" ? new Date(date) : date
  return d.toLocaleTimeString(LOCALE, {
    hour: "2-digit",
    minute: "2-digit",
  })
}

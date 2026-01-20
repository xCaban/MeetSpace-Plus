import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { api } from "@/api/client"
import type { Reservation, ReservationCreate } from "@/api/types"

export const useReservationsStore = defineStore("reservations", () => {
  const list = ref<Reservation[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchList(params?: {
    room_id?: number
    from?: string
    to?: string
    status?: string
    mine?: boolean
  }) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<Reservation[]>("/reservations/", { params })
      list.value = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd ładowania rezerwacji"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: number) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<Reservation>(`/reservations/${id}/`)
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd ładowania rezerwacji"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(payload: ReservationCreate) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post<Reservation>("/reservations/", payload)
      list.value = [data, ...list.value]
      return data
    } catch (e: unknown) {
      const err = e as { message?: string; status?: number }
      error.value = err?.message ?? "Błąd tworzenia rezerwacji"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function confirm(id: number) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post<Reservation>(`/reservations/${id}/confirm/`)
      const i = list.value.findIndex((r) => r.id === id)
      if (i >= 0) list.value[i] = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd potwierdzania rezerwacji"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function cancel(id: number) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post<Reservation>(`/reservations/${id}/cancel/`)
      const i = list.value.findIndex((r) => r.id === id)
      if (i >= 0) list.value[i] = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd anulowania rezerwacji"
      throw e
    } finally {
      loading.value = false
    }
  }

  const listCount = computed(() => list.value.length)
  const isListEmpty = computed(() => list.value.length === 0 && !loading.value)
  const hasError = computed(() => error.value != null)

  return {
    list,
    loading,
    error,
    listCount,
    isListEmpty,
    hasError,
    fetchList,
    fetchOne,
    create,
    confirm,
    cancel,
  }
})

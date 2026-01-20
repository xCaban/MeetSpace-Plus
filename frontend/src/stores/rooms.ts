import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { api } from "@/api/client"
import type { Room, RoomDetail } from "@/api/types"

export interface RoomCreatePayload {
  name: string
  capacity?: number
  location?: string
}

export const useRoomsStore = defineStore("rooms", () => {
  const list = ref<Room[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchList() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<Room[]>("/rooms/")
      list.value = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd ładowania sal"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: number) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<RoomDetail>(`/rooms/${id}/`)
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd ładowania sali"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(payload: RoomCreatePayload) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post<Room>("/rooms/", payload)
      list.value = [data, ...list.value]
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd tworzenia sali"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function update(id: number, payload: Partial<RoomCreatePayload>) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.patch<Room>(`/rooms/${id}/`, payload)
      const i = list.value.findIndex((r) => r.id === id)
      if (i >= 0) list.value[i] = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd aktualizacji sali"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/rooms/${id}/`)
      list.value = list.value.filter((r) => r.id !== id)
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd usuwania sali"
      throw e
    } finally {
      loading.value = false
    }
  }

  const listCount = computed(() => list.value.length)

  return {
    list,
    loading,
    error,
    listCount,
    fetchList,
    fetchOne,
    create,
    update,
    remove,
  }
})

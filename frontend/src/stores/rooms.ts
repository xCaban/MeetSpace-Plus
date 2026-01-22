import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { api } from "@/api/client"
import type { Room, RoomDetail, RoomEquipmentInput, Equipment } from "@/api/types"

export interface RoomCreatePayload {
  name: string
  capacity?: number
  location?: string
  equipment?: RoomEquipmentInput[]
}

export interface RoomFilters {
  capacity_min?: number
  location?: string
  equipment_ids?: number[]
}

export const useRoomsStore = defineStore("rooms", () => {
  const list = ref<Room[]>([])
  const equipmentList = ref<Equipment[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const filters = ref<RoomFilters>({})

  function setFilters(p: Partial<RoomFilters>) {
    filters.value = { ...filters.value, ...p }
  }

  const filteredList = computed(() => {
    const l = list.value
    const { capacity_min, location, equipment_ids } = filters.value
    return l.filter((r) => {
      const capOk = capacity_min == null || capacity_min <= 0 || r.capacity >= capacity_min
      const locOk =
        location == null ||
        String(location).trim() === "" ||
        (r.location || "").toLowerCase().includes(String(location).trim().toLowerCase())
      const eqOk =
        equipment_ids == null ||
        equipment_ids.length === 0 ||
        (r.equipment && equipment_ids.every((eqId) => r.equipment?.some((eq) => eq.id === eqId)))
      return capOk && locOk && eqOk
    })
  })

  async function fetchEquipment() {
    try {
      const { data } = await api.get<Equipment[]>("/equipment/")
      equipmentList.value = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd ładowania sprzętu"
      throw e
    }
  }

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
  const isListEmpty = computed(() => list.value.length === 0 && !loading.value)
  const hasError = computed(() => error.value != null)

  return {
    list,
    equipmentList,
    loading,
    error,
    listCount,
    filters,
    setFilters,
    filteredList,
    isListEmpty,
    hasError,
    fetchEquipment,
    fetchList,
    fetchOne,
    create,
    update,
    remove,
  }
})

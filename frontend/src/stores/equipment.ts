import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { api } from "@/api/client"
import type { Equipment } from "@/api/types"

export interface EquipmentCreatePayload {
  name: string
}

export const useEquipmentStore = defineStore("equipment", () => {
  const list = ref<Equipment[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchList() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<Equipment[]>("/equipment/")
      list.value = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd ładowania sprzętu"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(payload: EquipmentCreatePayload) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post<Equipment>("/equipment/", payload)
      list.value = [data, ...list.value]
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd tworzenia sprzętu"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function update(id: number, payload: Partial<EquipmentCreatePayload>) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.patch<Equipment>(`/equipment/${id}/`, payload)
      const i = list.value.findIndex((e) => e.id === id)
      if (i >= 0) list.value[i] = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd aktualizacji sprzętu"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/equipment/${id}/`)
      list.value = list.value.filter((e) => e.id !== id)
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } }; message?: string }
      error.value = err?.response?.data?.detail ?? err?.message ?? "Błąd usuwania sprzętu"
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
    create,
    update,
    remove,
  }
})

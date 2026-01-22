import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { api } from "@/api/client"
import type { AdminUser, AdminUserCreate, AdminUserUpdate } from "@/api/types"

export const useUsersStore = defineStore("users", () => {
  const list = ref<AdminUser[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref("")

  const filteredList = computed(() => {
    const q = searchQuery.value.toLowerCase().trim()
    if (!q) return list.value
    return list.value.filter(
      (u) =>
        u.email.toLowerCase().includes(q) ||
        u.first_name.toLowerCase().includes(q) ||
        u.last_name.toLowerCase().includes(q)
    )
  })

  async function fetchList() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<AdminUser[]>("/admin/users/")
      list.value = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd ładowania użytkowników"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: number) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<AdminUser>(`/admin/users/${id}/`)
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd ładowania użytkownika"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(payload: AdminUserCreate) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post<AdminUser>("/admin/users/", payload)
      list.value = [data, ...list.value]
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd tworzenia użytkownika"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function update(id: number, payload: AdminUserUpdate) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.patch<AdminUser>(`/admin/users/${id}/`, payload)
      const i = list.value.findIndex((u) => u.id === id)
      if (i >= 0) list.value[i] = data
      return data
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd aktualizacji użytkownika"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/admin/users/${id}/`)
      list.value = list.value.filter((u) => u.id !== id)
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd usuwania użytkownika"
      throw e
    } finally {
      loading.value = false
    }
  }

  async function resetPassword(id: number, password: string) {
    loading.value = true
    error.value = null
    try {
      await api.post(`/admin/users/${id}/reset-password/`, { password })
    } catch (e: unknown) {
      const err = e as { message?: string }
      error.value = err?.message ?? "Błąd resetowania hasła"
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
    searchQuery,
    filteredList,
    listCount,
    isListEmpty,
    hasError,
    fetchList,
    fetchOne,
    create,
    update,
    remove,
    resetPassword,
  }
})

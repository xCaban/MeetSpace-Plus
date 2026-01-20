import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { api } from "@/api/client"
import type { User, LoginRequest } from "@/api/types"

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null)
  const _initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.roles?.includes("admin") ?? false)
  const roles = computed(() => user.value?.roles ?? [])

  async function login(payload: LoginRequest) {
    const { data } = await api.post<{ access: string; refresh: string; user: User }>(
      "/auth/login",
      payload
    )
    localStorage.setItem("access", data.access)
    localStorage.setItem("refresh", data.refresh)
    user.value = data.user
    return data
  }

  async function logout() {
    const refresh = localStorage.getItem("refresh")
    if (refresh) {
      try {
        await api.post("/auth/logout", { refresh })
      } catch {
        /* ignore */
      }
    }
    localStorage.removeItem("access")
    localStorage.removeItem("refresh")
    user.value = null
  }

  async function fetchMe() {
    const { data } = await api.get<User>("/me")
    user.value = data
    return data
  }

  async function init() {
    if (_initialized.value) return
    if (!localStorage.getItem("access")) {
      _initialized.value = true
      return
    }
    try {
      await fetchMe()
    } catch {
      localStorage.removeItem("access")
      localStorage.removeItem("refresh")
      user.value = null
    }
    _initialized.value = true
  }

  function clearUser() {
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    roles,
    login,
    logout,
    fetchMe,
    init,
    clearUser,
  }
})

import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { api } from "@/api/client"
import type { User, LoginRequest, RegisterRequest } from "@/api/types"

/**
 * Konfiguracja httpOnly cookie (refresh token):
 * 1) Backend – login: w odpowiedzi ustaw Set-Cookie, np.:
 *    response.set_cookie("refresh_token", str(refresh), max_age=7*24*3600,
 *                       httponly=True, secure=not DEBUG, samesite="lax")
 * 2) Backend – /auth/refresh: jeśli brak body.refresh, odczytaj z request.COOKIES.get("refresh_token").
 * 3) Frontend: ustaw VITE_USE_HTTPONLY_REFRESH=true, w refreshToken nie przekazuj body,
 *    wywołuj: api.post("/auth/refresh", null, { withCredentials: true }).
 * 4) Axios: api.defaults.withCredentials = true, aby wysyłać ciasteczka.
 * Poniżej: fallback – refresh w pamięci, POST { refresh }.
 */
const USE_HTTPONLY_REFRESH = import.meta.env.VITE_USE_HTTPONLY_REFRESH === "true"

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null)
  const access = ref<string | null>(null)
  const refresh = ref<string | null>(null)
  const _initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value && !!access.value)
  const isAdmin = computed(() => user.value?.roles?.includes("admin") ?? false)
  const roles = computed(() => user.value?.roles ?? [])

  function getAccessToken(): string | null {
    return access.value
  }

  async function login(payload: LoginRequest) {
    const { data } = await api.post<{ access: string; refresh: string; user: User }>(
      "/auth/login",
      payload
    )
    access.value = data.access
    if (!USE_HTTPONLY_REFRESH && data.refresh) {
      refresh.value = data.refresh
    } else {
      refresh.value = null
    }
    user.value = data.user
    return data
  }

  async function register(payload: RegisterRequest) {
    const { data } = await api.post<{ access: string; refresh: string; user: User }>(
      "/auth/register",
      payload
    )
    access.value = data.access
    if (!USE_HTTPONLY_REFRESH && data.refresh) {
      refresh.value = data.refresh
    } else {
      refresh.value = null
    }
    user.value = data.user
    return data
  }

  /**
   * Odświeża access używając refresh (fallback: w body; httpOnly: cookie + withCredentials).
   * @throws przy błędzie (np. 401) – wtedy wywołaj logout.
   */
  async function refreshToken(): Promise<string> {
    if (USE_HTTPONLY_REFRESH) {
      const { data } = await api.post<{ access: string }>("/auth/refresh", null, {
        withCredentials: true,
      })
      access.value = data.access
      return data.access
    }
    const r = refresh.value
    if (!r) throw new Error("No refresh token")
    const { data } = await api.post<{ access: string }>("/auth/refresh", { refresh: r })
    access.value = data.access
    return data.access
  }

  async function logout() {
    try {
      if (USE_HTTPONLY_REFRESH) {
        await api.post("/auth/logout", null, { withCredentials: true })
      } else if (refresh.value) {
        await api.post("/auth/logout", { refresh: refresh.value })
      }
    } catch {
      /* ignore – blacklist może być niedostępny */
    }
    access.value = null
    refresh.value = null
    user.value = null
    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event("auth:logout"))
    }
  }

  async function fetchMe() {
    const { data } = await api.get<User>("/me")
    user.value = data
    return data
  }

  async function init() {
    if (_initialized.value) return
    if (!access.value) {
      _initialized.value = true
      return
    }
    try {
      await fetchMe()
    } catch {
      access.value = null
      refresh.value = null
      user.value = null
    }
    _initialized.value = true
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    roles,
    getAccessToken,
    login,
    register,
    refreshToken,
    logout,
    fetchMe,
    init,
  }
})

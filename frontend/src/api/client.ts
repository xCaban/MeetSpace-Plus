import axios, { type AxiosError } from "axios"
import type { ApiError } from "./types"

const baseURL =
  import.meta.env.VITE_API_BASE || (typeof window !== "undefined" ? "" : "http://localhost:8000/api")

export const api = axios.create({
  baseURL: baseURL ? `${baseURL.replace(/\/$/, "")}` : "/api",
  headers: {
    "Content-Type": "application/json",
  },
})

/** Interceptor request: dołącza Bearer access token ze store (pamięć). */
api.interceptors.request.use(async (config) => {
  const { useAuthStore } = await import("@/stores/auth")
  const token = useAuthStore().getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** Interceptor response: 401 → jedna próba refresh, potem logout. */
api.interceptors.response.use(
  (res) => res,
  async (err: AxiosError<ApiError>) => {
    const orig = err.config
    if (!orig || orig._retry) {
      return Promise.reject(normalizeError(err))
    }
    const url = orig.url ?? ""

    if (err.response?.status === 401) {
      if (url.includes("/auth/login") || url.includes("/auth/refresh")) {
        return Promise.reject(normalizeError(err))
      }
      orig._retry = true
      const { useAuthStore } = await import("@/stores/auth")
      const auth = useAuthStore()
      try {
        await auth.refreshToken()
        const token = auth.getAccessToken()
        if (orig.headers && token) {
          orig.headers.Authorization = `Bearer ${token}`
        }
        return api(orig)
      } catch {
        await auth.logout()
        return Promise.reject(normalizeError(err))
      }
    }

    return Promise.reject(normalizeError(err))
  }
)

declare module "axios" {
  interface InternalAxiosRequestConfig {
    _retry?: boolean
  }
}

function normalizeError(
  err: AxiosError<ApiError>
): { message: string; status?: number; data?: ApiError } {
  const status = err.response?.status
  const data = err.response?.data
  let message = err.message
  if (data?.detail && typeof data.detail === "string") message = data.detail
  else if (data && typeof data === "object") {
    const first = Object.values(data).flat().find((v) => typeof v === "string")
    if (first) message = first as string
  }
  return { message, status, data }
}

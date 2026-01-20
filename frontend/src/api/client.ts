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

/** Interceptor request: dołącza JWT z localStorage. */
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** Interceptor response: 401 → próba refresh, błędy → ujednolicony format. */
api.interceptors.response.use(
  (res) => res,
  async (err: AxiosError<ApiError>) => {
    const orig = err.config
    if (!orig || orig._retry) {
      return Promise.reject(normalizeError(err))
    }

    if (err.response?.status === 401) {
      orig._retry = true
      const refresh = localStorage.getItem("refresh")
      if (refresh) {
        try {
          const { data } = await axios.post<{ access: string }>(
            `${api.defaults.baseURL}/auth/refresh`,
            { refresh }
          )
          localStorage.setItem("access", data.access)
          if (orig.headers) orig.headers.Authorization = `Bearer ${data.access}`
          return api(orig)
        } catch {
          localStorage.removeItem("access")
          localStorage.removeItem("refresh")
          window.dispatchEvent(new Event("auth:logout"))
        }
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

function normalizeError(err: AxiosError<ApiError>): { message: string; status?: number; data?: ApiError } {
  const status = err.response?.status
  const data = err.response?.data
  let message = err.message
  if (data?.detail && typeof data.detail === "string") message = data.detail
  else if (data && typeof data === "object") {
    const first = Object.values(data).flat().find((v) => typeof v === "string")
    if (first) message = first
  }
  return { message, status, data }
}

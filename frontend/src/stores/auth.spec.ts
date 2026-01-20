import { describe, it, expect, beforeEach } from "vitest"
import { setActivePinia, createPinia } from "pinia"
import { useAuthStore } from "./auth"

describe("useAuthStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("starts unauthenticated", () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
    expect(store.isAdmin).toBe(false)
    expect(store.user).toBeNull()
    expect(store.getAccessToken()).toBeNull()
  })
})

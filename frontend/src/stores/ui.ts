import { defineStore } from "pinia"
import { ref } from "vue"

export const useUiStore = defineStore("ui", () => {
  const sidebarOpen = ref(true)
  const globalToast = ref<{ text: string; type?: "info" | "success" | "warning" | "error" } | null>(
    null
  )

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function setSidebarOpen(value: boolean) {
    sidebarOpen.value = value
  }

  function showToast(text: string, type: "info" | "success" | "warning" | "error" = "info") {
    globalToast.value = { text, type }
  }

  function clearToast() {
    globalToast.value = null
  }

  return {
    sidebarOpen,
    globalToast,
    toggleSidebar,
    setSidebarOpen,
    showToast,
    clearToast,
  }
})

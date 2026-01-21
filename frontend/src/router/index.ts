import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import MainLayout from "@/layouts/MainLayout.vue"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { guest: true },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("@/views/RegisterView.vue"),
      meta: { guest: true },
    },
    {
      path: "/",
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        { path: "", redirect: { name: "rooms" } },
        {
          path: "rooms",
          name: "rooms",
          component: () => import("@/views/RoomListView.vue"),
        },
        {
          path: "calendar",
          name: "calendar",
          component: () => import("@/views/CalendarView.vue"),
        },
        {
          path: "my",
          name: "my",
          component: () => import("@/views/MyReservationsView.vue"),
        },
        {
          path: "admin/rooms",
          name: "admin-rooms",
          component: () => import("@/views/AdminRoomsView.vue"),
          meta: { requiresAdmin: true },
        },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: { name: "rooms" } },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.init()

  if (to.meta.guest) {
    if (auth.isAuthenticated) return { name: "rooms" }
    return
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } }
  }

  if (to.path.startsWith("/admin") && !auth.isAdmin) {
    return { name: "login", query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: "rooms" }
  }
})

export default router

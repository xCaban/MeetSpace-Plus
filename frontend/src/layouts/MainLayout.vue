<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { RouterLink, useRoute } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import BaseButton from "@/components/base/BaseButton.vue"

const route = useRoute()
const auth = useAuthStore()

const mobileMenuOpen = ref(false)

onMounted(() => {
  auth.init()
})

function onLogout() {
  auth.logout()
}

const nav = computed(() => {
  const items = [
    { name: "Sale", to: { name: "rooms" } },
    { name: "Kalendarz", to: { name: "calendar" } },
    { name: "Moje rezerwacje", to: { name: "my" } },
  ]
  if (auth.isAdmin) {
    items.push({ name: "Panel admina", to: { name: "admin-rooms" } })
  }
  return items
})
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-inner container">
        <RouterLink :to="{ name: 'rooms' }" class="brand">MeetSpace Plus</RouterLink>

        <button
          type="button"
          class="menu-trigger"
          aria-label="Menu"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <span class="menu-icon" />
        </button>

        <nav class="nav" :class="{ 'nav--open': mobileMenuOpen }">
          <RouterLink
            v-for="item in nav"
            :key="String(item.to.name)"
            :to="item.to"
            class="nav-link"
            :class="{ 'nav-link--active': route.name === item.to.name }"
            @click="mobileMenuOpen = false"
          >
            {{ item.name }}
          </RouterLink>
          <div class="nav-user">
            <span class="nav-email">{{ auth.user?.email }}</span>
            <BaseButton variant="outline" size="sm" @click="onLogout">Wyloguj</BaseButton>
          </div>
        </nav>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  height: var(--header-height);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  gap: var(--space-4);
}

.brand {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text);
}

.brand:hover {
  text-decoration: none;
  color: var(--color-primary);
}

.menu-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
}

.menu-icon {
  display: block;
  width: 1.25rem;
  height: 2px;
  background: var(--color-text);
  box-shadow: 0 6px 0 var(--color-text), 0 -6px 0 var(--color-text);
}

.nav {
  display: none;
  flex-direction: column;
  gap: var(--space-2);
}

.nav-link {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-weight: var(--font-medium);
}

.nav-link:hover,
.nav-link--active {
  color: var(--color-primary);
  background: var(--color-primary-muted);
  text-decoration: none;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-top: var(--space-2);
  margin-top: var(--space-2);
  border-top: 1px solid var(--color-border);
}

.nav-email {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

@media (min-width: 768px) {
  .menu-trigger {
    display: none;
  }

  .nav {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: var(--space-1);
    padding-top: 0;
  }

  .nav-user {
    margin-top: 0;
    padding-top: 0;
    border-top: none;
    margin-left: var(--space-4);
    padding-left: var(--space-4);
    border-left: 1px solid var(--color-border);
  }
}

@media (max-width: 767px) {
  .nav--open {
    display: flex;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--color-bg);
    border-bottom: 1px solid var(--color-border);
    padding: var(--space-4);
    box-shadow: var(--shadow-md);
  }
}

.main {
  flex: 1;
  padding-block: var(--space-6);
}
</style>

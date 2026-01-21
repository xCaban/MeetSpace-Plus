<script setup lang="ts">
import { ref, reactive } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseInput from "@/components/base/BaseInput.vue"

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const loading = ref(false)
const error = ref<string | null>(null)
const emailError = ref<string | null>(null)
const passwordError = ref<string | null>(null)
const form = reactive({ email: "", password: "" })

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate(): boolean {
  emailError.value = null
  passwordError.value = null
  let ok = true
  if (!form.email.trim()) {
    emailError.value = "E-mail jest wymagany"
    ok = false
  } else if (!EMAIL_RE.test(form.email)) {
    emailError.value = "Nieprawidłowy format e-mail"
    ok = false
  }
  if (!form.password) {
    passwordError.value = "Hasło jest wymagane"
    ok = false
  }
  return ok
}

async function onSubmit() {
  error.value = null
  if (!validate()) return
  loading.value = true
  try {
    await auth.login(form)
    const redirect = (route.query.redirect as string) || "/rooms"
    router.replace(redirect.startsWith("/") ? redirect : "/rooms")
  } catch (e: unknown) {
    const err = e as { message?: string }
    error.value = err?.message ?? "Logowanie nie powiodło się"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login">
    <div class="login-card">
      <img src="/logo.png" alt="MeetSpace Plus" class="login-logo" />
      <h1 class="login-title">MeetSpace Plus</h1>
      <p class="login-subtitle">Zaloguj się do systemu rezerwacji sal</p>

      <form class="login-form" @submit.prevent="onSubmit">
        <BaseInput
          v-model="form.email"
          type="email"
          label="E-mail"
          name="email"
          placeholder="user@example.com"
          :error="emailError ?? undefined"
        />
        <BaseInput
          v-model="form.password"
          type="password"
          label="Hasło"
          name="password"
          placeholder="••••••••"
          :error="passwordError ?? undefined"
        />
        <p v-if="error" class="login-form-error">{{ error }}</p>
        <BaseButton type="submit" :disabled="loading" block>
          {{ loading ? "Logowanie…" : "Zaloguj" }}
        </BaseButton>
      </form>

      <p class="login-link">
        Nie masz konta?
        <router-link to="/register">Zarejestruj się</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background: var(--color-bg-alt);
}

.login-card {
  width: 100%;
  max-width: 24rem;
  padding: var(--space-8);
  background: var(--color-bg);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
}

.login-logo {
  display: block;
  height: 5rem;
  width: auto;
  margin: 0 auto var(--space-4);
  object-fit: contain;
}

.login-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  text-align: center;
  margin-bottom: var(--space-2);
}

.login-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  text-align: center;
  margin-bottom: var(--space-6);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.login-form-error {
  font-size: var(--text-sm);
  color: var(--color-danger);
  margin: 0;
}

.login-link {
  font-size: var(--text-sm);
  text-align: center;
  margin-top: var(--space-4);
  color: var(--color-text-muted);
}

.login-link a {
  color: var(--color-primary);
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>

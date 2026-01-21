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
const passwordConfirmError = ref<string | null>(null)

const form = reactive({
  email: "",
  password: "",
  password_confirm: "",
  first_name: "",
  last_name: "",
})

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate(): boolean {
  emailError.value = null
  passwordError.value = null
  passwordConfirmError.value = null
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
  } else if (form.password.length < 8) {
    passwordError.value = "Hasło musi mieć co najmniej 8 znaków"
    ok = false
  }

  if (!form.password_confirm) {
    passwordConfirmError.value = "Potwierdzenie hasła jest wymagane"
    ok = false
  } else if (form.password !== form.password_confirm) {
    passwordConfirmError.value = "Hasła nie są zgodne"
    ok = false
  }

  return ok
}

async function onSubmit() {
  error.value = null
  if (!validate()) return
  loading.value = true
  try {
    await auth.register(form)
    const redirect = (route.query.redirect as string) || "/rooms"
    router.replace(redirect.startsWith("/") ? redirect : "/rooms")
  } catch (e: unknown) {
    const err = e as { message?: string }
    error.value = err?.message ?? "Rejestracja nie powiodła się"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register">
    <div class="register-card">
      <h1 class="register-title">MeetSpace Plus</h1>
      <p class="register-subtitle">Utwórz nowe konto</p>

      <form class="register-form" @submit.prevent="onSubmit">
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
        <BaseInput
          v-model="form.password_confirm"
          type="password"
          label="Potwierdź hasło"
          name="password_confirm"
          placeholder="••••••••"
          :error="passwordConfirmError ?? undefined"
        />
        <BaseInput
          v-model="form.first_name"
          type="text"
          label="Imię (opcjonalne)"
          name="first_name"
          placeholder="Jan"
        />
        <BaseInput
          v-model="form.last_name"
          type="text"
          label="Nazwisko (opcjonalne)"
          name="last_name"
          placeholder="Kowalski"
        />
        <p v-if="error" class="register-form-error">{{ error }}</p>
        <BaseButton type="submit" :disabled="loading" block>
          {{ loading ? "Rejestracja…" : "Zarejestruj się" }}
        </BaseButton>
      </form>

      <p class="register-link">
        Masz już konto?
        <router-link to="/login">Zaloguj się</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background: var(--color-bg-alt);
}

.register-card {
  width: 100%;
  max-width: 24rem;
  padding: var(--space-8);
  background: var(--color-bg);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
}

.register-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  text-align: center;
  margin-bottom: var(--space-2);
}

.register-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  text-align: center;
  margin-bottom: var(--space-6);
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.register-form-error {
  font-size: var(--text-sm);
  color: var(--color-danger);
  margin: 0;
}

.register-link {
  font-size: var(--text-sm);
  text-align: center;
  margin-top: var(--space-4);
  color: var(--color-text-muted);
}

.register-link a {
  color: var(--color-primary);
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>

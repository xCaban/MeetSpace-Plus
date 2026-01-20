<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue"
import { useRoomsStore } from "@/stores/rooms"
import { useReservationsStore } from "@/stores/reservations"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseInput from "@/components/base/BaseInput.vue"
import BaseSelect from "@/components/base/BaseSelect.vue"
import type { SelectOption } from "@/components/base/BaseSelect.vue"

const props = withDefaults(
  defineProps<{ initialRoomId?: number }>(),
  { initialRoomId: undefined }
)
const emit = defineEmits<{ created: []; cancel: [] }>()

const rooms = useRoomsStore()
const reservations = useReservationsStore()

const formError = ref<string | null>(null)
const form = reactive({
  room_id: "" as number | "",
  start_at: "",
  end_at: "",
})

const roomOptions = computed<SelectOption[]>(() =>
  rooms.list.map((r) => ({ value: r.id, label: `${r.name} (${r.location || "—"})` }))
)

onMounted(() => {
  if (props.initialRoomId != null) form.room_id = props.initialRoomId
  if (rooms.list.length === 0) rooms.fetchList()
})

async function onSubmit() {
  formError.value = null
  const rid = form.room_id
  const start = form.start_at
  const end = form.end_at

  if (rid === "" || !start || !end) {
    formError.value = "Wypełnij wszystkie pola."
    return
  }
  const startD = new Date(start)
  const endD = new Date(end)
  if (startD >= endD) {
    formError.value = "Data zakończenia musi być późniejsza niż data rozpoczęcia."
    return
  }

  try {
    await reservations.create({
      room_id: rid as number,
      start_at: startD.toISOString(),
      end_at: endD.toISOString(),
    })
    form.room_id = ""
    form.start_at = ""
    form.end_at = ""
    emit("created")
  } catch (e: unknown) {
    const err = e as { message?: string; status?: number }
    formError.value =
      err?.message ??
      (err?.status === 409 ? "Kolizja: wybrany termin koliduje z inną rezerwacją." : "Błąd tworzenia rezerwacji.")
  }
}

function onCancel() {
  formError.value = null
  form.room_id = ""
  form.start_at = ""
  form.end_at = ""
  emit("cancel")
}
</script>

<template>
  <form class="form" @submit.prevent="onSubmit">
    <h2 class="form-title">Nowa rezerwacja</h2>

    <p v-if="formError" class="form-error" role="alert">
      {{ formError }}
    </p>

    <BaseSelect
      v-model="form.room_id"
      :options="roomOptions"
      label="Sala"
      name="room_id"
      placeholder="— Wybierz salę —"
    />
    <BaseInput
      v-model="form.start_at"
      type="datetime-local"
      label="Od"
      name="start_at"
    />
    <BaseInput
      v-model="form.end_at"
      type="datetime-local"
      label="Do"
      name="end_at"
    />

    <div class="form-actions">
      <BaseButton type="submit" :disabled="reservations.loading">
        Zarezerwuj
      </BaseButton>
      <BaseButton type="button" variant="outline" @click="onCancel">
        Anuluj
      </BaseButton>
    </div>
  </form>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
  background: var(--color-bg-alt);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.form-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
}

.form-error {
  font-size: var(--text-sm);
  color: var(--color-danger);
}

.form-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}
</style>

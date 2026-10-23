<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">My Profile</div>

    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner color="primary" size="40px" />
    </div>

    <q-card v-else bordered style="max-width: 520px">
      <q-form @submit="save">
        <q-card-section class="q-gutter-md">
          <q-input :model-value="user.username" label="Username" filled readonly />
          <q-input :model-value="auth.roleName" label="Role" filled readonly />
          <q-input v-model="form.first_name" :rules="[required]" lazy-rules label="First Name" filled />
          <q-input v-model="form.middle_name" label="Middle Name" filled />
          <q-input v-model="form.last_name" :rules="[required]" lazy-rules label="Last Name" filled />
          <q-input v-model="form.email" :rules="[optionalEmail]" lazy-rules label="Email" filled />
          <q-input v-model="form.mobile_number" label="Mobile Number" filled />
          <q-input v-model="form.date_of_birth" :rules="[optionalDate]" lazy-rules label="Date of Birth" filled hint="YYYY-MM-DD" />
          <q-input
            v-model="form.password" :rules="[required]" lazy-rules
            label="Password"
            type="password"
            filled
            hint="Required to save: re-enter your current password or set a new one"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Reset" @click="loadProfile" />
          <q-btn color="primary" label="Save" type="submit" :loading="saving" />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'
import { errorMessage } from '@/utils/notify-error'
import { required, optionalDate, optionalEmail } from '@/utils/validation'

const $q = useQuasar()
const auth = useAuthStore()

const loading = ref(true)
const saving = ref(false)
const user = ref({})
const form = ref({})

async function loadProfile () {
  loading.value = true
  try {
    const { data } = await api.get(`/users/${auth.userId}`)
    user.value = data
    form.value = {
      email: data.email,
      mobile_number: data.mobile_number,
      first_name: data.first_name,
      middle_name: data.middle_name,
      last_name: data.last_name,
      date_of_birth: data.date_of_birth,
      password: '',
    }
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load profile') })
  } finally {
    loading.value = false
  }
}

async function save () {
  saving.value = true
  try {
    // PUT /users/{id} replaces the whole record, so send every field,
    // keeping the ones a user can't change themselves (username, role, status).
    const { data } = await api.put(`/users/${auth.userId}`, {
      ...form.value,
      username: user.value.username,
      role_id: user.value.role_id,
      account_status: user.value.account_status,
    })
    user.value = data
    form.value.password = ''
    auth.firstName = data.first_name
    auth.lastName = data.last_name
    auth.persist()
    $q.notify({ type: 'positive', message: 'Profile saved' })
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

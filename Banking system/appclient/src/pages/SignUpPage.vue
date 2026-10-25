<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="signup-page">
        <section class="signup-panel">
          <div class="signup-brand">
            <div class="signup-brand__mark"><q-icon name="account_balance" size="22px" /></div>
            <span>{{ BANK_NAME }}</span>
          </div>

          <h1>Create your account</h1>
          <p class="signup-lead">Sign up as a customer. A bank staff member opens your savings or checking account for you.</p>

          <q-form class="signup-fields" @submit="onSubmit">
            <div class="row q-col-gutter-sm">
              <div class="col-12 col-sm-6">
                <q-input v-model="form.first_name" label="First Name" outlined autocomplete="given-name" :rules="[required]" lazy-rules />
              </div>
              <div class="col-12 col-sm-6">
                <q-input v-model="form.last_name" label="Last Name" outlined autocomplete="family-name" :rules="[required]" lazy-rules />
              </div>
            </div>
            <q-input
              v-model="form.username" label="Username" outlined autocomplete="username"
              :rules="[required, usernameRule]" lazy-rules
              hint="Letters, numbers, dots, dashes or underscores"
            />
            <q-input v-model="form.email" label="Email (optional)" type="email" outlined autocomplete="email" :rules="[optionalEmail]" lazy-rules />
            <q-input v-model="form.mobile_number" label="Mobile Number (optional)" type="tel" outlined autocomplete="tel" />
            <q-input
              v-model="form.password" label="Password" outlined autocomplete="new-password"
              :type="showPassword ? 'text' : 'password'" :rules="[password]" lazy-rules
            >
              <template #append>
                <q-btn
                  flat dense round
                  :icon="showPassword ? 'visibility_off' : 'visibility'"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  @click="showPassword = !showPassword"
                />
              </template>
            </q-input>
            <q-input
              v-model="confirm" label="Confirm Password" outlined autocomplete="new-password"
              :type="showPassword ? 'text' : 'password'" :rules="[(val) => val === form.password || 'Passwords do not match']" lazy-rules
            />

            <q-banner v-if="errorText" dense rounded class="signup-error" role="alert">
              <template #avatar><q-icon name="error_outline" /></template>
              {{ errorText }}
            </q-banner>

            <q-btn type="submit" label="Create account" color="primary" size="lg" class="full-width signup-submit" :loading="loading" unelevated />
          </q-form>

          <p class="signup-switch">
            Already have an account?
            <router-link to="/login">Sign in</router-link>
          </p>
        </section>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'
import { errorMessage } from '@/utils/notify-error'
import { required, optionalEmail, password } from '@/utils/validation'

// Same name as on the login page.
const BANK_NAME = 'Tipon'

const $q = useQuasar()
const auth = useAuthStore()
const router = useRouter()

const form = ref({ first_name: '', last_name: '', username: '', email: '', mobile_number: '', password: '' })
const confirm = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorText = ref('')

// Same rule as the backend (RegisterIn in appserver/app/schemas/auth.py).
const usernameRule = (val) => /^[A-Za-z0-9._-]{3,100}$/.test(val || '') || 'At least 3 letters, numbers, dots, dashes or underscores'

async function onSubmit () {
  loading.value = true
  errorText.value = ''
  try {
    // Empty optional fields go as null.
    await api.post('/auth/register', {
      ...form.value,
      username: form.value.username.trim(),
      email: form.value.email || null,
      mobile_number: form.value.mobile_number || null,
    })
    // Signed up: log straight in (a CUSTOMER, so this works in the Android app too).
    await auth.login(form.value.username.trim(), form.value.password)
    $q.notify({ type: 'positive', message: `Welcome to ${BANK_NAME}, ${auth.firstName}!` })
    router.push('/')
  } catch (err) {
    errorText.value = errorMessage(err, 'Sign-up failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Tipon card on the sage background, like the design's sign-in panel. */
.signup-page {
  min-height: 100vh;
  max-width: none;
  display: grid;
  place-items: center;
  padding: 24px 16px !important;
  background: var(--bank-bg);
}

.signup-panel {
  width: 100%;
  max-width: 460px;
  padding: 1.6rem 1.4rem;
  background: var(--bank-surface);
  border: 1.5px solid var(--bank-border);
  border-radius: var(--bank-radius);
}

.signup-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--tipon-display);
  font-weight: 800;
  font-size: 1.3rem;
  letter-spacing: -0.02em;
  margin-bottom: 1rem;
}

.signup-brand__mark {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--tipon-ink);
  background: var(--tipon-mango);
}

.signup-panel h1 {
  font-family: var(--tipon-display);
  font-size: 1.9rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.1;
  margin: 0;
}

.signup-lead {
  margin: 0.5rem 0 1.2rem;
  color: var(--bank-muted);
}

.signup-fields {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.signup-submit {
  margin-top: 8px;
  height: 50px;
}

.signup-error {
  background: var(--tipon-bad-tint);
  color: var(--bank-debit);
  border: 1.5px solid var(--bank-debit);
}

.signup-switch {
  margin: 1rem 0 0;
  text-align: center;
  color: var(--bank-muted);
}

.signup-switch a {
  color: var(--tipon-sea);
  font-weight: 600;
}
</style>

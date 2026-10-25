<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="login-page">
        <!-- Brand panel (Tipon style: ink panel, mango accents, water band) -->
        <section class="login-hero bank-hero" aria-hidden="true">
          <div class="login-hero__brand">
            <div class="login-hero__mark"><q-icon name="account_balance" size="24px" /></div>
            <span>{{ BANK_NAME }}</span>
          </div>

          <div class="login-hero__copy">
            <h1>Savings you can see, share and trust.</h1>
            <p>Manage accounts, deposits, transfers and records in one secure place.</p>
          </div>

          <div class="login-card">
            <div class="login-card__water" />
            <div class="row items-center justify-between">
              <span class="bank-eyebrow">Savings Account</span>
              <q-icon name="contactless" size="22px" />
            </div>
            <div class="login-card__chip" />
            <div class="login-card__number">•••• •••• •••• 2026</div>
            <div class="row justify-between items-end">
              <div>
                <div class="login-card__label">Available balance</div>
                <div class="login-card__amount bank-amount">₱ ••••••</div>
              </div>
              <span class="login-card__brand">{{ BANK_NAME.toUpperCase() }}</span>
            </div>
          </div>

          <ul class="login-hero__points">
            <li><q-icon name="verified_user" /> Encrypted, signed sessions</li>
            <li><q-icon name="history" /> Every change recorded in the audit log</li>
            <li><q-icon name="menu_book" /> Balances always match the ledger</li>
          </ul>
        </section>

        <!-- Sign-in form -->
        <section class="login-form-wrap">
          <div class="login-form">
            <div class="login-form__mobile-brand lt-md">
              <div class="login-hero__mark"><q-icon name="account_balance" size="22px" /></div>
              <span>{{ BANK_NAME }}</span>
            </div>

            <h2>Welcome back</h2>
            <p class="login-form__lead">Sign in to your account to continue.</p>

            <q-form class="login-fields" @submit="onSubmit">
              <q-input
                v-model="username"
                label="Username"
                outlined
                autofocus
                autocomplete="username"
                :rules="[(val) => !!val || 'Username is required']"
              >
                <template #prepend><q-icon name="person_outline" /></template>
              </q-input>
              <q-input
                v-model="password"
                label="Password"
                outlined
                autocomplete="current-password"
                :type="showPassword ? 'text' : 'password'"
                :rules="[(val) => !!val || 'Password is required']"
              >
                <template #prepend><q-icon name="lock_outline" /></template>
                <template #append>
                  <q-btn
                    flat
                    dense
                    round
                    :icon="showPassword ? 'visibility_off' : 'visibility'"
                    :aria-label="showPassword ? 'Hide password' : 'Show password'"
                    @click="showPassword = !showPassword"
                  />
                </template>
              </q-input>

              <q-banner v-if="errorMessage" dense rounded class="login-error" role="alert">
                <template #avatar><q-icon name="error_outline" /></template>
                {{ errorMessage }}
              </q-banner>

              <q-btn
                type="submit"
                label="Sign in"
                color="primary"
                size="lg"
                class="full-width login-submit"
                :loading="loading"
                unelevated
              />
            </q-form>

            <p class="login-form__hint">Five wrong passwords in a row lock sign-in for 15 minutes.</p>
            <div class="login-form__secure">
              <q-icon name="lock" size="16px" />
              Your connection to {{ BANK_NAME }} is protected.
            </div>
          </div>
        </section>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'

// The bank's name, shown on this page. Change it here (and in MainLayout.vue).
const BANK_NAME = 'Tipon'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

const auth = useAuthStore()
const router = useRouter()

async function onSubmit () {
  loading.value = true
  errorMessage.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    if (err.response) {
      // Backend rejected the request (e.g. wrong credentials on /auth/login)
      errorMessage.value = err.response.data?.detail || `Login failed (HTTP ${err.response.status}).`
    } else if (err.request) {
      // Request never got a response at all: wrong API base URL, backend down, or CORS block
      errorMessage.value = 'Could not reach the backend API. Check that it is running and that the API base URL in .env is correct.'
    } else {
      // Something failed in our own post-login logic (e.g. no matching user record)
      errorMessage.value = err.message || 'Login failed for an unknown reason.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
  min-height: 100vh;
  max-width: none;
  padding: 0 !important;
  background: var(--bank-bg);
}

/* --- Brand panel (Tipon ink, with the water band from .bank-hero) --- */
.login-hero {
  margin: 16px;
  padding: 40px 48px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.login-hero__brand,
.login-form__mobile-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--tipon-display);
  font-weight: 800;
  font-size: 1.5rem;
  letter-spacing: -0.02em;
}

.login-hero__mark {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--tipon-ink);
  background: var(--tipon-mango);
}

.login-hero__copy h1 {
  font-family: var(--tipon-display);
  font-size: clamp(2rem, 3.2vw, 2.9rem);
  line-height: 1.05;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 24px 0 12px;
  max-width: 15ch;
}

.login-hero__copy p {
  font-size: 1.05rem;
  color: #C4D3CD;
  max-width: 42ch;
  margin: 0;
}

/* The card: a flat Tipon panel on the ink, part-filled with "water" like the
   pocket jars in the design. */
.login-card {
  position: relative;
  overflow: hidden;
  width: min(100%, 380px);
  aspect-ratio: 1.6;
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #F7FAF8;
  background: #1C2D4F;
  border: 1.5px solid rgba(196, 211, 205, 0.28);
  border-radius: var(--bank-radius);
}

.login-card > *:not(.login-card__water) {
  position: relative;
}

.login-card__water {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 38%;
  background: linear-gradient(var(--tipon-water), var(--tipon-sea));
  opacity: 0.55;
}

.login-card__chip {
  width: 44px;
  height: 32px;
  border-radius: 7px;
  background: var(--tipon-mango);
}

.login-card__number {
  font-size: 1.15rem;
  letter-spacing: 0.14em;
  font-variant-numeric: tabular-nums;
}

.login-card__label {
  font-size: 0.72rem;
  color: #E6EEF0;
}

.login-card__amount {
  font-size: 1.4rem;
}

.login-card__brand {
  font-family: var(--tipon-display);
  font-weight: 800;
  letter-spacing: 0.14em;
  font-size: 0.85rem;
  color: var(--tipon-mango);
}

.login-hero__points {
  list-style: none;
  padding: 0;
  margin: auto 0 0;
  display: grid;
  gap: 10px;
  color: #E6EEF0;
}

.login-hero__points li {
  display: flex;
  align-items: center;
  gap: 10px;
}

.login-hero__points .q-icon {
  color: var(--tipon-mango);
  font-size: 20px;
}

/* --- Form --- */
.login-form-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
}

.login-form {
  width: 100%;
  max-width: 400px;
}

.login-form h2 {
  font-family: var(--tipon-display);
  font-size: 2.1rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 6px;
  line-height: 1.1;
}

.login-form__lead {
  color: var(--bank-muted);
  margin: 0 0 28px;
}

.login-form__mobile-brand {
  margin-bottom: 28px;
  color: var(--bank-text);
}

.login-fields {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.login-submit {
  margin-top: 8px;
  height: 52px;
  font-size: 1rem;
}

.login-error {
  background: var(--tipon-bad-tint);
  color: var(--bank-debit);
  border: 1.5px solid var(--bank-debit);
}

.login-form__hint {
  margin: 1rem 0 0;
  color: var(--bank-muted);
  font-size: 0.85rem;
  text-align: center;
}

.login-form__secure {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--bank-muted);
  font-size: 0.85rem;
}

@media (max-width: 1023px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .login-hero {
    display: none;
  }
}
</style>

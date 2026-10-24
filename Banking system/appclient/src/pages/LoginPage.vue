<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="login-page">
        <!-- Brand panel -->
        <section class="login-hero bank-hero" aria-hidden="true">
          <div class="login-hero__brand">
            <div class="login-hero__mark"><q-icon name="account_balance" size="24px" /></div>
            <span>Mini Bank</span>
          </div>

          <div class="login-hero__copy">
            <h1>Banking you can trust, from anywhere.</h1>
            <p>Manage accounts, deposits, transfers and records in one secure place.</p>
          </div>

          <div class="login-card bank-glass">
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
              <span class="login-card__brand">MINI BANK</span>
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
              <span>Mini Bank</span>
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

            <div class="login-form__secure">
              <q-icon name="lock" size="16px" />
              Your connection to Mini Bank is protected.
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

/* --- Brand panel --- */
.login-hero {
  margin: 16px;
  padding: 40px 48px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  border-radius: 24px;
}

.login-hero__brand,
.login-form__mobile-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  font-size: 1.15rem;
}

.login-hero__mark {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--bank-navy-900);
  background: linear-gradient(135deg, var(--bank-gold-light), var(--bank-gold));
}

.login-hero__copy h1 {
  font-size: clamp(1.9rem, 3vw, 2.6rem);
  line-height: 1.15;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 24px 0 12px;
  max-width: 16ch;
}

.login-hero__copy p {
  font-size: 1.05rem;
  color: #CBD5E1;
  max-width: 42ch;
  margin: 0;
}

.login-card {
  width: min(100%, 380px);
  aspect-ratio: 1.6;
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 30px 60px rgba(2, 6, 23, 0.45);
}

.login-card__chip {
  width: 44px;
  height: 32px;
  border-radius: 7px;
  background: linear-gradient(135deg, #FDE68A, var(--bank-gold));
}

.login-card__number {
  font-size: 1.15rem;
  letter-spacing: 0.14em;
  font-variant-numeric: tabular-nums;
}

.login-card__label {
  font-size: 0.72rem;
  color: #CBD5E1;
}

.login-card__amount {
  font-size: 1.3rem;
}

.login-card__brand {
  font-weight: 700;
  letter-spacing: 0.18em;
  font-size: 0.8rem;
  color: var(--bank-gold-light);
}

.login-hero__points {
  list-style: none;
  padding: 0;
  margin: auto 0 0;
  display: grid;
  gap: 10px;
  color: #E2E8F0;
}

.login-hero__points li {
  display: flex;
  align-items: center;
  gap: 10px;
}

.login-hero__points .q-icon {
  color: var(--bank-gold-light);
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
  font-size: 1.9rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 6px;
  line-height: 1.2;
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
  background: #FEF2F2;
  color: var(--bank-debit);
  border: 1px solid #FECACA;
}

.login-form__secure {
  margin-top: 24px;
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

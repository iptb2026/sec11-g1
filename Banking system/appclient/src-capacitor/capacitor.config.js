const { defineCapacitorConfig } = require('@quasar/app-vite/capacitor');

module.exports = defineCapacitorConfig({
  appId: 'com.tipon.bank',
  appName: 'Tipon Bank',
  server: {
    // The backend is plain http (127.0.0.1:8000 through `adb reverse`, or a
    // LAN address), so the app must load over http too: from Capacitor's
    // default https origin, Android blocks those calls as mixed content.
    androidScheme: 'http',
    cleartext: true
  }
});

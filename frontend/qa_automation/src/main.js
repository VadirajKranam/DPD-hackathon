import './assets/main.css'
import 'vuetify/styles'
// Imports
import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
// Import your root component
import App from './App.vue'
// Create Vuetify instance
const vuetify = createVuetify({
  components,
  directives,
})
// Create and mount the app
createApp(App)
  .use(vuetify)
  .mount('#app')
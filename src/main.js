import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router' // Import the router instance
import 'vue-toastification/dist/index.css'; // Import the CSS FIRST
import Toast from 'vue-toastification'; // Import vue-toastification

const app = createApp(App);

app.use(router); // Use the router
app.use(Toast); // Use vue-toastification

app.mount('#app');

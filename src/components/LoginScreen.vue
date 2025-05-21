<template>
  <div class="login-container">
    <div class="login-box">
      <header class="app-header">
        <!-- Placeholder for Logo -->
        <img src="/public/vite.svg" alt="App Logo" class="app-logo">
        <h1>Surgery Scheduling System</h1>
      </header>
      <h2 class="form-title">{{ isRegistering ? 'Create Account' : 'Login' }}</h2>

      <!-- Login Form -->
      <form v-if="!isRegistering" class="login-form" @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Username</label>
          <input type="text" id="username" name="username" v-model="username" required>
        </div>
        <div class="input-group">
          <label for="password">Password</label>
          <input type="password" id="password" name="password" v-model="password" required>
          <!-- Password visibility toggle could be added later -->
        </div>
        <button type="submit" class="login-button">Login</button>
        <p class="toggle-form-link">
          Don't have an account? <a href="#" @click.prevent="toggleForm">Create one</a>
        </p>
        <!-- Forgot password link only if FR-AUTH-005 is implemented, included for now -->
        <a href="#" class="forgot-password-link">Forgot Password?</a>
      </form>

      <!-- Registration Form -->
      <form v-if="isRegistering" class="login-form" @submit.prevent="handleRegister">
        <div class="input-group">
          <label for="new-username">Username</label>
          <input type="text" id="new-username" v-model="newUsername" required>
        </div>
        <div class="input-group">
          <label for="new-password">Password</label>
          <input type="password" id="new-password" v-model="newPassword" required>
        </div>
        <div class="input-group">
          <label for="confirm-password">Confirm Password</label>
          <input type="password" id="confirm-password" v-model="confirmPassword" required>
        </div>
        <button type="submit" class="login-button">Create Account</button>
        <p class="toggle-form-link">
          Already have an account? <a href="#" @click.prevent="toggleForm">Login</a>
        </p>
      </form>

      <p v-if="loginError && !isRegistering" class="error-message">{{ loginError }}</p>
      <p v-if="registrationError && isRegistering" class="error-message">{{ registrationError }}</p>
      <p v-if="registrationSuccess && !isRegistering" class="success-message">{{ registrationSuccess }}</p>
      <!-- Optional Footer -->
      <footer class="app-footer">
        <p>&copy; 2023 Your Organization. All rights reserved.</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router'; // Import useRouter
import { setAuthenticated } from '../router'; // Import setAuthenticated

const router = useRouter(); // Get router instance

const username = ref('');
const password = ref('');
const loginError = ref('');
const registrationError = ref('');
const registrationSuccess = ref('');

const isRegistering = ref(false);
const newUsername = ref('');
const newPassword = ref('');
const confirmPassword = ref('');

// Simulated user store (using localStorage)
const getUsers = () => {
  const users = localStorage.getItem('users');
  return users ? JSON.parse(users) : [];
};

const saveUsers = (users) => {
  localStorage.setItem('users', JSON.stringify(users));
};

const handleLogin = () => {
  loginError.value = ''; // Clear previous errors

  if (!username.value || !password.value) {
    loginError.value = 'Please enter both username and password.';
    return;
  }

  // Placeholder login logic
  console.log('Attempting login with:', username.value, password.value);

  // --- Simulated Login Logic ---
  // In a real app, you would send a request to your backend here.
  // On successful response:

  // --- Simulated Login Logic ---
  const users = getUsers();
  const user = users.find(u => u.username === username.value && u.password === password.value);

  if (user) {
    setAuthenticated(true);
    router.push({ name: 'Dashboard' });
  } else {
    loginError.value = 'Invalid username or password.';
    setAuthenticated(false);
  }
  // ------------------------------
};

const handleRegister = () => {
  loginError.value = '';
  registrationError.value = '';
  registrationSuccess.value = '';

  if (!newUsername.value || !newPassword.value || !confirmPassword.value) {
    registrationError.value = 'Please fill in all fields.';
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    registrationError.value = 'Passwords do not match.';
    return;
  }

  const users = getUsers();
  if (users.find(u => u.username === newUsername.value)) {
    registrationError.value = 'Username already exists.';
    return;
  }

  users.push({ username: newUsername.value, password: newPassword.value });
  saveUsers(users);

  registrationSuccess.value = 'Account created successfully! Please log in.';
  // Reset registration form and switch to login
  newUsername.value = '';
  newPassword.value = '';
  confirmPassword.value = '';
  isRegistering.value = false;
};

const toggleForm = () => {
  isRegistering.value = !isRegistering.value;
  loginError.value = '';
  registrationError.value = '';
  registrationSuccess.value = '';
  // Clear input fields when toggling
  username.value = '';
  password.value = '';
  newUsername.value = '';
  newPassword.value = '';
  confirmPassword.value = '';
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--color-background); /* Use global background */
  color: var(--color-very-dark-gray); /* Use global text color */
}

.login-box {
  background-color: var(--color-white); /* White box */
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); /* Slightly stronger shadow */
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.app-header {
  margin-bottom: 25px; /* Increased margin */
}

.app-logo {
  height: 70px; /* Slightly larger logo */
  margin-bottom: 15px;
}

.app-header h1 {
  font-size: 1.9em; /* Adjusted heading size */
  color: var(--color-very-dark-gray);
  margin: 0;
}

.form-title {
  font-size: 1.6em; /* Adjusted title size */
  color: var(--color-very-dark-gray);
  margin-bottom: 30px;
}

.login-form {
  text-align: left;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600; /* Semi-bold labels */
  color: var(--color-dark-gray); /* Slightly lighter label color */
}

.input-group input[type="text"],
.input-group input[type="password"] {
  width: 100%;
  padding: 12px; /* More padding */
  border: 1px solid var(--color-gray);
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 1em;
  color: var(--color-very-dark-gray);
}

.login-button {
  width: 100%;
  padding: 12px; /* Consistent padding with inputs */
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: 4px;
  font-size: 1.1em;
  cursor: pointer;
  transition: background-color 0.25s ease;
}

.login-button:hover {
  background-color: var(--color-primary-dark);
}

.forgot-password-link {
  display: block;
  margin-top: 15px;
  font-size: 0.9em;
  color: var(--color-primary);
  text-decoration: none;
}

.forgot-password-link:hover {
  text-decoration: underline;
}

.toggle-form-link {
  text-align: center;
  margin-top: 15px;
  font-size: 0.9em;
}

.toggle-form-link a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: bold;
}

.toggle-form-link a:hover {
  text-decoration: underline;
}

.app-footer {
  margin-top: 30px;
  font-size: 0.8em;
  color: var(--color-dark-gray); /* Footer text color */
}

.error-message {
  color: var(--color-danger); /* Red color for error messages */
  margin-top: 15px;
  font-size: 0.9em;
}

.success-message {
  color: var(--color-success, #28a745); /* Green color for success messages */
  margin-top: 15px;
  font-size: 0.9em;
  text-align: center;
}
</style>

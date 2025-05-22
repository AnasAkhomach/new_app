// src/stores/authStore.js
import { defineStore } from 'pinia';
import router from '@/router'; // Import the router instance

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: localStorage.getItem('isAuthenticated') === 'true', // Load initial state from local storage
    user: JSON.parse(localStorage.getItem('user') || 'null'), // Load user info from local storage
    isLoading: false,
    error: null,
  }),
  getters: {
    // isAuthenticated: (state) => state.isAuthenticated, // Can be a simple state property
    // user: (state) => state.user,
  },
  actions: {
    async login(username, password) {
      this.isLoading = true;
      this.error = null;

      // --- Simulate API Call for Login ---
      console.log('Auth Store: Simulating login attempt...');
      try {
        // In a real app, send login request to backend:
        // const response = await api.post('/auth/login', { username, password });
        // const userData = response.data.user;
        // const authToken = response.data.token;

        // Simulate a successful login after a delay
        await new Promise(resolve => setTimeout(resolve, 500));

         // Simulate checking credentials against local storage (replace with actual backend validation)
         const users = JSON.parse(localStorage.getItem('users' ) || '[]'); // Using the temporary user storage
         const user = users.find(u => u.username === username && u.password === password);

        if (user) {
           console.log('Auth Store: Simulated login successful.');
          // Update state
          this.isAuthenticated = true;
           // Simulate storing user info and token (replace with actual token handling)
           this.user = { username: user.username, role: 'Scheduler' }; // Assign a role for demo
           localStorage.setItem('isAuthenticated', 'true');
           localStorage.setItem('user', JSON.stringify(this.user));
           // localStorage.setItem('authToken', authToken);

          // Redirect to dashboard
          router.push({ name: 'Dashboard' }); // Use router instance imported above

        } else {
           console.warn('Auth Store: Simulated login failed: Invalid credentials.');
          this.error = 'Invalid username or password.';
           this.isAuthenticated = false;
           this.user = null;
           localStorage.setItem('isAuthenticated', 'false');
           localStorage.removeItem('user');
           // localStorage.removeItem('authToken');
        }

      } catch (error) {
         console.error('Auth Store: Simulated login error:', error);
        this.error = 'An error occurred during login.';
         this.isAuthenticated = false;
         this.user = null;
         localStorage.setItem('isAuthenticated', 'false');
         localStorage.removeItem('user');
         // localStorage.removeItem('authToken');
      } finally {
        this.isLoading = false;
      }
    },

    async register(username, password) {
        this.isLoading = true;
        this.error = null;
        let success = false; // Flag to indicate registration success

        // --- Simulate API Call for Registration ---
        console.log('Auth Store: Simulating registration attempt...');
        try {
            // In a real app, send registration request to backend:
            // const response = await api.post('/auth/register', { username, password });
            // Assuming backend handles checking for existing username

            // Simulate a registration attempt after a delay
            await new Promise(resolve => setTimeout(resolve, 500));

             // Simulate checking if username exists and saving to local storage
             const users = JSON.parse(localStorage.getItem('users' ) || '[]');
             if (users.find(u => u.username === username)) {
                console.warn('Auth Store: Simulated registration failed: Username exists.');
                this.error = 'Username already exists.';
             } else {
                users.push({ username: username, password: password });
                localStorage.setItem('users', JSON.stringify(users));
                console.log('Auth Store: Simulated registration successful.');
                // Don't set isAuthenticated or user here, user needs to log in after registering
                success = true; // Indicate success
             }

        } catch (error) {
             console.error('Auth Store: Simulated registration error:', error);
             this.error = 'An error occurred during registration.';
        } finally {
            this.isLoading = false;
        }
        return success; // Return success status to the component
    },

    logout() {
       console.log('Auth Store: Logging out.');
      // Clear auth state
      this.isAuthenticated = false;
      this.user = null;
      this.error = null; // Clear any lingering errors
      // Remove auth data from local storage
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('user');
      // localStorage.removeItem('authToken'); // Clear token if used

      // Redirect to login page
      router.push({ name: 'Login' }); // Use router instance
    }
  }
});

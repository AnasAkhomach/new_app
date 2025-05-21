import { createRouter, createWebHistory } from 'vue-router';
import { ref } from 'vue';

import LoginScreen from '../components/LoginScreen.vue';
import AppLayout from '../components/AppLayout.vue'; // Import the layout component
import DashboardScreen from '../components/DashboardScreen.vue';
// Import other placeholder components
import SchedulingScreen from '../components/SchedulingScreen.vue';
import ResourceManagementScreen from '../components/ResourceManagementScreen.vue';
import SDSTDataManagementScreen from '../components/SDSTDataManagementScreen.vue';
import ReportingAnalyticsScreen from '../components/ReportingAnalyticsScreen.vue';
import NotificationsScreen from '../components/NotificationsScreen.vue';
import AdministrationScreen from '../components/AdministrationScreen.vue';
import MyProfileSettingsScreen from '../components/MyProfileSettingsScreen.vue';
import HelpDocumentationScreen from '../components/HelpDocumentationScreen.vue';
import NotFound from '../components/NotFound.vue'; // Import the new NotFound component

// Simple authentication state (for simulation)
const isAuthenticated = ref(false);

// Function to set authentication status
const setAuthenticated = (status) => {
  isAuthenticated.value = status;
};

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginScreen,
  },
  {
    path: '/', // Use a parent route for authenticated sections
    component: AppLayout, // Use the layout component
    meta: { requiresAuth: true }, // Apply auth guard to this parent route
    children: [
        {
            path: '/dashboard',
            name: 'Dashboard',
            component: DashboardScreen,
        },
        {
            path: '/scheduling',
            name: 'Scheduling',
            component: SchedulingScreen,
        },
        {
            path: '/resource-management',
            name: 'ResourceManagement',
            component: ResourceManagementScreen,
        },
        {
            path: '/sdst-data-management',
            name: 'SDSTDataManagement',
            component: SDSTDataManagementScreen,
        },
        {
            path: '/reporting-analytics',
            name: 'ReportingAnalytics',
            component: ReportingAnalyticsScreen,
        },
        {
            path: '/notifications',
            name: 'Notifications',
            component: NotificationsScreen,
        },
        {
            path: '/administration',
            name: 'Administration',
            component: AdministrationScreen,
        },
        {
            path: '/my-profile-settings',
            name: 'MyProfileSettings',
            component: MyProfileSettingsScreen,
        },
        {
            path: '/help-documentation',
            name: 'HelpDocumentation',
            component: HelpDocumentationScreen,
        },
         // Add a redirect for the base authenticated path if needed
        {
            path: '',
            redirect: '/dashboard' // Redirect / to /dashboard when authenticated
        }
    ]
  },
  // Add a catch-all route for 404s if needed
  {
    path: '/:pathMatch(.*)*', // Catch-all route
    name: 'NotFound',
    // Use the imported 404 component
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !isAuthenticated.value) {
    // User is not authenticated and route requires auth, redirect to login
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (to.name === 'Login' && isAuthenticated.value) {
    // If the user is authenticated and tries to go to login, redirect to dashboard
     next({ name: 'Dashboard' });
  }else {
    // Otherwise, allow navigation
    next();
  }
});

export default router;
export { setAuthenticated }; // Export the function to be used in LoginScreen

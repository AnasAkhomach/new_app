<template>
  <div :class="['app-layout', { 'sidebar-collapsed': isSidebarCollapsed }]">
    <header class="top-nav-bar">
      <div class="app-brand">
         <button @click="toggleSidebar" class="icon-button toggle-sidebar-button">
             <!-- Hamburger or arrow icon -->
             <span v-if="isSidebarCollapsed">&#x25BA;</span> <!-- Right arrow -->
             <span v-else>&#x25C4;</span> <!-- Left arrow -->
         </button>
        <!-- App Logo/Name -->
        <img src="/public/vite.svg" alt="App Logo" class="app-logo-small">
        <span v-if="!isSidebarCollapsed">Surgery Scheduler</span>
      </div>
      <div class="global-search">
        <!-- Global Search Bar -->
        <input type="text" placeholder="Search..." v-model="searchTerm" @input="handleSearch">
      </div>
      <div class="user-utilities">
        <!-- Notification Icon -->
        <button class="icon-button">🔔</button>
        <!-- User Profile Dropdown -->
        <div class="user-profile">
          <span>User Name</span>
          <!-- Dropdown icon/button here -->
        </div>
      </div>
    </header>

    <aside class="left-sidebar">
      <!-- Navigation Links -->
      <nav>
        <ul>
          <li><router-link to="/dashboard"><span v-if="!isSidebarCollapsed">Dashboard</span></router-link></li>
          <li><router-link to="/scheduling"><span v-if="!isSidebarCollapsed">Scheduling</span></router-link></li>
          <li><router-link to="/resource-management"><span v-if="!isSidebarCollapsed">Resource Management</span></router-link></li>
          <li><router-link to="/sdst-data-management"><span v-if="!isSidebarCollapsed">SDST Data Management</span></router-link></li>
          <li><router-link to="/reporting-analytics"><span v-if="!isSidebarCollapsed">Reporting & Analytics</span></router-link></li>
          <li><router-link to="/notifications"><span v-if="!isSidebarCollapsed">Notifications</span></router-link></li>
          <li><router-link to="/administration"><span v-if="!isSidebarCollapsed">Administration</span></router-link></li>
          <li><router-link to="/my-profile-settings"><span v-if="!isSidebarCollapsed">My Profile / Settings</span></router-link></li>
          <li><router-link to="/help-documentation"><span v-if="!isSidebarCollapsed">Help / Documentation</span></router-link></li>
          <li class="logout-item"><button @click="handleLogout" class="logout-button"><span v-if="!isSidebarCollapsed">Logout (Simulated)</span></button></li>
        </ul>
      </nav>
    </aside>

    <main class="main-content">
      <!-- Router View renders the specific page component -->
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'; // Import ref
import { useRouter } from 'vue-router';
import { setAuthenticated } from '../router'; // Import setAuthenticated

const router = useRouter();

const isSidebarCollapsed = ref(false); // State for sidebar collapse
const searchTerm = ref(''); // State for global search input

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const handleLogout = () => {
  setAuthenticated(false); // Set the global auth state to false
  router.push({ name: 'Login' }); // Redirect to login
};

const handleSearch = () => {
  // Placeholder for actual search logic
  console.log('Searching for:', searchTerm.value);
  // In a real app, this would trigger a search action, 
  // potentially navigating to a search results page or filtering data.
};

</script>

<style scoped>
.app-layout {
  display: grid;
  grid-template-columns: 240px 1fr; /* Default: Wider Sidebar */
  grid-template-rows: 60px 1fr; /* Top nav fixed height */
  height: 100vh; /* Full viewport height */
  background-color: var(--color-background);
  overflow: hidden; /* Prevent scrollbars on layout itself */
  transition: grid-template-columns 0.3s ease; /* Smooth transition for collapse */
}

.app-layout.sidebar-collapsed {
    grid-template-columns: 60px 1fr; /* Collapsed: Narrower Sidebar */
}

.top-nav-bar {
  grid-column: 1 / 3; /* Span across both columns */
  grid-row: 1;
  background-color: var(--color-white);
  padding: 0 20px; /* Horizontal padding */
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08); /* Softer shadow */
  z-index: 10; /* Ensure it's above other content */
  height: 60px; /* Match grid row height */
}

.app-brand {
  display: flex;
  align-items: center;
  font-size: 1.3em; /* Slightly larger font */
  font-weight: 600; /* Semi-bold */
  color: var(--color-very-dark-gray);
}

.toggle-sidebar-button {
    margin-right: 10px;
    font-size: 1em;
    padding: 5px; /* Adjust padding for button */
    background: none; /* No background */
    border: none;
    color: var(--color-dark-gray);
    cursor: pointer;
    transition: transform 0.3s ease; /* Transition for icon */
}

.app-logo-small {
    height: 35px; /* Slightly larger logo */
    margin-right: 12px;
    transition: margin-right 0.3s ease; /* Smooth transition */
}

.app-layout.sidebar-collapsed .app-logo-small {
     margin-right: 0; /* Remove margin when collapsed */
}

.global-search input[type="text"] {
    padding: 8px 15px; /* More horizontal padding */
    border: 1px solid var(--color-gray); /* Use gray from palette */
    border-radius: 20px; /* Pill shape */
    font-size: 0.9em;
    width: 250px; /* Adjust as needed */
    background-color: var(--color-light-gray); /* Light gray background for search */
    color: var(--color-very-dark-gray);
}

.user-utilities {
    display: flex;
    align-items: center;
}

.icon-button {
    background: none;
    border: none;
    font-size: 1.3em; /* Slightly larger icon */
    cursor: pointer;
    margin-right: 20px; /* More space */
    padding: 8px; /* Increased padding */
    color: var(--color-dark-gray); /* Icon color */
    border-radius: 4px;
    transition: background-color 0.2s ease;
}

.icon-button:hover {
    background-color: var(--color-light-gray);
}

.user-profile {
    display: flex;
    align-items: center;
    cursor: pointer; /* Indicate clickable */
}

.user-profile span {
    margin-right: 8px;
    color: var(--color-very-dark-gray);
    font-weight: 500;
}

/* Placeholder for a user icon */
.user-profile::after {
    content: '👤'; /* Example icon */
    font-size: 1.3em;
    color: var(--color-dark-gray);
}


.left-sidebar {
  grid-column: 1; /* First column */
  grid-row: 2; /* Second row */
  background-color: var(--color-white);
  padding: 20px 0; /* Vertical padding */
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.08); /* Softer shadow */
  overflow-y: auto; /* Add scrolling if content overflows */
  border-right: 1px solid var(--color-mid-light-gray); /* Subtle border */
  transition: width 0.3s ease; /* Transition for sidebar width */
}

.app-layout.sidebar-collapsed .left-sidebar {
    /* Grid column handles the width, just need to adjust padding/content */
    align-items: center; /* Center content when collapsed */
    padding: 20px 0; /* Adjust padding if needed */
}

.left-sidebar nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.left-sidebar nav li {
  margin-bottom: 0; /* Remove space between list items, padding on link handles spacing */
}

.left-sidebar nav a {
  display: flex; /* Use flex for alignment */
  align-items: center;
  padding: 12px 20px; /* Increased padding */
  color: var(--color-very-dark-gray); /* Default link color */
  text-decoration: none;
  transition: background-color 0.2s ease, color 0.2s ease, padding 0.3s ease; /* Add padding transition */
  font-size: 1.05em; /* Slightly larger font */
}

.app-layout.sidebar-collapsed .left-sidebar nav a {
    justify-content: center; /* Center content when collapsed */
    padding: 12px; /* Reduced padding for icon-only view */
}

.left-sidebar nav a:hover {
  background-color: var(--color-light-gray); /* Highlight on hover */
  color: var(--color-primary); /* Primary color on hover */
}

.left-sidebar nav .router-link-active {
    background-color: var(--color-primary); /* Active link color */
    color: var(--color-white); /* Active link text color */
    font-weight: 600; /* Semi-bold */
    border-left: 4px solid var(--color-primary-dark); /* Highlight active link */
    padding-left: 16px; /* Adjust padding due to border */
}

.app-layout.sidebar-collapsed .left-sidebar nav .router-link-active {
     padding-left: 12px; /* No border when collapsed, adjust padding */
     border-left: none; /* Remove border when collapsed */
}

/* Add spacing between link text and potential icon if added later */
.left-sidebar nav a span {
    margin-right: 10px; /* Space between text and icon */
}

.app-layout.sidebar-collapsed .left-sidebar nav a span {
    margin-right: 0; /* Remove margin when text is hidden */
}

.logout-item {
    margin-top: 30px; /* Space above logout button */
    text-align: center; /* Center button when collapsed */
}

.logout-button {
    display: block;
    width: calc(100% - 40px); /* Adjust width considering padding */
    margin: 0px auto; /* Center button */
    padding: 10px;
    background-color: var(--color-danger); /* Use danger color for logout */
    color: var(--color-white);
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    transition: background-color 0.2s ease;
}

.app-layout.sidebar-collapsed .logout-button {
    width: calc(100% - 24px); /* Adjust width for narrower sidebar padding */
    padding: 10px 5px; /* Adjust padding */
}

.logout-button:hover {
    background-color: #c82333; /* Darker red */
}

.main-content {
  grid-column: 2; /* Second column */
  grid-row: 2; /* Second row */
  padding: 20px; /* Padding inside main content area */
  overflow-y: auto; /* Add scrolling for main content */
}

/* Hide text content in sidebar when collapsed */
.app-layout.sidebar-collapsed .left-sidebar nav a span,
.app-layout.sidebar-collapsed .logout-button span {
    display: none; /* Hide text */
}

/* Adjust app brand text visibility */
.app-brand span {
    transition: opacity 0.3s ease;
}

.app-layout.sidebar-collapsed .app-brand span {
    opacity: 0; /* Hide text in app brand */
    width: 0; /* Collapse width */
    overflow: hidden; /* Prevent text overflow */
}

</style>

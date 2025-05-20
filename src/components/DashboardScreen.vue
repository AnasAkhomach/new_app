<template>
  <div class="dashboard-container">
    <h1>Dashboard</h1>

    <div v-if="isLoading" class="loading-message">
      Loading dashboard data...
    </div>

    <div v-if="!isLoading">
      <div class="dashboard-widgets">
        <!-- Quick Actions Widget -->
        <div class="widget quick-actions-widget">
          <h2>Quick Actions</h2>
          <div class="quick-action-buttons">
            <button @click="scheduleNewSurgery">Schedule New Elective Surgery</button>
            <button class="button-secondary" @click="addEmergencyCase">Add Emergency Case</button>
            <button @click="goToMasterSchedule">Go to Master Schedule</button>
            <button @click="manageResources">Manage Resources</button>
            <button class="button-secondary" @click="runOptimization">Run Optimization</button>
          </div>
        </div>

        <!-- Key Performance Indicators (KPIs) Widget -->
        <div class="widget kpis-widget">
          <h2>Key Performance Indicators</h2>
          <div class="kpi-list">
            <div class="kpi-item" @click="handleKpiClick('OR Utilization')">
              <span class="kpi-label">OR Utilization (Today):</span>
              <span class="kpi-value">{{ orUtilizationToday }}%</span>
            </div>
            <div class="kpi-item" @click="handleKpiClick('Avg. SDST')">
              <span class="kpi-label">Avg. SDST (Today):</span>
              <span class="kpi-value">{{ avgSdstToday }} min</span>
            </div>
            <div class="kpi-item" @click="handleKpiClick('Emergency Cases')">
              <span class="kpi-label">Emergency Cases (Today):</span>
              <span class="kpi-value">{{ emergencyCasesToday }}</span>
            </div>
            <div class="kpi-item" @click="handleKpiClick('Cancelled Surgeries')">
              <span class="kpi-label">Cancelled Surgeries (Today):</span>
              <span class="kpi-value">{{ cancelledSurgeriesToday }}</span>
            </div>
          </div>
          <!-- Placeholder for charts/visualizations -->
          <p><em>(Placeholder for KPI charts/visualizations)</em></p>
        </div>

        <!-- Today's OR Schedule Overview Widget -->
        <div class="widget schedule-overview-widget">
          <h2>Today's OR Schedule Overview</h2>
          <!-- Placeholder for compact timeline/Gantt view or simple list -->
          <ul v-if="todaySchedule.length > 0" class="schedule-list">
            <li v-for="surgery in todaySchedule" :key="surgery.id">{{ surgery.time }} - OR {{ surgery.or }}: {{ surgery.description }}</li>
          </ul>
          <p>Provides at-a-glance view of today's operations across all ORs.</p>
        </div>

        <!-- Critical Resource Alerts Widget -->
        <div class="widget alerts-widget">
          <h2>Critical Resource Alerts</h2>
          <ul>
            <li v-for="alert in criticalAlerts" :key="alert.id" class="alert-item" @click="handleAlertClick(alert)">{{ alert.message }}</li>
            <li v-if="criticalAlerts.length === 0" class="no-items">No critical alerts</li>
          </ul>
        </div>

        <!-- SDST Conflict Summary Widget -->
        <div class="widget sdst-conflicts-widget">
          <h2>SDST Conflict Summary</h2>
          <ul>
            <li v-for="conflict in sdstConflicts" :key="conflict.id" class="conflict-item" @click="handleConflictClick(conflict)">{{ conflict.message }}</li>
            <li v-if="sdstConflicts.length === 0" class="no-items">No SDST conflicts</li>
          </ul>
        </div>

        <!-- Conflict Details Display Area -->
        <div v-if="selectedConflict" class="widget conflict-details-widget">
          <h2>Conflict Details</h2>
          Conflict details will be displayed here.

          <!-- Conflict Resolution Actions -->
          <button @click="viewConflictingSurgeries">View Conflicting Surgeries</button>
          <button class="button-secondary" @click="ignoreConflict">Ignore Conflict</button>
        </div>

        <!-- Pending Surgeries Queue Widget -->
        <div class="widget pending-surgeries-widget">
          <h2>Pending Surgeries Queue</h2>
          <ul class="pending-surgeries-list">
            <li v-for="surgery in pendingSurgeries" :key="surgery.id" class="pending-surgery-item" @click="handlePendingSurgeryClick(surgery)">{{ surgery.patient }} - {{ surgery.type }}</li>
            <li v-if="pendingSurgeries.length === 0" class="no-items">No pending surgeries</li>
          </ul>
          <p>Sortable list of surgeries awaiting scheduling.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// TODO: Conduct a comprehensive accessibility review and implement WCAG 2.1 AA compliance, especially for custom interactive elements.
// This component represents the Scheduler's dashboard. Dashboards for other roles (Surgeon, Nurse, Admin) would be separate components.
import { ref } from 'vue'; // Import ref for reactive variables
import { onMounted } from 'vue';
import { useRouter } from 'vue-router'; // Import useRouter

const router = useRouter(); // Get router instance

// Loading state
const isLoading = ref(true);
const selectedConflict = ref(null); // New ref to hold selected conflict details
const todaySchedule = ref([]); // New ref for today's schedule

// Simulated data for KPIs
const orUtilizationToday = ref(85);
const avgSdstToday = ref(30);
const emergencyCasesToday = ref(2);
const cancelledSurgeriesToday = ref(1);

// Simulated data for other widgets
const criticalAlerts = ref([
  { id: 1, message: 'OR 3: A/C Maintenance Overdue' },
  { id: 2, message: 'Anesthesia Machine X: Unavailable' },
]);

const sdstConflicts = ref([
  { id: 1, message: "SDST Conflict: Requires 60 min setup, only 45 min available before Patient Z's surgery" },
]);

const pendingSurgeries = ref([
  { id: 1, patient: 'Patient A', type: 'Appendectomy' },
  { id: 2, patient: 'Patient B', type: 'Knee Replacement' },
  { id: 3, patient: 'Patient C', type: 'Cataract Surgery' },
]);

// --- Quick Action Button Handlers ---
const scheduleNewSurgery = () => {
  console.log('Navigate to Schedule New Surgery form');
  // In a real app, navigate to the surgery creation page/modal
  // router.push({ name: 'CreateSurgery' });
};

const addEmergencyCase = () => {
  console.log('Navigate to Add Emergency Case form');
  // In a real app, navigate to the emergency case entry page/modal
  // router.push({ name: 'AddEmergencyCase' });
};

const goToMasterSchedule = () => {
  console.log('Navigate to Master Schedule');
  router.push({ name: 'Scheduling' }); // Navigate to the Scheduling route
};

const manageResources = () => {
  console.log('Navigate to Resource Management');
  router.push({ name: 'ResourceManagement' }); // Navigate to the Resource Management route
};

const runOptimization = () => {
  console.log('Trigger Optimization Engine');
  // In a real app, this would likely open a modal or navigate to an optimization control page
  // router.push({ name: 'OptimizationControl' });
};
// -------------------------------------

// --- KPI Click Handler ---
const fetchDashboardData = async () => {
  // Simulate fetching data from an API
  await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate 1-second delay

  // Simulate populating today's schedule
  todaySchedule.value = [
    { id: 101, or: 'OR 1', time: '08:00', description: 'Patient X - Appendectomy' },
    { id: 102, or: 'OR 2', time: '09:30', description: 'Patient Y - Knee Replacement' },
    { id: 103, or: 'OR 1', time: '11:00', description: 'Patient Z - Cataract Surgery' },
    { id: 104, or: 'OR 3', time: '10:00', description: 'Patient W - Emergency Case' },
  ];

  isLoading.value = false; // Set loading to false when data is fetched
};

const navigateToReport = (kpiName) => {
  console.log(`Navigating to report for: ${kpiName}`);
  // Implement actual navigation later
};

// --- Placeholder Action Methods ---
const handleKpiClick = (kpiName) => {
  navigateToReport(kpiName);
};

// --- Alert Click Handler ---
const handleAlertClick = (alert) => {
  console.log('View details for alert:', alert);
  // Implement modal or navigation to alert details later
};

// --- Pending Surgery Click Handler ---
const handlePendingSurgeryClick = (surgery) => {
  viewSurgeryDetails(surgery);
};

// --- Conflict Click Handler ---
const handleConflictClick = (conflict) => {
  selectedConflict.value = conflict; // Set the selected conflict
};

const viewConflictingSurgeries = () => {
  console.log('View conflicting surgeries for:', selectedConflict.value);
  // In a real app, open a modal or navigate to a view showing related surgeries
};

const ignoreConflict = () => {
  console.log('Ignore conflict:', selectedConflict.value);
  // In a real app, send an API call to mark the conflict as ignored or resolved
};

const viewSurgeryDetails = (surgery) => {
  console.log('View details for pending surgery:', surgery);
  // Implement modal or navigation to pending surgery details later
};

// Component logic for fetching real data would go here later
onMounted(() => {
  fetchDashboardData();
});
</script>

<style scoped>
/* Define CSS variables for consistent colors */
:root {
  --color-white: #ffffff;
  --color-primary: #0075c2;
  --color-secondary: #6c757d;
  --color-danger: #dc3545;
  --color-warning: #ffc107;
  --color-light-gray: #f5f5f5;
  --color-mid-light-gray: #e0e0e0;
  --color-mid-gray: #aaaaaa;
  --color-dark-gray: #555555;
  --color-very-dark-gray: #333333;
}

/* TODO: Manage colors using CSS variables or a color palette for consistency across the application. */
.dashboard-container {
  padding: 20px;
}

.dashboard-widgets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); /* Responsive grid */
  gap: 20px; /* Space between widgets */
  margin-top: 20px;
}

.widget {
  background-color: var(--color-white);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--color-mid-light-gray); /* Subtle border */
}

.widget h2 {
  font-size: 1.3em;
  margin-top: 0;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-mid-light-gray); /* Separator */
  color: var(--color-very-dark-gray);
}

/* Quick Actions Widget Specific Styles */
.quick-actions-widget .quick-action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px; /* Space between buttons */
}

.quick-actions-widget button {
  /* Inherits base button styles */
  padding: 10px 15px; /* Adjust padding */
  font-size: 0.95em;
  cursor: pointer;
  border-radius: 4px;
  border: none;
  background-color: var(--color-primary);
  color: var(--color-white);
  transition: background-color 0.2s ease;
}

.quick-actions-widget button:hover {
  background-color: #005a94; /* Darker primary on hover */
}

.quick-actions-widget .button-secondary {
  background-color: var(--color-secondary); /* Use secondary color for some actions */
  color: var(--color-white);
}

.quick-actions-widget .button-secondary:hover {
  background-color: #5a6268; /* Darker secondary on hover */
}

/* KPI Widget Specific Styles */
.kpi-list {
  display: grid;
  grid-template-columns: 1fr 1fr; /* Two columns for KPI items */
  gap: 15px;
}

.kpi-item {
  text-align: left;
  cursor: pointer; /* Indicate it's clickable */
  transition: background-color 0.2s ease; /* Smooth transition for hover effect */
  padding: 10px;
  border-radius: 4px;
}

.kpi-item:hover {
  background-color: var(--color-light-gray); /* Subtle background change on hover */
}

.kpi-item .kpi-label {
  display: block;
  font-size: 0.9em;
  color: var(--color-dark-gray); /* Or a slightly lighter shade if needed */
  margin-bottom: 6px; /* Increased spacing */
}

.kpi-item .kpi-value {
  font-size: 1.5em; /* Increased font size */
  font-weight: bold;
  color: var(--color-primary);
  line-height: 1.2; /* Adjust line height if needed */
}

/* Specific widget adjustments can go here */
.schedule-overview-widget p,
.pending-surgeries-widget p {
  font-size: 0.9em;
  color: var(--color-dark-gray);
}

.alerts-widget ul,
.sdst-conflicts-widget ul,
.pending-surgeries-widget ul,
.schedule-overview-widget ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.alerts-widget li,
.sdst-conflicts-widget li,
.pending-surgeries-widget li,
.schedule-overview-widget li {
  margin-bottom: 8px;
  padding: 8px;
  border-bottom: 1px dashed var(--color-light-gray);
  font-size: 0.95em;
}

.alerts-widget li:last-child,
.sdst-conflicts-widget li:last-child,
.pending-surgeries-widget li:last-child,
.schedule-overview-widget li:last-child {
  border-bottom: none;
}

.pending-surgeries-widget li,
.alerts-widget li,
.sdst-conflicts-widget li {
  cursor: pointer; /* Indicate it's clickable */
  transition: background-color 0.2s ease; /* Smooth transition for hover effect */
}

.pending-surgeries-widget li:hover,
.alerts-widget li:hover,
.sdst-conflicts-widget li:hover {
  background-color: var(--color-light-gray); /* Subtle background change on hover */
}

.no-items {
  text-align: center;
  color: var(--color-mid-gray);
  font-style: italic;
}

.loading-message {
  font-size: 1.2em;
  color: var(--color-dark-gray);
  text-align: center;
  padding: 20px;
}

/* Add specific styling for alerts/conflicts later */
.alert-item {
  border-left: 5px solid var(--color-danger);
  padding-left: 15px; /* Add space for the border */
  color: var(--color-danger); /* Use danger color for alerts */
  font-weight: 500;
}

.conflict-item {
  color: var(--color-warning); /* Use warning color for conflicts */
  font-weight: 500;
  border-left: 5px solid var(--color-warning);
  padding-left: 15px; /* Add space for the border */
}
</style>

<template>
  <div class="dashboard-screen">
    <h1>Dashboard</h1>
    <p>Welcome to the Surgery Scheduling Application Dashboard!</p>

    <div class="dashboard-widgets">
      <div class="widget">
        <h2>Upcoming Surgeries</h2>
        <p><em>(Widget content for upcoming surgeries will go here)</em></p>
      </div>
      <div class="widget">
        <h2>Resource Availability</h2>
        <p><em>(Widget content for resource availability will go here)</em></p>
      </div>
      <div class="widget">
        <h2>System Alerts</h2>
        <p><em>(Widget content for system alerts will go here)</em></p>
      </div>
    </div>
  </div>
</template>

<script setup>
// No script logic needed for this basic placeholder yet
</script>

<style scoped>
.dashboard-screen {
  padding: 20px;
  background-color: #f9f9f9; /* Light background for the content area */
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.dashboard-screen h1 {
  color: var(--color-text-primary, #333);
  margin-bottom: 20px;
  border-bottom: 2px solid var(--color-primary, #4A90E2);
  padding-bottom: 10px;
}

.dashboard-widgets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.widget {
  background-color: var(--color-surface, #fff);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}

.widget h2 {
  color: var(--color-primary-dark, #357ABD);
  font-size: 1.2em;
  margin-bottom: 10px;
}

.widget p {
  color: var(--color-text-secondary, #555);
  font-style: italic;
}
</style>
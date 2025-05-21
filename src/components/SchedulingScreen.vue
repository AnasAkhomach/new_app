<template>
  <div class="scheduling-container">
    <h1>Surgery Scheduling</h1>

    <div class="scheduling-layout">
      <!-- Left Panel: Pending Surgeries & Filters -->
      <aside class="left-panel">
        <h2>Pending Surgeries</h2>
        <p>Drag and drop surgeries from this list onto the schedule.</p>

        <div class="filters-section">
             <h3>Filters</h3>
             <div class="filter-group">
                <label for="filter-priority">Priority:</label>
                <select id="filter-priority" v-model="filters.priority" @change="applyFilters">
                    <option value="">All</option>
                    <option value="STAT">STAT</option>
                    <option value="Urgent">Urgent</option>
                    <option value="Elective">Elective</option>
                </select>
             </div>
             <div class="filter-group">
                <label for="filter-specialty">Specialty:</label>
                <input type="text" id="filter-specialty" v-model="filters.specialty" placeholder="e.g., Cardiac" @input="applyFilters">
             </div>
             <div class="filter-group">
                <label for="filter-status">Status:</label>
                <select id="filter-status" v-model="filters.status" @change="applyFilters">
                    <option value="">All</option>
                    <option value="Pending">Pending</option>
                    <option value="Confirmed">Confirmed</option>
                    <!-- Add other relevant statuses -->
                </select>
             </div>
             <!-- TODO: Add more filters as needed: date range, surgeon, etc. -->
         </div>

        <!-- TODO: Implement drag functionality for these items -->
        <div class="pending-surgeries-list">
            <ul>
                <li
                    v-for="surgery in filteredPendingSurgeries"
                    :key="surgery.id"
                    class="pending-surgery-item"
                    draggable="true"
                    @dragstart="handleDragStart(surgery, $event)"
                    @click="selectSurgeryForDetails(surgery, 'pending')"
                >
                    <div class="item-header">Patient: {{ surgery.patientId }} ({{ surgery.priority }})</div>
                    <div class="item-details">Type: {{ surgery.type }} | Est. Duration: {{ surgery.estimatedDuration }} min</div>
                    <div class="item-status">Status: {{ surgery.status || 'Pending' }}</div>
                    <div class="item-actions">
                        <button class="button-small" @click.stop="selectSurgeryForDetails(surgery, 'pending')">View Details</button>
                        <!-- TODO: Add action to schedule directly if applicable -->
                    </div>
                </li>
                 <li v-if="filteredPendingSurgeries && filteredPendingSurgeries.length === 0" class="no-items">No pending surgeries matching filters.</li>
            </ul>
        </div>
      </aside>

      <!-- Main Panel: Master Schedule View (Gantt Chart) -->
      <main class="main-panel">
        <div class="schedule-header">
            <h2>Master Schedule View</h2>
            <div class="schedule-controls">
                <!-- TODO: Implement Gantt chart controls (Date navigation, view options, zoom) -->
                <button @click="ganttNavigate('prev')">Previous Day</button>
                <span>{{ currentGanttViewDateRange }}</span>
                <button @click="ganttNavigate('next')">Next Day</button>
                <button @click="ganttZoom('in')">Zoom In</button>
                <button @click="ganttZoom('out')">Zoom Out</button>
                <button @click="showCreateNewSurgeryForm">Create New Surgery</button>
            </div>
        </div>

        <!--
          Gantt Chart Integration Point
          This div will host the Gantt chart component.
          Consider creating a dedicated child component (e.g., <GanttChartComponent />)
          to encapsulate the Gantt library's logic and pass data via props.
        -->
        <div
          id="gantt-chart-container"
          class="gantt-chart-container"
          @drop="handleDropOnGantt($event)"
          @dragover.prevent
        >
          <!--
            The chosen Gantt library (e.g., Bryntum, DHTMLX, Toast UI Gantt, Frappe Gantt)
            will be initialized and rendered here.
            It will typically require:
            - A list of tasks (surgeries) with start/end dates, durations, dependencies.
            - Configuration for columns, timeline, resources, etc.
            - Event listeners for interactions (click, drag, resize, dependency creation).
          -->
          <p v-if="!isGanttInitialized" class="gantt-placeholder-text">
            Gantt Chart Area - Awaiting Library Integration
            <br>
            (Drop pending surgeries here to schedule)
          </p>
          <!-- Example: <ActualGanttComponent :tasks="ganttTasks" :resources="ganttResources" @task-updated="handleGanttTaskUpdate" /> -->
        </div>

        <div class="gantt-info-panel">
            <p><strong>SDST (Setup, Disinfection, Sterilization Time):</strong> Not yet calculated. Will be factored into scheduling.</p>
            <p><strong>Resource Conflicts:</strong> Conflict detection pending Gantt integration.</p>
        </div>
      </main>

      <!-- Right Panel: Surgery Details / Create New -->
      <aside class="right-panel">
        <div v-if="selectedSurgery">
          <h2>Surgery Details ({{ selectedSurgerySource === 'pending' ? 'Pending' : 'Scheduled' }})</h2>
          <form @submit.prevent="saveSurgeryDetails">
            <div class="form-group">
              <label for="patientId">Patient ID:</label>
              <input type="text" id="patientId" v-model="selectedSurgery.patientId" :disabled="formMode === 'view'">
            </div>
            <div class="form-group">
              <label for="surgeryType">Surgery Type:</label>
              <input type="text" id="surgeryType" v-model="selectedSurgery.type" :disabled="formMode === 'view'">
            </div>
            <div class="form-group">
              <label for="estimatedDuration">Estimated Duration (min):</label>
              <input type="number" id="estimatedDuration" v-model="selectedSurgery.estimatedDuration" :disabled="formMode === 'view'">
            </div>
            <div class="form-group">
              <label for="priority">Priority Level:</label>
              <select id="priority" v-model="selectedSurgery.priority" :disabled="formMode === 'view'">
                <option value="STAT">STAT</option>
                <option value="Urgent">Urgent</option>
                <option value="Elective">Elective</option>
              </select>
            </div>
            <div class="form-group" v-if="selectedSurgerySource === 'scheduled'">
              <label for="scheduledTime">Scheduled Time:</label>
              <input type="datetime-local" id="scheduledTime" v-model="selectedSurgery.scheduledTime" :disabled="formMode === 'view'">
            </div>
             <div class="form-group">
              <label for="status">Status:</label>
              <select id="status" v-model="selectedSurgery.status" :disabled="formMode === 'view'">
                <option value="Pending">Pending</option>
                <option value="Confirmed">Confirmed</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>
            <!-- TODO: Add fields for Surgeon, Required Staff, Equipment, OR, Notes -->
            <div class="form-actions">
              <button type="button" v-if="formMode === 'view'" @click="formMode = 'edit'">Edit</button>
              <button type="submit" v-if="formMode !== 'view'">Save Changes</button>
              <button type="button" @click="clearSelectionOrCancel">{{ formMode === 'new' ? 'Cancel' : 'Close' }}</button>
              <button type="button" v-if="selectedSurgerySource === 'pending' && formMode !== 'new'" @click="scheduleSelectedSurgery">Schedule This Surgery</button>
            </div>
          </form>
        </div>
        <div v-else>
          <h2>Surgery Details</h2>
          <p>Select a pending surgery to view its details, or drag it to the schedule. Click "Create New Surgery" to add a new entry.</p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';

// --- State ---
const pendingSurgeries = ref([]);
const scheduledSurgeries = ref([]); // This will eventually be populated by the Gantt chart's data source
const selectedSurgery = ref(null);
const selectedSurgerySource = ref(''); // 'pending' or 'scheduled'
const formMode = ref('view'); // 'view', 'edit', 'new'

const filters = ref({
  priority: '',
  specialty: '',
  status: '',
  // Add other filter properties here
});

const currentScheduleDateRange = ref('Today'); // Placeholder for date range display
const currentGanttViewDateRange = ref('Today'); // Placeholder for Gantt's current date range display
const isGanttInitialized = ref(false); // To track if the Gantt library is loaded

// --- Data for Gantt Chart (to be passed as props or managed by the Gantt library wrapper) ---
const ganttTasks = ref([]); // Holds tasks formatted for the Gantt library
const ganttResources = ref([]); // Holds resources (ORs, Surgeons, Staff, Equipment)

// --- Computed Properties ---
const filteredPendingSurgeries = computed(() => {
  if (!pendingSurgeries.value) return []; // Ensure pendingSurgeries.value is not null or undefined

  return pendingSurgeries.value.filter(surgery => {
    const matchesPriority = !filters.value.priority || surgery.priority === filters.value.priority;
    const matchesSpecialty = !filters.value.specialty || (surgery.requiredSpecialty && surgery.requiredSpecialty.toLowerCase().includes(filters.value.specialty.toLowerCase()));
    const matchesStatus = !filters.value.status || surgery.status === filters.value.status;
    // TODO: Add logic for other filters
    return matchesPriority && matchesSpecialty && matchesStatus;
  });
});

// --- Methods ---

// Simulate fetching initial data
const fetchInitialData = () => {
  // Simulated pending surgeries data
  pendingSurgeries.value = [
    { id: 'p1', patientId: 'P001', type: 'Appendectomy', estimatedDuration: 60, priority: 'Urgent', status: 'Pending', details: 'Acute appendicitis', requiredSpecialty: 'General Surgery' },
    { id: 'p2', patientId: 'P002', type: 'Knee Replacement', estimatedDuration: 120, priority: 'Elective', status: 'Pending', details: 'Osteoarthritis', requiredSpecialty: 'Orthopedics' },
    { id: 'p3', patientId: 'P003', type: 'CABG', estimatedDuration: 240, priority: 'STAT', status: 'Pending', details: 'Severe CAD', requiredSpecialty: 'Cardiothoracic' },
    { id: 'p4', patientId: 'P004', type: 'Hernia Repair', estimatedDuration: 90, priority: 'Elective', status: 'Confirmed', details: 'Inguinal hernia', requiredSpecialty: 'General Surgery' },
    { id: 'p5', patientId: 'P005', type: 'Cholecystectomy', estimatedDuration: 75, priority: 'Urgent', status: 'Pending', details: 'Gallstones', requiredSpecialty: 'General Surgery' },
  ];

  // TODO: Fetch actual scheduled surgeries and format them for the Gantt chart
  // This data will populate `ganttTasks`
  // Example:
  // ganttTasks.value = [
  //   { id: 's1', text: 'P00X - Example Scheduled', startDate: '2023-10-27T09:00', duration: 2, durationUnit: 'hour', resourceId: 'OR1', ...otherGanttProps },
  // ];
  // scheduledSurgeries.value = ganttTasks.value.map(transformGanttTaskToSurgery); // Keep scheduledSurgeries in sync if needed elsewhere

  // TODO: Fetch resources for the Gantt chart (ORs, staff, equipment)
  // ganttResources.value = [
  //  { id: 'OR1', name: 'Operating Room 1' },
  //  { id: 'surgeon1', name: 'Dr. Smith (Cardio)'}
  // ];

  // Simulate Gantt initialization after a short delay (replace with actual library init)
  setTimeout(() => {
    // isGanttInitialized.value = true; // Set this once the Gantt library is actually loaded and ready
    console.log('Gantt chart would be initialized here.');
    // transformScheduledSurgeriesToGanttTasks(); // Populate ganttTasks from scheduledSurgeries
  }, 500);
};

// Helper to transform surgery data to Gantt task format (example)
const transformSurgeryToGanttTask = (surgery, scheduledTime) => {
  // This is highly dependent on the chosen Gantt library's expected format
  return {
    id: surgery.id,
    text: `${surgery.patientId} - ${surgery.type}`,
    startDate: scheduledTime, // Ensure this is a valid date/time format for the library
    duration: surgery.estimatedDuration,
    durationUnit: 'minute', // Or 'hour', 'day' depending on library
    priority: surgery.priority,
    status: surgery.status,
    // Add other relevant fields: resourceId (OR, surgeon), dependencies, color, etc.
    ...surgery // Spread other surgery details that might be useful
  };
};

// Helper to transform scheduled surgeries (if fetched separately) to Gantt tasks
const transformScheduledSurgeriesToGanttTasks = () => {
  ganttTasks.value = scheduledSurgeries.value.map(surgery => {
    // Assuming surgery objects in scheduledSurgeries have a 'scheduledTime' and 'id'
    return transformSurgeryToGanttTask(surgery, surgery.scheduledTime);
  });
  // TODO: Notify Gantt chart to refresh/load new tasks
};

// Watch for changes in scheduledSurgeries to update Gantt tasks
// This is a basic example; a real Gantt integration might handle this internally or via its API
watch(scheduledSurgeries, (newScheduledList) => {
  // transformScheduledSurgeriesToGanttTasks();
  console.log('Scheduled surgeries updated, Gantt tasks should refresh:', newScheduledList);
}, { deep: true });

const applyFilters = () => {
  // The computed property `filteredPendingSurgeries` will update automatically.
  // This function is here if any imperative logic is needed on filter change.
  console.log('Filters applied:', filters.value);
};

const selectSurgeryForDetails = (surgery, source) => {
  selectedSurgery.value = { ...surgery }; // Clone to avoid direct mutation if editing
  selectedSurgerySource.value = source;
  formMode.value = 'view';
  console.log(`Viewing ${source} surgery:`, surgery.id);
};

const showCreateNewSurgeryForm = () => {
  selectedSurgery.value = {
    patientId: '',
    type: '',
    estimatedDuration: 60,
    priority: 'Elective',
    status: 'Pending',
    // Initialize other fields for a new surgery
  };
  selectedSurgerySource.value = 'new';
  formMode.value = 'new';
  console.log('Showing form to create new surgery');
};

const saveSurgeryDetails = () => {
  if (!selectedSurgery.value) return;
  console.log('Saving surgery details:', selectedSurgery.value);
  // TODO: Implement actual save logic (API call)
  // This will differ based on whether it's a new, pending, or scheduled surgery update

  if (formMode.value === 'new') {
    // Add to pending list or directly to schedule based on workflow
    const newSurgery = { ...selectedSurgery.value, id: `p${Date.now()}` }; // Simple ID generation
    pendingSurgeries.value.push(newSurgery);
    alert('New surgery added to pending list.');
  } else if (selectedSurgerySource.value === 'pending') {
    const index = pendingSurgeries.value.findIndex(s => s.id === selectedSurgery.value.id);
    if (index !== -1) pendingSurgeries.value.splice(index, 1, { ...selectedSurgery.value });
    alert('Pending surgery details updated.');
  } else if (selectedSurgerySource.value === 'scheduled') {
    const index = scheduledSurgeries.value.findIndex(s => s.id === selectedSurgery.value.id);
    if (index !== -1) scheduledSurgeries.value.splice(index, 1, { ...selectedSurgery.value });
    // TODO: Update Gantt chart if a scheduled item is modified
    alert('Scheduled surgery details updated.');
  }
  formMode.value = 'view'; // Revert to view mode after save
};

const clearSelectionOrCancel = () => {
  selectedSurgery.value = null;
  selectedSurgerySource.value = '';
  formMode.value = 'view';
  console.log('Selection cleared or form cancelled');
};

const scheduleSelectedSurgery = () => {
  if (!selectedSurgery.value || selectedSurgerySource.value !== 'pending') return;
  // This is a simplified scheduling action. Real implementation would involve the Gantt chart.
  const surgeryToSchedule = { ...selectedSurgery.value, status: 'Confirmed', scheduledTime: new Date().toISOString().slice(0, 16) }; // Example time
  scheduledSurgeries.value.push(surgeryToSchedule);

  // Remove from pending list
  pendingSurgeries.value = pendingSurgeries.value.filter(s => s.id !== selectedSurgery.value.id);

  alert(`Surgery ${selectedSurgery.value.patientId} scheduled.`);
  selectSurgeryForDetails(surgeryToSchedule, 'scheduled'); // View the newly scheduled item
  // TODO: Integrate with Gantt chart for proper placement, conflict checks, etc.
};

// --- Drag and Drop Handlers ---
const handleDragStart = (surgery, event) => {
  console.log('Dragging surgery:', surgery.id);
  event.dataTransfer.setData('application/json', JSON.stringify(surgery));
  event.dataTransfer.effectAllowed = 'move';
  // TODO: Add visual feedback for dragging
};

const handleDropOnSchedule = (event) => {
  event.preventDefault();
  const surgeryDataString = event.dataTransfer.getData('application/json');
  if (!surgeryDataString) return;

  const droppedSurgery = JSON.parse(surgeryDataString);
  console.log('Dropped surgery on schedule:', droppedSurgery.id);

  // TODO: Advanced logic for placing on Gantt chart:
  // - Determine exact time/resource based on drop position
  // - Perform conflict checks (SDST, resource availability)
  // - Update surgery status and details
  // - Visually add to the Gantt chart

  // Simplified: Add to scheduled list and remove from pending
  const alreadyScheduled = scheduledSurgeries.value.find(s => s.id === droppedSurgery.id);
  if (alreadyScheduled) {
      alert('This surgery is already on the schedule.');
      return;
  }

  const newScheduledItem = {
    ...droppedSurgery,
    scheduledTime: new Date().toISOString().slice(0, 16), // Placeholder, should come from Gantt drop position
    status: 'Confirmed',
    // Potentially assign OR, staff based on drop context if Gantt supports it
  };
  scheduledSurgeries.value.push(newScheduledItem);
  pendingSurgeries.value = pendingSurgeries.value.filter(s => s.id !== droppedSurgery.id);

  selectSurgeryForDetails(newScheduledItem, 'scheduled');
  alert(`Surgery ${droppedSurgery.patientId} scheduled via drag and drop.`);
};

// --- Gantt Chart Specific (Placeholders) ---
const prevDateRange = () => {
  // TODO: Implement date navigation for Gantt chart
  alert('Navigate to Previous Day/Week (Not Implemented)');
  currentScheduleDateRange.value = 'Previous Period';
};

const nextDateRange = () => {
  // TODO: Implement date navigation for Gantt chart
  alert('Navigate to Next Day/Week (Not Implemented)');
  currentScheduleDateRange.value = 'Next Period';
};

// TODO: Add methods for interacting with the Gantt chart library once integrated
// (e.g., handling item resize, move, click events from the chart itself)

// Initial data fetch on component mount
onMounted(() => {
  fetchInitialData();
});

// Renamed handleDropOnSchedule to handleDropOnGantt for clarity as per template
const handleDropOnGantt = handleDropOnSchedule;

// Placeholder functions for Gantt chart controls
const ganttNavigate = (direction) => {
    console.log('Gantt navigation attempted:', direction);
    // TODO: Implement actual Gantt navigation
};

const ganttZoom = (level) => {
     console.log('Gantt zoom attempted:', level);
    // TODO: Implement actual Gantt zoom
};

</script>

<style scoped>
.scheduling-container {
  padding: 20px;
  background-color: var(--background-color);
  color: var(--text-color);
  height: calc(100vh - 60px); /* Assuming header is 60px */
  display: flex;
  flex-direction: column;
}

h1 {
  color: var(--primary-color);
  margin-bottom: 20px;
  text-align: center;
}

.scheduling-layout {
  display: flex;
  flex-grow: 1;
  gap: 20px;
  overflow: hidden; /* Prevent layout from exceeding container height */
}

.left-panel, .right-panel {
  width: 25%;
  background-color: var(--surface-color);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  overflow-y: auto; /* Allow scrolling within panels */
}

.main-panel {
  flex-grow: 1;
  background-color: var(--surface-color);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Important for Gantt chart layout */
}

.left-panel h2, .main-panel h2, .right-panel h2 {
  color: var(--secondary-color);
  margin-top: 0;
  margin-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.filters-section {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color-light);
}

.filters-section h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: var(--text-color-secondary);
}

.filter-group {
  margin-bottom: 10px;
}

.filter-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 0.9em;
  color: var(--text-color-secondary);
}

.filter-group select,
.filter-group input[type="text"] {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--background-color);
  color: var(--text-color);
}

.pending-surgeries-list {
  flex-grow: 1;
  overflow-y: auto;
}

.pending-surgeries-list ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.pending-surgery-item {
  background-color: var(--background-color);
  border: 1px solid var(--border-color-light);
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  cursor: grab;
  transition: background-color 0.2s ease;
}

.pending-surgery-item:hover {
  background-color: var(--hover-color);
}

.item-header {
  font-weight: bold;
  margin-bottom: 5px;
}

.item-details {
  font-size: 0.9em;
  color: var(--text-color-secondary);
  margin-bottom: 5px;
}

.item-status {
  font-size: 0.8em;
  font-style: italic;
  color: var(--accent-color-dark);
  margin-bottom: 8px;
}

.item-actions .button-small {
    padding: 4px 8px;
    font-size: 0.8em;
    background-color: var(--secondary-color);
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}
.item-actions .button-small:hover {
    background-color: var(--secondary-color-dark);
}

.no-items, .no-scheduled-items {
    padding: 10px;
    text-align: center;
    color: var(--text-color-secondary);
    font-style: italic;
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.schedule-controls button {
  margin-left: 10px;
  padding: 8px 12px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.schedule-controls button:hover {
  background-color: var(--primary-color-dark);
}

.schedule-controls span {
    margin: 0 10px;
    font-weight: bold;
}

.gantt-chart-placeholder {
  flex-grow: 1;
  border: 2px dashed var(--border-color);
  display: flex;
  flex-direction: column; /* To stack p and ul */
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--text-color-secondary);
  border-radius: 4px;
  background-color: var(--background-color-light);
  min-height: 300px; /* Ensure it has some height */
  overflow-y: auto; /* If debug list gets long */
}

.scheduled-surgery-list-debug {
    list-style: none;
    padding: 0;
    margin-top: 10px;
    font-size: 0.9em;
}
.scheduled-surgery-list-debug li {
    padding: 5px;
    border-bottom: 1px solid var(--border-color-light);
    cursor: pointer;
}
.scheduled-surgery-list-debug li:hover {
    background-color: var(--hover-color);
}


.right-panel form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: bold;
  font-size: 0.9em;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="datetime-local"],
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--background-color);
  color: var(--text-color);
  font-size: 1em;
}

.form-group input:disabled,
.form-group select:disabled,
.form-group textarea:disabled {
    background-color: var(--disabled-bg-color);
    color: var(--disabled-text-color);
    cursor: not-allowed;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap; /* Allow buttons to wrap on smaller screens */
}

.form-actions button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.form-actions button[type="submit"], .form-actions button:nth-of-type(1) {
  background-color: var(--primary-color);
  color: white;
}
.form-actions button[type="submit"]:hover, .form-actions button:nth-of-type(1):hover {
  background-color: var(--primary-color-dark);
}

.form-actions button[type="button"] {
  background-color: var(--secondary-color);
  color: white;
}
.form-actions button[type="button"]:hover {
  background-color: var(--secondary-color-dark);
}

/* Responsive adjustments if needed */
@media (max-width: 1200px) {
  .scheduling-layout {
    flex-direction: column; /* Stack panels on smaller screens */
    overflow: visible;
  }
  .left-panel, .right-panel, .main-panel {
    width: 100%;
    margin-bottom: 20px;
    max-height: 50vh; /* Limit height when stacked */
    overflow-y: auto;
  }
  .main-panel {
      min-height: 400px; /* Ensure Gantt area is usable */
  }
}

</style>
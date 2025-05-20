<template>
  <div class="scheduling-container">
    <h1>Surgery Scheduling</h1>

    <div class="scheduling-layout">
      <!-- Left Panel: Pending Surgeries & Filters -->
      <aside class="left-panel">
        <h2>Pending Surgeries</h2>
        <p>Drag and drop surgeries from this list onto the schedule.</p>

        <div class="pending-surgeries-list">
            <ul>
                <!-- Bind to pendingSurgeries data -->
                <li
                    v-for="surgery in pendingSurgeries"
                    :key="surgery.id"
                    class="pending-surgery-item"
                    @click="viewPendingSurgery(surgery)"
                >
                    <div class="item-header">Patient: {{ surgery.patientId }}</div>
                    <div class="item-details">Type: {{ surgery.type }} | Est. Duration: {{ surgery.estimatedDuration }} hrs</div>
                    <div class="item-actions">
                        <button class="button-small">View Details</button>
                    </div>
                </li>
                 <li v-if="pendingSurgeries.length === 0" class="no-items">No pending surgeries.</li>
            </ul>
        </div>

        <!-- Placeholder for Filters -->
         <div class="filters-section">
             <h3>Filters</h3>
             <p>Placeholder for filter controls (priority, specialty, date).</p>
         </div>

      </aside>

      <!-- Main Panel: Master Schedule View (Gantt Chart) -->
      <main class="main-panel">
        <h2>Master Schedule View</h2>

        <!-- Placeholder for Interactive Gantt Chart Component -->
        <!-- This area will be replaced by a third-party Gantt chart library component -->
         <div id="gantt-chart-area" class="gantt-chart-placeholder">
             <p>Interactive Gantt Chart will be rendered here.</p>
             <p>Needs integration with a library like Bryntum Gantt, DHTMLX Gantt, etc.</p>
         </div>

        <!-- Placeholder for Gantt chart controls (Date navigation, view options, zoom) -->
         <div class="gantt-controls">
             <p>Placeholder for date navigation, view options (Day/Week/Month), and zoom controls.</p>
         </div>

      </main>

      <!-- Right Panel: Contextual Details / Form -->
      <aside class="right-panel">
        <h2>Surgery Details / Form</h2>

        <div class="surgery-form">
             <!-- Conditionally display placeholder message or surgery details/form -->
             <div v-if="!selectedSurgery">
                <p>Select a surgery from the schedule or pending list, or click an empty slot to add a new one.</p>
                 <button class="button-primary" @click="createNewSurgery">Add New Surgery</button> <!-- Button to add new -->
             </div>

             <div v-else>
                <!-- Basic Form Structure (Active for viewing/editing/adding) -->
                 <div class="form-section">
                     <h3>{{ selectedSurgery.id ? 'Edit Surgery Information' : 'New Surgery Information' }}</h3>
                     <div class="input-group">
                         <label for="patientId">Patient Identifier</label>
                         <input type="text" id="patientId" v-model="selectedSurgery.patientId" placeholder="Search EHR or Enter ID" required>
                         <button class="button-small">Lookup EHR</button> <!-- Placeholder EHR lookup -->
                     </div>
                      <div class="input-group">
                         <label for="surgeryType">Surgery Type</label>
                         <select id="surgeryType" v-model="selectedSurgery.type" required>
                             <option value="">Select Type</option>
                             <option value="Cardiac - CABG">Cardiac - CABG</option>
                             <option value="Orthopedic - TKR">Orthopedic - TKR</option>
                             <option value="General - Appendectomy">General - Appendectomy</option>
                             <!-- Options populated from SDST Data Management -->
                         </select>
                     </div>
                      <div class="input-group">
                         <label for="estimatedDuration">Estimated Duration (minutes)</label>
                         <input type="number" id="estimatedDuration" v-model.number="selectedSurgery.estimatedDuration" required min="0">
                     </div>
                      <div class="input-group">
                         <label for="priorityLevel">Priority Level</label>
                         <select id="priorityLevel" v-model="selectedSurgery.priority" required>
                             <option value="">Select Priority</option>
                             <option value="Elective">Elective</option>
                             <option value="Urgent">Urgent</option>
                             <option value="STAT">STAT</option>
                             <!-- Define priority levels -->
                         </select>
                     </div>
                       <div class="input-group">
                         <label for="requiredSurgeon">Required Surgeon(s)</label>
                         <select id="requiredSurgeon" v-model="selectedSurgery.surgeon">
                             <option value="">Select Surgeon</option>
                              <option value="Dr. Jane Smith">Dr. Jane Smith</option>
                             <!-- Options populated from Resource Management -->
                         </select>
                         <!-- Could be multi-select later -->
                     </div>
                     <div class="input-group">
                         <label for="requiredStaff">Required Staff Roles</label>
                         <select id="requiredStaff" multiple v-model="selectedSurgery.requiredStaff"> <!-- Multi-select placeholder -->
                             <option value="scrubNurse">Scrub Nurse</option>
                             <option value="anesthetist">Anesthetist</option>
                             <!-- Options populated from Resource Management -->
                         </select>
                     </div>
                      <div class="input-group">
                         <label for="requiredEquipment">Required Equipment</label>
                         <select id="requiredEquipment" multiple v-model="selectedSurgery.requiredEquipment"> <!-- Multi-select placeholder -->
                             <option value="carm">C-Arm</option>
                             <option value="microscope">Microscope</option>
                             <!-- Options populated from Resource Management -->
                         </select>
                     </div>
                      <div class="input-group">
                         <label for="notes">Notes</label>
                         <textarea id="notes" rows="3" v-model="selectedSurgery.notes"></textarea>
                     </div>
                 </div>

                 <div class="sdst-info-section">
                     <h3>SDST Information (Contextual)</h3>
                     <p>Calculated SDST for current placement will appear here.</p>
                      <p>Conflict alerts (Resource, SDST) will be shown here.</p>
                      <!-- Placeholder for SDST and Conflict details -->
                 </div>

                 <div class="form-actions">
                     <button class="button-primary" @click="handleSaveSurgery">Save / Schedule</button>
                     <button class="button-danger" v-if="selectedSurgery.id" @click="cancelScheduledSurgery(selectedSurgery.id)">Cancel Surgery</button> <!-- Show only if editing existing -->
                     <button class="button-secondary" @click="handleCancelSurgeryForm">Cancel</button> <!-- Cancel editing or adding -->
                 </div>

             </div>

        </div>

      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Simulated Data for Pending Surgeries
const pendingSurgeries = ref([
    { id: 1, patientId: 'P101', type: 'Cardiac - CABG', estimatedDuration: 3, priority: 'Elective', surgeon: 'Dr. Jane Smith', requiredStaff: ['scrubNurse'], requiredEquipment: ['carm'], notes: 'Patient has history of heart disease.' },
    { id: 2, patientId: 'P102', type: 'Orthopedic - TKR', estimatedDuration: 2, priority: 'Elective', surgeon: 'Dr. Jane Smith', requiredStaff: [], requiredEquipment: [], notes: 'Right knee replacement.' },
    { id: 3, patientId: 'P103', type: 'General - Appendectomy', estimatedDuration: 1, priority: 'Urgent', surgeon: null, requiredStaff: [], requiredEquipment: [], notes: 'Patient presented with acute appendicitis.' },
]);

// Simulated Data for Scheduled Surgeries (initially empty)
const scheduledSurgeries = ref([]); // Will hold surgeries placed on the Gantt chart

// State for selected surgery in the right panel
const selectedSurgery = ref(null);

// Method to view details of a pending surgery (or potentially a scheduled one later)
const viewPendingSurgery = (surgery) => {
    console.log('Viewing pending surgery:', surgery);
    // Create a deep copy to allow editing without affecting the original list item immediately
    selectedSurgery.value = JSON.parse(JSON.stringify(surgery));
};

// Placeholder method for viewing/editing a scheduled surgery from the Gantt chart
const viewScheduledSurgery = (surgery) => {
     console.log('Viewing scheduled surgery:', surgery);
      // Create a deep copy for editing
     selectedSurgery.value = JSON.parse(JSON.stringify(surgery));
      // In a real app, this would likely trigger displaying an editable form or detailed view
}

// Method for creating a new surgery (e.g., by clicking an empty slot or 'Add New' button)
const createNewSurgery = () => {
     console.log('Creating new surgery');
     // Initialize selectedSurgery with default or empty values to show a blank form
     selectedSurgery.value = {
         id: null, // Use null to indicate a new surgery (not saved yet)
         patientId: '',
         type: '',
         estimatedDuration: null,
         priority: 'Elective', // Default priority
         surgeon: '',
         requiredStaff: [],
         requiredEquipment: [],
         notes: '',
          // Add scheduling-specific fields later (OR, startTime, etc.)
     };
}


// Placeholder methods for saving/cancelling surgery edits or creation
const handleSaveSurgery = () => {
    console.log('Attempting to save surgery:', selectedSurgery.value);

    if (!selectedSurgery.value) return; // Should not happen if form is visible, but safety check

    // Basic Validation (add more comprehensive validation later)
    if (!selectedSurgery.value.patientId || !selectedSurgery.value.type || selectedSurgery.value.estimatedDuration === null || selectedSurgery.value.estimatedDuration < 0) {
         alert('Please fill in required fields (Patient ID, Type, non-negative Duration).');
         return;
    }

    if (selectedSurgery.value.id) {
        // --- Simulate Updating Existing Surgery (only in pending list for now) ---
        console.log('Simulating update for surgery ID:', selectedSurgery.value.id);
         // In a real app, send update request to backend

         // Find the surgery in pending list and update it
        const pendingIndex = pendingSurgeries.value.findIndex(s => s.id === selectedSurgery.value.id);
        if (pendingIndex !== -1) {
            // Use splice to maintain reactivity if needed, or simply reassign
            pendingSurgeries.value[pendingIndex] = selectedSurgery.value; // Update pending list
             console.log('Pending surgery updated:', selectedSurgery.value);
        } else {
            // If not in pending, it must be in scheduled list (logic to be added later)
             console.warn('Selected surgery not found in pending list. (Scheduled list update not yet implemented)');
        }
         // Show a success message (placeholder)

    } else {
        // --- Simulate Adding New Surgery to Pending List ---
        console.log('Simulating adding new surgery.');
        // In a real app, send create request to backend, backend assigns ID

        // Simulate assigning a new ID for the new surgery (basic increment)
        const newId = pendingSurgeries.value.length > 0 ? Math.max(...pendingSurgeries.value.map(s => s.id)) + 1 : 1;
        const newSurgery = { ...selectedSurgery.value, id: newId }; // Add generated ID

        // Add the new surgery to the pending list
        pendingSurgeries.value.push(newSurgery);
         console.log('New surgery added to pending:', newSurgery);
        // Show a success message (placeholder)

    }

    // Clear the selected surgery after save (simulating closing the form)
    selectedSurgery.value = null;
};

const handleCancelSurgeryForm = () => {
     console.log('Cancelling surgery form');
    // Clear selectedSurgery without saving
     selectedSurgery.value = null;
}

// Placeholder for cancelling a *scheduled* surgery (different from cancelling the form)
const cancelScheduledSurgery = (surgeryId) => {
    console.log('Attempting to cancel scheduled surgery with ID:', surgeryId);
     // In a real app, show confirmation and send cancel request to backend
     const confirmCancel = confirm('Are you sure you want to cancel this scheduled surgery?');
     if(confirmCancel) {
         // Simulate removing from scheduled list and potentially moving back to pending
         // Need scheduledSurgeries array and logic to remove/move
          console.log('Scheduled surgery cancellation confirmed (simulated). ID:', surgeryId);
          // After successful cancellation from backend:
         selectedSurgery.value = null; // Close form after cancelling
     } else {
         console.log('Scheduled surgery cancellation cancelled by user.');
     }
}

</script>

<style scoped>
.scheduling-container {
  padding: 20px;
  background-color: var(--color-white); /* Match layout background */
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%; /* Take full height of parent */
  display: flex; /* Use flex to manage internal layout */
  flex-direction: column;
}

h1 {
  color: var(--color-very-dark-gray);
  margin-bottom: 20px;
}

.scheduling-layout {
  display: grid;
  grid-template-columns: 250px 1fr 300px; /* Left panel fixed, main grows, right fixed */
  gap: 20px; /* Space between panels */
  flex-grow: 1; /* Allow layout to take available height */
   overflow: hidden; /* Prevent internal layout causing scroll */
}

.left-panel,
.right-panel {
  background-color: var(--color-light-gray); /* Subtle background for side panels */
  padding: 15px;
  border-radius: 4px;
  overflow-y: auto; /* Allow scrolling within panels if content overflows */
  display: flex; /* Use flex for internal layout */
  flex-direction: column;
}

.main-panel {
  background-color: var(--color-background); /* Differentiate main panel */
  padding: 15px;
  border-radius: 4px;
  overflow: hidden; /* Hide overflow of gantt/content */
  display: flex; /* Use flex to manage inner main panel content */
  flex-direction: column;
}

/* --- Gantt Chart Placeholder Styles --- */
.gantt-chart-placeholder {
    flex-grow: 1; /* Allow placeholder to take remaining height */
    background-color: var(--color-white); /* White area for gantt */
    border: 1px dashed var(--color-dark-gray); /* Dashed border to show it's a placeholder */
    display: flex;
    flex-direction: column; /* Arrange text vertically */
    justify-content: center;
    align-items: center;
    font-size: 1.2em; /* Slightly smaller font for multiple lines */
    color: var(--color-dark-gray);
    border-radius: 4px;
     text-align: center; /* Center text */
}

.gantt-chart-placeholder p {
    margin: 5px 0; /* Space between paragraphs */
}

.gantt-controls {
    margin-top: 15px; /* Space above controls */
    padding-top: 10px;
    border-top: 1px solid var(--color-gray);
    text-align: center; /* Center controls placeholder */
     font-size: 0.9em;
     color: var(--color-dark-gray);
}
/* --- End Gantt Chart Placeholder Styles --- */

/* Adjust font size for placeholder text in panels */
.left-panel p:not(.no-items), .right-panel p:not(.no-items) {
    font-size: 0.9em;
    color: var(--color-dark-gray);
}

/* --- Pending Surgeries List Styles --- */
.pending-surgeries-list ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.pending-surgery-item {
    background-color: var(--color-white);
    border: 1px solid var(--color-gray);
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 10px;
    cursor: grab; /* Indicate draggable */
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
     transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.pending-surgery-item:active {
    cursor: grabbing; /* Indicate dragging */
    transform: rotate(2deg); /* Subtle rotation when dragging */
    box-shadow: 0 5px 15px rgba(0,0,0,0.15); /* Larger shadow when dragging */
}

.item-header {
    font-weight: 600;
    color: var(--color-primary-dark);
    margin-bottom: 5px;
}

.item-details {
    font-size: 0.85em;
    color: var(--color-very-dark-gray);
    margin-bottom: 8px;
}

.item-actions {
    text-align: right;
}

.filters-section {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid var(--color-gray);
}

.filters-section h3 {
     font-size: 1em;
     color: var(--color-dark-gray);
     margin-top: 0;
     margin-bottom: 10px;
}

/* --- Surgery Form Styles --- */
.surgery-form h3 {
     font-size: 1em;
     color: var(--color-dark-gray);
     margin-top: 15px;
     margin-bottom: 10px;
     border-bottom: 1px dotted var(--color-gray); /* Dotted separator */
     padding-bottom: 5px;
}

.surgery-form .input-group {
    margin-bottom: 15px;
}

.surgery-form .input-group label {
     display: block;
     font-size: 0.9em;
     color: var(--color-dark-gray);
     margin-bottom: 5px;
     font-weight: 500;
}

.surgery-form .input-group input[type="text"],
.surgery-form .input-group input[type="number"],
.surgery-form .input-group select,
.surgery-form .input-group textarea {
    width: 100%;
    padding: 8px;
    border: 1px solid var(--color-gray);
    border-radius: 4px;
    box-sizing: border-box; /* Include padding and border in element's total width */
    font-size: 0.9em;
    color: var(--color-very-dark-gray);
    background-color: var(--color-white);
}

.sdst-info-section {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid var(--color-gray);
}

.sdst-info-section h3 {
    font-size: 1em;
    color: var(--color-dark-gray);
    margin-top: 0;
    margin-bottom: 10px;
}

.form-actions {
    margin-top: 20px;
    text-align: right;
    border-top: 1px solid var(--color-gray);
    padding-top: 15px;
}

.form-actions button {
    padding: 8px 15px;
    margin-left: 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
     transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease;
}

.button-primary {
    background-color: var(--color-primary);
    color: var(--color-white);
    border: 1px solid var(--color-primary);
}

.button-primary:hover {
    background-color: var(--color-primary-dark);
    border-color: var(--color-primary-dark);
}

.button-danger {
    background-color: var(--color-danger);
}

.button-danger:hover {
    background-color: #c82333;
}

.button-secondary {
    background-color: transparent;
    color: var(--color-dark-gray);
    border: 1px solid var(--color-dark-gray);
}

.button-secondary:hover {
    background-color: var(--color-dark-gray);
    color: var(--color-white);
}

.button-small {
     padding: 5px 10px; /* Defined small button style */
     font-size: 0.85em;
     margin-left: 5px; /* Space from input */
     border-radius: 4px;
     cursor: pointer;
     transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease;
      background-color: var(--color-light-gray);
     color: var(--color-very-dark-gray);
     border: 1px solid var(--color-gray);
}

.button-small:hover {
     background-color: var(--color-gray);
     color: var(--color-very-dark-gray);
}

/* Style adjustment for input-button group */
.input-group {
    display: flex; /* Use flexbox to align input and button */
    align-items: center;
    margin-bottom: 15px;
}

.input-group input[type="text"] {
    flex-grow: 1; /* Allow input to take available space */
     margin-right: 5px; /* Space between input and button */
}

.no-items {
    font-style: italic;
    color: var(--color-dark-gray);
 text-align: center;
    background-color: var(--color-light-gray); /* Subtle background color */
    padding: 10px;
     border-radius: 4px;
}

</style>

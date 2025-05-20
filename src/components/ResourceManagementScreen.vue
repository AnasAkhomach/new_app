<template>
  <div class="resource-management-container">
    <h1>Resource Management</h1>

    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'ors' }"
        @click="activeTab = 'ors'"
      >Operating Rooms</button>
      <button 
        :class="{ active: activeTab === 'staff' }"
        @click="activeTab = 'staff'"
      >Staff</button>
      <button 
        :class="{ active: activeTab === 'equipment' }"
        @click="activeTab = 'equipment'"
      >Equipment</button>
    </div>

    <div class="tab-content">
      <div v-if="activeTab === 'ors'" class="resource-section">
        <h2>Operating Rooms List</h2>
        <button class="button-primary" @click="showAddOrForm = true" v-if="!showAddOrForm">Add New OR</button>

        <!-- Add OR Form (conditionally displayed) -->
        <AddOrForm v-if="showAddOrForm" @cancel="showAddOrForm = false" @save="handleSaveOr" />
        
        <table v-else>
          <thead>
            <tr>
              <th scope="col">Name/ID</th>
              <th scope="col">Location</th>
              <th scope="col">Status</th>
              <th scope="col">Primary Service</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="or in operatingRooms" :key="or.id">
              <td>{{ or.name }}</td>
              <td>{{ or.location }}</td>
              <td v-bind:class="'status-' + or.status.toLowerCase().replace(' ', '-')">{{ or.status }}</td>
              <td>{{ or.primaryService }}</td>
              <td>
                <button class="button-small">View/Edit</button>
                <button class="button-small button-danger" @click="deleteOr(or.id)">Delete</button>
              </td>
            </tr>
             <tr v-if="operatingRooms.length === 0">
                <td colspan="5" class="no-items">No operating rooms found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'staff'" class="resource-section">
        <h2>Staff List</h2>
         <button class="button-primary" @click="showAddStaffForm = true" v-if="!showAddStaffForm">Add New Staff</button>

         <!-- Add Staff Form (conditionally displayed) -->
         <AddStaffForm v-if="showAddStaffForm" @cancel="showAddStaffForm = false" @save="handleSaveStaff" />

         <table v-else>
            <thead>
                <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Role</th>
                    <th scope="col">Specialization(s)</th> 
                    <th scope="col">Status</th>
                     <th scope="col">Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="person in staff" :key="person.id">
                    <td>{{ person.name }}</td>
                    <td>{{ person.role }}</td>
                    <td>{{ person.specializations.join(', ') }}</td> 
                    <td>{{ person.status }}</td>
                    <td>
                        <button class="button-small">View/Edit</button>
                        <button class="button-small button-danger" @click="deleteStaff(person.id)">Delete</button>
                    </td>
                </tr>
                 <tr v-if="staff.length === 0">
                    <td colspan="5" class="no-items">No staff found.</td>
                </tr>
            </tbody>
         </table>
      </div>

      <div v-if="activeTab === 'equipment'" class="resource-section">
        <h2>Equipment List</h2>
        <button class="button-primary" @click="showAddEquipmentForm = true" v-if="!showAddEquipmentForm">Add New Equipment</button>
        
        <!-- Add Equipment Form (conditionally displayed) -->
        <AddEquipmentForm v-if="showAddEquipmentForm" @cancel="showAddEquipmentForm = false" @save="handleSaveEquipment" />

        <table v-else>
            <thead>
                <tr>
                    <th scope="col">Name/ID</th>
                    <th scope="col">Type</th>
                    <th scope="col">Status</th>
                    <th scope="col">Location</th>
                    <th scope="col">Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="item in equipment" :key="item.id">
                    <td>{{ item.name }}</td>
                    <td>{{ item.type }}</td> 
                    <td>{{ item.status }}</td>
                    <td>{{ item.location }}</td>
                    <td>
                        <button class="button-small">View/Edit</button>
                        <button class="button-small button-danger" @click="deleteEquipment(item.id)">Delete</button>
                    </td>
                </tr>
                 <tr v-if="equipment.length === 0">
                    <td colspan="5" class="no-items">No equipment found.</td>
                </tr>
            </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AddOrForm from './AddOrForm.vue'; 
import AddStaffForm from './AddStaffForm.vue'; 
import AddEquipmentForm from './AddEquipmentForm.vue'; 

const activeTab = ref('ors'); // Default active tab
const showAddOrForm = ref(false); // State to control OR form visibility
const showAddStaffForm = ref(false); // State to control Staff form visibility
const showAddEquipmentForm = ref(false); // State to control Equipment form visibility

// Simulated data for resources
const operatingRooms = ref([
    { id: 1, name: 'OR 1', location: 'Main Building, 2nd Floor', status: 'Active', primaryService: 'General Surgery' },
    { id: 2, name: 'OR 2', location: 'Main Building, 2nd Floor', status: 'Active', primaryService: 'Orthopedics' },
    { id: 3, name: 'OR 3', location: 'Main Building, 3rd Floor', status: 'Under Maintenance', primaryService: 'Cardiac Surgery' },
]);

const staff = ref([
    { id: 101, name: 'Dr. Jane Smith', role: 'Surgeon', specializations: ['Orthopedics', 'Sports Medicine'], status: 'Active' },
    { id: 102, name: 'Nurse John Doe', role: 'Scrub Nurse', specializations: ['General Surgery'], status: 'Active' },
    { id: 103, name: 'Dr. Emily Carter', role: 'Anesthetist', specializations: [], status: 'On Leave' },
]);

const equipment = ref([
    { id: 201, name: 'C-Arm Unit 1', type: 'C-Arm', status: 'Available', location: 'Storage Room A' },
    { id: 202, name: 'Anesthesia Machine B', type: 'Anesthesia Machine', status: 'In Use', location: 'OR 2' },
    { id: 203, name: 'Microscope Model X', type: 'Surgical Microscope', status: 'Available', location: 'Storage Room B' },
]);

// --- OR Management Logic ---
const handleSaveOr = (newOrData) => {
    console.log('Received new OR data:', newOrData);
    // Simulate adding to the list
    const newId = operatingRooms.value.length > 0 ? Math.max(...operatingRooms.value.map(or => or.id)) + 1 : 1;
    operatingRooms.value.push({ id: newId, ...newOrData });
    showAddOrForm.value = false; // Hide the form after save
};

// Placeholder methods for View/Edit and Delete
const viewEditOr = (or) => {
    console.log('Viewing/Editing OR:', or);
    // In a real app, navigate to an edit form or open a modal
};

const deleteOr = (orId) => {
    console.log('Attempting to delete OR with ID:', orId);
    // Simulate deletion from the list
    operatingRooms.value = operatingRooms.value.filter(or => or.id !== orId);
};
// --------------------------

// --- Staff Management Logic ---
const handleSaveStaff = (newStaffData) => {
     console.log('Received new Staff data:', newStaffData);
    // Simulate adding to the list
    const newId = staff.value.length > 0 ? Math.max(...staff.value.map(person => person.id)) + 1 : 101;
    staff.value.push({ id: newId, ...newStaffData });
    showAddStaffForm.value = false; // Hide the form after save
};

// Placeholder methods for View/Edit and Delete staff
const viewEditStaff = (person) => {
     console.log('Viewing/Editing Staff:', person);
     // In a real app, navigate to an edit form or open a modal
};

const deleteStaff = (personId) => {
     console.log('Attempting to delete Staff with ID:', personId);
     // Simulate deletion from the list
     staff.value = staff.value.filter(person => person.id !== personId);
};
// ----------------------------

// --- Equipment Management Logic ---
const handleSaveEquipment = (newEquipmentData) => {
     console.log('Received new Equipment data:', newEquipmentData);
    // Simulate adding to the list
    const newId = equipment.value.length > 0 ? Math.max(...equipment.value.map(item => item.id)) + 1 : 201;
    equipment.value.push({ id: newId, ...newEquipmentData });
    showAddEquipmentForm.value = false; // Hide the form after save
};

const viewEditEquipment = (item) => {
     console.log('Viewing/Editing Equipment:', item);
     // In a real app, navigate to an edit form or open a modal
};

const deleteEquipment = (itemId) => {
     console.log('Attempting to delete Equipment with ID:', itemId);
     // Simulate deletion from the list
     equipment.value = equipment.value.filter(item => item.id !== itemId);
};
// ----------------------------------

</script>

<style scoped>
.resource-management-container {
  padding: 20px;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--color-mid-light-gray);
}

.tabs button {
  padding: 10px 15px;
  border: none;
  background-color: transparent;
  cursor: pointer;
  font-size: 1em;
  color: var(--color-dark-gray);
  transition: color 0.2s ease, border-bottom-color 0.2s ease;
  border-bottom: 2px solid transparent; /* For active state underline */
  margin-right: 10px; /* Space between tabs */
}

.tabs button:hover {
  color: var(--color-very-dark-gray);
}

.tabs button.active {
  color: var(--color-primary-dark); /* Darker primary for active tab text */
  border-bottom-color: var(--color-primary); /* Primary color underline for active tab */
  font-weight: bold;
}

.tab-content {
  /* Styling for content area if needed */
}

.resource-section h2 {
    font-size: 1.2em;
    margin-top: 15px;
    margin-bottom: 10px;
     border-bottom: 1px solid var(--color-light-gray); /* Separator below sub-heading */
     padding-bottom: 5px;
}

.resource-section button.button-primary {
    margin-bottom: 15px; /* Space below add button */
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px; /* Space below add button or form */
  background-color: var(--color-white);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--color-mid-light-gray);
}

thead tr {
  background-color: var(--color-light-gray);
  border-bottom: 1px solid var(--color-mid-light-gray);
}

th,
td {
  padding: 10px 15px; /* Slightly reduced padding */
  text-align: left;
  border-bottom: 1px solid var(--color-mid-light-gray);
}

th {
  font-weight: 600;
  color: var(--color-very-dark-gray);
  font-size: 0.95em;
}

tbody tr:nth-child(even) {
  background-color: var(--color-light-gray); /* Zebra striping */
}

tbody tr:hover {
  background-color: #e9f5fe; /* Light blue hover effect */
}

.resource-section:nth-of-type(2) tbody tr:hover { /* Targeting Staff table */
  background-color: #e9f5fe; /* Light blue hover effect */
}

.resource-section:nth-of-type(3) tbody tr:hover { /* Targeting Equipment table */
  background-color: #e9f5fe; /* Light blue hover effect */
}

td:last-child { /* Target the Actions column */
    white-space: nowrap; /* Prevent buttons from wrapping */
}


.button-small {
     padding: 5px 10px; /* Defined small button style */
     font-size: 0.85em;
     margin-right: 5px;
}

.button-danger {
    background-color: var(--color-danger);
}

.button-danger:hover {
    background-color: #c82333;
}

.no-items {
    font-style: italic;
    color: var(--color-dark-gray);
 text-align: center;
    background-color: var(--color-light-gray); /* Subtle background color */
    padding: 20px;
}

.status-active {
    color: var(--color-success); /* Green for active/available */
    font-weight: bold;
}

.status-under-maintenance,
.status-in-use {
    color: var(--color-warning); /* Orange for in-use/under maintenance */
    font-weight: bold;
}

.status-available {
     color: var(--color-success); /* Green for active/available */
     font-weight: normal; /* Slightly less bold than active if needed */
}

.status-on-leave {
    color: var(--color-danger); /* Red for on leave */
    font-weight: bold;
}
</style>

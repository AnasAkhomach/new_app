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
      <!-- Operating Rooms Section -->
      <div v-if="activeTab === 'ors'" class="resource-section">
        <h2>Operating Rooms List</h2>
        <button class="button-primary" @click="openOrFormForAdd" v-if="!showAddOrForm">Add New OR</button>
        <AddOrForm
          v-if="showAddOrForm"
          :or-to-edit="currentOrToEdit"
          @cancel="handleCancelOrForm"
          @save="handleSaveOr"
        />
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
              <td :class="'status-' + or.status.toLowerCase().replace(' ', '-')">{{ or.status }}</td>
              <td>{{ or.primaryService }}</td>
              <td>
                <button class="button-small" @click="openOrFormForEdit(or)">View/Edit</button>
                <button class="button-small button-danger" @click="deleteOr(or)">Delete</button>  <!-- Pass the whole 'or' object -->
              </td>
            </tr>
            <tr v-if="operatingRooms.length === 0">
              <td colspan="5" class="no-items">No operating rooms found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Staff Section -->
      <div v-if="activeTab === 'staff'" class="resource-section">
        <h2>Staff List</h2>
        <button class="button-primary" @click="openStaffFormForAdd" v-if="!showAddStaffForm">Add New Staff</button>
        <AddStaffForm
          v-if="showAddStaffForm"
          :staff-to-edit="currentStaffToEdit"
          @cancel="handleCancelStaffForm"
          @save="handleSaveStaff"
        />
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
              <td :class="'status-' + person.status.toLowerCase().replace(' ', '-')">{{ person.status }}</td>
              <td>
                <button class="button-small" @click="openStaffFormForEdit(person)">View/Edit</button>
                <button class="button-small button-danger" @click="deleteStaff(person)">Delete</button> <!-- Pass the whole 'person' object -->
              </td>
            </tr>
            <tr v-if="staff.length === 0">
              <td colspan="5" class="no-items">No staff found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Equipment Section -->
      <div v-if="activeTab === 'equipment'" class="resource-section">
        <h2>Equipment List</h2>
        <button class="button-primary" @click="openEquipmentFormForAdd" v-if="!showAddEquipmentForm">Add New Equipment</button>
        <AddEquipmentForm
          v-if="showAddEquipmentForm"
          :equipment-to-edit="currentEquipmentToEdit"
          @cancel="handleCancelEquipmentForm"
          @save="handleSaveEquipment"
        />
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
              <td :class="'status-' + item.status.toLowerCase().replace(' ', '-')">{{ item.status }}</td>
              <td>{{ item.location }}</td>
              <td>
                <button class="button-small" @click="openEquipmentFormForEdit(item)">View/Edit</button>
                <button class="button-small button-danger" @click="deleteEquipment(item)">Delete</button> <!-- Pass the whole 'item' object -->
              </td>
            </tr>
            <tr v-if="equipment.length === 0">
              <td colspan="5" class="no-items">No equipment found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <ConfirmationModal
      v-if="showConfirmationModal"
      :title="confirmationTitle"
      :message="confirmationMessage"
      @confirm="handleConfirmDelete"
      @cancel="handleCancelDelete"
    />

  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useToast } from 'vue-toastification'; // Add this import
import AddOrForm from './AddOrForm.vue';
import AddStaffForm from './AddStaffForm.vue';
import AddEquipmentForm from './AddEquipmentForm.vue';
import ConfirmationModal from './ConfirmationModal.vue'; // Added import

const toast = useToast(); // Initialize useToast
const activeTab = ref('ors'); // Default active tab

// --- Confirmation Modal State & Logic ---
const showConfirmationModal = ref(false);
const itemToDelete = ref(null);
const itemTypeToDelete = ref(''); // 'or', 'staff', 'equipment'
const confirmationTitle = ref('Confirm Deletion');
const confirmationMessage = ref('Are you sure you want to delete this item? This action cannot be undone.');

const openConfirmationModal = (item, type, title, message) => {
  itemToDelete.value = item;
  itemTypeToDelete.value = type;
  confirmationTitle.value = title || 'Confirm Deletion';
  confirmationMessage.value = message || 'Are you sure you want to delete this item? This action cannot be undone.';
  showConfirmationModal.value = true;
};

const handleConfirmDelete = async () => { // Make the function async
  if (!itemToDelete.value || !itemTypeToDelete.value) return;

  const item = itemToDelete.value;
  const type = itemTypeToDelete.value;
  const itemName = item.name; // Get item name before potential deletion
  const itemTypeDisplay = type.charAt(0).toUpperCase() + type.slice(1);

  // Simulate API call
  try {
    // Simulate a delay and potential failure
    await new Promise((resolve, reject) => {
      setTimeout(() => {
        // Randomly succeed or fail for demonstration purposes
        if (Math.random() > 0.2) { // 80% chance of success
          resolve({ success: true });
        } else {
          reject(new Error('Simulated backend error'));
        }
      }, 1000); // 1 second delay
    });

    // If successful, update the local array
    if (type === 'or') {
      operatingRooms.value = operatingRooms.value.filter(or => or.id !== item.id);
    } else if (type === 'staff') {
      staff.value = staff.value.filter(s => s.id !== item.id);
    } else if (type === 'equipment') {
      equipment.value = equipment.value.filter(e => e.id !== item.id);
    }
    console.log(`Deleted ${type}:`, item);
    toast.success(`${itemTypeDisplay} '${itemName}' deleted successfully!`);

  } catch (error) {
    console.error(`Failed to delete ${type}:`, item, error);
    toast.error(`Failed to delete ${itemTypeDisplay} '${itemName}'. Please try again.`);
  }

  handleCancelDelete(); // Close modal and reset state regardless of outcome
};

const handleCancelDelete = () => {
  showConfirmationModal.value = false;
  itemToDelete.value = null;
  itemTypeToDelete.value = '';
  confirmationTitle.value = 'Confirm Deletion'; // Reset to default
  confirmationMessage.value = 'Are you sure you want to delete this item? This action cannot be undone.'; // Reset to default
};

// --- OR Management State & Logic ---
const showAddOrForm = ref(false);
const currentOrToEdit = ref(null);
const operatingRooms = ref([
  { id: 1, name: 'OR 1', location: 'Main Building, 2nd Floor', status: 'Active', primaryService: 'General Surgery' },
  { id: 2, name: 'OR 2', location: 'Main Building, 2nd Floor', status: 'Active', primaryService: 'Orthopedics' },
  { id: 3, name: 'OR 3', location: 'Main Building, 3rd Floor', status: 'Under Maintenance', primaryService: 'Cardiac Surgery' },
]);

const openOrFormForAdd = () => {
  currentOrToEdit.value = null;
  showAddOrForm.value = true;
};
const openOrFormForEdit = (or) => {
  currentOrToEdit.value = { ...or };
  showAddOrForm.value = true;
};
const handleCancelOrForm = () => {
  showAddOrForm.value = false;
  currentOrToEdit.value = null;
};
const handleSaveOr = (orData) => {
  if (currentOrToEdit.value) {
    // Editing existing OR
    const index = operatingRooms.value.findIndex(or => or.id === orData.id);
    if (index !== -1) {
      operatingRooms.value[index] = { ...operatingRooms.value[index], ...orData };
      toast.success(`Operating Room '${orData.name}' updated successfully!`); // Add this line
    }
  } else {
    // Adding new OR
    const newOr = {
      id: Date.now().toString(), // Simple unique ID generator
      ...orData,
    };
    operatingRooms.value.push(newOr);
    toast.success(`Operating Room '${orData.name}' added successfully!`); // Add this line
  }
  showAddOrForm.value = false;
  currentOrToEdit.value = null;
};
const deleteOr = (orItem) => {
  openConfirmationModal(
    orItem,
    'or',
    'Delete Operating Room?',
    `Are you sure you want to delete the operating room "${orItem.name}"? This action cannot be undone.`
  );
};

// --- Staff Management State & Logic ---
const showAddStaffForm = ref(false);
const currentStaffToEdit = ref(null);
const staff = ref([
  { id: 101, name: 'Dr. Jane Smith', role: 'Surgeon', specializations: ['Orthopedics', 'Sports Medicine'], status: 'Active' },
  { id: 102, name: 'Nurse John Doe', role: 'Scrub Nurse', specializations: ['General Surgery'], status: 'Active' },
  { id: 103, name: 'Dr. Emily Carter', role: 'Anesthetist', specializations: [], status: 'On Leave' },
]);

const openStaffFormForAdd = () => {
  currentStaffToEdit.value = null;
  showAddStaffForm.value = true;
};
const openStaffFormForEdit = (staffMember) => {
  currentStaffToEdit.value = { ...staffMember };
  showAddStaffForm.value = true;
};
const handleCancelStaffForm = () => {
  showAddStaffForm.value = false;
  currentStaffToEdit.value = null;
};
const handleSaveStaff = (staffData) => {
  if (currentStaffToEdit.value) {
    // Editing existing staff
    const index = staff.value.findIndex(s => s.id === staffData.id);
    if (index !== -1) {
      staff.value[index] = { ...staff.value[index], ...staffData };
      toast.success(`Staff member '${staffData.name}' updated successfully!`); // Add this line
    }
  } else {
    // Adding new staff
    const newStaff = {
      id: Date.now().toString(), // Simple unique ID generator
      ...staffData,
    };
    staff.value.push(newStaff);
    toast.success(`Staff member '${staffData.name}' added successfully!`); // Add this line
  }
  showAddStaffForm.value = false;
  currentStaffToEdit.value = null;
};
const deleteStaff = (staffItem) => {
  openConfirmationModal(
    staffItem,
    'staff',
    'Delete Staff Member?',
    `Are you sure you want to delete staff member "${staffItem.name}"? This action cannot be undone.`
  );
};

// --- Equipment Management State & Logic ---
const showAddEquipmentForm = ref(false);
const currentEquipmentToEdit = ref(null); // Added for equipment editing
const equipment = ref([
  { id: 201, name: 'C-Arm Unit 1', type: 'C-Arm', status: 'Available', location: 'Storage Room A' },
  { id: 202, name: 'Anesthesia Machine B', type: 'Anesthesia Machine', status: 'In Use', location: 'OR 2' },
  { id: 203, name: 'Microscope Model X', type: 'Surgical Microscope', status: 'Available', location: 'Storage Room B' },
]);

const openEquipmentFormForAdd = () => {
  currentEquipmentToEdit.value = null;
  showAddEquipmentForm.value = true;
};

const openEquipmentFormForEdit = (equipmentItem) => {
  currentEquipmentToEdit.value = { ...equipmentItem };
  showAddEquipmentForm.value = true;
};

const handleCancelEquipmentForm = () => {
  showAddEquipmentForm.value = false;
  currentEquipmentToEdit.value = null;
};

const handleSaveEquipment = (equipmentData) => {
  if (currentEquipmentToEdit.value) {
    // Editing existing equipment
    const index = equipment.value.findIndex(eq => eq.id === equipmentData.id);
    if (index !== -1) {
      equipment.value[index] = { ...equipment.value[index], ...equipmentData };
      toast.success(`Equipment '${equipmentData.name}' updated successfully!`); // Add this line
    }
  } else {
    // Adding new equipment
    const newEquipment = {
      id: Date.now().toString(), // Simple unique ID generator
      ...equipmentData,
    };
    equipment.value.push(newEquipment);
    toast.success(`Equipment '${equipmentData.name}' added successfully!`); // Add this line
  }
  showAddEquipmentForm.value = false;
  currentEquipmentToEdit.value = null;
};

const deleteEquipment = (equipmentItem) => {
  openConfirmationModal(
    equipmentItem,
    'equipment',
    'Delete Equipment?',
    `Are you sure you want to delete equipment "${equipmentItem.name}"? This action cannot be undone.`
  );
};

// Removed duplicate deleteEquipment function

// TODO: Add backend integration for all CRUD operations
// TODO: Add form validation to all forms
// TODO: Improve UI/UX (e.g., loading states, success/error notifications)

</script>

<style scoped>
.resource-management-container {
  padding: 20px;
  font-family: sans-serif;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ccc;
}

.tabs button {
  padding: 10px 20px;
  cursor: pointer;
  border: none;
  background-color: transparent;
  font-size: 16px;
  border-bottom: 3px solid transparent; /* For active state */
  margin-bottom: -1px; /* Align with container's border */
}

.tabs button.active {
  border-bottom: 3px solid #007bff;
  color: #007bff;
  font-weight: bold;
}

.tab-content .resource-section {
  margin-bottom: 30px;
}

.resource-section h2 {
  margin-bottom: 15px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.button-primary {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 15px; /* Space before the table or form */
}

.button-primary:hover {
  background-color: #0056b3;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

th, td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
}

th {
  background-color: #e9ecef;
  color: #495057;
  font-weight: bold;
}

.button-small {
  padding: 5px 10px;
  font-size: 12px;
  margin-right: 5px;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid #ccc;
  background-color: #f8f9fa;
}

.button-small:hover {
  background-color: #e2e6ea;
}

.button-danger {
  background-color: #dc3545;
  color: white;
  border-color: #dc3545;
}

.button-danger:hover {
  background-color: #c82333;
  border-color: #bd2130;
}

.no-items {
    text-align: center;
    color: #6c757d;
    padding: 20px;
    font-style: italic;
}

/* Status-specific styling */
.status-active,
.status-available {
  color: #28a745; /* Green */
  font-weight: bold;
}

.status-under-maintenance {
  color: #ffc107; /* Yellow */
  font-weight: bold;
}

.status-inactive,
.status-on-leave,
.status-retired {
  color: #dc3545; /* Red */
  font-weight: bold;
}

.status-in-use {
    color: #fd7e14; /* Orange */
    font-weight: bold;
}

</style>
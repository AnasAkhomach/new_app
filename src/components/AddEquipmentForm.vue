<template>
  <div class="add-equipment-form">
    <h3>Add New Equipment</h3>
    <form @submit.prevent="handleSubmit">
      <div class="input-group">
        <label for="equipment-name">Name/ID</label>
        <input type="text" id="equipment-name" v-model="equipmentData.name" required>
      </div>

      <div class="input-group">
        <label for="equipment-type">Type</label>
        <input type="text" id="equipment-type" v-model="equipmentData.type" required>
      </div>

      <div class="input-group">
        <label for="equipment-status">Status</label>
        <select id="equipment-status" v-model="equipmentData.status" required>
          <option value="">Select Status</option>
          <option value="Available">Available</option>
          <option value="In Use">In Use</option>
          <option value="Maintenance">Maintenance</option>
          <option value="Retired">Retired</option>
        </select>
      </div>

       <div class="input-group">
        <label for="equipment-location">Location</label>
        <input type="text" id="equipment-location" v-model="equipmentData.location">
         <small>E.g., OR 5, Storage Room B</small>
      </div>

      <div class="form-actions">
        <button type="submit" class="button-primary">Save Equipment</button>
        <button type="button" class="button-secondary" @click="handleCancel">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Define initial form data structure
const equipmentData = ref({
  name: '',
  type: '',
  status: '',
  location: '',
});

// Define emits to communicate with parent (e.g., ResourceManagementScreen)
const emit = defineEmits(['save', 'cancel']);

const handleSubmit = () => {
  console.log('Submitting Equipment data:', equipmentData.value);
  // In a real app, send this data to the backend to save
  // For now, emit the data to the parent component
  emit('save', equipmentData.value);
  // Reset form after simulated save
   equipmentData.value = { name: '', type: '', status: '', location: '' };
};

const handleCancel = () => {
  console.log('Cancelling Equipment form');
  // Reset form
  equipmentData.value = { name: '', type: '', status: '', location: '' };
  // Emit an event to parent to indicate cancellation
  emit('cancel');
};

</script>

<style scoped>
.add-equipment-form {
  background-color: var(--color-white);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--color-mid-light-gray);
  margin-top: 20px; /* Space above the form */
  max-width: 600px; /* Limit form width */
  margin-left: auto;
  margin-right: auto; /* Center the form */
}

.add-equipment-form h3 {
    font-size: 1.1em;
    margin-top: 0;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--color-mid-light-gray);
}

.input-group {
  margin-bottom: 15px;
}

.input-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: var(--color-dark-gray);
  font-size: 0.9em;
}

.input-group input[type="text"],
.input-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-gray);
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 1em;
  color: var(--color-very-dark-gray);
  background-color: var(--color-white);
}

.input-group input:focus,
.input-group select:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.input-group small {
    display: block;
    margin-top: 5px;
    color: var(--color-dark-gray);
    font-size: 0.85em;
    font-style: italic;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end; /* Align buttons to the right */
  gap: 10px; /* Space between buttons */
}

.form-actions button {
    padding: 10px 20px;
    font-size: 1em;
}

.button-primary {
     background-color: var(--color-primary);
     color: var(--color-white);
     border: none;
}

.button-primary:hover {
    background-color: var(--color-primary-dark);
}

.button-secondary {
     background-color: var(--color-secondary);
     color: var(--color-white);
     border: none;
}

.button-secondary:hover {
     background-color: #5a6268;
}


</style>
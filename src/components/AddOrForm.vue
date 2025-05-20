<template>
  <div class="add-or-form">
    <h3>Add New Operating Room</h3>
    <form @submit.prevent="handleSubmit">
      <div class="input-group">
        <label for="or-name">Name/ID</label>
        <input type="text" id="or-name" v-model="orData.name" required>
      </div>

      <div class="input-group">
        <label for="or-location">Location</label>
        <input type="text" id="or-location" v-model="orData.location">
      </div>

      <div class="input-group">
        <label for="or-status">Status</label>
        <select id="or-status" v-model="orData.status" required>
          <option value="">Select Status</option>
          <option value="Active">Active</option>
          <option value="Under Maintenance">Under Maintenance</option>
          <option value="Inactive">Inactive</option>
        </select>
      </div>

      <div class="input-group">
        <label for="or-service">Primary Service</label>
        <input type="text" id="or-service" v-model="orData.primaryService">
      </div>

      <div class="form-actions">
        <button type="submit" class="button-primary">Save OR</button>
        <button type="button" class="button-secondary" @click="handleCancel">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Define initial form data structure
const orData = ref({
  name: '',
  location: '',
  status: '',
  primaryService: '',
});

const handleSubmit = () => {
  console.log('Submitting OR data:', orData.value);
  // Placeholder for sending data to backend or parent component
  // After successful save, reset form and close/hide form
};

const handleCancel = () => {
  console.log('Cancelling OR form');
  // Placeholder for resetting form and closing/hiding form
  orData.value = { name: '', location: '', status: '', primaryService: '' }; // Reset form
  // Emit an event to parent to indicate cancellation
  // emit('cancel'); 
};

// Define emits if using events to communicate with parent
// const emit = defineEmits(['save', 'cancel']);

</script>

<style scoped>
.add-or-form {
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

.add-or-form h3 {
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
<template>
  <div class="gantt-container">
    <div class="gantt-header">
      <!-- Date navigation and view controls would go here -->
      <h3>Operating Room Schedule (Hourly View)</h3>
      <div class="view-controls">
          <!-- Example controls -->
           <button class="btn btn-secondary" @click="scheduleStore.updateGanttViewMode('Day')">Day</button>
           <button class="btn btn-secondary" @click="scheduleStore.updateGanttViewMode('Week')">Week</button>
           <!-- <button class="btn btn-secondary" @click="scheduleStore.updateGanttViewMode('Month')">Month</button> -->
           <!-- Date picker for navigation -->
           <!-- <input type="date" @change="handleDateChange($event.target.value)" /> -->
      </div>
    </div>
    <div class="gantt-grid" ref="ganttGrid">
      <div class="gantt-time-axis">
        <!-- Hourly markers (adjust based on view mode) -->
        <div v-for="hour in hours" :key="hour" class="time-marker">{{ String(hour).padStart(2, '0') }}:00</div>
      </div>
      <div class="gantt-or-rows">
          <div v-for="or in availableOperatingRooms" :key="or.id" class="gantt-or-row"
               @dragover.prevent="onDragOver($event, or.id)"
               @drop="onDrop($event, or.id)"
               :aria-label="`Operating Room: ${or.name}`"
          >
            <div class="or-label">{{ or.name }}</div>
            <div class="or-timeline">
              <!-- Surgery blocks will be positioned here -->
              <div
                v-for="surgery in getSurgeriesForOR(or.id)"
                :key="surgery.id"
                :style="getSurgeryBlockStyle(surgery)"
                :class="{'surgery-block': true, 'has-conflict': surgery.conflicts && surgery.conflicts.length > 0}"
                @mouseover="showTooltip($event, surgery)"
                @mouseleave="hideTooltip"
                @click="selectSurgery(surgery)"
                draggable="true"
                @dragstart="onDragStart($event, surgery)"
                :aria-label="getSurgeryAccessibleLabel(surgery)"
                :aria-invalid="surgery.conflicts && surgery.conflicts.length > 0 ? 'true' : null"
                tabindex="0" <!-- Make surgery blocks focusable -->
              >
                <div class="sdst-segment" :style="getSDSTSegmentStyle(surgery)"></div>
                <div class="surgery-info">
                  {{ surgery.patientName }} - {{ surgery.type }}
                </div>
                <!-- Conflict Indicator Icon (WCAG 1.4.1 - not relying on color alone) -->
                 <span v-if="surgery.conflicts && surgery.conflicts.length > 0" class="conflict-indicator" aria-hidden="true">⚠️</span>
              </div>
            </div>
          </div>
      </div>
    </div>

    <!-- Basic tooltip component (replace with a proper one) -->
     <div v-if="tooltip.visible" class="surgery-tooltip" :style="tooltip.style" role="tooltip">
        <strong>{{ tooltip.surgery?.patientName }}</strong><br>
        Type: {{ tooltip.surgery?.fullType }}<br>
        Surgeon: {{ tooltip.surgery?.surgeon }}<br>
        Time: {{ formatTime(tooltip.surgery?.startTime) }} - {{ formatTime(tooltip.surgery?.endTime) }}<br>
        Duration: {{ tooltip.surgery?.duration }} min<br>
        SDST: {{ tooltip.surgery?.sdsTime }} min (from {{ tooltip.surgery?.precedingType || 'Initial' }} to {{ tooltip.surgery?.type }})
         <div v-if="tooltip.surgery?.conflicts && tooltip.surgery.conflicts.length > 0" class="tooltip-conflicts">
             <strong>Conflicts:</strong>
             <ul>
                 <li v-for="(c, idx) in tooltip.surgery.conflicts" :key="idx">{{ c }}</li>
             </ul>
         </div>
     </div>

    <!-- Accessible Table View (Visually Hidden) -->
    <GanttAccessibleTable />

    <!-- Loading Indicator -->
    <div v-if="scheduleStore.isLoading" class="loading-overlay">Loading Schedule...</div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useScheduleStore } from '@/stores/scheduleStore';
import { storeToRefs } from 'pinia';
import GanttAccessibleTable from './GanttAccessibleTable.vue';

const scheduleStore = useScheduleStore();
// Use storeToRefs to get reactive state and getters from the store
const { visibleScheduledSurgeries, availableOperatingRooms, currentDateRange, isLoading } = storeToRefs(scheduleStore);

const tooltip = ref({
  visible: false,
  surgery: null,
  style: {}
});

// Computed property for generating hourly time markers based on current view range
const hours = computed(() => {
  const start = currentDateRange.value.start;
  const end = currentDateRange.value.end;
  const startHour = start.getHours();
  const endHour = end.getHours(); // Assuming end is within the same day for hourly view
  // Adjust this logic for Week/Month view modes
  if (scheduleStore.ganttViewMode === 'Day') {
     const hoursArray = [];
     // Ensure we include the end hour if it's on the hour
     for(let h = startHour; h <= endHour; h++) {
         hoursArray.push(h);
     }
     return hoursArray;
  } else {
      // Logic for Week/Month view time markers (e.g., days of the week, weeks of the month)
      return []; // Placeholder
  }
});

// Get surgeries for a specific OR within the current view, sorted by time (using store getter)
const getSurgeriesForOR = (orId) => {
  // Directly use the getter from the store instance
  return scheduleStore.getSurgeriesForOR(orId);
};

// --- Styling Logic (Simplified) ---
// Define a scale (pixels per minute) for the Gantt chart based on the view mode
const pixelsPerMinute = computed(() => {
    // Adjust scaling based on view mode (Day, Week, Month)
    if (scheduleStore.ganttViewMode === 'Day') {
        // Assuming 100px per hour marker, calculate pixels per minute
        return 100 / 60; // 100px per hour = 100/60 pixels per minute
    } else if (scheduleStore.ganttViewMode === 'Week') {
         // Example scale for week view (e.g., 24px per hour, 24*24 = 576px per day)
        return (24) / 60; // 24px per hour = 24/60 pixels per minute
    } else {
        return 0; // Placeholder for other modes
    }
});

const getSurgeryBlockStyle = (surgery) => {
  const startTime = new Date(surgery.startTime);
  const endTime = new Date(surgery.endTime); // Use endTime from processed data in store
  const durationWithSDST = (endTime.getTime() - startTime.getTime()) / (1000 * 60); // Duration including SDST in minutes

  const viewStartTime = currentDateRange.value.start;
  const startMinutesFromViewStart = (startTime.getTime() - viewStartTime.getTime()) / (1000 * 60);


  const leftPosition = startMinutesFromViewStart * pixelsPerMinute.value;
  const width = durationWithSDST * pixelsPerMinute.value;

  // Get the surgery type color using CSS variable convention
  const surgeryTypeColorVar = `--color-surgery-${surgery.type.toLowerCase()}`; // Assuming type is a short code like 'CABG', 'KNEE'
   // Access global CSS variables via getComputedStyle from the document element
   const element = document.documentElement; // Or a specific element if variables are scoped differently
  const surgeryColor = getComputedStyle(element).getPropertyValue(surgeryTypeColorVar).trim();


  return {
    left: `${leftPosition}px`,
    width: `${width}px`,
    backgroundColor: surgeryColor || 'var(--vt-c-blue)', // Apply type-specific color, fallback to a default
  };
};

const getSDSTSegmentStyle = (surgery) => {
   const sdstWidth = surgery.sdsTime * pixelsPerMinute.value; // Width based on calculated SDST and scale

   return {
     width: `${sdstWidth}px`,
     'background-color': `var(--color-sdst-segment)`, // Distinct color for SDST (using global variable)
     'border-right': '1px solid var(--color-sdst-border)', // Separator (using global variable)
     'flex-shrink': 0, // Prevent shrinking of the segment
   };
}

// --- Interaction Logic ---
const selectSurgery = (surgery) => {
  scheduleStore.selectSurgery(surgery.id);
};

const showTooltip = (event, surgery) => {
  tooltip.value.surgery = surgery;
  tooltip.value.visible = true;

  // Position tooltip near the element
  const rect = event.target.getBoundingClientRect();
  tooltip.value.style = {
    top: `${rect.bottom + 5}px`, // Position below the element
    left: `${rect.left}px`,
    // Adjust positioning if near edge of screen
    transform: 'translateX(-50%)', // Center tooltip above the element
    left: `${rect.left + rect.width / 2}px`,
  };
};

const hideTooltip = () => {
  tooltip.value.visible = false;
  tooltip.value.surgery = null;
  tooltip.value.style = {};
};

const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
};

// --- Drag and Drop Logic (Conceptual) ---
let draggedSurgeryId = null;

const onDragStart = (event, surgery) => {
  draggedSurgeryId = surgery.id;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', surgery.id);
  // Add a class to the dragged item for visual feedback
  setTimeout(() => {
      event.target.classList.add('is-dragging');
  }, 0); // Use setTimeout to allow drag image to be set before class is added
};

const onDragOver = (event, orId) => {
  event.preventDefault(); // Necessary to allow dropping

  // --- Conceptual Real-time Feedback During Drag ---
  // This is complex and would involve:
  // 1. Calculating the precise potential drop time based on event.clientX, OR row, scroll position, zoom level.
  // 2. Using the store/API to get potential SDST for the drop location (preceding surgery type).
  // 3. Using the store/API to check for resource and time conflicts at the potential new time.
  // 4. Visually updating a temporary representation of the dragged surgery + SDST on the timeline.
  // 5. Highlighting conflicts visually.
  // This requires a sophisticated drag logic or a feature-rich Gantt library.

  event.dataTransfer.dropEffect = 'move';
};

// handle drag leave to remove visual cues
// const onDragLeave = (event) => {
//      event.target.closest('.gantt-or-row').classList.remove('drag-over');
// };

const onDrop = (event, targetORId) => {
  event.preventDefault();

  const surgeryId = event.dataTransfer.getData('text/plain');

  // --- Calculate Drop Time ---
  // This is highly simplified. Needs to map pixel position to date/time accurately.
  const ganttTimeline = event.target.closest('.or-timeline');
  if (!ganttTimeline) {
      console.warn("Drop target is not a timeline.");
      return;
  }
  const timelineRect = ganttTimeline.getBoundingClientRect();
  const clickX = event.clientX - timelineRect.left;
  const scrollX = ganttTimeline.parentElement.parentElement.scrollLeft; // Account for horizontal scroll
  const totalX = clickX + scrollX;

  const minutesFromViewStart = totalX / pixelsPerMinute.value;
  const newStartTime = new Date(currentDateRange.value.start.getTime() + minutesFromViewStart * 60 * 1000);

   // Optional: Snap to grid (e.g., snap to nearest 15 minutes)
    const minutes = newStartTime.getMinutes();
    newStartTime.setMinutes(Math.round(minutes / 15) * 15, 0, 0);


  console.log(`Dropped surgery ${surgeryId} in OR ${targetORId} at potential time ${newStartTime.toISOString()}`);

  // --- Call Store Action to Reschedule ---
  // The store action will handle the actual state update and backend communication.
  scheduleStore.rescheduleSurgery(surgeryId, targetORId, newStartTime);

   // Remove dragging class after drop (or after store update confirms success)
   const draggedElement = document.querySelector('.surgery-block.is-dragging');
   if(draggedElement) {
       draggedElement.classList.remove('is-dragging');
   }

  draggedSurgeryId = null; // Reset
};

// --- Accessibility ---
const getSurgeryAccessibleLabel = (surgery) => {
    // Provide a comprehensive label for screen readers, including conflict info
    let label = `Surgery: ${surgery.fullType} for ${surgery.patientName}, scheduled in OR ${surgery.orName} from ${formatTime(surgery.startTime)} to ${formatTime(surgery.endTime)}. Estimated duration: ${surgery.estimatedDuration} minutes.`;

    if (surgery.sdsTime > 0) {
        label += ` Requires ${surgery.sdsTime} minutes setup time due to preceding ${surgery.precedingType || 'Initial'} surgery.`;
    }

     if (surgery.conflicts && surgery.conflicts.length > 0) {
         label += ` Alerts: ${surgery.conflicts.join(', ')}.`;
     }

    return label;
};

// Lifecycle hook to load initial data when component is mounted
onMounted(() => {
    // Ensure initial data is loaded for the schedule
    // This might be called here, or in a parent component like SurgerySchedulingScreen,
    // or triggered by router navigation.
    // Calling here ensures data is present if this is the entry point or refreshed when component is mounted/re-mounted.
    scheduleStore.loadInitialData();
});

</script>

<style scoped>
.gantt-container {
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Keep layout clean */
  height: 100%; /* Takes full height of parent */
  position: relative; /* Needed for absolute positioning of tooltip/loading */
}

.gantt-header {
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0; /* Prevent header from shrinking */
}

.view-controls button {
    margin-left: var(--spacing-sm);
}

.gantt-grid {
  display: flex;
  flex-grow: 1;
  overflow-x: auto; /* Allow horizontal scrolling for the timeline */
  position: relative;
  padding-left: 80px; /* Space for OR labels */
  padding-bottom: var(--spacing-md); /* Add padding for scrollbar */
}

.gantt-time-axis {
  position: sticky; /* Keep time axis visible on horizontal scroll */
  left: 80px; /* Position after OR labels */
  top: 0; /* Stick to the top of the scrollable area */
  height: 100%;
  display: flex;
  flex-direction: row; /* Ensure markers are in a row */
  pointer-events: none; /* Allow clicks/drags to pass through */
   z-index: 1; /* Ensure it's above the timeline background */
   background-color: var(--color-background-soft); /* Use global variable */
   border-right: 1px solid var(--color-border); /* Add border for separation */
}

.time-marker {
  width: 100px; /* Fixed width per hour */
  min-width: 100px; /* Ensure fixed width */
  border-right: 1px dashed var(--color-border-soft); /* Use global variable */
  padding-top: var(--spacing-sm); /* Use global variable */
  font-size: var(--font-size-sm); /* Use global variable */
  color: var(--color-text-secondary); /* Use global variable */
  flex-shrink: 0; /* Prevent shrinking */
   text-align: center;
}

.gantt-or-rows {
    display: flex;
    flex-direction: column; /* Stack OR rows vertically */
    flex-grow: 1;
    /* The min-width here should be the calculated total width of the timeline based on date range and scale */
    min-width: calc(100px * 14); /* Example: 14 hours visible, 100px per hour */
    position: relative; /* Container for absolute positioned surgery blocks */
    padding-left: 0;
}

.gantt-or-row {
  display: flex;
  border-bottom: 1px solid var(--color-border); /* Use global variable */
  min-height: 50px; /* Row height */
  flex-shrink: 0;
  width: 100%;
}

.or-label {
  width: 80px; /* Fixed width for OR label */
  min-width: 80px; /* Ensure fixed width */
  flex-shrink: 0;
  text-align: right;
  padding: var(--spacing-sm); /* Use global variable */
  font-weight: var(--font-weight-bold); /* Use global variable */
  border-right: 1px solid var(--color-border); /* Use global variable */
  background-color: var(--color-background-soft); /* Use global variable */
  display: flex;
  align-items: center;
  justify-content: flex-end;
  position: sticky;
  left: 0;
   z-index: 2;
}

.or-timeline {
  position: relative;
  flex-grow: 1;
  /* Add background grid lines here if simulating without library */
  /* Example grid lines (vertical) */
  /* background-image: linear-gradient(to right, var(--color-border-soft) 1px, transparent 1px); */
  /* background-size: 100px 100%; /* Match time-marker width */
}

.surgery-block {
  position: absolute;
  top: 5px;
  bottom: 5px;
  background-color: var(--vt-c-blue); /* Fallback or default color */
  border-radius: var(--border-radius-sm); /* Use global variable */
  color: var(--color-text-inverted); /* Use global variable */
  padding: var(--spacing-xs); /* Use global variable */
  overflow: hidden;
  white-space: nowrap;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.2s ease; /* Smooth transition on hover */
  box-sizing: border-box;
  font-size: var(--font-size-sm); /* Use global variable */
  z-index: 5;
}

.surgery-block:hover {
   box-shadow: 0 0 5px rgba(0,0,0,0.2);
}

.surgery-block.is-dragging {
    opacity: 0.6;
    border: 2px dashed var(--color-accent); /* Use global variable */
    background-color: var(--color-background-mute); /* Use global variable */
}

/* Style for conflicts */
.surgery-block.has-conflict {
    background-color: var(--color-error); /* Error color for background */
     outline: 2px solid rgba(0, 0, 0, 0.2); /* Use rgba for darkening effect */
     /* Add visual pattern for accessibility */
     background-image: linear-gradient(45deg, rgba(255, 255, 255, 0.15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, 0.15) 50%, rgba(255, 255, 255, 0.15) 75%, transparent 75%, transparent);
    background-size: 15px 15px;
}

/* Ensure text is readable on red background */
.surgery-block.has-conflict .surgery-info {
    color: var(--color-text-inverted);
}

.sdst-segment {
  height: 100%;
  background-color: var(--color-sdst-segment); /* Use global variable */
  margin-right: var(--spacing-xs); /* Use global variable */
  flex-shrink: 0;
   border-top-left-radius: var(--border-radius-sm); /* Use global variable */
   border-bottom-left-radius: var(--border-radius-sm); /* Use global variable */
}

.surgery-info {
  flex-grow: 1;
  text-overflow: ellipsis;
  overflow: hidden;
}

.conflict-indicator {
    margin-left: var(--spacing-xs); /* Use global variable */
    font-size: var(--font-size-base); /* Use global variable */
    color: var(--color-text-inverted); /* Icon color */
    flex-shrink: 0;
}

.surgery-tooltip {
  position: fixed;
  background-color: var(--color-background); /* Use global variable */
  border: 1px solid var(--color-border); /* Use global variable */
  padding: var(--spacing-sm); /* Use global variable */
  border-radius: var(--border-radius-sm); /* Use global variable */
  pointer-events: none;
  z-index: var(--z-index-tooltip); /* Use variable */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
   color: var(--color-text); /* Use global variable */
   font-size: var(--font-size-sm); /* Use global variable */
   max-width: 300px;
   word-wrap: break-word;
}

.tooltip-conflicts {
    margin-top: var(--spacing-sm); /* Use global variable */
    padding-top: var(--spacing-sm); /* Use global variable */
    border-top: 1px solid var(--color-border-soft); /* Use global variable */
    color: var(--color-error); /* Use global variable */
}

.tooltip-conflicts ul {
    padding-left: var(--spacing-md); /* Use global variable */
    margin-bottom: 0;
}

.tooltip-conflicts li {
    margin-bottom: var(--spacing-xs); /* Use global variable */
}

.loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: var(--font-size-lg); /* Use global variable */
    color: var(--color-primary); /* Use global variable */
    z-index: var(--z-index-modal); /* Above other content */
}

/* Add drag-over styles for drop targets if desired */
/* .gantt-or-row.drag-over .or-timeline { outline: 2px dashed var(--color-accent); } */

</style>

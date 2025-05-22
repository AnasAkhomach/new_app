// src/stores/scheduleStore.js
import { defineStore } from 'pinia';
// Assuming these API services exist for fetching/updating data
// import { fetchScheduleData, updateSchedule, cancelSurgeryApi, fetchSDSTData, fetchResourceData } from '@/api';

export const useScheduleStore = defineStore('schedule', {
  state: () => ({
    // --- Core Schedule Data ---
    scheduledSurgeries: [
      // Example Data Structure (will be fetched from backend)
      {
        id: 's-1', patientId: 'P101', patientName: 'Alice Smith',
        type: 'CABG', fullType: 'Cardiac - Coronary Artery Bypass Graft',
        estimatedDuration: 240, duration: 240, priority: 'High',
        startTime: '2023-10-27T08:00:00Z', endTime: '2023-10-27T12:00:00Z',
        orId: 'OR1', orName: 'Operating Room 1',
        surgeonId: 'SG1', surgeon: 'Dr. Jane Smith',
        requiredSurgeons: ['Dr. Jane Smith'], requiredStaffRoles: ['Anesthetist', 'Scrub Nurse'], requiredEquipment: ['Heart-Lung Machine'],
        status: 'Scheduled',
        // These will be calculated/added after fetching schedule data based on sequence
        sdsTime: 30, // Example calculated SDST
        precedingType: 'Knee Replacement', // Example preceding surgery type
        conflicts: [], // Example: ['Surgeon unavailable']
      },
       {
        id: 's-2', patientId: 'P102', patientName: 'Bob Johnson',
        type: 'KNEE', fullType: 'Orthopedic - Knee Replacement',
        estimatedDuration: 120, duration: 120, priority: 'Medium',
        startTime: '2023-10-27T12:30:00Z', endTime: '2023-10-27T14:30:00Z', // Assuming 30 min setup after s-1
        orId: 'OR1', orName: 'Operating Room 1',
        surgeonId: 'SG2', surgeon: 'Dr. Bill Adams',
        requiredSurgeons: ['Dr. Bill Adams'], requiredStaffRoles: ['Scrub Nurse'], requiredEquipment: ['Arthroscope'],
        status: 'Scheduled',
        sdsTime: 15, // Example calculated SDST
        precedingType: 'CABG', // Example preceding surgery type
        conflicts: [],
      },
       {
        id: 's-3', patientId: 'P103', patientName: 'Charlie Davis',
        type: 'APPEN', fullType: 'General - Appendectomy',
        estimatedDuration: 60, duration: 60, priority: 'High',
        startTime: '2023-10-27T09:00:00Z', endTime: '2023-10-27T10:00:00Z',
        orId: 'OR2', orName: 'Operating Room 2',
        surgeonId: 'SG3', surgeon: 'Dr. Sarah Chen',
        requiredSurgeons: ['Dr. Sarah Chen'], requiredStaffRoles: ['Circulating Nurse'], requiredEquipment: [],
        status: 'Scheduled',
        sdsTime: 0, // Example calculated SDST (e.g., initial setup might be 0 or included in surgery duration)
        precedingType: 'Initial', // First case of the day
        conflicts: [],
      },
       {
        id: 's-4', patientId: 'P104', patientName: 'Donna Miller',
        type: 'CABG', fullType: 'Cardiac - Coronary Artery Bypass Graft',
        estimatedDuration: 240, duration: 240, priority: 'Medium',
        startTime: '2023-10-27T10:30:00Z', endTime: '2023-10-27T14:30:00Z', // Assuming 30 min setup after s-3 type APPEN
        orId: 'OR2', orName: 'Operating Room 2',
        surgeonId: 'SG1', surgeon: 'Dr. Jane Smith', // Dr. Smith double booked? - this is a conflict!
        requiredSurgeons: ['Dr. Jane Smith'], requiredStaffRoles: ['Anesthetist', 'Scrub Nurse'], requiredEquipment: ['Heart-Lung Machine'],
        status: 'Scheduled',
        sdsTime: 30, // Example calculated SDST (APPEN -> CABG)
        precedingType: 'APPEN',
        conflicts: ['Surgeon Dr. Jane Smith unavailable (scheduled in OR1)'], // Example conflict
      },
    ],
    pendingSurgeries: [
      // Example Pending Surgeries (will be fetched from backend)
      {
        id: 'p-1', patientId: 'P105', patientName: 'Ethan Brown',
        type: 'APPEN', fullType: 'General - Appendectomy',
        estimatedDuration: 75, duration: 75, priority: 'High',
        requestedDate: '2023-10-28T00:00:00Z', // Optional requested date
        requiredSurgeons: ['Dr. Sarah Chen'], requiredStaffRoles: ['Circulating Nurse'], requiredEquipment: [],
        status: 'Pending',
        sdsTime: null, // SDST not applicable until scheduled
        precedingType: null,
        conflicts: [],
      },
       {
        id: 'p-2', patientId: 'P106', patientName: 'Fiona Green',
        type: 'KNEE', fullType: 'Orthopedic - Knee Replacement',
        estimatedDuration: 150, duration: 150, priority: 'Medium',
         requestedDate: '2023-10-29T00:00:00Z',
        requiredSurgeons: ['Dr. Bill Adams'], requiredStaffRoles: ['Scrub Nurse'], requiredEquipment: ['Arthroscope'],
        status: 'Pending',
        sdsTime: null,
        precedingType: null,
        conflicts: [],
      },
    ],

    // --- Resource Data (Minimal Example) ---
    operatingRooms: [
      { id: 'OR1', name: 'Operating Room 1', status: 'Active' },
      { id: 'OR2', name: 'Operating Room 2', status: 'Active' },
      { id: 'OR3', name: 'Operating Room 3', status: 'Under Maintenance' },
    ],
     staff: [], // Full staff list would be here
     equipment: [], // Full equipment list would be here

    // --- SDST Data (Minimal Example) ---
    sdsRules: {
      'CABG': { 'KNEE': 30, 'APPEN': 45 },
      'KNEE': { 'CABG': 45, 'APPEN': 15 },
      'APPEN': { 'CABG': 30, 'KNEE': 15 },
      // Add rules for 'Initial' preceding type if different from initialSetupTimes
    },
    initialSetupTimes: {
        'CABG': 60,
        'KNEE': 45,
        'APPEN': 30,
    },


    // --- UI State ---
    selectedSurgeryId: null, // ID of the currently selected surgery
    currentDateRange: { // Date range for the Gantt chart view
        start: new Date('2023-10-27T07:00:00Z'), // Start of the day/view
        end: new Date('2023-10-27T19:00:00Z'), // End of the day/view
    },
    ganttViewMode: 'Day', // 'Day', 'Week', 'Month'
    isLoading: false,
    error: null,
  }),
  getters: {
    // Filter scheduled surgeries for the current view
    visibleScheduledSurgeries: (state) => {
        const startTime = state.currentDateRange.start.getTime();
        const endTime = state.currentDateRange.end.getTime();
        return state.scheduledSurgeries.filter(surgery => {
            const surgeryStart = new Date(surgery.startTime).getTime();
            const surgeryEnd = new Date(surgery.endTime).getTime();
            // Show surgeries that are at least partially within the view range
            return (surgeryStart < endTime && surgeryEnd > startTime);
        });
    },

    // Get surgeries for a specific OR within the current view
    getSurgeriesForOR: (state) => (orId) => {
      return state.visibleScheduledSurgeries
            .filter(s => s.orId === orId)
            .sort((a, b) => new Date(a.startTime) - new Date(b.startTime)); // Sort by time
    },

    // Get the currently selected surgery object
    selectedSurgery: (state) => {
        if (!state.selectedSurgeryId) return null;
        // Find in both scheduled and pending lists
        return state.scheduledSurgeries.find(s => s.id === state.selectedSurgeryId) ||
               state.pendingSurgeries.find(s => s.id === state.selectedSurgeryId);
    },

    // Get operating rooms that are not under maintenance (for scheduling)
    availableOperatingRooms: (state) => {
        return state.operatingRooms.filter(or => or.status !== 'Under Maintenance');
    }


    // ... other getters for filtered staff, equipment, reports etc.
  },
  actions: {
    // Action to simulate loading initial data
    async loadInitialData() {
      this.isLoading = true;
      this.error = null;
      try {
        // In a real app, this would be API calls:
        // const [scheduleData, sdstData, resourceData] = await Promise.all([
        //     fetchScheduleData(this.currentDateRange), // Pass date range to API
        //     fetchSDSTData(),
        //     fetchResourceData(),
        // ]);
        // this.scheduledSurgeries = scheduleData.surgeries;
        // this.pendingSurgeries = scheduleData.pending;
        // this.sdsRules = sdstData.rules;
        // this.initialSetupTimes = sdstData.initialTimes;
        // this.operatingRooms = resourceData.ors;
        // this.staff = resourceData.staff;
        // this.equipment = resourceData.equipment;

        // Simulate processing after fetch (to add sdsTime, precedingType, conflicts)
         this.processScheduleData();


      } catch (err) {
        // this.error = 'Failed to load schedule data.';
        console.error("Simulated data load failed:", err);
         this.error = 'Simulated data load error.';
      } finally {
        this.isLoading = false;
      }
    },

    // Simulate processing fetched schedule data to include SDST and conflicts
    // In a real app, this might happen on the backend or involve complex front-end logic
    processScheduleData() {
        // This is a simplified simulation of how SDST and conflicts *could* be added
        // based on the sequence in each OR.
        const processedSurgeries = [];

        this.operatingRooms.forEach(or => {
            const surgeriesInOR = this.scheduledSurgeries
                .filter(s => s.orId === or.id)
                .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

            for (let i = 0; i < surgeriesInOR.length; i++) {
                const currentSurgery = surgeriesInOR[i];
                const precedingSurgery = i > 0 ? surgeriesInOR[i - 1] : null;
                const precedingType = precedingSurgery ? precedingSurgery.type : 'Initial';
                const succeedingSurgery = i < surgeriesInOR.length - 1 ? surgeriesInOR[i + 1] : null;
                const succeedingType = succeedingSurgery ? succeedingSurgery.type : 'End of Day';

                let sdsTime = 0;
                if (precedingType === 'Initial') {
                    sdsTime = this.initialSetupTimes[currentSurgery.type] || 0;
                } else if (this.sdsRules[precedingType] && this.sdsRules[precedingType][currentSurgery.type]) {
                     sdsTime = this.sdsRules[precedingType][currentSurgery.type];
                }
                 // Ensure sdsTime is at least 0
                 sdsTime = Math.max(0, sdsTime);


                // Simulate conflict checking (very basic: check for double booking)
                 const conflicts = [];
                 // Check if the surgeon is double booked (very simple check across all scheduled surgeries)
                 const surgeonConflicts = this.scheduledSurgeries.filter(s =>
                     s.id !== currentSurgery.id && // Not the same surgery
                     s.surgeonId === currentSurgery.surgeonId && // Same surgeon
                     (
                         (new Date(currentSurgery.startTime) < new Date(s.endTime) && new Date(currentSurgery.endTime) > new Date(s.startTime)) || // Overlap
                          // Also check if SDST overlaps with another surgery start
                          (new Date(currentSurgery.startTime) - (sdsTime * 60 * 1000) < new Date(s.endTime) && new Date(currentSurgery.startTime) > new Date(s.startTime))
                     )
                 );
                 if (surgeonConflicts.length > 0) {
                     surgeonConflicts.forEach(conflict => {
                          conflicts.push(`Surgeon ${currentSurgery.surgeon} unavailable (scheduled in ${conflict.orName} at ${new Date(conflict.startTime).toLocaleTimeString()})`);
                     });
                 }

                 // Check for SDST violation (if the gap before is less than required SDST)
                 if (precedingSurgery) {
                     const gapBefore = (new Date(currentSurgery.startTime).getTime() - new Date(precedingSurgery.endTime).getTime()) / (1000 * 60); // Gap in minutes
                      if (gapBefore < sdsTime) {
                         conflicts.push(`SDST Violation: Requires ${sdsTime} min setup, only ${Math.max(0, Math.floor(gapBefore))} min available after ${precedingSurgery.patientName}.`);
                      }
                 } else if (precedingType === 'Initial') {
                      // Check initial setup time if needed, though often assumed available before first case start
                 }


                processedSurgeries.push({
                    ...currentSurgery,
                    sdsTime,
                    precedingType,
                    conflicts, // Add calculated conflicts
                    // Recalculate endTime based on duration + SDST if needed
                     endTime: new Date(new Date(currentSurgery.startTime).getTime() + (currentSurgery.duration + sdsTime) * 60 * 1000).toISOString()
                });
            }
        });

        this.scheduledSurgeries = processedSurgeries; // Update the state with processed data
    },


    // Action to select a surgery to view details
     selectSurgery(surgeryId) {
        this.selectedSurgeryId = surgeryId;
     },

     // Action to clear the selected surgery
     clearSelectedSurgery() {
         this.selectedSurgeryId = null;
     },

    // Action to handle rescheduling a surgery (simulated)
    async rescheduleSurgery(surgeryId, targetORId, newStartTime) {
        this.isLoading = true; // Show loading indicator
        this.error = null;
        try {
            console.log(`Attempting to reschedule surgery ${surgeryId} to OR ${targetORId} at ${newStartTime.toISOString()}`);
            // In a real app, this would call the backend API to update the surgery
            // const updatedSurgeryData = await updateSchedule(surgeryId, {
            //     orId: targetORId,
            //     startTime: newStartTime.toISOString(),
            // });

            // Simulate backend success and state update
             const surgeryIndex = this.scheduledSurgeries.findIndex(s => s.id === surgeryId);
             if (surgeryIndex !== -1) {
                 // Remove from old position and add to new (simplified)
                 const [surgeryToMove] = this.scheduledSurgeries.splice(surgeryIndex, 1);

                 // Update its properties
                 surgeryToMove.orId = targetORId;
                 surgeryToMove.orName = this.operatingRooms.find(or => or.id === targetORId)?.name || 'Unknown OR'; // Find OR Name
                 surgeryToMove.startTime = newStartTime.toISOString();
                 // endTime, sdsTime, precedingType, and conflicts will be recalculated in processScheduleData

                 // Add back to the list (order doesn't matter before processing)
                 this.scheduledSurgeries.push(surgeryToMove);

                 // Re-process the entire schedule to update SDSTs and conflicts
                 this.processScheduleData();

                 console.log(`Simulated successful reschedule for surgery ${surgeryId}`);
             } else {
                 console.warn(`Surgery ${surgeryId} not found in scheduled list.`);
                  this.error = `Surgery not found: ${surgeryId}`;
             }


        } catch (err) {
            this.error = 'Failed to reschedule surgery.';
            console.error("Simulated reschedule failed:", err);
            // In a real app, handle reverting UI or showing specific error
        } finally {
            this.isLoading = false;
        }
    },

     // Action to add a new surgery (from pending, simulated)
     async addSurgeryFromPending(pendingSurgeryId, targetORId, startTime) {
        this.isLoading = true;
        this.error = null;
        try {
             console.log(`Attempting to schedule pending surgery ${pendingSurgeryId} in OR ${targetORId} at ${startTime.toISOString()}`);
            // In a real app, call backend API
            // const newScheduledSurgery = await schedulePendingSurgery(pendingSurgeryId, {
            //     orId: targetORId,
            //     startTime: startTime.toISOString(),
            // });

            // Simulate moving from pending to scheduled
             const pendingIndex = this.pendingSurgeries.findIndex(p => p.id === pendingSurgeryId);
             if (pendingIndex !== -1) {
                 const [surgeryToSchedule] = this.pendingSurgeries.splice(pendingIndex, 1);

                 // Update properties for scheduled state
                 surgeryToSchedule.id = 's-' + Math.random().toString(36).substr(2, 9); // Assign new scheduled ID
                 surgeryToSchedule.orId = targetORId;
                 surgeryToSchedule.orName = this.operatingRooms.find(or => or.id === targetORId)?.name || 'Unknown OR';
                 surgeryToSchedule.startTime = startTime.toISOString();
                 surgeryToSchedule.status = 'Scheduled';
                 // endTime, sdsTime, precedingType, conflicts will be calculated in processScheduleData

                 // Add to scheduled list
                 this.scheduledSurgeries.push(surgeryToSchedule);

                 // Re-process the entire schedule
                 this.processScheduleData();

                 console.log(`Simulated successful scheduling of pending surgery ${pendingSurgeryId}`);
             } else {
                 console.warn(`Pending surgery ${pendingSurgeryId} not found.`);
                 this.error = `Pending surgery not found: ${pendingSurgeryId}`;
             }

        } catch (err) {
             this.error = 'Failed to schedule pending surgery.';
             console.error("Simulated scheduling failed:", err);
        } finally {
            this.isLoading = false;
        }
     },

    // Action to update the visible date range for the Gantt chart
    updateDateRange(newStartDate, newEndDate) {
        this.currentDateRange.start = newStartDate;
        this.currentDateRange.end = newEndDate;
        // In a real app, you might need to refetch data from the backend
        // if the new range goes beyond the data currently loaded.
        // this.loadInitialData(); // Might need parameters for the range
    },

    // Action to update the Gantt view mode
     updateGanttViewMode(mode) {
        this.ganttViewMode = mode;
        // Logic to adjust currentDateRange based on mode (Day, Week, Month)
        // and potentially refetch data would go here.
     },

     // Placeholder action for editing a surgery
     async editSurgery(surgeryId, updatedData) {
        this.isLoading = true;
        this.error = null;
        console.log(`Schedule Store: Simulating editing surgery ${surgeryId} with data:`, updatedData);
        try {
            // In a real app, call backend API to update the surgery
            // const response = await updateSurgeryApi(surgeryId, updatedData);
            // const updatedSurgery = response.data;

            // Simulate update after a delay
            await new Promise(resolve => setTimeout(resolve, 500));

            // Simulate finding and updating the surgery in the state
            const index = this.scheduledSurgeries.findIndex(s => s.id === surgeryId);
            if (index !== -1) {
                const updatedSurgery = { ...this.scheduledSurgeries[index], ...updatedData };
                // Re-calculate derived properties if necessary based on updatedData (e.g., endTime)
                 updatedSurgery.endTime = new Date(new Date(updatedSurgery.startTime).getTime() + updatedSurgery.duration * 60 * 1000 + updatedSurgery.sdsTime * 60 * 1000).toISOString();

                this.scheduledSurgeries.splice(index, 1, updatedSurgery);

                // Re-process the schedule potentially needed if sequencing or resources changed
                this.processScheduleData();

                console.log(`Schedule Store: Simulated edit successful for surgery ${surgeryId}`);
            } else {
                console.warn(`Schedule Store: Surgery ${surgeryId} not found for editing.`);
                this.error = `Surgery not found for editing: ${surgeryId}`;
            }

        } catch (err) {
             this.error = 'Failed to edit surgery.';
             console.error("Schedule Store: Simulated edit failed:", err);
        } finally {
            this.isLoading = false;
        }
     },

      // Placeholder action for canceling a surgery
     async cancelSurgery(surgeryId) {
        this.isLoading = true;
        this.error = null;
        console.log(`Schedule Store: Simulating canceling surgery ${surgeryId}`);
        try {
             // In a real app, call backend API to cancel the surgery
            // await cancelSurgeryApi(surgeryId);

            // Simulate cancellation after a delay
            await new Promise(resolve => setTimeout(resolve, 500));

            // Simulate finding and updating the surgery status in the state
            const index = this.scheduledSurgeries.findIndex(s => s.id === surgeryId);
            if (index !== -1) {
                 // Option 1: Change status to 'Cancelled'
                 this.scheduledSurgeries[index].status = 'Cancelled';
                 // Option 2: Remove the surgery from the scheduled list (depends on desired UI/reporting)
                 // this.scheduledSurgeries.splice(index, 1);

                // Re-process the schedule potentially needed if the cancellation frees up resources/time
                this.processScheduleData();

                console.log(`Schedule Store: Simulated cancel successful for surgery ${surgeryId}`);
            } else {
                 console.warn(`Schedule Store: Surgery ${surgeryId} not found for canceling.`);
                this.error = `Surgery not found for canceling: ${surgeryId}`;
            }

        } catch (err) {
             this.error = 'Failed to cancel surgery.';
             console.error("Schedule Store: Simulated cancel failed:", err);
        } finally {
            this.isLoading = false;
        }
     }
  }
});

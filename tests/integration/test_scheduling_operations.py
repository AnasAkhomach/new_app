import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.schedule_generator import ScheduleGenerator

def test_basic_scheduling(db_setup):
    # Setup: Prepare your test environment with available resources
    # Assuming db_setup is a fixture to prepare your database
    surgery_details = {
        'surgeon_id': 'available_surgeon',
        'room_id': 'available_room',
        'equipment_id': 'available_equipment',
        'start_time': '2023-01-01T09:00:00',
        'end_time': '2023-01-01T11:00:00',
    }
    
    # Action: Attempt to schedule the surgery
    result = ScheduleGenerator.schedule_surgery(surgery_details)
    
    # Assert: The surgery is successfully scheduled
    assert result['status'] == 'success'

def test_tabu_condition_encounter(db_setup):
    # Setup: Mark a room as under maintenance, creating a tabu condition
    db_setup.mark_room_as_maintenance('room_under_maintenance')
    
    surgery_details = {
        'surgeon_id': 'available_surgeon',
        'room_id': 'room_under_maintenance',  # This room is under maintenance
        'equipment_id': 'available_equipment',
        'start_time': '2023-01-02T09:00:00',
        'end_time': '2023-01-02T11:00:00',
    }
    
    # Action: Attempt to schedule the surgery
    result = ScheduleGenerator.schedule_surgery(surgery_details)
    
    # Assert: The surgery scheduling is blocked due to a tabu condition
    assert result['status'] == 'tabu'

def test_conflict_resolution(db_setup):
    # Setup: Schedule an initial surgery that occupies a specific room and time
    db_setup.schedule_surgery('initial_surgery_details')
    
    # Attempt to schedule another surgery that overlaps with the initial one
    overlapping_surgery_details = { ... }  # Similar to above, but overlaps with the initial surgery
    
    # Action: Schedule the overlapping surgery
    result = ScheduleGenerator.schedule_surgery(overlapping_surgery_details)
    
    # Assert: The system resolves the conflict, possibly by suggesting an alternative time or room
    assert result['status'] == 'resolved'




def test_resource_reallocation(db_setup):
    # Setup: Schedule a surgery, then mark one of its allocated resources as unavailable
    scheduled_surgery_id = db_setup.schedule_surgery('surgery_details')
    db_setup.mark_resource_as_unavailable('allocated_resource_id')
    
    # Action: Trigger the system to re-evaluate scheduled surgeries
    result = ScheduleGenerator.reallocate_resources(scheduled_surgery_id)
    
    # Assert: The system successfully reallocates resources, maintaining the surgery schedule
    assert result['status'] == 'reallocation_success'

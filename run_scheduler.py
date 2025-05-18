import os
import sys
import logging
from datetime import datetime

from simple_models import Surgery, OperatingRoom, SurgeryRoomAssignment
from scheduler_utils import SchedulerUtils, DatetimeWrapper
from tabu_optimizer import TabuOptimizer
from simple_feasibility_checker import FeasibilityChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_test_data():
    """Create test data for the scheduler."""
    # Set a fixed time for testing
    DatetimeWrapper.set_fixed_now(datetime(2025, 5, 16, 7, 0, 0))

    # Create test surgeries
    surgeries = [
        Surgery(surgery_id=1, surgery_type_id=1, duration_minutes=60, surgeon_id=101, urgency_level="Medium"),
        Surgery(surgery_id=2, surgery_type_id=2, duration_minutes=90, surgeon_id=102, urgency_level="High"),
        Surgery(surgery_id=3, surgery_type_id=1, duration_minutes=120, surgeon_id=103, urgency_level="Low"),
        Surgery(surgery_id=4, surgery_type_id=3, duration_minutes=45, surgeon_id=101, urgency_level="Medium"),
        Surgery(surgery_id=5, surgery_type_id=2, duration_minutes=75, surgeon_id=104, urgency_level="High")
    ]

    # Create test operating rooms
    operating_rooms = [
        OperatingRoom(room_id=1, operational_start_time=datetime(2025, 5, 16, 8, 0, 0).time(), name="OR 1"),
        OperatingRoom(room_id=2, operational_start_time=datetime(2025, 5, 16, 9, 0, 0).time(), name="OR 2"),
        OperatingRoom(room_id=3, operational_start_time=datetime(2025, 5, 16, 8, 30, 0).time(), name="OR 3")
    ]

    # Create sequence-dependent setup times
    sds_times = {
        (1, 1): 15,  # From type 1 to type 1: 15 minutes
        (1, 2): 30,  # From type 1 to type 2: 30 minutes
        (1, 3): 20,  # From type 1 to type 3: 20 minutes
        (2, 1): 25,  # From type 2 to type 1: 25 minutes
        (2, 2): 15,  # From type 2 to type 2: 15 minutes
        (2, 3): 35,  # From type 2 to type 3: 35 minutes
        (3, 1): 20,  # From type 3 to type 1: 20 minutes
        (3, 2): 30,  # From type 3 to type 2: 30 minutes
        (3, 3): 15   # From type 3 to type 3: 15 minutes
    }

    return surgeries, operating_rooms, sds_times

def print_solution(solution):
    """Print the solution in a human-readable format."""
    if not solution:
        print("No solution found.")
        return

    print("\n===== SURGERY SCHEDULE =====")
    print(f"Total surgeries scheduled: {len(solution)}")

    # Group by room
    by_room = {}
    for assignment in solution:
        if assignment.room_id not in by_room:
            by_room[assignment.room_id] = []
        by_room[assignment.room_id].append(assignment)

    # Sort rooms
    for room_id in sorted(by_room.keys()):
        print(f"\nROOM {room_id}:")
        print("-" * 60)
        print(f"{'Surgery ID':<12}{'Start Time':<20}{'End Time':<20}{'Duration':<10}")
        print("-" * 60)

        # Sort assignments by start time
        assignments = sorted(by_room[room_id], key=lambda a: a.start_time)

        for a in assignments:
            duration = (a.end_time - a.start_time).total_seconds() / 60
            print(f"{a.surgery_id:<12}{a.start_time.strftime('%Y-%m-%d %H:%M'):<20}"
                  f"{a.end_time.strftime('%Y-%m-%d %H:%M'):<20}{int(duration):<10}")

    print("\n" + "=" * 30)

def main():
    """Main function to run the scheduler."""
    # Create test data
    surgeries, operating_rooms, sds_times = create_test_data()

    # Create feasibility checker
    feasibility_checker = FeasibilityChecker(None, surgeries, operating_rooms, None)

    # Create scheduler utils
    scheduler_utils = SchedulerUtils(
        db_session=None,
        surgeries=surgeries,
        operating_rooms=operating_rooms,
        feasibility_checker=feasibility_checker,
        surgery_equipments=[],
        surgery_equipment_usages=[],
        sds_times_data=sds_times
    )

    # Create and run optimizer
    optimizer = TabuOptimizer(
        scheduler_utils=scheduler_utils,
        tabu_list_size=5,
        max_iterations=10,
        max_no_improvement=5
    )

    # Generate initial solution
    logger.info("Generating initial solution...")
    initial_solution = scheduler_utils.initialize_solution()

    if not initial_solution:
        logger.error("Failed to generate an initial solution.")
        return 1

    logger.info(f"Initial solution has {len(initial_solution)} assignments.")
    print_solution(initial_solution)

    # Run optimization
    logger.info("Running optimization...")
    optimized_solution = optimizer.optimize(initial_solution)

    if not optimized_solution:
        logger.error("Optimization failed.")
        return 1

    logger.info(f"Optimized solution has {len(optimized_solution)} assignments.")
    print_solution(optimized_solution)

    # Calculate improvement
    initial_cost = optimizer.calculate_cost(initial_solution)
    optimized_cost = optimizer.calculate_cost(optimized_solution)
    improvement = (initial_cost - optimized_cost) / initial_cost * 100 if initial_cost > 0 else 0

    logger.info(f"Initial cost: {initial_cost:.2f}")
    logger.info(f"Optimized cost: {optimized_cost:.2f}")
    logger.info(f"Improvement: {improvement:.2f}%")

    return 0

if __name__ == "__main__":
    sys.exit(main())

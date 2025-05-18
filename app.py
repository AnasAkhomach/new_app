import argparse
import logging
import json
from datetime import datetime, timedelta
import sys
import os

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

class SchedulerApp:
    """
    Main application class for the Surgery Scheduler.

    This class provides a simple interface to the scheduling system,
    allowing users to load data, run the optimizer, and view/save results.
    """

    def __init__(self):
        self.surgeries = []
        self.operating_rooms = []
        self.sds_times = {}  # Sequence-dependent setup times
        self.surgery_equipments = []
        self.surgery_equipment_usages = []
        self.db_session = None  # We're not using a real DB for the MVP

    def load_data_from_json(self, surgeries_file, rooms_file, sds_times_file=None):
        """
        Load data from JSON files.

        Args:
            surgeries_file: Path to surgeries JSON file
            rooms_file: Path to operating rooms JSON file
            sds_times_file: Optional path to sequence-dependent setup times JSON file
        """
        # Load surgeries
        try:
            with open(surgeries_file, 'r') as f:
                surgeries_data = json.load(f)

            self.surgeries = []
            for s in surgeries_data:
                surgery = Surgery(
                    surgery_id=s['surgery_id'],
                    surgery_type_id=s['surgery_type_id'],
                    duration_minutes=s['duration_minutes'],
                    surgeon_id=s['surgeon_id'],
                    urgency_level=s.get('urgency_level', 'Medium')
                )
                self.surgeries.append(surgery)

            logger.info(f"Loaded {len(self.surgeries)} surgeries")
        except Exception as e:
            logger.error(f"Error loading surgeries: {e}")
            return False

        # Load operating rooms
        try:
            with open(rooms_file, 'r') as f:
                rooms_data = json.load(f)

            self.operating_rooms = []
            for r in rooms_data:
                # Parse operational start time
                if 'operational_start_time' in r:
                    if isinstance(r['operational_start_time'], str):
                        op_start = datetime.strptime(r['operational_start_time'], "%H:%M:%S").time()
                    else:
                        op_start = None
                else:
                    op_start = None

                room = OperatingRoom(
                    room_id=r['room_id'],
                    operational_start_time=op_start,
                    name=r.get('name', f"Room {r['room_id']}")
                )
                self.operating_rooms.append(room)

            logger.info(f"Loaded {len(self.operating_rooms)} operating rooms")
        except Exception as e:
            logger.error(f"Error loading operating rooms: {e}")
            return False

        # Load sequence-dependent setup times if provided
        if sds_times_file:
            try:
                with open(sds_times_file, 'r') as f:
                    sds_data = json.load(f)

                self.sds_times = {}
                for entry in sds_data:
                    from_type = entry['from_surgery_type_id']
                    to_type = entry['to_surgery_type_id']
                    setup_time = entry['setup_time_minutes']
                    self.sds_times[(from_type, to_type)] = setup_time

                logger.info(f"Loaded {len(self.sds_times)} sequence-dependent setup times")
            except Exception as e:
                logger.error(f"Error loading sequence-dependent setup times: {e}")
                # Continue without SDS times

        return True

    def run_scheduler(self, max_iterations=100, tabu_list_size=10):
        """
        Run the scheduler to generate an optimized schedule.

        Args:
            max_iterations: Maximum number of iterations for the Tabu Search
            tabu_list_size: Size of the tabu list

        Returns:
            List of SurgeryRoomAssignment objects representing the optimized schedule
        """
        if not self.surgeries or not self.operating_rooms:
            logger.error("Cannot run scheduler: No surgeries or operating rooms loaded")
            return []

        # Create feasibility checker
        feasibility_checker = FeasibilityChecker(
            db_session=self.db_session,
            surgeries_data=self.surgeries,
            operating_rooms_data=self.operating_rooms,
            all_surgery_equipments_data=self.surgery_equipments
        )

        # Create scheduler utils
        scheduler_utils = SchedulerUtils(
            self.db_session,
            self.surgeries,
            self.operating_rooms,
            feasibility_checker,
            self.surgery_equipments,
            self.surgery_equipment_usages,
            self.sds_times
        )

        # Create and run optimizer
        optimizer = TabuOptimizer(
            scheduler_utils,
            tabu_list_size=tabu_list_size,
            max_iterations=max_iterations
        )

        # Run optimization
        logger.info("Starting optimization...")
        solution = optimizer.optimize()
        logger.info(f"Optimization complete. Found {len(solution)} assignments")

        return solution

    def save_solution_to_json(self, solution, output_file):
        """
        Save the solution to a JSON file.

        Args:
            solution: List of SurgeryRoomAssignment objects
            output_file: Path to output JSON file
        """
        try:
            # Convert solution to serializable format
            serialized = []
            for assignment in solution:
                serialized.append({
                    'surgery_id': assignment.surgery_id,
                    'room_id': assignment.room_id,
                    'start_time': assignment.start_time.isoformat(),
                    'end_time': assignment.end_time.isoformat()
                })

            with open(output_file, 'w') as f:
                json.dump(serialized, f, indent=2)

            logger.info(f"Solution saved to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving solution: {e}")
            return False

    def print_solution(self, solution):
        """
        Print the solution in a human-readable format.

        Args:
            solution: List of SurgeryRoomAssignment objects
        """
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
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Surgery Scheduler')
    parser.add_argument('--surgeries', required=True, help='Path to surgeries JSON file')
    parser.add_argument('--rooms', required=True, help='Path to operating rooms JSON file')
    parser.add_argument('--sds', help='Path to sequence-dependent setup times JSON file')
    parser.add_argument('--output', help='Path to output JSON file')
    parser.add_argument('--iterations', type=int, default=100, help='Maximum iterations for Tabu Search')
    parser.add_argument('--tabu-size', type=int, default=10, help='Size of tabu list')

    args = parser.parse_args()

    app = SchedulerApp()

    # Load data
    if not app.load_data_from_json(args.surgeries, args.rooms, args.sds):
        logger.error("Failed to load data. Exiting.")
        return 1

    # Run scheduler
    solution = app.run_scheduler(max_iterations=args.iterations, tabu_list_size=args.tabu_size)

    if not solution:
        logger.error("Scheduler failed to find a solution.")
        return 1

    # Print solution
    app.print_solution(solution)

    # Save solution if output file specified
    if args.output:
        app.save_solution_to_json(solution, args.output)

    return 0

if __name__ == "__main__":
    sys.exit(main())

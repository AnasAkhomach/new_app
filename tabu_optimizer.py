import logging
from datetime import datetime, timedelta
from scheduler_utils import SchedulerUtils, DatetimeWrapper
import random

logger = logging.getLogger(__name__)

class TabuOptimizer:
    """
    Tabu Search optimizer for surgery scheduling.

    This class implements a Tabu Search algorithm to optimize surgery room assignments
    by minimizing a cost function while respecting constraints.
    """

    def __init__(self, scheduler_utils, tabu_list_size=10, max_iterations=100, max_no_improvement=20):
        """
        Initialize the Tabu Optimizer.

        Args:
            scheduler_utils: SchedulerUtils instance with access to surgeries, rooms, and constraints
            tabu_list_size: Size of the tabu list (number of recent moves to avoid)
            max_iterations: Maximum number of iterations for the search
            max_no_improvement: Maximum number of iterations without improvement before stopping
        """
        self.scheduler_utils = scheduler_utils
        self.tabu_list_size = tabu_list_size
        self.max_iterations = max_iterations
        self.max_no_improvement = max_no_improvement
        self.tabu_list = []  # List of recent moves that are forbidden

    def optimize(self, initial_solution=None):
        """
        Run the Tabu Search optimization algorithm.

        Args:
            initial_solution: Optional initial solution. If None, one will be generated.

        Returns:
            The best solution found (list of SurgeryRoomAssignment objects)
        """
        # Generate initial solution if not provided
        if initial_solution is None:
            current_solution = self.scheduler_utils.initialize_solution()
        else:
            current_solution = initial_solution.copy()

        if not current_solution:
            logger.warning("Failed to generate an initial solution. No surgeries could be scheduled.")
            return []

        best_solution = current_solution.copy()
        best_cost = self.calculate_cost(best_solution)

        iterations_without_improvement = 0

        for iteration in range(self.max_iterations):
            # Generate neighborhood (possible moves)
            neighbors = self.generate_neighbors(current_solution)

            if not neighbors:
                logger.info("No feasible neighbors found. Stopping search.")
                break

            # Find best non-tabu neighbor
            best_neighbor = None
            best_neighbor_cost = float('inf')

            for neighbor, move in neighbors:
                neighbor_cost = self.calculate_cost(neighbor)

                # Check if move is not in tabu list or satisfies aspiration criteria
                if (move not in self.tabu_list or
                    neighbor_cost < best_cost):  # Aspiration criterion

                    if neighbor_cost < best_neighbor_cost:
                        best_neighbor = neighbor
                        best_neighbor_cost = neighbor_cost
                        best_move = move

            # If no non-tabu move found, pick the best tabu move
            if best_neighbor is None and neighbors:
                best_neighbor, best_move = min(neighbors, key=lambda x: self.calculate_cost(x[0]))
                best_neighbor_cost = self.calculate_cost(best_neighbor)

            # Update current solution
            current_solution = best_neighbor

            # Update tabu list
            self.tabu_list.append(best_move)
            if len(self.tabu_list) > self.tabu_list_size:
                self.tabu_list.pop(0)  # Remove oldest move

            # Update best solution if improved
            if best_neighbor_cost < best_cost:
                best_solution = best_neighbor.copy()
                best_cost = best_neighbor_cost
                iterations_without_improvement = 0
                logger.info(f"Iteration {iteration}: Found improved solution with cost {best_cost}")
            else:
                iterations_without_improvement += 1

            # Check stopping criterion
            if iterations_without_improvement >= self.max_no_improvement:
                logger.info(f"Stopping after {iteration+1} iterations due to no improvement")
                break

        logger.info(f"Tabu Search completed. Best solution cost: {best_cost}")
        return best_solution

    def generate_neighbors(self, solution):
        """
        Generate neighboring solutions by applying moves to the current solution.

        Args:
            solution: Current solution (list of SurgeryRoomAssignment objects)

        Returns:
            List of (neighbor_solution, move) tuples
        """
        neighbors = []

        # Move 1: Swap two surgeries between rooms
        swap_neighbors = self._generate_swap_neighbors(solution)
        neighbors.extend(swap_neighbors)

        # Move 2: Move a surgery to a different time slot in the same room
        move_neighbors = self._generate_move_neighbors(solution)
        neighbors.extend(move_neighbors)

        return neighbors

    def _generate_swap_neighbors(self, solution):
        """Generate neighbors by swapping surgeries between rooms."""
        neighbors = []

        for i in range(len(solution)):
            for j in range(i+1, len(solution)):
                # Skip if surgeries are in the same room
                if solution[i].room_id == solution[j].room_id:
                    continue

                # Create a new solution with swapped room assignments
                new_solution = solution.copy()

                # Check if swap is feasible
                if self._is_swap_feasible(solution[i], solution[j]):
                    # Perform the swap
                    new_i = self._create_swapped_assignment(solution[i], solution[j].room_id)
                    new_j = self._create_swapped_assignment(solution[j], solution[i].room_id)

                    # Replace the original assignments
                    new_solution[i] = new_i
                    new_solution[j] = new_j

                    # Define the move for tabu list
                    move = ('swap', solution[i].surgery_id, solution[j].surgery_id)

                    neighbors.append((new_solution, move))

        return neighbors

    def _generate_move_neighbors(self, solution):
        """Generate neighbors by moving surgeries to different time slots."""
        neighbors = []

        for i, assignment in enumerate(solution):
            # Try moving the surgery earlier or later
            for time_shift in [-30, 30]:  # Try 30 minutes earlier or later
                new_start = assignment.start_time + timedelta(minutes=time_shift)
                new_end = assignment.end_time + timedelta(minutes=time_shift)

                # Check if the new time slot is feasible
                if self._is_time_slot_feasible(assignment.surgery_id, assignment.room_id,
                                              new_start, new_end, solution, assignment):
                    # Create a new solution with the moved assignment
                    new_solution = solution.copy()
                    new_assignment = self._create_moved_assignment(assignment, new_start, new_end)
                    new_solution[i] = new_assignment

                    # Define the move for tabu list
                    move = ('move', assignment.surgery_id, time_shift)

                    neighbors.append((new_solution, move))

        return neighbors

    def _is_swap_feasible(self, assignment1, assignment2):
        """Check if swapping two assignments is feasible."""
        # This is a simplified check - in a real implementation, you would need to:
        # 1. Check if the rooms can accommodate the surgeries (equipment, etc.)
        # 2. Check if the surgeons are available at the swapped times
        # 3. Check if the new assignments don't conflict with other surgeries
        return True  # Placeholder - implement actual feasibility check

    def _is_time_slot_feasible(self, surgery_id, room_id, start_time, end_time,
                              current_solution, current_assignment):
        """Check if a new time slot for a surgery is feasible."""
        # This is a simplified check - in a real implementation, you would need to:
        # 1. Check if the new time slot doesn't overlap with other surgeries in the same room
        # 2. Check if the surgeon is available at the new time
        # 3. Check if the equipment is available at the new time
        return True  # Placeholder - implement actual feasibility check

    def _create_swapped_assignment(self, original_assignment, new_room_id):
        """Create a new assignment with a different room."""
        from simple_models import SurgeryRoomAssignment

        return SurgeryRoomAssignment(
            surgery_id=original_assignment.surgery_id,
            room_id=new_room_id,
            start_time=original_assignment.start_time,
            end_time=original_assignment.end_time
        )

    def _create_moved_assignment(self, original_assignment, new_start, new_end):
        """Create a new assignment with a different time slot."""
        from simple_models import SurgeryRoomAssignment

        return SurgeryRoomAssignment(
            surgery_id=original_assignment.surgery_id,
            room_id=original_assignment.room_id,
            start_time=new_start,
            end_time=new_end
        )

    def calculate_cost(self, solution):
        """
        Calculate the cost of a solution.

        The cost function can include various factors such as:
        - Total makespan (time to complete all surgeries)
        - Idle time between surgeries
        - Overtime beyond regular hours
        - Preference violations (surgeon preferences, etc.)

        Args:
            solution: List of SurgeryRoomAssignment objects

        Returns:
            Cost value (lower is better)
        """
        if not solution:
            return float('inf')

        # Calculate makespan (time from start of first surgery to end of last surgery)
        start_times = [a.start_time for a in solution]
        end_times = [a.end_time for a in solution]

        earliest_start = min(start_times) if start_times else DatetimeWrapper.now()
        latest_end = max(end_times) if end_times else DatetimeWrapper.now()

        makespan = (latest_end - earliest_start).total_seconds() / 60  # in minutes

        # Calculate idle time between surgeries in each room
        idle_time = self._calculate_idle_time(solution)

        # Calculate overtime (surgeries scheduled beyond regular hours)
        overtime = self._calculate_overtime(solution)

        # Combine the factors with weights
        cost = makespan + 2 * idle_time + 3 * overtime

        return cost

    def _calculate_idle_time(self, solution):
        """Calculate total idle time between surgeries in all rooms."""
        # Group assignments by room
        room_assignments = {}
        for assignment in solution:
            if assignment.room_id not in room_assignments:
                room_assignments[assignment.room_id] = []
            room_assignments[assignment.room_id].append(assignment)

        total_idle_time = 0

        # Calculate idle time in each room
        for room_id, assignments in room_assignments.items():
            # Sort assignments by start time
            sorted_assignments = sorted(assignments, key=lambda a: a.start_time)

            for i in range(1, len(sorted_assignments)):
                prev_end = sorted_assignments[i-1].end_time
                curr_start = sorted_assignments[i].start_time

                if curr_start > prev_end:
                    idle_minutes = (curr_start - prev_end).total_seconds() / 60
                    total_idle_time += idle_minutes

        return total_idle_time

    def _calculate_overtime(self, solution):
        """Calculate total overtime beyond regular hours."""
        # Define regular hours (e.g., 8:00 AM to 5:00 PM)
        regular_end_hour = 17  # 5:00 PM

        total_overtime = 0

        for assignment in solution:
            # Check if the surgery ends after regular hours
            if assignment.end_time.hour >= regular_end_hour:
                # Calculate minutes past regular hours
                regular_end = datetime.combine(assignment.end_time.date(),
                                             datetime.min.time().replace(hour=regular_end_hour))

                if assignment.end_time > regular_end:
                    overtime_minutes = (assignment.end_time - regular_end).total_seconds() / 60
                    total_overtime += overtime_minutes

        return total_overtime

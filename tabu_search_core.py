# This file will contain the core Tabu Search algorithm logic.
import time
import copy
import logging
from tabu_list import TabuList
from datetime import datetime, timedelta # Added for placeholder times

logger = logging.getLogger(__name__)

class TabuSearchCore:
    def __init__(self, solution_evaluator, neighborhood_generator, initial_solution_assignments):
        """
        Initializes the TabuSearchCore.
        Args:
            solution_evaluator: An instance of SolutionEvaluator.
            neighborhood_generator: An instance of NeighborhoodStrategies.
            initial_solution_assignments: The initial set of surgery assignments (list of dicts).
        """
        self.solution_evaluator = solution_evaluator
        self.neighborhood_generator = neighborhood_generator
        logger.info(f"TabuSearchCore __init__: Received initial_solution_assignments with {len(initial_solution_assignments)} items: {initial_solution_assignments}")
        self.initial_solution_assignments = copy.deepcopy(initial_solution_assignments)
        logger.info(f"TabuSearchCore __init__: Stored self.initial_solution_assignments (deep copied) with {len(self.initial_solution_assignments)} items: {self.initial_solution_assignments}")
        logger.info(f"TabuSearchCore __init__: id(self.initial_solution_assignments) after deepcopy: {id(self.initial_solution_assignments)}")
        logger.info("TabuSearchCore initialized.")

    def search(
        self,
        max_iterations=100,
        tabu_tenure=10,
        max_iterations_without_improvement_ratio=0.25,
        time_limit_seconds=None,
    ):
        """Main Tabu Search optimization loop."""
        logger.info(
            "Starting Tabu Search with parameters: max_iterations=%s, tabu_tenure=%s, max_iterations_without_improvement_ratio=%s, time_limit_seconds=%s",
            max_iterations,
            tabu_tenure,
            max_iterations_without_improvement_ratio,
            time_limit_seconds,
        )

        logger.info(f"TabuSearchCore search(): id(self.initial_solution_assignments) at start of search: {id(self.initial_solution_assignments)}")
        logger.info(f"TabuSearchCore search(): Type of self.initial_solution_assignments: {type(self.initial_solution_assignments)}")
        logger.info(f"TabuSearchCore search(): Checking self.initial_solution_assignments with {len(self.initial_solution_assignments) if self.initial_solution_assignments is not None and isinstance(self.initial_solution_assignments, list) else 'N/A or not a list'} items: {self.initial_solution_assignments}")
        if not self.initial_solution_assignments or not isinstance(self.initial_solution_assignments, list):
            logger.error("Cannot run Tabu Search: initial solution is empty, not provided, or not a list.")
            return None, -float('inf')

        current_solution_assignments = copy.deepcopy(self.initial_solution_assignments)
        best_solution_assignments = copy.deepcopy(current_solution_assignments)

        # Placeholder schedule times for now - these should ideally be derived from the actual schedule's span
        # or a predefined operational window for the entire scheduling period.
        placeholder_start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        placeholder_end_time = placeholder_start_time + timedelta(days=1) # Assuming a 24-hour window for evaluation context

        best_score = self.solution_evaluator.evaluate_solution(best_solution_assignments, placeholder_start_time, placeholder_end_time)
        logger.info(f"Initial solution score: {best_score}")

        # Use max_tenure and min_tenure for TabuList constructor
        # Ensure TabuList is correctly imported and initialized
        tabu_list = TabuList(
            max_tenure=tabu_tenure, min_tenure=max(1, tabu_tenure // 2)
        )
        iterations_without_improvement = 0
        max_iterations_without_improvement = max(
            1, int(max_iterations * max_iterations_without_improvement_ratio)
        )

        start_time_process = time.process_time()

        for iteration in range(max_iterations):
            logger.info("Iteration %d/%d. Current best score: %s", iteration + 1, max_iterations, best_score)

            # Generate neighbor solutions using the NeighborhoodStrategies instance
            neighbor_solutions_info = self.neighborhood_generator.generate_neighbor_solutions(
                current_solution_assignments, tabu_list
            )

            if not neighbor_solutions_info:
                logger.info("No non-tabu or aspirated neighbors found. Stopping search.")
                break

            best_neighbor_assignments = None
            best_neighbor_score = -float("inf")
            best_neighbor_move = None

            for neighbor_info in neighbor_solutions_info:
                neighbor_assignments = neighbor_info["assignments"]
                move = neighbor_info["move"]
                score = self.solution_evaluator.evaluate_solution(neighbor_assignments, placeholder_start_time, placeholder_end_time)

                is_aspirated = tabu_list.is_tabu(move) and score > best_score

                if not tabu_list.is_tabu(move) or is_aspirated:
                    if score > best_neighbor_score:
                        best_neighbor_assignments = neighbor_assignments
                        best_neighbor_score = score
                        best_neighbor_move = move
                        if is_aspirated:
                            logger.info(
                                "Aspiration criteria met for move %s. Tabu overridden. New score: %s (Global best: %s)",
                                move, score, best_score
                            )
                # Consider non-tabu moves that might not be improving but are chosen to escape local optima
                # This part of original logic was a bit ambiguous, simplifying to: if it's not tabu OR aspirated, consider it.
                # If we want to allow non-improving moves that are not tabu, that's implicitly handled if they become best_neighbor_score.

            if best_neighbor_assignments is None:
                logger.info("No suitable neighbor found in this iteration (all tabu and not meeting aspiration, or no neighbors generated). Stopping search.")
                break # No valid (non-tabu or aspirated) neighbor was better than -inf

            current_solution_assignments = best_neighbor_assignments
            if best_neighbor_move is not None: # Only add to tabu if a move was actually made
                tabu_list.add(best_neighbor_move)
            else:
                logger.warning("Best neighbor move was None, cannot add to tabu list. This might indicate an issue.")

            if best_neighbor_score > best_score:
                best_solution_assignments = copy.deepcopy(best_neighbor_assignments)
                best_score = best_neighbor_score
                logger.info(
                    "New global best solution found with score: %s at iteration %d",
                    best_score,
                    iteration + 1,
                )
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1

            if iterations_without_improvement >= max_iterations_without_improvement:
                logger.info(
                    "Stopping early: No improvement in best solution for %d iterations (threshold: %d).",
                    iterations_without_improvement,
                    max_iterations_without_improvement,
                )
                break

            if time_limit_seconds is not None:
                elapsed_time = time.process_time() - start_time_process
                if elapsed_time >= time_limit_seconds:
                    logger.info(
                        "Stopping early: Time limit of %d seconds reached. Elapsed: %.2fs.",
                        time_limit_seconds,
                        elapsed_time,
                    )
                    break

        elapsed_total_time = time.process_time() - start_time_process
        logger.info("Tabu Search finished. Total iterations: %d. Total time: %.2fs. Best score: %s", iteration +1, elapsed_total_time, best_score)
        return best_solution_assignments, best_score
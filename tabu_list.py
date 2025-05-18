import random
import logging

logger = logging.getLogger(__name__)

class TabuList:
    """
    Manages the tabu list for a Tabu Search algorithm.

    The tabu list stores attributes of recently performed moves or characteristics of
    recently visited solutions, marking them as "tabu" (forbidden) for a specific duration (tenure).
    This prevents the search from immediately reversing a move and cycling between a small set of solutions.

    Key features:
    - Stores tabu attributes with their remaining tenure.
    - Supports adding attributes with specific or default tenures.
    - Decrements tenure at each iteration and removes expired attributes.
    - Provides methods for checking if an attribute is tabu.
    - Includes mechanisms for dynamic and adaptive tenure management:
        - Randomized tenure: Assigns a random tenure within a defined range.
        - Frequency-based tenure adjustment: Modifies tenure based on how often an attribute has been involved in (potentially problematic) moves.
        - Progress-based tenure adjustment: Adapts tenure based on overall search progress.
    """
    def __init__(self, default_max_tenure, default_min_tenure):
        """
        Initializes the TabuList.

        Args:
            default_max_tenure (int): The default maximum tenure for a tabu attribute if not specified.
            default_min_tenure (int): The default minimum tenure for a tabu attribute, used in randomized tenure.
        """
        self.entries = {}  # Stores tabu_attribute: remaining_tenure
        self.default_max_tenure = default_max_tenure
        self.default_min_tenure = default_min_tenure
        if default_min_tenure > default_max_tenure:
            logger.warning(f"Min tenure ({default_min_tenure}) is greater than max tenure ({default_max_tenure}). Adjusting min_tenure to max_tenure.")
            self.default_min_tenure = default_max_tenure
        self.temporary_tenure_increases = {} # Stores attribute: (original_tenure, remaining_duration)

    def add(self, attribute, tenure=None):
        """
        Adds an attribute to the tabu list or updates its tenure if already present.

        Args:
            attribute (any hashable): The attribute to make tabu (e.g., a tuple representing a move).
            tenure (int, optional): The specific tenure for this attribute.
                                     If None, a randomized tenure between min_tenure and max_tenure is used.
                                     If 0 or negative, the attribute is not added or removed if present.
        """
        if tenure is None:
            # Apply randomized tenure by default if no specific tenure is given
            if self.default_min_tenure == self.default_max_tenure:
                effective_tenure = self.default_max_tenure
            else:
                effective_tenure = random.randint(self.default_min_tenure, self.default_max_tenure)
        else:
            effective_tenure = tenure

        if effective_tenure <= 0:
            if attribute in self.entries:
                del self.entries[attribute]
                logger.debug(f"Removed attribute {attribute} from tabu list due to zero/negative tenure.")
            return

        self.entries[attribute] = effective_tenure
        logger.debug(f"Added attribute {attribute} to tabu list with tenure {effective_tenure}.")

    def is_tabu(self, attribute):
        """
        Checks if a given attribute is currently tabu.

        Args:
            attribute (any hashable): The attribute to check.

        Returns:
            bool: True if the attribute is tabu, False otherwise.
        """
        return attribute in self.entries

    def get_tenure(self, attribute):
        """
        Gets the remaining tenure for a tabu attribute.

        Args:
            attribute (any hashable): The attribute to check.

        Returns:
            int or None: The remaining tenure if the attribute is tabu, None otherwise.
        """
        return self.entries.get(attribute)

    def decrement_tenure(self):
        """
        Decrements the tenure of all tabu attributes by one.
        Removes attributes whose tenure reaches zero or less.
        This method should be called once per iteration of the Tabu Search.
        """
        to_remove = []
        for attribute, tenure in self.entries.items():
            new_tenure = tenure - 1
            if new_tenure <= 0:
                to_remove.append(attribute)
            else:
                self.entries[attribute] = new_tenure

        for attribute in to_remove:
            del self.entries[attribute]
            logger.debug(f"Attribute {attribute} expired and removed from tabu list.")

        # Handle temporary tenure increases duration
        temp_increases_to_remove = []
        for attr, (original_tenure, remaining_duration) in list(self.temporary_tenure_increases.items()):
            new_remaining_duration = remaining_duration - 1
            if new_remaining_duration <= 0:
                # Duration expired, revert to original tenure or remove if original was to expire
                if attr in self.entries:
                    self.entries[attr] = original_tenure # Revert to original
                    if self.entries[attr] <= 0: # If original tenure would have made it expire
                        del self.entries[attr]
                        logger.debug(f"Attribute {attr} reverted from temporary increase and expired.")
                    else:
                        logger.debug(f"Attribute {attr} reverted to original tenure {original_tenure} after temporary increase.")
                temp_increases_to_remove.append(attr)
            else:
                self.temporary_tenure_increases[attr] = (original_tenure, new_remaining_duration)

        for attr in temp_increases_to_remove:
            if attr in self.temporary_tenure_increases: # Ensure it wasn't already handled (e.g. by main expiry)
                del self.temporary_tenure_increases[attr]

    def clear(self):
        """
        Removes all entries from the tabu list.
        """
        self.entries.clear()
        self.temporary_tenure_increases.clear()
        logger.info("Tabu list cleared, including temporary tenure increases.")

    def increase_all_tenures(self, factor, duration):
        """
        Temporarily increases the tenure of all current tabu items by a factor for a specified duration.
        Args:
            factor (float): The factor by which to increase the tenure (e.g., 1.5 for a 50% increase).
            duration (int): The number of iterations for which the increased tenure should last.
        """
        if factor <= 1.0:
            logger.warning(f"Attempted to increase tenures with a non-increasing factor {factor}. No change made.")
            return
        if duration <= 0:
            logger.warning(f"Attempted to increase tenures for a non-positive duration {duration}. No change made.")
            return

        logger.info(f"Temporarily increasing all tenures by factor {factor} for {duration} iterations.")
        for attribute, current_tenure in list(self.entries.items()): # Iterate over a copy
            if attribute not in self.temporary_tenure_increases: # Only apply if not already under a temp increase
                original_tenure = current_tenure
                new_tenure = int(current_tenure * factor)
                self.entries[attribute] = new_tenure
                self.temporary_tenure_increases[attribute] = (original_tenure, duration)
                logger.debug(f"Attribute {attribute} tenure temporarily increased from {original_tenure} to {new_tenure} for {duration} iterations.")
            else:
                logger.debug(f"Attribute {attribute} is already under a temporary tenure increase. Skipping.")

    # --- Specific attribute formatting examples (customize as needed for your problem) ---
    def _format_surgery_room_attribute(self, surgery_id, room_id):
        return ('surgery_room_assignment', surgery_id, room_id)

    def _format_surgeon_attribute(self, surgery_id, surgeon_id):
        return ('surgeon_assignment', surgery_id, surgeon_id)

    def _format_time_slot_attribute(self, surgery_id, start_time):
        # Ensure start_time is hashable, e.g., convert datetime to string or timestamp if necessary
        return ('time_slot_assignment', surgery_id, str(start_time))

    def _format_equipment_attribute(self, surgery_id, equipment_id):
        return ('equipment_assignment', surgery_id, equipment_id)

    def add_surgery_room_assignment(self, surgery_id, room_id, tenure=None):
        self.add(self._format_surgery_room_attribute(surgery_id, room_id), tenure)

    def add_surgeon_assignment(self, surgery_id, surgeon_id, tenure=None):
        self.add(self._format_surgeon_attribute(surgery_id, surgeon_id), tenure)

    def add_time_slot_assignment(self, surgery_id, start_time, tenure=None):
        self.add(self._format_time_slot_attribute(surgery_id, start_time), tenure)

    def add_equipment_assignment(self, surgery_id, equipment_id, tenure=None):
        self.add(self._format_equipment_attribute(surgery_id, equipment_id), tenure)

    def is_surgery_room_tabu(self, surgery_id, room_id):
        return self.is_tabu(self._format_surgery_room_attribute(surgery_id, room_id))

    def is_surgeon_tabu(self, surgery_id, surgeon_id):
        return self.is_tabu(self._format_surgeon_attribute(surgery_id, surgeon_id))

    def is_time_slot_tabu(self, surgery_id, start_time):
        return self.is_tabu(self._format_time_slot_attribute(surgery_id, start_time))

    def is_equipment_tabu(self, surgery_id, equipment_id):
        return self.is_tabu(self._format_equipment_attribute(surgery_id, equipment_id))

    # --- Adaptive Tenure Mechanisms ---
    def update_tenure_randomly(self, attribute=None):
        """
        Applies a new random tenure (between default_min_tenure and default_max_tenure)
        to a specific attribute or all attributes if None.
        This implements a form of dynamic tenure.
        """
        if self.default_min_tenure == self.default_max_tenure:
            new_tenure = self.default_max_tenure
        else:
            new_tenure = random.randint(self.default_min_tenure, self.default_max_tenure)

        if attribute:
            if attribute in self.entries:
                self.entries[attribute] = new_tenure
                logger.debug(f"Randomly updated tenure for {attribute} to {new_tenure}.")
        else: # Apply to all
            for attr_key in list(self.entries.keys()): # Iterate over a copy of keys for safe modification
                self.entries[attr_key] = new_tenure
            logger.debug(f"Randomly updated tenure for all attributes to {new_tenure}.")

    def adjust_tenure_by_frequency(self, attribute, attribute_visit_frequency, max_freq_impact=5, min_freq_impact=-2):
        """
        Adjusts the tenure of an attribute based on its visit frequency (Reactive Tabu Search idea).
        High frequency might indicate cycling, so tenure is increased.
        Low frequency might allow tenure reduction.

        Args:
            attribute (any hashable): The attribute whose tenure to adjust.
            attribute_visit_frequency (int): How frequently this attribute has been part of a move or solution.
            max_freq_impact (int): Maximum amount to increase tenure by due to high frequency.
            min_freq_impact (int): Maximum amount to decrease tenure by (negative value for decrease).
        """
        if attribute not in self.entries:
            return

        current_tenure = self.entries[attribute]
        # Example: Simple linear adjustment based on frequency. More sophisticated models can be used.
        # This is a conceptual example; actual frequency tracking and impact calculation would be problem-specific.
        if attribute_visit_frequency > 5: # Arbitrary threshold for high frequency
            adjustment = max_freq_impact
        elif attribute_visit_frequency < 2: # Arbitrary threshold for low frequency
            adjustment = min_freq_impact
        else:
            adjustment = 0

        new_tenure = current_tenure + adjustment
        new_tenure = max(self.default_min_tenure, min(new_tenure, self.default_max_tenure * 2)) # Cap tenure
        self.entries[attribute] = new_tenure
        logger.debug(f"Adjusted tenure for {attribute} from {current_tenure} to {new_tenure} based on frequency {attribute_visit_frequency}.")

    def adjust_tenure_by_search_progress(self, search_progress_factor):
        """
        Adjusts all tenures based on the overall search progress (e.g., 0.0 to 1.0).
        Early in search (low progress), longer tenures might be preferred for diversification.
        Later in search (high progress), shorter tenures might be preferred for intensification.

        Args:
            search_progress_factor (float): A value between 0.0 (start of search) and 1.0 (end of search).
        """
        if not (0.0 <= search_progress_factor <= 1.0):
            logger.warning(f"Search progress factor {search_progress_factor} out of range [0,1]. No tenure adjustment applied.")
            return

        for attribute in list(self.entries.keys()): # Iterate over a copy of keys
            current_tenure = self.entries[attribute]
            # Example: Linearly scale tenure. Longer at start, shorter at end.
            # This is a conceptual example. The scaling logic can be more complex.
            # Effective tenure range could shift from [min_tenure, max_tenure*1.5] to [min_tenure*0.5, max_tenure]
            scale_factor = (1.0 - search_progress_factor) * 0.5 + 0.5 # Scale from 1.0 down to 0.5

            base_tenure = random.randint(self.default_min_tenure, self.default_max_tenure)
            new_tenure = int(base_tenure * scale_factor)
            new_tenure = max(1, new_tenure) # Ensure tenure is at least 1

            self.entries[attribute] = new_tenure
        logger.debug(f"Adjusted all tenures based on search progress factor {search_progress_factor}.")

    def __str__(self):
        return f"TabuList(entries={self.entries}, min_tenure={self.default_min_tenure}, max_tenure={self.default_max_tenure})"

    def __len__(self):
        return len(self.entries)

# Example of how TabuList might be used within the main search loop (conceptual):
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # Initialize Tabu List
    # These tenure values would typically be tuned based on the problem size and characteristics.
    # For example, sqrt(N) or N/10 where N is number of surgeries or variables.
    tabu_list = TabuList(default_max_tenure=10, default_min_tenure=3)

    # Simulate some moves and adding to tabu list
    move1_attribute = ('surgery_room_assignment', 'surgery_123', 'room_A')
    tabu_list.add(move1_attribute) # Uses randomized tenure by default
    print(f"After adding {move1_attribute}: {tabu_list}")

    move2_attribute = ('surgeon_assignment', 'surgery_456', 'surgeon_X')
    tabu_list.add(move2_attribute, tenure=5) # Specific tenure
    print(f"After adding {move2_attribute}: {tabu_list}")

    # Simulate search iterations
    for i in range(15):
        print(f"\nIteration {i+1}")
        tabu_list.decrement_tenure()
        print(f"After decrement: {tabu_list}")

        # Example: Check if a potential move is tabu
        potential_move_attr = ('surgery_room_assignment', 'surgery_123', 'room_A')
        if tabu_list.is_tabu(potential_move_attr):
            print(f"Move attribute {potential_move_attr} IS TABU (tenure: {tabu_list.get_tenure(potential_move_attr)}).")
        else:
            print(f"Move attribute {potential_move_attr} is NOT TABU.")

        # Periodically apply adaptive tenure strategies (example)
        if (i + 1) % 7 == 0:
            print("Applying random tenure update to all.")
            tabu_list.update_tenure_randomly()
            print(f"After random tenure update: {tabu_list}")

        if (i + 1) % 5 == 0:
            # Simulate frequency data for a specific attribute
            # In a real scenario, this frequency would be tracked by the main algorithm
            example_freq_attr = move1_attribute
            if tabu_list.is_tabu(example_freq_attr):
                 # Simulate high frequency for an existing tabu item
                tabu_list.adjust_tenure_by_frequency(example_freq_attr, attribute_visit_frequency=6)
                print(f"After frequency adjustment for {example_freq_attr}: {tabu_list}")

        if (i + 1) % 10 == 0:
            progress = (i+1) / 15 # Simulate search progress
            print(f"Applying progress-based tenure adjustment (progress: {progress:.2f}).")
            tabu_list.adjust_tenure_by_search_progress(search_progress_factor=progress)
            print(f"After progress-based adjustment: {tabu_list}")

    tabu_list.clear()
    print(f"\nAfter clearing: {tabu_list}")
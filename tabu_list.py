import random

class TabuList:
    def __init__(self, max_tenure, min_tenure):
        self.entries = {}  # Using a dictionary to store attribute and tenure
        self.max_tenure = max_tenure
        self.min_tenure = min_tenure

    def add(self, attribute, tenure=None):
        if tenure is None:
            tenure = self.max_tenure
        self.entries[attribute] = tenure

    def is_tabu(self, attribute):
        return attribute in self.entries

    def decrement_tenure(self):
        to_remove = [attribute for attribute, tenure in self.entries.items() if tenure - 1 <= 0]
        for attribute in to_remove:
            del self.entries[attribute]
        for attribute in self.entries:
            self.entries[attribute] -= 1

    def clear(self):
        self.entries.clear()


    # Specific methods to handle different types of tabu entries
    def add_surgery_room_assignment(self, surgery_id, room_id, tenure):
        self.add(('surgery_room', surgery_id, room_id), tenure)

    def add_surgeon_assignment(self, surgery_id, surgeon_id, tenure):
        self.add(('surgeon', surgery_id, surgeon_id), tenure)

    def add_equipment_assignment(self, surgery_id, equipment_id, tenure):
        self.add(('equipment', surgery_id, equipment_id), tenure)

    def is_surgery_room_tabu(self, surgery_id, room_id):
        """
        Checks if a surgery room assignment for a surgery is currently tabu.
        """
        return self.is_tabu(('surgery_room', surgery_id, room_id))

    def is_surgeon_tabu(self, surgery_id, surgeon_id):
        """
        Checks if a surgeon assignment for a surgery is currently tabu.
        """
        return self.is_tabu(('surgeon', surgery_id, surgeon_id))

    def is_time_slot_tabu(self, surgery_id, start_time):
        """
        Checks if a time slot assignment for a surgery is currently tabu.
        """
        return self.is_tabu(('time_slot', surgery_id, start_time))

    def is_equipment_tabu(self, surgery_id, equipment_id):
        """
        Checks if an equipment assignment for a surgery is currently tabu.
        """
        return self.is_tabu(('equipment', surgery_id, equipment_id))
    
    def update_tenure_based_on_progress(self, progress_calculator):
        for attribute, tenure in self.entries.items():
            progress = progress_calculator()
            self.entries[attribute] = int(tenure * (1 - progress))

    def apply_randomized_tenure(self):
        for attribute in self.entries:
            self.entries[attribute] = random.randint(self.min_tenure, self.max_tenure)

    def adjust_frequency_based_tenure(self, attribute, frequency_dict):
        frequency = frequency_dict.get(attribute, 0)
        if frequency > 0:
            self.entries[attribute] = min(self.entries.get(attribute, self.max_tenure) + frequency, self.max_tenure)
        else:
            self.entries[attribute] = max(self.entries.get(attribute, self.min_tenure) - 1, self.min_tenure)

# Example usage:
tabu_list = TabuList(max_tenure=10, min_tenure=5)
tabu_list.add('attribute1')
tabu_list.add('attribute2', tenure=7)
# Assuming we have a function that returns the search progress
progress_calculator = lambda: 0.5  # Example function that returns 50% progress
tabu_list.update_tenure_based_on_progress(progress_calculator)
tabu_list.apply_randomized_tenure()

# Assuming we have a frequency dictionary for attributes
frequency_dict = {'attribute1': 3, 'attribute2': 1}
tabu_list.adjust_frequency_based_tenure('attribute1', frequency_dict)

# Output the tabu list entries and tenures
print(tabu_list.entries)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient
import random

from pymongo import MongoClient

class TabuList:
    def __init__(self, max_tenure=None, min_tenure=None):
        self.db = MongoDBClient.get_db()
        self.tabu_collection = self.db.tabu_entries
        self.max_tenure = max_tenure
        self.min_tenure = min_tenure
        # Initialize other necessary cl
    # Example of adding a new tabu entry with MongoDB
        
    def add_complex(self, surgeon_id, room_id, equipment_id, time_slot, tenure=None):
        if tenure is None:
            tenure = self.max_tenure
        # Define a complex attribute as a combination of provided parameters
        complex_attribute = {
            'surgeon_id': surgeon_id,
            'room_id': room_id,
            'equipment_id': equipment_id,
            'time_slot': time_slot
        }
        self.tabu_collection.update_one(complex_attribute, {'$set': {'tenure': tenure}}, upsert=True)

    # Other methods adapted to use MongoDB...

    def is_complex_tabu(self, surgeon_id, room_id, equipment_id, time_slot):
        complex_attribute = {
            'surgeon_id': surgeon_id,
            'room_id': room_id,
            'equipment_id': equipment_id,
            'time_slot': time_slot
        }
        return self.tabu_collection.find_one(complex_attribute) is not None

    def decrement_tenure(self):
        self.tabu_collection.update_many({}, {'$inc': {'tenure': -1}})
        self.tabu_collection.delete_many({'tenure': {'$lte': 0}})


    def update_tenure_based_on_progress(self, progress_calculator):
        progress = progress_calculator()
        tabu_entries = self.tabu_collection.find()
        for entry in tabu_entries:
            new_tenure = max(int(entry['tenure'] * (1 - progress)), 1)  # Prevent tenure from becoming 0 prematurely
            self.tabu_collection.update_one({'_id': entry['_id']}, {'$set': {'tenure': new_tenure}})



    def clear(self):
        self.tabu_collection.delete_many({})
    

    def adjust_frequency_based_tenure(self, frequency_dict, min_tenure=None, max_tenure=None):
        # Use class attributes if specific values are not provided
        min_tenure = min_tenure if min_tenure is not None else self.min_tenure
        max_tenure = max_tenure if max_tenure is not None else self.max_tenure

        for attribute, frequency in frequency_dict.items():
            tabu_entry = self.tabu_collection.find_one({'attribute': attribute})
            frequency_dict = {}

            if tabu_entry:
                current_tenure = tabu_entry.get('tenure', max_tenure)
                if frequency > 0:
                    new_tenure = min(current_tenure + frequency, max_tenure)
                else:
                    new_tenure = max(current_tenure - 1, min_tenure)
                self.tabu_collection.update_one({'_id': tabu_entry['_id']}, {'$set': {'tenure': new_tenure}})
            else:
                # Handle the case where there is no entry for this attribute, e.g., create a new one or ignore
                print(f"No tabu entry found for attribute: {attribute}")

    def adjust_tenures_based_on_global_condition(self):
        # Example global condition adjustment logic remains abstract; specifics depend on the condition being evaluated
        tabu_entries = self.tabu_collection.find()
        for entry in tabu_entries:
            # Adjust tenure based on the global condition, e.g., decrement by one until reaching min_tenure
            new_tenure = max(entry.get('tenure', self.max_tenure) - 1, self.min_tenure)
            self.tabu_collection.update_one({'_id': entry['_id']}, {'$set': {'tenure': new_tenure}})


    def apply_randomized_tenure(self, min_tenure=None, max_tenure=None):
        min_tenure = min_tenure if min_tenure is not None else self.min_tenure
        max_tenure = max_tenure if max_tenure is not None else self.max_tenure
        tabu_entries = self.tabu_collection.find()
        for entry in tabu_entries:
            new_tenure = random.randint(min_tenure, max_tenure)
            self.tabu_collection.update_one({'_id': entry['_id']}, {'$set': {'tenure': new_tenure}})



# Example usage:
tabu_list = TabuList(max_tenure=10, min_tenure=5)

# Assuming we have a function that returns the search progress
progress_calculator = lambda: 0.5  # Example function that returns 50% progress
tabu_list.update_tenure_based_on_progress(progress_calculator)
tabu_list.apply_randomized_tenure()

#tabu_list.adjust_frequency_based_tenure()
tabu_list.adjust_tenures_based_on_global_condition()

# Output the tabu list entries and tenures
#print(tabu_list.entries)
tabu_entries = list(tabu_list.tabu_collection.find())
for entry in tabu_entries:
    print(entry)
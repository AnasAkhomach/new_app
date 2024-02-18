import unittest
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.time_management_utils import TimeManagementUtils


class TestTimeManagementUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This method can be used to set up any class-level fixtures, if necessary.
        pass

    def setUp(self):
        # This method will run before each test method.
        # Initialize your TimeManagementUtils instance here, potentially with mocked database access.
        self.time_utils = TimeManagementUtils()


    def test_shift_surgery_time_positive(self):
        # Test shifting time forward
        new_time = TimeManagementUtils.shift_surgery_time('2023-01-01T09:00:00', 60)
        self.assertEqual(new_time, '2023-01-01T10:00:00')

    def test_shift_surgery_time_negative(self):
        # Test shifting time backward
        new_time = TimeManagementUtils.shift_surgery_time('2023-01-01T09:00:00', -30)
        self.assertEqual(new_time, '2023-01-01T08:30:00')

    @patch('TimeManagementUtils.MongoDBClient.get_db')
    def test_is_time_slot_tabu(self, mock_get_db):
        # Mock the find_one method to return a tabu entry
        mock_get_db.return_value.tabu_entries.find_one.return_value = {'surgery_id': '123', 'start_time': '2023-01-01T09:00:00'}
        
        is_tabu = self.time_utils.is_time_slot_tabu('123', '2023-01-01T09:00:00')
        self.assertTrue(is_tabu)

    @patch('TimeManagementUtils.MongoDBClient.get_db')
    def test_find_next_available_time_slots(self, mock_get_db):
        # Mock the find_one method to simulate the latest appointment's end time
        mock_get_db.return_value.surgery_room_assignments.find_one.return_value = {'end_time': '2023-01-01T11:00:00'}

        available_slots = self.time_utils.find_next_available_time_slots('room1', 60)
        self.assertTrue(len(available_slots) > 0)  # Add more specific assertions based on your logic


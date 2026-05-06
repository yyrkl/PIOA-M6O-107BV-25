
from src.db.backend.memory import StudentTable

import unittest

class TestMemory(unittest.TestCase):

    def test_student_table_allocation(self):
        student_table = StudentTable() 
        self.assertIsInstance(student_table, StudentTable)

    def test_create_record(self):
        test_data = (1, "John", "Doe", 20, "M")

        student_table = StudentTable()
        record = student_table.create_record(*test_data) # AttributeError: 'StudentTable' object has no attribute 'create_record'
        self.assertEqual(record, test_data)

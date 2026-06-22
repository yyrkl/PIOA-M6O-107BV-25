import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import (
    InvalidAgeError,
    DuplicateIDError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError
)


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()
        self.db.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))

    def _insert_test_data(self):
        """Вспомогательный метод для вставки тестовых данных"""
        test_data = [
            {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"},
            {"student_id": 2, "first_name": "Jane", "second_name": "Smith", "age": 22, "sex": "F"},
            {"student_id": 3, "first_name": "Alice", "second_name": "Johnson", "age": 19, "sex": "F"},
            {"student_id": 4, "first_name": "Bob", "second_name": "Brown", "age": 21, "sex": "M"},
            {"student_id": 5, "first_name": "Charlie", "second_name": "Davis", "age": 18, "sex": "M"},
            {"student_id": 6, "first_name": "Eve", "second_name": "Miller", "age": 23, "sex": "F"},
            {"student_id": 7, "first_name": "Frank", "second_name": "Wilson", "age": 20, "sex": "M"},
            {"student_id": 8, "first_name": "Grace", "second_name": "Moore", "age": 22, "sex": "F"},
            {"student_id": 9, "first_name": "Hank", "second_name": "Taylor", "age": 19, "sex": "M"},
            {"student_id": 10, "first_name": "Ivy", "second_name": "Anderson", "age": 21, "sex": "F"},
        ]
        for record in test_data:
            self.db.insert_record("students", record)
        return test_data

    def test_create_record(self):
        """Тест создания записи"""
        test_data = [
            {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"},
            {"student_id": 2, "first_name": "Jane", "second_name": "Smith", "age": 22, "sex": "F"},
        ]
        
        for record in test_data:
            with self.subTest(record=record):
                self.db.insert_record("students", record)
                records = self.db.select_records("students", student_id=record["student_id"])
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0], record)

    def test_create_record_negative_age(self):
        """Тест создания записи с отрицательным возрастом"""
        invalid_records = [
            {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": -1, "sex": "M"},
            {"student_id": 2, "first_name": "Jane", "second_name": "Smith", "age": -5, "sex": "F"},
            {"student_id": 3, "first_name": "Alice", "second_name": "Johnson", "age": -10, "sex": "F"},
        ]
        
        for record in invalid_records:
            with self.subTest(record=record):
                with self.assertRaises(InvalidAgeError):
                    self.db.insert_record("students", record)

    def test_create_record_duplicate_id(self):
        """Тест создания записи с дублирующим ID"""
        record1 = {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"}
        record2 = {"student_id": 1, "first_name": "Jane", "second_name": "Smith", "age": 22, "sex": "F"}
        
        self.db.insert_record("students", record1)
        
        with self.assertRaises(DuplicateIDError):
            self.db.insert_record("students", record2)

    def test_select_record(self):
        """Тест поиска записей с фильтрами"""
        test_data = self._insert_test_data()
        
        test_cases = [
            {
                "name": "Выбор без фильтров",
                "filters": {},
                "expected_count": 10,
            },
            {
                "name": "Фильтр по ID",
                "filters": {"student_id": 1},
                "expected_count": 1,
                "expected_name": "John",
            },
            {
                "name": "Фильтр по имени",
                "filters": {"first_name": "Jane"},
                "expected_count": 1,
                "expected_name": "Jane",
            },
            {
                "name": "Фильтр по фамилии",
                "filters": {"second_name": "Johnson"},
                "expected_count": 1,
                "expected_name": "Alice",
            },
            {
                "name": "Фильтр по возрасту",
                "filters": {"age": 20},
                "expected_count": 2,  # John и Frank
            },
            {
                "name": "Фильтр по полу",
                "filters": {"sex": "F"},
                "expected_count": 5,  # Jane, Alice, Eve, Grace, Ivy
            },
        ]
        
        for case in test_cases:
            with self.subTest(case=case["name"]):
                records = self.db.select_records("students", **case["filters"])
                self.assertEqual(len(records), case["expected_count"])

    def test_update_record(self):
        """Тест обновления записи"""
        self.db.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        
        updated = self.db.update_records(
            "students",
            filters={"student_id": 1},
            updates={
                "first_name": "Johnny",
                "second_name": "Does",
                "age": 21,
                "sex": "M"
            }
        )
        
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0]["first_name"], "Johnny")
        self.assertEqual(updated[0]["second_name"], "Does")
        self.assertEqual(updated[0]["age"], 21)
        
        records = self.db.select_records("students")
        self.assertEqual(records[0]["first_name"], "Johnny")
        self.assertEqual(records[0]["second_name"], "Does")
        self.assertEqual(records[0]["age"], 21)

    def test_update_record_no_filter(self):
        """Тест обновления без фильтра - должно быть исключение"""
        self.db.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        
        with self.assertRaises(ValueError):
            self.db.update_records(
                "students",
                filters={},  # Пустой фильтр
                updates={"first_name": "Test"}
            )

    def test_update_record_no_new_values(self):
        """Тест обновления без новых значений - должно быть исключение"""
        self.db.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        
        with self.assertRaises(ValueError):
            self.db.update_records(
                "students",
                filters={"student_id": 1},
                updates={}  # Пустые обновления
            )

    def test_update_record_negative_age(self):
        """Тест обновления с отрицательным возрастом"""
        self.db.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        
        with self.assertRaises(InvalidAgeError):
            self.db.update_records(
                "students",
                filters={"student_id": 1},
                updates={"age": -5}
            )

    def test_delete_record(self):
        """Тест удаления записи"""
        self.db.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        self.db.insert_record("students", {"student_id": 2, "first_name": "Jane", "second_name": "Smith", "age": 22, "sex": "F"})
        
        deleted = self.db.delete_records("students", filters={"student_id": 1})
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0]["student_id"], 1)
        
        remaining = self.db.select_records("students")
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["student_id"], 2)

    def test_delete_record_no_filter(self):
        """Тест удаления без фильтра - должно быть исключение"""
        self.db.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        
        with self.assertRaises(ValueError):
            self.db.delete_records("students", filters={})

    def test_delete_record_by_name(self):
        """Тест удаления нескольких записей по фамилии"""
        self.db.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        self.db.insert_record("students", {"student_id": 2, "first_name": "Jane", "second_name": "Doe", "age": 22, "sex": "F"})
        
        deleted = self.db.delete_records("students", filters={"second_name": "Doe"})
        self.assertEqual(len(deleted), 2)
        
        remaining = self.db.select_records("students")
        self.assertEqual(len(remaining), 0)


if __name__ == "__main__":
    unittest.main()
    
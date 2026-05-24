# tests/test_tui.py
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
import os
from src.db.backend.memory import create_record, select_record, _default_table

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Правильные импорты для вашей структуры - tui в db, а не в backend
from src.db.tui import (
    _print_menu,
    _read_int,
    _add_student,
    _print_records,
    _show_all_students,
    _read_optional_int,
    _find_students_by_filter,
    _update_students_by_filter,
    _delete_students_by_filter,
    run,
)
from src.db.backend.memory import create_record, select_record


class TestTUIHelpers(unittest.TestCase):
    """Тесты для вспомогательных функций TUI"""
    
    def test_print_menu(self):
        """Тест вывода меню"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _print_menu()
            output = mock_stdout.getvalue()
            self.assertIn("=== База студентов ===", output)
            self.assertIn("1. Добавить запись", output)
            self.assertIn("0. Выход", output)
    
    def test_read_int_valid(self):
        """Тест чтения корректного целого числа"""
        with patch('builtins.input', return_value='42'):
            result = _read_int("Enter: ")
            self.assertEqual(result, 42)
    
    def test_read_int_invalid_then_valid(self):
        """Тест чтения числа с некорректным вводом"""
        with patch('builtins.input', side_effect=['abc', '123']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = _read_int("Enter: ")
                self.assertEqual(result, 123)
                self.assertIn("Ошибка: введите целое число", mock_stdout.getvalue())
    
    def test_print_records_with_records(self):
        """Тест вывода списка записей"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
        ]
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _print_records(records)
            output = mock_stdout.getvalue()
            self.assertIn("(1, 'John', 'Doe', 20, 'M')", output)
            self.assertIn("(2, 'Jane', 'Smith', 22, 'F')", output)
    
    def test_print_records_empty(self):
        """Тест вывода пустого списка"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _print_records([])
            self.assertIn("Записи не найдены", mock_stdout.getvalue())
    
    def test_read_optional_int_valid(self):
        """Тест чтения опционального целого числа"""
        with patch('builtins.input', return_value='25'):
            result = _read_optional_int("Age: ")
            self.assertEqual(result, 25)
    
    def test_read_optional_int_empty(self):
        """Тест чтения пустого значения"""
        with patch('builtins.input', return_value=''):
            result = _read_optional_int("Age: ")
            self.assertIsNone(result)
    
    def test_read_optional_int_invalid(self):
        """Тест чтения некорректного опционального числа"""
        with patch('builtins.input', side_effect=['abc', '30']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = _read_optional_int("Age: ")
                self.assertEqual(result, 30)
                self.assertIn("Ошибка: введите целое число", mock_stdout.getvalue())


class TestTUIAddStudent(unittest.TestCase):
    """Тесты для добавления студента"""
    
    def setUp(self):
        # Очищаем таблицу перед каждым тестом через приватную переменную
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
    
    @patch('src.db.tui._read_int')
    @patch('builtins.input')
    def test_add_student_success(self, mock_input, mock_read_int):
        """Тест успешного добавления студента"""
        mock_read_int.side_effect = [1, 20]  # id, age
        mock_input.side_effect = ["John", "Doe", "M"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _add_student()
            output = mock_stdout.getvalue()
            self.assertIn("Запись добавлена", output)
            self.assertIn("John", output)
    
    @patch('src.db.tui._read_int')
    @patch('builtins.input')
    def test_add_student_duplicate_id(self, mock_input, mock_read_int):
        """Тест добавления дублирующего ID"""
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
        
        # Добавляем первого студента
        create_record(1, "John", "Doe", 20, "M")
        
        mock_read_int.side_effect = [1, 20]  # id, age
        mock_input.side_effect = ["Jane", "Smith", "F"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _add_student()
            output = mock_stdout.getvalue()
            self.assertIn("Ошибка", output)
            self.assertIn("уже существует", output)
    
    @patch('src.db.tui._read_int')
    @patch('builtins.input')
    def test_add_student_negative_age(self, mock_input, mock_read_int):
        """Тест добавления с отрицательным возрастом"""
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
        
        mock_read_int.side_effect = [1, -5]  # id, age
        mock_input.side_effect = ["John", "Doe", "M"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _add_student()
            output = mock_stdout.getvalue()
            self.assertIn("Ошибка", output)
            self.assertIn("не может быть отрицательным", output)


class TestTUIShowAllStudents(unittest.TestCase):
    """Тесты для показа всех студентов"""
    
    def setUp(self):
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
    
    def test_show_all_students_empty(self):
        """Тест показа пустого списка"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _show_all_students()
            self.assertIn("Записи не найдены", mock_stdout.getvalue())
    
    def test_show_all_students_with_data(self):
        """Тест показа непустого списка"""
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
        create_record(1, "John", "Doe", 20, "M")
        create_record(2, "Jane", "Smith", 22, "F")
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _show_all_students()
            output = mock_stdout.getvalue()
            self.assertIn("John", output)
            self.assertIn("Jane", output)


class TestTUIFindStudents(unittest.TestCase):
    """Тесты для поиска студентов"""
    
    def setUp(self):
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
        # Создаем тестовые данные перед каждым тестом
        create_record(1, "John", "Doe", 20, "M")
        create_record(2, "Jane", "Smith", 22, "F")
        create_record(3, "John", "Smith", 21, "M")
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_find_by_id(self, mock_input, mock_read_int):
        """Тест поиска по ID"""
        # student_id=1, age=None (Enter)
        mock_read_int.side_effect = [1, None]
        # Все строковые поля пропускаем (Enter)
        mock_input.side_effect = ["", "", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _find_students_by_filter()
            output = mock_stdout.getvalue()
            # Проверяем, что запись с ID=1 найдена
            self.assertIn("John", output)
            self.assertIn("Doe", output)
            self.assertIn("20", output)
            # Проверяем, что нет других записей
            self.assertNotIn("Jane", output)
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_find_by_name(self, mock_input, mock_read_int):
        """Тест поиска по имени"""
        mock_read_int.side_effect = [None, None]
        mock_input.side_effect = ["John", "", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _find_students_by_filter()
            output = mock_stdout.getvalue()
            # Должно быть две записи с John
            self.assertEqual(output.count("John"), 2)
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_find_by_age(self, mock_input, mock_read_int):
        """Тест поиска по возрасту"""
        mock_read_int.side_effect = [None, 20]
        mock_input.side_effect = ["", "", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _find_students_by_filter()
            output = mock_stdout.getvalue()
            # Должна быть одна запись с возрастом 20
            self.assertIn("John", output)
            self.assertIn("Doe", output)
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_find_no_results(self, mock_input, mock_read_int):
        """Тест поиска без результатов"""
        mock_read_int.side_effect = [999, None]
        mock_input.side_effect = ["", "", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _find_students_by_filter()
            output = mock_stdout.getvalue()
            self.assertIn("Записи не найдены", output)


class TestTUIUpdateStudents(unittest.TestCase):
    """Тесты для обновления студентов"""
    
    def setUp(self):
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
        create_record(1, "John", "Doe", 20, "M")
        create_record(2, "Jane", "Smith", 22, "F")
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_update_no_criteria(self, mock_input, mock_read_int):
        """Тест обновления без указания критериев"""
        mock_read_int.return_value = None
        mock_input.return_value = ""  # Все поля пустые
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _update_students_by_filter()
            output = mock_stdout.getvalue()
            self.assertIn("нужно указать хотя бы один критерий", output)
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_update_cancel_operation(self, mock_input, mock_read_int):
        """Тест отмены обновления"""
        mock_read_int.side_effect = [None, None]  # id и age
        mock_input.side_effect = ["John", "", "", "н"]  # Имя John, отмена
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _update_students_by_filter()
            output = mock_stdout.getvalue()
            self.assertIn("Обновление отменено", output)
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_update_no_new_values(self, mock_input, mock_read_int):
        """Тест обновления без указания новых значений"""
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
        create_record(1, "John", "Doe", 20, "M")
    
    # Мокаем _read_optional_int для всех вызовов
    # Вызовы: student_id, age, new_age
        mock_read_int.side_effect = [None, None, None]
    
    # Мокаем все input вызовы:
    # 1. first_name = "John"
    # 2. second_name = "" (Enter)
    # 3. sex = "" (Enter)  
    # 4. confirm = "д"
    # 5. new_first_name = "" (Enter)
    # 6. new_second_name = "" (Enter)
    # 7. new_sex = "" (Enter)
        mock_input.side_effect = ["John", "", "", "д", "", "", ""]
    
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _update_students_by_filter()
            output = mock_stdout.getvalue()
        # Проверяем, что появилось сообщение об ошибке
            self.assertIn("нужно указать хотя бы одно поле", output)


class TestTUIDeleteStudents(unittest.TestCase):
    """Тесты для удаления студентов"""
    
    def setUp(self):
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
        create_record(1, "John", "Doe", 20, "M")
        create_record(2, "Jane", "Smith", 22, "F")
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_delete_no_criteria(self, mock_input, mock_read_int):
        """Тест удаления без критериев"""
        mock_read_int.return_value = None
        mock_input.return_value = ""
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _delete_students_by_filter()
            output = mock_stdout.getvalue()
            self.assertIn("укажите критерий для поиска", output)
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_delete_cancel(self, mock_input, mock_read_int):
        """Тест отмены удаления"""
        mock_read_int.return_value = None
        mock_input.side_effect = ["John", "", "", "н"]  # Имя John, отмена
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _delete_students_by_filter()
            self.assertIn("Удаление отменено", mock_stdout.getvalue())
        
        # Проверяем, что записи не удалились
        records = select_record()
        self.assertEqual(len(records), 2)
    
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_delete_success(self, mock_input, mock_read_int):
        """Тест успешного удаления"""
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
        create_record(1, "John", "Doe", 20, "M")
        
        mock_read_int.return_value = None
        mock_input.side_effect = ["John", "", "", "д"]  # Имя John, подтверждение
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _delete_students_by_filter()
            output = mock_stdout.getvalue()
            self.assertIn("Удаленные записи", output)
        
        # Проверяем, что записи удалились
        records = select_record()
        self.assertEqual(len(records), 0)


class TestTUIRun(unittest.TestCase):
    """Тесты для главного цикла программы"""
    
    def setUp(self):
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
    
    @patch('builtins.input')
    def test_run_exit(self, mock_input):
        """Тест выхода из программы"""
        mock_input.side_effect = ["0"]  # Сразу выход
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('src.db.tui._print_menu'):
                run()
                self.assertIn("Выход из программы", mock_stdout.getvalue())
    
    @patch('builtins.input')
    def test_run_invalid_command(self, mock_input):
        """Тест некорректной команды"""
        mock_input.side_effect = ["999", "0"]  # Неверная команда, потом выход
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('src.db.tui._print_menu'):
                run()
                output = mock_stdout.getvalue()
                self.assertIn("Неизвестная команда", output)
    
    @patch('builtins.input')
    @patch('src.db.tui._add_student')
    def test_run_add_student(self, mock_add_student, mock_input):
        """Тест выбора добавления студента"""
        mock_input.side_effect = ["1", "0"]  # Сначала 1, потом выход
        
        with patch('sys.stdout', new_callable=StringIO):
            with patch('src.db.tui._print_menu'):
                run()
                mock_add_student.assert_called_once()


class TestTUIIntegration(unittest.TestCase):
    """Интеграционные тесты TUI с реальной базой данных"""
    
    def setUp(self):
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
    
    @patch('src.db.tui._read_int')
    @patch('src.db.tui._read_optional_int')
    @patch('builtins.input')
    def test_full_workflow(self, mock_input, mock_read_optional, mock_read_int):
        """Полный workflow: добавление -> поиск -> удаление"""
        from src.db.backend.memory import _default_table
        _default_table._student.clear()
        
        # Добавление студента 
        # _add_student() вызывает:
        # - _read_int 2 раза (id, age)
        # - input 3 раза (first_name, second_name, sex)
        mock_read_int.side_effect = [1, 20]
        mock_input.side_effect = ["John", "Doe", "M"]
        
        with patch('sys.stdout', new_callable=StringIO):
            _add_student()
        
        # Проверяем, что студент добавился
        records = select_record()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 1)
        self.assertEqual(records[0][1], "John")
        
        # Поиск студента 
        # _find_students_by_filter() вызывает:
        # - _read_optional_int 2 раза (id, age)
        # - input 3 раза (first_name, second_name, sex)
        mock_read_optional.side_effect = [1, None]  # id=1, age=None
        mock_input.side_effect = ["", "", ""]  # все поля пропускаем (Enter)
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _find_students_by_filter()
            output = mock_stdout.getvalue()
            # Проверяем, что студент найден
            self.assertIn("John", output)
            self.assertIn("Doe", output)
        
        # Удаление студента 
        # _delete_students_by_filter() вызывает:
        # - _read_optional_int 2 раза (id, age)
        # - input 4 раза (first_name, second_name, sex, confirm)
        mock_read_optional.side_effect = [1, None]  # id=1, age=None
        mock_input.side_effect = ["", "", "", "д"]  # все поля пропускаем, подтверждаем
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            _delete_students_by_filter()
            output = mock_stdout.getvalue()
            self.assertIn("Удаленные записи", output)
        
        # Проверяем, что студент удалился
        records = select_record()
        self.assertEqual(len(records), 0)


if __name__ == '__main__':
    unittest.main()
    
import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.db.backend.memory import MemoryDatabase
from src.db.backend.file import FileDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
    DuplicateIDError,
    InvalidAgeError,
)


class TUI:
    """Текстовый пользовательский интерфейс."""

    def __init__(self) -> None:
        self.database = None
        self.current_table = "students"
        self._select_database()

    def _select_database(self) -> None:
        """Выбор типа базы данных."""
        print("\n=== Выбор типа базы данных ===")
        print("1. In-memory (данные не сохраняются)")
        print("2. File-based (данные сохраняются в файл)")

        while True:
            choice = input("Выберите тип (1/2): ").strip()
            if choice == "1":
                self.database = MemoryDatabase()
                print("Выбран in-memory режим.")
                break
            elif choice == "2":
                directory = input("Введите путь для хранения файлов (Enter для 'data'): ").strip()
                if not directory:
                    directory = "data"
                self.database = FileDatabase(directory)
                print(f"Выбран файловый режим. Данные хранятся в '{directory}/'")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

        self._init_students_table()

    def _init_students_table(self) -> None:
        """Инициализация таблицы students."""
        try:
            self.database.create_table(
                "students",
                ("student_id", "first_name", "second_name", "age", "sex")
            )
        except TableAlreadyExistsError:
            pass  # Таблица уже существует - хорошо

    def _read_int(self, prompt: str) -> int:
        """Чтение целого числа."""
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> int | None:
        """Чтение опционального целого числа."""
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _print_menu(self) -> None:
        """Вывод меню."""
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить записи по фильтру")
        print("5. Удалить записи по фильтру")
        print("0. Выход")

    def _add_student(self) -> None:
        """Добавление студента."""
        print("\nДобавление записи")

        try:
            student_id = self._read_int("id: ")
            first_name = input("first_name: ").strip()
            second_name = input("second_name: ").strip()
            age = self._read_int("age: ")
            sex = input("sex: ").strip()

            # Валидация
            if age < 0:
                raise InvalidAgeError("Поле age не может быть отрицательным.")

            # Проверка на дубликат ID
            existing = self.database.select_records(
                self.current_table,
                student_id=student_id
            )
            if existing:
                raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

            record = {
                "student_id": student_id,
                "first_name": first_name,
                "second_name": second_name,
                "age": age,
                "sex": sex,
            }
            self.database.insert_record(self.current_table, record)
            print(f"Запись добавлена: {record}")

        except (DuplicateIDError, InvalidAgeError, MissingColumnError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")

    def _print_records(self, records: list[dict]) -> None:
        """Вывод записей."""
        if not records:
            print("Записи не найдены.")
            return

        for record in records:
            print(f"({record['student_id']}, '{record['first_name']}', "
                  f"'{record['second_name']}', {record['age']}, '{record['sex']}')")

    def _show_all_students(self) -> None:
        """Показать всех студентов."""
        print("\nСписок записей")
        try:
            records = self.database.select_records(self.current_table)
            self._print_records(records)
        except TableNotFoundError as e:
            print(f"Ошибка: {e}")

    def _find_students_by_filter(self) -> None:
        """Поиск студентов по фильтру."""
        print("\nПоиск по фильтру (Enter = пропустить поле)")

        student_id = self._read_optional_int("id: ")
        first_name = input("first_name: ").strip() or None
        second_name = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        filters = {}
        if student_id is not None:
            filters["student_id"] = student_id
        if first_name is not None:
            filters["first_name"] = first_name
        if second_name is not None:
            filters["second_name"] = second_name
        if age is not None:
            filters["age"] = age
        if sex is not None:
            filters["sex"] = sex

        try:
            records = self.database.select_records(self.current_table, **filters)
            self._print_records(records)
        except (TableNotFoundError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")

    def _update_students_by_filter(self) -> None:
        """Обновление студентов по фильтру."""
        print("\nПоиск записи для обновления")

        # Сбор фильтров
        student_id = self._read_optional_int("ID студента (Enter - пропустить): ")
        first_name = input("Имя (Enter - пропустить): ").strip() or None
        second_name = input("Фамилия (Enter - пропустить): ").strip() or None
        age = self._read_optional_int("Возраст (Enter - пропустить): ")
        sex = input("Пол (М/Ж, Enter - пропустить): ").strip().upper() or None

        filters = {}
        if student_id is not None:
            filters["student_id"] = student_id
        if first_name is not None:
            filters["first_name"] = first_name
        if second_name is not None:
            filters["second_name"] = second_name
        if age is not None:
            filters["age"] = age
        if sex is not None:
            filters["sex"] = sex

        if not filters:
            print("\nОшибка: нужно указать хотя бы один критерий поиска!")
            return

        try:
            matching = self.database.select_records(self.current_table, **filters)
            print(f"\nНайдено записей для обновления: {len(matching)}")

            if not matching:
                print("Нет записей, соответствующих критериям.")
                return

            print("\nЗаписи, которые будут обновлены:")
            self._print_records(matching)

            confirm = input("\nПродолжить обновление? (д/н): ").strip().lower()
            if confirm != 'д':
                print("Обновление отменено.")
                return

            print("\n--- НОВЫЕ ЗНАЧЕНИЯ ---")
            print("(Оставьте поле пустым, если не хотите его менять)")

            updates = {}
            new_first_name = input("Новое имя (Enter - не менять): ").strip()
            if new_first_name:
                updates["first_name"] = new_first_name

            new_second_name = input("Новая фамилия (Enter - не менять): ").strip()
            if new_second_name:
                updates["second_name"] = new_second_name

            new_age = self._read_optional_int("Новый возраст (Enter - не менять): ")
            if new_age is not None:
                if new_age < 0:
                    print("Ошибка: возраст не может быть отрицательным!")
                    return
                updates["age"] = new_age

            new_sex = input("Новый пол (М/Ж, Enter - не менять): ").strip().upper()
            if new_sex:
                updates["sex"] = new_sex

            if not updates:
                print("\nОшибка: нужно указать хотя бы одно поле для обновления!")
                return

            updated = self.database.update_records(self.current_table, filters, updates)

            if updated:
                print("\nОбновленные записи:")
                self._print_records(updated)
            else:
                print("\nЗаписи не найдены или не обновлены")

        except (TableNotFoundError, UnknownColumnError, ValueError) as e:
            print(f"\nОшибка: {e}")

    def _delete_students_by_filter(self) -> None:
        """Удаление студентов по фильтру."""
        print("\nПоиск записей для удаления")

        # Сбор фильтров
        student_id = self._read_optional_int("ID студента (Enter - пропустить): ")
        first_name = input("Имя (Enter - пропустить): ").strip() or None
        second_name = input("Фамилия (Enter - пропустить): ").strip() or None
        age = self._read_optional_int("Возраст (Enter - пропустить): ")
        sex = input("Пол (М/Ж, Enter - пропустить): ").strip().upper() or None

        filters = {}
        if student_id is not None:
            filters["student_id"] = student_id
        if first_name is not None:
            filters["first_name"] = first_name
        if second_name is not None:
            filters["second_name"] = second_name
        if age is not None:
            filters["age"] = age
        if sex is not None:
            filters["sex"] = sex

        if not filters:
            print("\nОшибка: укажите критерий для поиска")
            return

        try:
            records_to_delete = self.database.select_records(self.current_table, **filters)
            print(f"\nЗаписи для удаления: {len(records_to_delete)}")

            if not records_to_delete:
                print("Нет таких записей")
                return

            print("\nЗаписи для удаления:")
            for i, record in enumerate(records_to_delete, 1):
                print(f"  {i}. ID: {record['student_id']}, {record['first_name']} "
                      f"{record['second_name']}, {record['age']} лет, {record['sex']}")

            print("\nПодтверждение")
            confirm = input("Вы точно хотите удалить эти записи? (д/н): ").strip().lower()
            if confirm != 'д':
                print("Удаление отменено.")
                return

            deleted = self.database.delete_records(self.current_table, filters)

            if deleted:
                print("\nУдаленные записи:")
                for i, record in enumerate(deleted, 1):
                    print(f"  {i}. ID: {record['student_id']}, {record['first_name']} "
                          f"{record['second_name']}, {record['age']} лет, {record['sex']}")

        except (TableNotFoundError, UnknownColumnError) as e:
            print(f"\nОшибка: {e}")

    def run(self) -> None:
        """Запуск основного цикла."""
        while True:
            self._print_menu()
            action = input("Выберите действие: ").strip()

            if action == "1":
                self._add_student()
            elif action == "2":
                self._show_all_students()
            elif action == "3":
                self._find_students_by_filter()
            elif action == "4":
                self._update_students_by_filter()
            elif action == "5":
                self._delete_students_by_filter()
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")


def run() -> None:
    """Точка входа для TUI."""
    app = TUI()
    app.run()


if __name__ == "__main__":
    run()


"""from .backend.memory import (
    create_record, 
    select_record, 
    update_record, 
    delete_record, 
    StudentTable,
)

def _print_menu() -> None:
    # Символ \n обозначает перевод строки.
    print("\n=== База студентов ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи по фильтру")
    print("4. Обновить записи по фильтру")
    print("5. Удалить записи по фильтру")
    print("0. Выход")

# Функция чтения целочисленного значения из консоли.
def _read_int(prompt: str) -> int:
    # Используется цикл с повторением до получения корректного ввода.
    while True:
        # Получение строки из консоли с удалением пробельных символов
        # в начале и в конце строки.
        raw = input(prompt).strip()
        try:
            # Преобразование строки к целому числу.
            return int(raw)
        except ValueError:
            # Исключение возникает при невозможности преобразования.
            # Пользователю выводится сообщение об ошибке,
            # после чего ввод повторяется.
            print("Ошибка: введите целое число.")

# Функция добавления новой записи в базу данных.
from src.db.backend.errors import DuplicateIDError, InvalidAgeError

def _add_student() -> None:
    print("\nДобавление записи")
    student_id = _read_int("id: ")
    first_name = input("first_name: ").strip()
    second_name = input("second_name: ").strip()
    age = _read_int("age: ")
    sex = input("sex: ").strip()
    try:
        record = create_record(student_id, first_name, second_name, age, sex)
        print(f"Запись добавлена: {record}")

    except (DuplicateIDError, InvalidAgeError) as exc:
        print(f"Ошибка: {exc}")

# Вспомогательная функция вывода списка записей.
def _print_records(records: list[tuple[int, str, str, int, str]]) -> None:
    # Проверка на пустой список.
    if not records:
        print("Записи не найдены.")
        return

    # Последовательный вывод записей.
    for record in records:
        print(record)

# Функция вывода всех записей из базы данных.
def _show_all_students() -> None:
    print("\nСписок записей")
    _print_records(select_record())

# Функция чтения необязательного целочисленного значения.
# Пустой ввод интерпретируется как отсутствие фильтра (None).
def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()

        if raw == "":
            return None

        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")

# Функция поиска записей по заданным фильтрам.
def _find_students_by_filter() -> None:
    print("\nПоиск по фильтру (Enter = пропустить поле)")

    student_id = _read_optional_int("id: ")

    # Оператор `or` возвращает первое истинное значение.
    # Если строка после strip() пуста, будет возвращено None.
    first_name = input("first_name: ").strip() or None
    second_name = input("second_name: ").strip() or None

    age = _read_optional_int("age: ")
    sex = input("sex: ").strip() or None

    records = select_record(
        student_id=student_id,
        first_name=first_name,
        second_name=second_name,
        age=age,
        sex=sex,
  )

    _print_records(records)

def _update_students_by_filter() -> None:
    print("Поиск записи для обновления")
    
    student_id = _read_optional_int("ID студента(Enter - пропустить)")
    first_name = input("Имя (Enter - пропустить): ").strip()
    first_name = first_name if first_name else None
    second_name = input("Фамилия (Enter - пропустить): ").strip()
    second_name = second_name if second_name else None
    age = _read_optional_int("Возраст (Enter - пропустить): ")
    sex = input("Пол (М/Ж, Enter - пропустить): ").strip().upper()
    sex = sex if sex else None
    if (student_id is None and first_name is None and 
        second_name is None and age is None and sex is None):
        print("\n Ошибка: нужно указать хотя бы один критерий поиска!")
        return
    matching = select_record(student_id, first_name, second_name, age, sex)
    print(f"\nНайдено записей для обновления: {len(matching)}")
    
    if not matching:
        print("Нет записей, соответствующих критериям.")
        return
    print("\nЗаписи, которые будут обновлены:")
    for record in matching:
        print(f"  {record}")
    
    confirm = input("\nПродолжить обновление? (д/н): ").strip().lower()
    if confirm != 'д':
        print("Обновление отменено.")
        return
    print("\n--- НОВЫЕ ЗНАЧЕНИЯ ---")
    print("(Оставьте поле пустым, если не хотите его менять)")
    
    new_first_name = input("Новое имя (Enter - не менять): ").strip()
    new_first_name = new_first_name if new_first_name else None
    
    new_second_name = input("Новая фамилия (Enter - не менять): ").strip()
    new_second_name = new_second_name if new_second_name else None
    
    new_age = _read_optional_int("Новый возраст (Enter - не менять): ")
    
    new_sex = input("Новый пол (М/Ж, Enter - не менять): ").strip().upper()
    new_sex = new_sex if new_sex else None
    
    if (new_first_name is None and new_second_name is None and 
        new_age is None and new_sex is None):
        print("\n Ошибка: нужно указать хотя бы одно поле для обновления!")
        return
    
    try:
        updated = []
        for record in matching:
            result = update_record(
                student_id = record[0],
                new_first_name=new_first_name,
                new_second_name=new_second_name,
                new_age=new_age,
                new_sex=new_sex
            )
            updated.extend(result)

        if updated:
            print("\nОбновленные записи:")
            for record in updated:
                print(f"  {record}")
        else:
            print("\n Записи не найдены или не обновлены")
    
    except Exception as e:
        print(f"\n Ошибка: {e}")

def _delete_students_by_filter() -> None:
    student_id = _read_optional_int("\n ID студента(Enter - пропустить)")
    
    first_name = input("Имя (Enter - пропустить): ").strip()
    first_name = first_name if first_name else None
    
    second_name = input("Фамилия (Enter - пропустить): ").strip()
    second_name = second_name if second_name else None
    
    age = _read_optional_int("Возраст (Enter - пропустить): ")
    
    sex = input("Пол (М/Ж, Enter - пропустить): ").strip().upper()
    sex = sex if sex else None
    
    if (student_id is None and first_name is None and 
        second_name is None and age is None and sex is None):
        print("\n Ошибка: укажите критерий для поиска")
        return
    
    records_to_delete = select_record(
        student_id=student_id,
        first_name=first_name,
        second_name=second_name,
        age=age,
        sex=sex
    )
    
    print(f"\n Записи для удаления: {len(records_to_delete)}")
    
    if not records_to_delete:
        print("Нет таких записей")
        return
    
    print("\n Записи для удаления:")
    for i, record in enumerate(records_to_delete, 1):
        print(f"  {i}. ID: {record[0]}, {record[1]} {record[2]}, {record[3]} лет, {record[4]}")
    
    print("\n  Подтверждение")
    confirm1 = input("Вы точно хотите удалить эти записи? (д/н): ").strip().lower()
    
    if confirm1 != 'д':
        print("Удаление отменено.")
        return
    
    try:
        deleted = delete_record(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex
        )
        
        if deleted:
            print("\n Удаленные записи:")
            for i, record in enumerate(deleted, 1):
                print(f"  {i}. ID: {record[0]}, {record[1]} {record[2]}, {record[3]} лет, {record[4]}")
        
    except ValueError as e:
        print(f"\n Ошибка: {e}")
    except Exception as e:
        print(f"\n Ошибка: {e}")

def run() -> None:
    
    while True:
        # Отображение меню доступных действий.
        _print_menu()

        # Получение команды пользователя.
        # Метод strip() удаляет пробельные символы
        # в начале и в конце строки.
        action = input("Выберите действие: ").strip()

        # Диспетчеризация пользовательской команды.
        if action == "1":
            _add_student()

        elif action == "2":
            _show_all_students()

        elif action == "3":
            _find_students_by_filter()
        
        elif action == "4":
            _update_students_by_filter()
        
        elif action == "5":
            _delete_students_by_filter()

        elif action == "0":
            # Завершение работы программы.
            print("Выход из программы.")
            break

        else:
            # Обработка некорректного ввода команды.
            print("Неизвестная команда. Повторите ввод.") """

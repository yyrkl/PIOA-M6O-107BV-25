from .backend.memory import (
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
    """
    Запускает основной цикл текстового пользовательского интерфейса.

    Цикл выполняется до тех пор, пока пользователь явно
    не выберет завершение программы.
    """
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
            print("Неизвестная команда. Повторите ввод.")

from .errors import DuplicateIDError, InvalidAgeError

type StudentRecord = tuple[int, str, str, int, str]


class StudentTable:
    def __init__(self) -> None:
        self._student: list[StudentRecord] = []

    def create_record(
        self,
        student_id: int,
        first_name: str,
        second_name: str,
        age: int,
        sex: str,
    ) -> StudentRecord:
        if age < 0:
            raise InvalidAgeError("Поле age не может быть отрицательным.")
        if any(record[0] == student_id for record in self._student):
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

        new_record: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )
        self._student.append(new_record)
        return new_record

    def select_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
    ) -> list[StudentRecord]:
        if (
            student_id is None
            and first_name is None
            and second_name is None
            and age is None
            and sex is None
        ):
            return self._student.copy()

        result: list[StudentRecord] = []
        for record in self._student:
            if student_id is not None and record[0] != student_id:
                continue
            if first_name is not None and record[1] != first_name:
                continue
            if second_name is not None and record[2] != second_name:
                continue
            if age is not None and record[3] != age:
                continue
            if sex is not None and record[4] != sex:
                continue
            result.append(record)
        return result

    def update_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
        new_first_name: str | None = None,
        new_second_name: str | None = None,
        new_age: int | None = None,
        new_sex: str | None = None,
    ) -> list[StudentRecord]:
        if (student_id is None
            and first_name is None
            and second_name is None
            and age is None
            and sex is None):
            raise ValueError("Укажите параметр поиска")
        if (new_first_name is None
            and new_second_name is None
            and new_age is None
            and new_sex is None):
            raise ValueError("Укажите поле для обновления")
        if new_age is not None and new_age < 0:
            raise ValueError("Возраст не может быть отрицательным")

        updated_records = []
        for i, record in enumerate(self._student):
            if student_id is not None and record[0] != student_id:
                continue
            if first_name is not None and record[1] != first_name:
                continue
            if second_name is not None and record[2] != second_name:
                continue
            if age is not None and record[3] != age:
                continue
            if sex is not None and record[4] != sex:
                continue

            updated_record = list(record)
            if new_first_name is not None:
                updated_record[1] = new_first_name.strip()
            if new_second_name is not None:
                updated_record[2] = new_second_name.strip()
            if new_age is not None:
                updated_record[3] = new_age
            if new_sex is not None:
                updated_record[4] = new_sex.strip()

            new_record = tuple(updated_record)
            self._student[i] = new_record
            updated_records.append(new_record)
        return updated_records

    def delete_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
    ) -> list[StudentRecord]:
        if (student_id is None
            and first_name is None
            and second_name is None
            and age is None
            and sex is None):
            raise ValueError("Укажите параметр поиска")

        deleted_records = []
        for i in range(len(self._student) - 1, -1, -1):
            record = self._student[i]
            if student_id is not None and record[0] != student_id:
                continue
            if first_name is not None and record[1] != first_name:
                continue
            if second_name is not None and record[2] != second_name:
                continue
            if age is not None and record[3] != age:
                continue
            if sex is not None and record[4] != sex:
                continue
            deleted = self._student.pop(i)
            deleted_records.append(deleted)
        return deleted_records


# ---- СТАРЫЙ КОД (обёртки для tui.py) ----

_default_table = StudentTable()

def create_record(
    student_id: int,
    first_name: str,
    second_name: str,
    age: int,
    sex: str,
) -> StudentRecord:
    return _default_table.create_record(student_id, first_name, second_name, age, sex)

def select_record(
    student_id: int | None = None,
    first_name: str | None = None,
    second_name: str | None = None,
    age: int | None = None,
    sex: str | None = None,
) -> list[StudentRecord]:
    return _default_table.select_record(student_id, first_name, second_name, age, sex)

def update_record(
    student_id: int | None = None,
    first_name: str | None = None,
    second_name: str | None = None,
    age: int | None = None,
    sex: str | None = None,
    new_first_name: str | None = None,
    new_second_name: str | None = None,
    new_age: int | None = None,
    new_sex: str | None = None,
) -> list[StudentRecord]:
    return _default_table.update_record(
        student_id, first_name, second_name, age, sex,
        new_first_name, new_second_name, new_age, new_sex
    )

def delete_record(
    student_id: int | None = None,
    first_name: str | None = None,
    second_name: str | None = None,
    age: int | None = None,
    sex: str | None = None,
) -> list[StudentRecord]:
    return _default_table.delete_record(student_id, first_name, second_name, age, sex)
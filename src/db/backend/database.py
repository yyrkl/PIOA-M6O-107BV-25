from abc import ABC, abstractmethod
from typing import Any
from .errors import (
    TableAlreadyExistsError, 
    TableNotFoundError,
    DuplicateIDError,
    InvalidAgeError
)
from .table import Table


class Database(ABC):
    """Общий интерфейс базы данных."""

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(
                f"Таблица '{table_name}' уже существует."
            )
        self._save_table(table_name, Table(columns))

    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        """Добавляет запись в таблицу с валидацией."""
        # Валидация возраста
        if "age" in record and record["age"] < 0:
            raise InvalidAgeError("Поле age не может быть отрицательным.")
        
        # Загружаем таблицу
        table = self._load_table(table_name)
        
        # Проверка дубликата ID
        if "student_id" in record:
            for existing_record in table.records:
                if existing_record.get("student_id") == record["student_id"]:
                    raise DuplicateIDError(f"Запись с id={record['student_id']} уже существует.")
        
        # Вставляем запись через Table (там тоже есть валидация)
        table.insert_record(record)
        self._save_table(table_name, table)

    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.select_records(**filters)

    def update_records(
        self,
        table_name: str,
        filters: dict[str, Any],
        updates: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Обновляет записи с валидацией."""
        if not filters:
            raise ValueError("Укажите параметр поиска")
        
        if not updates:
            raise ValueError("Укажите поле для обновления")
        
        if "age" in updates and updates["age"] < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным")
        
        table = self._load_table(table_name)
        updated = table.update_records(filters, updates)
        self._save_table(table_name, table)
        return updated

    def delete_records(
        self,
        table_name: str,
        filters: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Удаляет записи с проверкой фильтра."""
        if not filters:
            raise ValueError("Укажите параметр поиска")
        
        table = self._load_table(table_name)
        deleted = table.delete_records(filters)
        self._save_table(table_name, table)
        return deleted

    @abstractmethod
    def _table_exists(self, table_name: str) -> bool:
        pass

    @abstractmethod
    def _load_table(self, table_name: str) -> Table:
        pass

    @abstractmethod
    def _save_table(self, table_name: str, table: Table) -> None:
        pass

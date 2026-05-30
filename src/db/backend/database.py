from abc import ABC, abstractmethod
from typing import Any

from .errors import TableAlreadyExistsError, TableNotFoundError
from .table import Table


class Database(ABC):
    """Общий интерфейс базы данных."""

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        """Создаёт новую таблицу."""
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(
                f"Таблица '{table_name}' уже существует."
            )

        self._save_table(table_name, Table(columns))

    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        """Добавляет запись в таблицу."""
        table = self._load_table(table_name)
        table.insert_record(record)
        self._save_table(table_name, table)

    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        """Ищет записи в таблице по фильтрам."""
        table = self._load_table(table_name)
        return table.select_records(**filters)

    def update_records(
        self,
        table_name: str,
        filters: dict[str, Any],
        updates: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Обновляет записи, соответствующие фильтрам."""
        table = self._load_table(table_name)
        updated = table.update_records(filters, updates)
        self._save_table(table_name, table)
        return updated

    def delete_records(
        self,
        table_name: str,
        filters: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Удаляет записи, соответствующие фильтрам."""
        table = self._load_table(table_name)
        deleted = table.delete_records(filters)
        self._save_table(table_name, table)
        return deleted

    @abstractmethod
    def _table_exists(self, table_name: str) -> bool:
        """Проверяет наличие таблицы."""
        pass

    @abstractmethod
    def _load_table(self, table_name: str) -> Table:
        """Загружает таблицу."""
        pass

    @abstractmethod
    def _save_table(self, table_name: str, table: Table) -> None:
        """Сохраняет таблицу."""
        pass
    
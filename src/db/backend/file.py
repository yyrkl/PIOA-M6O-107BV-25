import json
from pathlib import Path
from typing import Any

from src.db.backend.database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class FileDatabase(Database):
    """База данных, которая хранит таблицы в JSON-файлах."""

    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as error:
            raise InvalidStorageDataError(
                f"Не удалось создать директорию '{directory}': {error}"
            ) from error

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(
                f"Таблица '{table_name}' не существует."
            )

        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}.json' содержит некорректный JSON."
            ) from error
        except (PermissionError, OSError, IOError) as error:
            raise InvalidStorageDataError(
                f"Ошибка доступа к файлу '{table_name}.json': {error}"
            ) from error

        return self._deserialize_table(data, table_name)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)

        try:
            with table_path.open("w", encoding="utf-8") as file:
                json.dump(
                    self._serialize_table(table),
                    file,
                    ensure_ascii=False,
                    indent=2,
                )
        except (PermissionError, OSError, IOError) as error:
            raise InvalidStorageDataError(
                f"Ошибка сохранения файла '{table_name}.json': {error}"
            ) from error

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _serialize_table(self, table: Table) -> dict[str, Any]:
        return {
            "columns": list(table.columns),
            "records": [record.copy() for record in table.records],
        }

    def _deserialize_table(self, data: dict[str, Any], table_name: str) -> Table:
        # Проверка типа данных
        if not isinstance(data, dict):
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}.json' имеет некорректный формат: ожидается словарь, получен {type(data).__name__}"
            )

        # Проверка наличия обязательных полей
        if "columns" not in data:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}.json' не содержит поле 'columns'"
            )
        
        if "records" not in data:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}.json' не содержит поле 'records'"
            )

        # Проверка типа columns
        if not isinstance(data["columns"], list):
            raise InvalidStorageDataError(
                f"Поле 'columns' в таблице '{table_name}.json' должно быть списком, получен {type(data['columns']).__name__}"
            )

        # Проверка типа records
        if not isinstance(data["records"], list):
            raise InvalidStorageDataError(
                f"Поле 'records' в таблице '{table_name}.json' должно быть списком, получен {type(data['records']).__name__}"
            )

        # Проверка, что columns не пустой
        if len(data["columns"]) == 0:
            raise InvalidStorageDataError(
                f"Таблица '{table_name}.json' имеет пустой список колонок"
            )

        columns = tuple(data["columns"])
        records = data.get("records", [])
        
        # Проверка каждой записи
        for i, record in enumerate(records):
            if not isinstance(record, dict):
                raise InvalidStorageDataError(
                    f"Запись {i} в таблице '{table_name}.json' должна быть словарём, получен {type(record).__name__}"
                )
            
            # Проверка, что запись содержит все колонки
            for column in columns:
                if column not in record:
                    raise InvalidStorageDataError(
                        f"В записи {i} таблицы '{table_name}.json' отсутствует поле '{column}'"
                    )

        return Table(columns, records)


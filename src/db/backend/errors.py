class DatabaseError(Exception):
   """Базовый класс для ошибок базы данных."""
   pass


# ===== Исключения для таблицы (общая архитектура) =====
class TableAlreadyExistsError(DatabaseError):
   """Ошибка, возникающая при попытке создать уже существующую таблицу."""
   pass


class TableNotFoundError(DatabaseError):
   """Ошибка, возникающая при обращении к несуществующей таблице."""   
   pass


class MissingColumnError(DatabaseError):
   """Ошибка, возникающая при отсутствии обязательного поля в записи."""
   pass


class UnknownColumnError(DatabaseError):   
   """Ошибка, возникающая при использовании поля, которого нет в схеме таблицы."""
   pass


class InvalidStorageDataError(DatabaseError):
   """Ошибка, возникающая при чтении повреждённых данных из файла."""
   pass


class DuplicateIDError(DatabaseError):
   """Ошибка, возникающая при попытке создать запись с уже существующим идентификатором."""
   pass


class InvalidAgeError(DatabaseError):
   """Ошибка, возникающая при попытке создать запись с некорректным возрастом."""
   pass


class MissingParameterError(DatabaseError):
   """Ошибка, возникающая когда не указаны параметры поиска."""
   pass


class NoUpdateFieldsError(DatabaseError):
   """Ошибка, возникающая когда не указаны поля для обновления."""
   pass

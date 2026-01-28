from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from beartype import beartype
from tzlocal import get_localzone


class ProjectDateTime:
    _tz = get_localzone()
    _utc = ZoneInfo("UTC")

    def __init__(self, dt: datetime) -> None:
        if dt.tzinfo is None:
            dt_utc = dt.replace(tzinfo=self._utc)
        else:
            dt_utc = dt.astimezone(self._utc)
        self._dt = dt_utc

    @classmethod
    def now(cls) -> 'ProjectDateTime':
        return cls(datetime.now())

    @beartype
    def to_local_timezone(self) -> datetime:
        local_tz = get_localzone()
        return self._dt.astimezone(local_tz)

    @beartype
    def to_moscow(self) -> datetime:
        moscow_tz = ZoneInfo("Europe/Moscow")
        return self._dt.astimezone(moscow_tz)

    @classmethod
    def from_moscow(cls, dt: datetime) -> 'ProjectDateTime':
        if dt.tzinfo is None:
            moscow_dt = dt.replace(tzinfo=ZoneInfo("Europe/Moscow"))
        else:
            moscow_dt = dt.astimezone(ZoneInfo("Europe/Moscow"))

        return cls(moscow_dt)

    @classmethod
    def from_local(cls, dt: datetime) -> 'ProjectDateTime':
        if dt.tzinfo is None:
            local_dt = dt.replace(tzinfo=cls._tz)
        else:
            local_dt = dt.astimezone(cls._tz)

        return cls(local_dt)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProjectDateTime):
            return NotImplemented
        return self._dt == other._dt

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, ProjectDateTime):
            return NotImplemented
        return self._dt != other._dt

    def __lt__(self, other: 'ProjectDateTime') -> bool:
        if not isinstance(other, ProjectDateTime):
            return NotImplemented
        return self._dt < other._dt

    def __le__(self, other: 'ProjectDateTime') -> bool:
        if not isinstance(other, ProjectDateTime):
            return NotImplemented
        return self._dt <= other._dt

    def __gt__(self, other: 'ProjectDateTime') -> bool:
        if not isinstance(other, ProjectDateTime):
            return NotImplemented
        return self._dt > other._dt

    def __ge__(self, other: 'ProjectDateTime') -> bool:
        if not isinstance(other, ProjectDateTime):
            return NotImplemented
        return self._dt >= other._dt

    @beartype
    def __add__(self, other: timedelta) -> 'ProjectDateTime':
        return ProjectDateTime(self._dt + other)

    @beartype
    def __radd__(self, other: timedelta) -> 'ProjectDateTime':
        return self.__add__(other)

    @beartype
    def __sub__(self, other: 'ProjectDateTime | timedelta') -> 'ProjectDateTime | timedelta':
        if isinstance(other, ProjectDateTime):
            return self._dt - other._dt
        elif isinstance(other, timedelta):
            return ProjectDateTime(self._dt - other)
        else:
            return NotImplemented


# class ProjectDateTime(datetime):
#     """
#     Класс, расширяющий datetime.
#
#     При создании автоматически устанавливает локальный часовой пояс и
#     преобразует время в UTC. Внутренне хранит время в UTC.
#     """
#
#     def __new__(
#             cls,
#             year: int,
#             month: int,
#             day: int,
#             hour: int = 0,
#             minute: int = 0,
#             second: int = 0,
#             microsecond: int = 0,
#             tzinfo=None,
#             *,
#             fold: int = 0
#     ) -> 'ProjectDateTime':
#         """
#         Создание нового UTCDatetime.
#
#         Время считается в локальном часовом поясе и автоматически
#         преобразуется в UTC для внутреннего хранения.
#
#         Args:
#             year, month, day, hour, minute, second, microsecond: компоненты времени
#             tzinfo: игнорируется, всегда используется локальный часовой пояс
#             fold: флаг для неоднозначного времени (при переходе на летнее/зимнее время)
#         """
#         local_tz = get_localzone()
#         naive_dt = datetime(year, month, day, hour, minute, second, microsecond, fold=fold)
#         local_dt = naive_dt.replace(tzinfo=local_tz)
#         utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
#
#         instance = datetime.__new__(
#             cls,
#             utc_dt.year,
#             utc_dt.month,
#             utc_dt.day,
#             utc_dt.hour,
#             utc_dt.minute,
#             utc_dt.second,
#             utc_dt.microsecond,
#             tzinfo=utc_dt.tzinfo,
#             fold=utc_dt.fold
#         )
#         return instance
#
#     @classmethod
#     @beartype
#     def now(cls, tz: tzinfo | None = None) -> 'ProjectDateTime':
#         """
#         Создаёт UTCDatetime с текущим временем.
#
#         Returns:
#             UTCDatetime с текущим временем в UTC
#         """
#         tz = tz or get_localzone()
#         now_dt = datetime.now(tz)
#         utc_dt = now_dt.astimezone(ZoneInfo("UTC"))
#
#         instance = datetime.__new__(
#             cls,
#             utc_dt.year,
#             utc_dt.month,
#             utc_dt.day,
#             utc_dt.hour,
#             utc_dt.minute,
#             utc_dt.second,
#             utc_dt.microsecond,
#             tzinfo=utc_dt.tzinfo,
#             fold=utc_dt.fold
#         )
#         return instance
#
#     @classmethod
#     @beartype
#     def from_moscow(cls, dt: datetime) -> 'ProjectDateTime':
#         moscow_dt = dt.replace(tzinfo=ZoneInfo("Europe/Moscow"))
#         return cls.from_datetime(moscow_dt)
#
#     @classmethod
#     @beartype
#     def from_datetime(cls, dt: datetime) -> 'ProjectDateTime':
#         """
#         Создаёт UTCDatetime из существующего datetime объекта.
#
#         Если datetime имеет tzinfo (aware), конвертирует его в UTC.
#         Если datetime не имеет tzinfo (naive), интерпретирует его как локальное время
#         и конвертирует в UTC.
#
#         Args:
#             dt: datetime объект для конвертации
#
#         Returns:
#             UTCDatetime с временем в UTC
#         """
#         if dt.tzinfo is None:
#             local_tz = get_localzone()
#             dt_with_tz = dt.replace(tzinfo=local_tz)
#             utc_dt = dt_with_tz.astimezone(ZoneInfo("UTC"))
#         else:
#             utc_dt = dt.astimezone(ZoneInfo("UTC"))
#
#         instance = datetime.__new__(
#             cls,
#             utc_dt.year,
#             utc_dt.month,
#             utc_dt.day,
#             utc_dt.hour,
#             utc_dt.minute,
#             utc_dt.second,
#             utc_dt.microsecond,
#             tzinfo=utc_dt.tzinfo,
#             fold=utc_dt.fold
#         )
#         return instance
#
#     @beartype
#     def to_local_timezone(self) -> datetime:
#         """
#         Возвращает datetime в локальном часовом поясе.
#
#         Returns:
#             datetime объект в локальном часовом поясе
#         """
#         local_tz = get_localzone()
#         base_dt = datetime(
#             self.year, self.month, self.day,
#             self.hour, self.minute, self.second, self.microsecond,
#             tzinfo=self.tzinfo, fold=self.fold
#         )
#         return base_dt.astimezone(local_tz)
#
#     @beartype
#     def to_moscow(self) -> datetime:
#         """
#         Возвращает datetime в часовом поясе Europe/Moscow.
#
#         Returns:
#             datetime объект в московском часовом поясе
#         """
#         moscow_tz = ZoneInfo("Europe/Moscow")
#         base_dt = datetime(
#             self.year, self.month, self.day,
#             self.hour, self.minute, self.second, self.microsecond,
#             tzinfo=self.tzinfo, fold=self.fold
#         )
#         return base_dt.astimezone(moscow_tz)
#
#     def replace(self, *args, **kwargs) -> 'ProjectDateTime':
#         """
#         Возвращает новый UTCDatetime с изменёнными атрибутами.
#
#         При замене tzinfo время автоматически конвертируется обратно в UTC
#         для сохранения семантики класса.
#
#         Returns:
#             UTCDatetime с изменёнными атрибутами
#         """
#         result = super().replace(*args, **kwargs)
#         if result.tzinfo != ZoneInfo("UTC"):
#             result_dt = result.astimezone(ZoneInfo("UTC"))
#         else:
#             result_dt = result
#
#         instance = datetime.__new__(
#             self.__class__,
#             result_dt.year,
#             result_dt.month,
#             result_dt.day,
#             result_dt.hour,
#             result_dt.minute,
#             result_dt.second,
#             result_dt.microsecond,
#             tzinfo=result_dt.tzinfo,
#             fold=result_dt.fold
#         )
#         return instance
#
#     @beartype
#     def astimezone(self, tz: tzinfo | None = None) -> 'ProjectDateTime':
#         """
#         Возвращает новый UTCDatetime в указанном часовом поясе.
#
#         Args:
#             tz: целевой часовой пояс (по умолчанию локальный)
#
#         Returns:
#             UTCDatetime в указанном часовом поясе
#         """
#         if tz is None:
#             tz = get_localzone()
#         result = super().astimezone(tz)
#
#         instance = datetime.__new__(
#             self.__class__,
#             result.year,
#             result.month,
#             result.day,
#             result.hour,
#             result.minute,
#             result.second,
#             result.microsecond,
#             tzinfo=result.tzinfo,
#             fold=result.fold
#         )
#         return instance
#

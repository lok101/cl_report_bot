import logging
from datetime import date
from pathlib import Path

_LOGGER_NAME: str = "sales_checker"
_IS_CONFIGURED: bool = False


def _get_log_file_path() -> Path:
    today: date = date.today()
    base_dir: Path = Path(__file__).resolve().parents[2]
    log_dir: Path = base_dir / "data"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / today.isoformat()


def _configure_logging() -> None:
    root_logger: logging.Logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    log_file: Path = _get_log_file_path()
    file_handler: logging.FileHandler = logging.FileHandler(log_file, encoding="utf-8")
    formatter: logging.Formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    stdout_handler: logging.StreamHandler = logging.StreamHandler()
    stdout_handler.setLevel(logging.WARNING)
    stdout_handler.setFormatter(formatter)
    root_logger.addHandler(stdout_handler)


def get_logger(name: str | None = None) -> logging.Logger:
    global _IS_CONFIGURED
    if not _IS_CONFIGURED:
        _configure_logging()
        _IS_CONFIGURED = True
    logger_name: str = name or _LOGGER_NAME
    logger: logging.Logger = logging.getLogger(logger_name)
    return logger

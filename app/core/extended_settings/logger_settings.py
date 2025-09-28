from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggerSettings(BaseSettings):
    level: str = "INFO"
    file_enabled: bool = True
    file_path: str = "logs/app.log"
    file_rotation: str = "10 MB"
    file_retention: str = "30 days"
    file_compression: str | None = None
    console_enabled: bool = True
    console_colorize: bool = True
    format_file: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    format_console: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}:{function}:{line}</cyan> | {message}"
    backtrace: bool = True
    diagnose: bool = True
    enqueue: bool = False
    catch: bool = True

    model_config = SettingsConfigDict(
        env_prefix="LOGGER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_file_config(self) -> dict | None:
        if not self.file_enabled:
            return None

        config = {
            "sink": self.file_path,
            "level": self.level,
            "format": self.format_file,
            "rotation": self.file_rotation,
            "retention": self.file_retention,
            "backtrace": self.backtrace,
            "diagnose": self.diagnose,
            "enqueue": self.enqueue,
        }

        if self.file_compression:
            config["compression"] = self.file_compression

        return config

    def get_console_config(self) -> dict | None:
        if not self.console_enabled:
            return None

        return {
            "sink": lambda msg: print(msg, end=""),
            "level": self.level,
            "format": self.format_console,
            "colorize": self.console_colorize,
            "backtrace": self.backtrace,
            "diagnose": self.diagnose,
            "enqueue": self.enqueue,
        }

    def setup_logger(self) -> None:
        """Configure loguru logger with file and console handlers."""
        from loguru import logger

        logger.remove()

        file_config = self.get_file_config()
        if file_config:
            logger.add(**file_config)

        console_config = self.get_console_config()
        if console_config:
            logger.add(**console_config)

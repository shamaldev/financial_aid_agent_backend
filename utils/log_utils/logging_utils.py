# logging_utils.py
import inspect
import logging.config
from configs.logging_config import LOG_CONFIG

# Apply config once
logging.config.dictConfig(LOG_CONFIG)

class LoggerUtility:
    """
    Generic logger utility that supports contextual logging with any named logger.
    """

    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def log(self, message: str, level: str = 'info'):
        """
        Logs a message with filename and function name context.

        :param message: Message to log
        :param level: Logging level ('debug', 'info', 'warning', 'error')
        """
        frame = inspect.currentframe().f_back
        filename = inspect.getfile(frame)
        func_name = frame.f_code.co_name
        formatted = f"{filename.split('/')[-1]}; {func_name}(); {message}"

        log_func = {
            'debug': self.logger.debug,
            'info': self.logger.info,
            'warning': self.logger.warning,
            'error': self.logger.error
        }.get(level.lower(), self.logger.info)

        log_func(formatted)

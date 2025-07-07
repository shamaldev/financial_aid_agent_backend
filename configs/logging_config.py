# import logging.config
from pythonjsonlogger import jsonlogger
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = log_record.get('asctime') or self.formatTime(record)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        if 'msg' in log_record:
            del log_record['msg']  # Clean redundancy
        return log_record

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "json": {
            '()': JsonFormatter,
            'fmt': '%(asctime)s %(levelname)s %(name)s %(message)s'
        }
    },

    "handlers": {
        "policy_chat_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/policy_chat.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json"
        },
        "application_chat_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/app_chat.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json"
        },
        "login_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/login.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json"
        },
        "app_process_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/app_process.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json"
        },
        "policy_process_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/policy_process.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json"
        },
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/app.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json"
        }
    },

    "loggers": {
        "policy_chat_logger": {
            "handlers": ["policy_chat_file"],
            "level": "INFO",
            "propagate": False
        },
        "app_chat_logger": {
            "handlers": ["application_chat_file"],
            "level": "INFO",
            "propagate": False
        },
        "login_logger": {
            "handlers": ["login_file"],
            "level": "INFO",
            "propagate": False
        },
        "app_process_logger": {
            "handlers": ["app_process_file"],
            "level": "INFO",
            "propagate": False
        },
        "policy_process_logger": {
            "handlers": ["policy_process_file"],
            "level": "INFO",
            "propagate": False
        },
        "app_logger": {
            "handlers": ["app_file"],
            "level": "INFO",
            "propagate": False
        }
    }
}

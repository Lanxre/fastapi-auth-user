import logging
from typing import NoReturn, List

from colorama import Style, Fore

from .types import Colors, LogLevel


class ColoredFormatter(logging.Formatter):

	success: str = "Success"
	error: str = "Error"
	warning: str = "Warning"

	def format(self, record):
		log_message = super(ColoredFormatter, self).format(record)
		data_message: List[str] = log_message.split(' ')
		message_type = record.getMessage().split(' ')[-1]
		log_message = self.format_message(data_message, message_type)
		return Colors.get(name=record.levelname, default_value='INFO') + log_message + Style.RESET_ALL

	def format_message(self, data_message, message_type):
		colors = {
			self.success: Fore.GREEN,
			self.error: Fore.RED,
			self.warning: Fore.RED + Fore.YELLOW
		}

		if message_type in colors:
			color = colors[message_type]
			log_message = ' '.join(elem for elem in data_message[:-1]) + color + ' ' + message_type
			return log_message


class SingletonMeta(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class FastApiAuthLogger(metaclass=SingletonMeta):
	def __init__(self, logger_name: str, level: LogLevel = logging.INFO):
		self.logger = logging.getLogger(logger_name.upper())
		self.logger.setLevel(level.value)

		formatter = ColoredFormatter(f'%(levelname)s{Style.RESET_ALL}:\t' +
		                             f'{Fore.LIGHTWHITE_EX}{Style.BRIGHT}%(asctime)s\t' +
		                             f'{Fore.RED + Fore.YELLOW}%(name)s\t' +
		                             f'{Fore.LIGHTWHITE_EX}%(message)s',
		                             datefmt='%Hh:%Mm:%Ss | %d/%m/%Y')

		handler = logging.StreamHandler()
		handler.setFormatter(formatter)

		self.logger.addHandler(handler)

	def info(self, message: str) -> NoReturn:
		self.logger.info(message)

	def debug(self, message: str) -> NoReturn:
		self.logger.debug(message)

	def warning(self, message: str) -> NoReturn:
		self.logger.warning(message)

	def error(self, message: str) -> NoReturn:
		self.logger.error(message)

	def critical(self, message: str) -> NoReturn:
		self.logger.critical(message)

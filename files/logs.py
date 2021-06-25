import json
from datetime import datetime
from typing import Dict, Any
from os import environ

from flask import request


class Logs:
	def __init__(self, object_name: str) -> None:
		self.level = environ.get('LOG_LEVEL', LogLevel.INFO)
		self.format = environ.get('LOG_FORMAT', LogFormats.TEXT)
		self.object_name = object_name

	def error(self, extra_fields: Dict[str, Any]) -> None:
		if self.level in [LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]:
			self.__print__(LogLevel.ERROR, extra_fields)

	def warning(self, extra_fields: Dict[str, Any]) -> None:
		if self.level in [LogLevel.INFO, LogLevel.WARNING]:
			self.__print__(LogLevel.WARNING, extra_fields)

	def info(self, extra_fields: Dict[str, Any]) -> None:
		if self.level == LogLevel.INFO:
			self.__print__(LogLevel.INFO, extra_fields)

	def __print__(self, level: str, extra_fields: Dict[str, Any]) -> None:
		self._print_fields({
			'date': self._now(),
			'level': level,
			'objectName': self.object_name,
			**self._get_ip_and_referrer(),
			**extra_fields
		})

	def _print_fields(self, fields: Dict[str, Any]) -> None:
		if self.format == LogFormats.JSON:
			print(json.dumps(fields))
		else:
			print(' - '.join(map(str, fields.values())))

	@staticmethod
	def _now() -> str:
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	@staticmethod
	def _get_ip_and_referrer() -> Dict[str, Any]:
		try:
			ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
			return {'ip': ip, 'referrer': request.headers.get('Referer')}
		except (AttributeError, RuntimeError):
			return {'ip': '', 'referrer': ''}


class LogLevel:
	INFO = 'INFO'
	WARNING = 'WARNING'
	ERROR = 'ERROR'


class LogFormats:
	TEXT = 'TEXT'
	JSON = 'JSON'

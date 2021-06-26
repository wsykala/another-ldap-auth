from datetime import datetime, timedelta

from files.logs import Logs


class BruteForce:
	def __init__(
			self,
			enabled: bool,
			expiration_in_seconds: int,
			block_after_failures: int
	) -> None:
		self.database = {}
		self.enabled = enabled
		self.expiration_in_seconds = expiration_in_seconds
		self.block_after_failures = block_after_failures
		self.logs = Logs(self.__class__.__name__)

	def add_failure(self, ip: str) -> bool:
		"""
		Increase IP failure
		"""
		if self._is_disabled():
			return False
		elif self._is_new(ip):
			self._add_new(ip)
		elif self._ip_has_expired(ip):
			return self._handle_expired_ip(ip)
		else:
			self._handle_existing_ip(ip)
		return False

	def is_ip_blocked(self, ip: str) -> bool:
		"""
		Returns True if the IP is blocked, False otherwise
		"""
		# Check if brute force protection is enabled
		if self._is_disabled():
			return False
		elif self._is_new(ip):
			self.logs.info({
				'message': 'The IP is not in the database and is not blocked.',
				'ip': ip
			})
			return False
		elif self._too_many_failures(ip):
			return self._handle_blocked_ip(ip)

		self.logs.info({'message': 'The IP is not blocked.', 'ip': ip})
		return False

	def _is_disabled(self) -> bool:
		return not self.enabled

	def _is_new(self, ip: str) -> bool:
		return ip not in self.database

	def _add_new(self, ip: str) -> None:
		self.logs.info({
			'message': 'Start IP failure counter.', 'ip': ip, 'failures': '1'
		})
		self.database[ip] = {
			'counter': 1, 'blockUntil': self._get_expiration_time()
		}

	def _handle_existing_ip(self, ip: str) -> None:
		self._increment_failures(ip)
		if self._too_many_failures(ip):
			self._block_ip(ip)

	def _too_many_failures(self, ip: str) -> bool:
		return self.database[ip]['counter'] >= self.block_after_failures

	def _handle_blocked_ip(self, ip):
		self.logs.warning({
			'message': 'The IP is blocked.', 'ip': ip,
			'blockUntil': str(self.database[ip]['blockUntil'])
		})

		if self._ip_has_expired(ip):
			self._remove_existing_ip(
				ip, 'Removing IP from the database, lucky guy, time expired.'
			)
			return False
		return True

	def _block_ip(self, ip):
		new_time = self._get_expiration_time()
		self.database[ip]['blockUntil'] = new_time
		self.logs.warning({
			'message': 'IP blocked.',
			'ip': ip,
			'blockUntil': str(new_time)
		})

	def _increment_failures(self, ip: str) -> None:
		entry = self.database[ip]
		entry['counter'] += 1
		self.logs.info({
			'message': 'Increase IP failure counter.', 'ip': ip,
			'failures': str(entry['counter'])}
		)

	def _ip_has_expired(self, ip: str) -> bool:
		return self.database[ip]['blockUntil'] < datetime.now()

	def _handle_expired_ip(self, ip: str) -> bool:
		msg = 'IP failure counter expired, removing IP...'
		self._remove_existing_ip(ip, msg)
		return self.add_failure(ip)

	def _remove_existing_ip(self, ip: str, message: str) -> None:
		self.logs.info({'message': message, 'ip': ip})
		del self.database[ip]

	def _get_expiration_time(self) -> datetime:
		return datetime.now() + timedelta(seconds=self.expiration_in_seconds)

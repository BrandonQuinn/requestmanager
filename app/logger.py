import datetime

class Severity:
	DEBUG = "DEBUG"
	INFO = "INFO"
	WARNING = "WARNING"
	ERROR = "ERROR"
	CRITICAL = "CRITICAL"

class Logger:
	def __init__(self, log_file="app.log"):
		self.log_file = log_file

	def log(self, message, severity=Severity.INFO):
		try:
			with open(self.log_file, "a") as f:
				f.write(f"[{datetime.now()}][{severity}]: {message}\n")
		except Exception as e:
			print(f"Failed to write to log file {self.log_file}: {e}")
			# Optionally, you could raise an exception or handle it in another way

	def debug(self, message):
		self.log(message, Severity.DEBUG)

	def info(self, message):
		self.log(message, Severity.INFO)

	def warning(self, message):
		self.log(message, Severity.WARNING)

	def error(self, message):
		self.log(message, Severity.ERROR)

	def critical(self, message):
		self.log(message, Severity.CRITICAL)
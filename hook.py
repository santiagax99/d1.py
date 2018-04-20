#!/usr/bin/env python

# Process hooking functions.

#from ptrace.binding import ptrace_detach
from ptrace.debugger.debugger import PtraceDebugger
#from ptrace.debugger.process import PtraceProcess
import psutil
import atexit

# Debugger.
dbg = PtraceDebugger()

def quit_debugger():
	"""
	Terminate the debugger.
	"""
	if dbg:
		dbg.quit()

# Terminate the debugger on exit.
atexit.register(quit_debugger)


def find_exe_name(pid):
	"""
	Locate the name of the executable with the given process ID.

	pid -- process ID
	"""

	for p in psutil.process_iter():
		if p.pid == pid:
			return p.name()
	return None


def find_pid(exe_name):
	"""
	Locate the process ID of the given executable.

	exe_name -- executable name
	"""

	for p in psutil.process_iter():
		if p.name() == exe_name:
			return p.pid
	return None


class Process:
	# Handle to the process.
	proc = None
	# Executable name.
	exe_name = ""
	# Process ID.
	pid = 0

	def __init__(self, exe_name="", pid=0):
		"""
		Hook into the process.

		exe_name -- executable name (optional)
		pid      -- process ID (optional)
		"""

		# Sanity checks.
		if not exe_name and not pid:
			print("missing required parameter; at least one of exe_name and pid must be specified")
			return

		self.exe_name = exe_name
		self.pid = pid
		# Locate executable name from PID.
		if not exe_name:
			self.exe_name = find_exe_name(self.pid)
			if not self.exe_name:
				print("unable to locate executable name of process with PID {}".format(self.pid))
				return

		# Locate PID from executable name.
		if not self.pid:
			self.pid = find_pid(self.exe_name)
			if not self.pid:
				print("unable to locate PID of executable {}".format(self.exe_name))
				return

		# Initialize debugger and attach process.
		print("hooking into process {} with PID {}\n".format(self.exe_name, self.pid))
		self.proc = dbg.addProcess(self.pid, False)


	def __enter__(self):
		return self


	def __exit__(self, type, value, traceback):
		self.__del__()


	def __del__(self):
		"""
		Unhook the process from the debugger.
		"""
		print("unhooking from process {} with PID {}\n".format(self.exe_name, self.pid))
		if self.proc:
			self.proc.detach()
			dbg.deleteProcess(self.proc)
			self.proc = None


	def read_mem(self, start, n):
		"""
		Read the memory region [start, start+n) of the process.

		start -- start address
		n     -- number of bytes to read
		"""

		return self.proc.readBytes(start, n)


	def write_mem(self, addr, buf):
		"""
		Write the buffer to the specified address of the process.

		start -- start address
		n     -- number of bytes to read
		"""

		return self.proc.writeBytes(addr, buf)

#!/usr/bin/env python

# Process hooking functions.

from ptrace.debugger.debugger import PtraceDebugger
from ptrace.linux_proc import searchProcessByName
import psutil
import logging


def find_exe_name(pid):
	'''
	Locate the name of the executable with the given process ID.

	pid -- process ID
	'''

	for p in psutil.process_iter():
		if p.pid == pid:
			return p.name()
	return None


class Process:
	# Debugger
	dbg = None
	# Handle to the process.
	proc = None
	# Executable name.
	exe_name = ""
	# Process ID.
	pid = 0

	def __init__(self, exe_name="", pid=0):
		'''
		Hook into the process.

		exe_name -- executable name (optional)
		pid      -- process ID (optional)
		'''
		assert exe_name or pid

		self.exe_name = exe_name
		self.pid = pid
		# Locate executable name from PID.
		if not exe_name:
			self.exe_name = find_exe_name(self.pid)
			if not self.exe_name:
				raise Exception("unable to locate executable name of process with PID {}".format(self.pid))

		# Locate PID from executable name.
		if not self.pid:
			self.pid = searchProcessByName(self.exe_name)
			if not self.pid:
				raise Exception("unable to locate PID of executable {}".format(self.exe_name))

		# Initialize debugger and attach process.
		logging.debug("hooking into process {} with PID {}\n".format(self.exe_name, self.pid))
		self.dbg = PtraceDebugger()
		self.proc = self.dbg.addProcess(self.pid, False)


	def __enter__(self):
		'''
		Implement `with` interface.
		'''

		return self


	def __exit__(self, type, value, traceback):
		'''
		Implement `with` interface.
		'''

		self.__del__()


	def __del__(self):
		'''
		Unhook the process from the debugger.
		'''

		if self.proc:
			logging.debug("unhooking from process {} with PID {}\n".format(self.exe_name, self.pid))
			self.proc.detach()
			self.proc = None
		if self.dbg:
			self.dbg.quit()
			self.dbg = None


	def read_mem(self, start, n):
		'''
		Read the memory region [start, start+n) of the process.

		start -- start address
		n     -- number of bytes to read
		'''

		return self.proc.readBytes(start, n)


	def write_mem(self, addr, buf):
		'''
		Write the buffer to the specified address of the process.

		start -- start address
		n     -- number of bytes to read
		'''

		return self.proc.writeBytes(addr, buf)

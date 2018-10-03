import os
import time
import subprocess

from mininet.node import Host
from mininet_test.pendingresult import PendingResult
from mininet_test.runresult import RunResult
from mininet_test.errors import RunResultError


class TestMonitorHost(Host):

    def __init__(self, *args, **kwargs):
        """ Host wrapper to intercept calls which launch new
            processes.
        """

        super(TestMonitorHost, self).__init__(*args, **kwargs)

        self.test_monitor = None

    def set_test_monitor(self, test_monitor):
        """ Set the process monintor """
        self.test_monitor = test_monitor

    def popen(self, args, cwd=None, daemon=False, **kwargs):

        if cwd is None:
            cwd = os.getcwd()

        process = super(TestMonitorHost, self).popen(
            args, cwd=cwd, **kwargs)

        if self.test_monitor:
            self.test_monitor.add_process(
                process=process, args=args, cwd=cwd, daemon=daemon)

        # If we are launching a deamon we wait 0.5 sec for
        # it to launch

        if daemon:
            time.sleep(0.5)

        return PendingResult(process=process, command=args, cwd=cwd)

    def pexec(self, args, cwd, **kwargs):

        popen = super(TestMonitorHost, self).popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=cwd, **kwargs)

        # Warning: this can fail with large numbers of fds!
        stdout, stderr = popen.communicate()
        returncode = popen.wait()

        result = RunResult(command=args, cwd=cwd, stdout=stdout,
                           stderr=stderr, returncode=returncode)

        if result.returncode != 0:
            raise RunResultError(runresult=result)

        return result

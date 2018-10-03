
import select
import textwrap


class TestMonitor(object):
    """
    The basic idea behind the monitor is to coordinate a
    test execution.

    Typically scenario:

    1. Run rely to create a tunnel between two hosts
    2. Start some application to send data over the tunnel.
    3. Stop the test once the application started in step 2 is done.

    We should also ensure that the applications started in 1 keeps
    running thoughout the test.
    """
    class Process(object):
        def __init__(self, process, args, cwd, daemon):
            self.process = process
            self.args = args
            self.cwd = cwd
            self.daemon = daemon

        def __str__(self):
            run_string = """
                Process
                args:
                {args}
                cwd:
                {cwd}
                stdout:
                {stdout}
                stderr:
                {stderr}
                returncode:
                {returncode}
                daemon:
                {daemon}"""
            return textwrap.dedent(run_string).format(
                args=self.args,
                cwd=self.cwd,
                stdout=self.process.stdout.read(),
                stderr=self.process.stderr.read(),
                returncode=self.process.returncode,
                daemon=self.daemon)

    def __init__(self):
        """ Create a new test monitor
        """
        self.running = {}
        self.dead = []
        self.poller = select.poll()

    def __enter__(self):
        pass

    def stop(self):
        for fd in self.running:
            process = self.running[fd].process
            process.poll()
            if process.returncode:
                assert 0
            process.terminate()
            process.wait()

    def __exit__(self, type, value, traceback):
        self.stop()

    def add_process(self, process, args, cwd, daemon=False):
        """ Add a process to the monitor.

        :param process: The process
        :param args: The arguments used to start the process
        :param cwd: The current working directory where the
            process was launched.
        :param daemon: If True the process is a deamon. Daemons will
            not keep the test monitor running, but are expected to
            run to the end of the test.
        """

        # Make sure the process is running
        process.poll()

        # The returncode should be None if the process is running
        if not process.returncode is None:
            raise RuntimeError("Process not running: "
                               "returncode={} stderr={}".format(
                                   process.returncode, process.stderr.read()))
        # Get the file descriptor
        fd = process.stdout.fileno()

        # Make sure we get signals when the process terminates
        self.poller.register(fd, select.POLLHUP | select.POLLERR)
        self.running[fd] = TestMonitor.Process(
            process=process, args=args, cwd=cwd, daemon=daemon)

    def run(self, timeout=500):
        """ Run the TestMonitor.

        :param timeout: A timeout in milliseconds. If this timeout
            expires we return.
        :return: True on timeout and processes are still running. If
            no processes are running anymore return False.

            The following simple loop can be used to keep the monitor
            running while waiting for processes to exit:

                while test_monitor.run():
                    pass
        """

        while self._keep_running():
            fds = self.poller.poll(timeout)

            if fds is None:
                # We got a timeout
                return True

            for fd, event in fds:
                # Some events happend
                self._died(fd=fd, event=event)

        return False

    def _died(self, fd, event):
        """ A process has died.

        When a process dies we move it from the running
        dict to the dead list.

        :param fd: File descriptor for the process.
        :param event: The event that occoured.
        """

        # Checkt the event is one o
        assert event in [select.POLLHUP, select.POLLERR]

        self.poller.unregister(fd)

        died = self.running[fd]
        self.dead.append(died)

        del self.running[fd]

        # Update the return code
        died.process.wait()

        # Check if we had a normal exit
        if died.process.returncode:

            # The process had a non-zero return code
            raise RuntimeError("Unexpected exit {}".format(died))

        if died.daemon:

            # The process was a daemon - these should not exit
            # until after the test is over
            raise RuntimeError(
                "Unexpected deamon exit {}".format(died))

    def _keep_running(self):
        """ Check if the test is over.

        The TestMonitor should continue running for as long as there
        are non daemon processes active.
        """

        for process in self.running.values():
            if not process.daemon:
                # A process which is not a daemon is still running
                return True

        # Only daemon processes running
        return False

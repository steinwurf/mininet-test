from mininet_test.runresult import RunResult


class PendingResult(object):
    def __init__(self, process, command, cwd):
        self.process = process
        self.command = command
        self.cwd = cwd
        self.result = None

    def match(self, stdout=None, stderr=None):
        if self.result:
            self.result.match(stdout=stdout, stderr=stderr)
        self.process.poll()
        if self.process.returncode is None:
            raise RuntimeError("Process {} in {} not terminated "
                               "while getting result".format(self.command,
                                                             self.cwd))
        self.result = RunResult(
            command=self.command, cwd=self.cwd,
            stdout=self.process.stdout.read(),
            stderr=self.process.stderr.read(),
            returncode=self.process.returncode)
        self.result.match(stdout=stdout, stderr=stderr)

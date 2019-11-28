from mininet_test.runresult import RunResult


class PendingResult(object):
    def __init__(self, process, command, cwd):
        self.process = process
        self.command = command
        self.cwd = cwd
        self.result = None

    def poll_result(self):

        if self.result:
            return self.result

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

        return self.result




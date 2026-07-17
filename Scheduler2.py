# Scheduler2.py -- the "survives a reboot" scheduler.
#
# scheduler.py runs a thread INSIDE the API, so it dies when the server closes.
# This one hands the job to Windows itself (schtasks), so the backup keeps
# running on its own even when the API is closed and after a restart.

import os 
import subprocess
import sys


class Scheduler:

    def __init__(self, task_name, script_path=None):
        self.task_name = task_name
        self.python_exe = sys.executable.replace("python.exe", "pythonw.exe")  # pythonw.exe so no terminal window appears
        self.script_path = script_path

    # every schtasks command goes through here.
    def _run(self, args):
        try:
            return subprocess.run(args, capture_output=True, text=True)
        except FileNotFoundError:
            # schtasks only exists on Windows. off Windows, report "no task"
            # instead of crashing, so /health and /task still answer.
            return subprocess.CompletedProcess(args, 1, "", "schtasks not available")

    def _query(self):
        return self._run(['schtasks', '/query', '/tn', self.task_name])

    def exists(self):
        return self._query().returncode == 0

    def is_active(self):
        return "Ready" in self._query().stdout

    def is_running(self):
        return "Running" in self._query().stdout

    def is_disabled(self):
        return "Disabled" in self._query().stdout

    def is_queued(self):
        return "Queued" in self._query().stdout

    def get_status(self):
        """
        returns a dict describing the task's state:
        {'exists': bool, 'status': str | None}

        status can be 'Ready', 'Running', 'Disabled', 'Queued' or None
        """
        result = self._query()
        found = result.returncode == 0        # FIX: was the bare name `exists`, which crashed
        status = None
        if found:
            for line in result.stdout.splitlines():
                if line.strip().startswith("Status:"):
                    status = line.split(":", 1)[1].strip()
                    break
        return {'exists': found, 'status': status}

    def start(self, min=2):
        # Creates a scheduled task that runs the given script every 'min' minutes
        cmd = [
            'schtasks', '/create', '/tn', self.task_name,
            '/tr', f'"{self.python_exe}" "{self.script_path}"',
            '/sc', 'minute', '/mo', str(min),
            '/f',   # overwrite if it already exists, so calling start twice is safe
        ]
        return self._run(cmd).returncode == 0

    def disable(self):
        # pause the task. it stays on the machine and can be turned back on.
        return self._run(['schtasks', '/change', '/tn', self.task_name, '/disable']).returncode == 0

    def enable(self):
        # un-pause the task.
        return self._run(['schtasks', '/change', '/tn', self.task_name, '/enable']).returncode == 0

    def end_now(self):
        # stop a run that is happening RIGHT NOW. does not delete the task.
        return self._run(['schtasks', '/end', '/tn', self.task_name]).returncode == 0

    def remove(self):
        # delete the task from the machine for good.
        return self._run(['schtasks', '/delete', '/tn', self.task_name, '/f']).returncode == 0


if __name__ == "__main__":
    # manual test: create the real task, then offer to remove it.
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_scheduled_backup.py")
    scheduler = Scheduler("321BackupTool", script_path=script_path)

    if not scheduler.exists():
        if scheduler.start():
            print("Task created successfully.")
        else:
            print("Failed to create task.")
    else:
        print("Task already exists.")

    print("Status:", scheduler.get_status())

    user_input = input("Type 'yes' to remove the task: ")
    if user_input.lower() == 'yes':
        if scheduler.remove():
            print("Task removed.")
        else:
            print("Failed to remove task.")
import os
import sys
import subprocess


class Scheduler:

    def __init__(self, task_name, script_path=None):
        self.task_name = task_name
        self.python_exe = sys.executable.replace("python.exe", "pythonw.exe") # using pythonw.exe so no terminal window appears.
        self.script_path = script_path

    def _query(self):
        return subprocess.run(
            ['schtasks', '/query', '/tn', self.task_name],
            capture_output=True, text=True
        )

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
        status = None
        if self.exists():
            for line in result.stdout.splitlines():
                if line.strip().startswith("Status:"):
                    status = line.split(":", 1)[1].strip()
                    break
        return {'exists': exists, 'status': status}


    def disable(self):
        result = subprocess.run(
            ['schtasks', '/end', '/tn', self.task_name],
            capture_output=True, text=True
        )
        return result.returncode == 0

    def remove(self):
        result = subprocess.run(
            ['schtasks', '/delete', '/tn', self.task_name, '/f'],
            capture_output=True, text=True
        )
        return result.returncode == 0

    def start(self, min=2):
        # Creates a scheduled task that runs the given script every 'min' minutes
        cmd = [
            'schtasks', '/create', '/tn', self.task_name,
            '/tr', f'"{self.python_exe}" "{self.script_path}"',
            '/sc', 'minute', '/mo', str(min)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0


if __name__ == "__main__":
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notify_windows.py")
    scheduler = Scheduler("321BackupTool", script_path=script_path)

    if not scheduler.exists():
        if scheduler.start():
            print("Task created successfully.")
        else:
            print("Failed to create task.")
    else:
        print("Task already exists.")

    user_input = input("Type 'yes' to remove the task: ")
    if user_input.lower() == 'yes':
        if scheduler.remove():
            print("Task removed.")
        else:
            print("Failed to remove task.")
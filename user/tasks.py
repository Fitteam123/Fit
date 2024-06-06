# tasks.py

from celery import shared_task
import subprocess

import subprocess

def run_python_script(filename):
    try:
        result = subprocess.run(['python', filename])
        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr
    except Exception as e:
        return str(e)



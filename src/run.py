import os
import subprocess

if __name__ == '__main__':
    # os.environ['MODE'] = 'PRO'
    servers = [
        ["pipenv", "run", "gunicorn", "-c", "config/dev_gunicorn.py", "--worker-class", "sanic.worker.GunicornWorker",
         "server:app"]
    ]
    procs = []
    for server in servers:
        proc = subprocess.Popen(server)
        procs.append(proc)
    for proc in procs:
        proc.wait()
        if proc.poll():
            exit(0)

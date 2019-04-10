import subprocess
# This file control the running of the project
if __name__ == '__main__':
    # Run server
    servers = [
        ["pipenv", "run", "gunicorn", "-c", "config/dev_gunicorn.py", "--worker-class", "sanic.worker.GunicornWorker",
         "server:app"]
    ]
    process = []
    # Allocation process and run process
    for server in servers:
        proc = subprocess.Popen(server)
        process.append(proc)
    for proc in process:
        proc.wait()
        if proc.poll():
            exit(0)

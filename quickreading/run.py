import subprocess

# This file control the running of the project
if __name__ == '__main__':
    # run server(run gunicorn configuration)
    # reference https://sanic.readthedocs.io/en/latest/sanic/deploying.html
    process = subprocess.Popen(["pipenv", "run", "gunicorn", "-c", "config/gunicorn.py",
                                "--worker-class", "sanic.worker.GunicornWorker", "server:app"])
    process.wait()
    if process.poll():
        exit(0)

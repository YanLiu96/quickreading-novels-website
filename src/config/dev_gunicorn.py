# gunicorn config
import os
# Number of worker processes to spawn.By default,
# Sanic listens in the main process using only one CPU core.
# To crank up the juice, just specify the number of workers in the run arguments.
WORKERS = os.getenv('WORKERS', 1)
TIMEOUT = os.getenv('TIMEOUT', 60)

bind = '0.0.0.0:8001'
backlog = 2048

workers = WORKERS
worker_connections = 1000
keepalive = 2

spew = False
daemon = False
umask = 0
timeout = TIMEOUT
preload = True

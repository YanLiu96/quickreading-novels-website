# gunicorn config (inorder to deploy)
import os
# Number of worker processes to spawn.By default,
# Sanic listens in the main process using only one CPU core.
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

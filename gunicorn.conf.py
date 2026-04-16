import os

bind = "0.0.0.0:8000"
workers = 2 * (os.cpu_count() or 1) + 1
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"

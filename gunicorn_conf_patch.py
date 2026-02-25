import uvicorn
bind = '0.0.0.0:8002'
workers = 4
worker_class = 'uvicorn.workers.UvicornWorker'

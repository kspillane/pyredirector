import redirect

bind = load_bind()
workers = 1
worker_class = 'sync'
worker_connections = 1000
daemon = False



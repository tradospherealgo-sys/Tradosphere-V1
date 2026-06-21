# Production Procfile for Railway

# Release phase: Run before deployment
release: python db_init.py

# Web server: Gunicorn with proper workers
web: gunicorn --workers 4 --worker-class sync --worker-connections 1000 --max-requests 1000 --max-requests-jitter 100 --timeout 60 --graceful-timeout 30 --bind 0.0.0.0:$PORT tradosphere_saas_server:app

# Optional: Worker process (not used in basic deployment)
# worker: python signal_generator_worker.py

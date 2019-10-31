#!/bin/bash
env/bin/gunicorn -w 2 -k uvicorn.workers.UvicornWorker --log-level info -b 0.0.0.0:4567 app:app
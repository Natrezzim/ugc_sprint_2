#!/bin/sh

python3 wait-for-kafka.py

uvicorn app.main:app --host 0.0.0.0 --port 8010
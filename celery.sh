#!/usr/bin/env bash
cd
source env/bin/activate
celery worker -A api.celery --concurrency=10 -E --loglevel=info -B

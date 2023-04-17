#!/bin/bash
echo "Running worker" && poetry run celery -A auction_worker worker -D && echo "Worker is running"
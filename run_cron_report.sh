#!/bin/sh
set -eu
. /app/cron_env.sh
cd /app
exec /usr/local/bin/python main.py "$@"

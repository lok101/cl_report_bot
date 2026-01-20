#!/bin/sh
set -e

: "${TELEGRAM_BOT_TOKEN:?Нужен TELEGRAM_BOT_TOKEN}"
: "${TELEGRAM_CHAT_ID:?Нужен TELEGRAM_CHAT_ID}"
: "${KIT_API_COMPANY_ID:?Нужен KIT_API_COMPANY_ID}"
: "${KIT_API_LOGIN:?Нужен KIT_API_LOGIN}"
: "${KIT_API_PASSWORD:?Нужен KIT_API_PASSWORD}"

cron_file="/etc/cron.d/sales_checker"

{
  printf '%s\n' "SHELL=/bin/sh"
  printf '%s\n' "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  printf '%s\n' "TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN"
  printf '%s\n' "TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID"
  printf '%s\n' "KIT_API_COMPANY_ID=$KIT_API_COMPANY_ID"
  printf '%s\n' "KIT_API_LOGIN=$KIT_API_LOGIN"
  printf '%s\n' "KIT_API_PASSWORD=$KIT_API_PASSWORD"
  printf '%s\n' "0 3 * * * root python /app/main.py --interval 24 >> /var/log/cron.log 2>&1"
  printf '%s\n' "0 10 * * * root python /app/main.py --interval 12 >> /var/log/cron.log 2>&1"
} > "$cron_file"

chmod 0644 "$cron_file"
touch /var/log/cron.log

python /app/main.py --listen >> /var/log/cron.log 2>&1 &

cron -f

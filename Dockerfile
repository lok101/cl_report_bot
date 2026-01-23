FROM python:3.12-slim

RUN apt-get update \
/get_sales_report (tg://bot_command?command=get_sales_report)    && apt-get install -y --no-install-recommends cron git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

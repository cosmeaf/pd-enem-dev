#!/bin/bash

APP_DIR="/opt/pd-enem"
VENV_DIR="$APP_DIR/venv/bin"
DJANGO_MANAGE="$APP_DIR/manage.py"
PID_FILE="$APP_DIR/django_server.pid"

start() {
    echo "Starting Django development server..."
    cd $APP_DIR
    nohup $VENV_DIR/python $DJANGO_MANAGE runserver 0.0.0.0:8000 > django_server.log 2>&1 &
    echo $! > $PID_FILE
    echo "Django server started with PID $(cat $PID_FILE)."
}

stop() {
    echo "Stopping Django development server..."
    if [ -f $PID_FILE ]; then
        kill -9 $(cat $PID_FILE)
        rm $PID_FILE
        echo "Django server stopped."
    else
        echo "PID file not found. Is the server running?"
    fi
}

restart() {
    stop
    start
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
esac


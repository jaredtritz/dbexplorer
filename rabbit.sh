#!/bin/sh

# sudo rabbitmqctl list_queues -p / name messages messages_unacknowledged consumers

if [[ $1 == "start" ]] ; then
    echo 'starting rabbit'
    rabbitmq-server &
elif [[ $1 == "stop" ]] ; then
    echo 'stopping rabbit'
    rabbitmqctl stop
else
    echo "params: <'start'|'stop'>"
fi




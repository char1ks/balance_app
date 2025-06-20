#!/bin/bash

CONFIG=$1
docker cp ./nginx/$CONFIG.conf nginx:/etc/nginx/nginx.conf
docker exec nginx nginx -s reload
echo "Switched to $CONFIG balancing"

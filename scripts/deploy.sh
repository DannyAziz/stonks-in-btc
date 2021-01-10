#!/bin/bash

docker image prune -f

sudo yes | cp nginx/default config/letsencrypt/nginx/site-confs

docker-compose -f docker-compose.prod.yml build

docker-compose -f docker-compose.prod.yml up --force-recreate -d
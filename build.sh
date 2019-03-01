#!/bin/bash
pipenv lock --requirements > requirements.txt
docker-compose build
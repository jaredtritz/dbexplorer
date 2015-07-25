#!/bin/sh

source /home/jtritz/virtualenv/v2/bin/activate
cd /home/jtritz/bitbucket/transfer

echo 'starting celery'
#celery -A tasks worker --loglevel=info
#celery -A 'transfer.settings' worker -l debug -B -E
#celery -A 'transfer' --workdir=/Users/jtritz/bitbucket/transfer worker -l debug -B -E
celery -A 'transfer' --workdir=/home/jtritz/bitbucket/transfer worker -l debug -B -E

# celery status
# celery inspect active


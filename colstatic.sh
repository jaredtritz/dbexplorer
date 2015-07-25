#!/bin/bash

export SCRIPT_DIR=$(pwd)

echo "-------running collectstatic------"
source ~/virtualenv/v2/bin/activate
python $SCRIPT_DIR/manage.py collectstatic --noinput --settings=transfer.settings
echo 'done'


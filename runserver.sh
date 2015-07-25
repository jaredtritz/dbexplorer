#!/bin/sh

sudo systemctl start mysqld.service
#mysql.server start 
# /usr/local/var/mysql/*.pid <<< file location
# /usr/local/bin/mysql.server --help
# Usage: mysql.server  {start|stop|restart|reload|force-reload|status}

# this works...
# ps aux | grep mysql
# sudo kill -15 ###
# where ### is the pid of bin/mysqld

#--pid-file=~/mypid

if [[ $1 == "" ]] ; then
    source ~/virtualenv/v2/bin/activate
    cd ~/bitbucket/transfer
    sudo python manage.py runserver localhost:80 --settings=transfer.settings
    #sudo python manage.py runserver localhost:80 --settings=transfer.settings
    #sudo python manage.py runserver 0.0.0.0:80 --settings=mydata4.settings
elif [[ $1 == "custom" ]] ; then
    echo 'no custom settings'
else
    echo "myrunserver < '' | 'custom' > to pick app settings"
fi




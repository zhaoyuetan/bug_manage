#!/bin/bash
 
INI="/www/mysite1/uwsgi/uwsgi.ini"
UWSGI="/virtualenvs/venv/bin/uwsgi"
PSID="ps aux | grep "uwsgi"| grep -v "grep" | wc -l"
 
if [ ! -n "$1" ]
then
    content="Usages: sh uwsgiserver.sh [start|stop|restart]"
    echo -e "\033[31m $content \033[0m"
    exit
fi
 
if [ $ = start ]
then
    if [ `eval $PSID` -gt  ]
    then
        content="uwsgi is running!"
        echo -e "\033[32m $content \033[0m"
        exit
    else
        $UWSGI $INI
        content="Start uwsgi service [OK]"
        echo -e "\033[32m $content \033[0m"
    fi
 
elif [ $ = stop ];then
    if [ `eval $PSID` -gt  ];then
        killall - uwsgi
    fi
    content="Stop uwsgi service [OK]"
    echo -e "\033[32m $content \033[0m"
elif [ $ = restart ];then
    if [ `eval $PSID` -gt  ];then
        killall - uwsgi
    fi
    $UWSGI --ini $INI
    content="Restart uwsgi service [OK]"
    echo -e "\033[32m $content \033[0m"
 
else
    content="Usages: sh uwsgiserver.sh [start|stop|restart]"
    echo -e "\033[31m $content \033[0m"
fi
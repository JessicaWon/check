#!/bin/bash
#tomorrow=`date -d"tomorrow" +"%Y.%m.%d"`
theday=`date -d"today" +"%Y.%m"`
echo ${theday}
curl -XPUT http://IP:9200/checkdata-isdocker-${theday} -d @"/formal_mapping/mydocker_mapping.json" >> /home/logs/create_index.log
curl -XPUT http://IP:9200/checkdata-isntdocker-${theday} -d @"/formal_mapping/myntdocker_mapping.json" >> /home/logs/create_index.log

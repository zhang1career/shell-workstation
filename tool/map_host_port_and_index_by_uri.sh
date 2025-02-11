#!/bin/bash

# check param cardinality
if [ $# -lt 1 ]; then
	echo "Error: user is not specified."
	exit 1
fi

awk -F '\t' '
{
	ip = $1;
	split($2, services, ","); # 以逗号分割应用:端口对

	for (i in services) {
		split(services[i], app_port, ":"); # 以冒号分割 应用:端口
		app = app_port[1];
		port = app_port[2];
		
		if (app_map[app] == "") {
			app_map[app] = ip ":" port;
		} else {
			app_map[app] = app_map[app] "," ip ":" port;
		}
	}
}
END {
	for (app in app_map) {
		print app "\t" app_map[app];
	}
}
' $1

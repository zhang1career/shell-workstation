aws_update_machine_public_ip() {
	aws ec2 describe-instances \
		--filters Name=instance-state-name,Values=running \
		--query 'Reservations[*].Instances[*].{name:Tags[?Key==`Name`]|[0].Value,sip:PublicIpAddress}' \
		--output text \
		| sed -E 's/\t/,/g' \
		> ${DATA_HOME}/shell/machine_ip.csv
}

aws_update_machine_private_ip() {
	aws ec2 describe-instances \
		--filters Name=instance-state-name,Values=running \
		--query 'Reservations[*].Instances[*].{name:Tags[?Key==`Name`]|[0].Value,sip:PrivateIpAddress}' \
		--output text \
		| sed -E 's/\t/,/g' \
		> ${DATA_HOME}/shell/machine_ip.csv
}

aws_update_private_ip_uri() {
	aws ec2 describe-instances \
		--filters Name=instance-state-name,Values=running \
		--query 'Reservations[*].Instances[*].{sip:PrivateIpAddress,uri:Tags[?Key==`UriMap`]|[0].Value}' \
		--output text \
		| awk -F '\t' '{ for (i = 1; i <= NF; i++) { if ($i == "None" || $i == "") next } print $0 }' \
		> ${DATA_HOME}/shell/ip_uri.csv
}

aws_update_uri_private_ip() {
	${TOOL_HOME}/map_host_port_and_index_by_uri.sh ${DATA_HOME}/shell/ip_uri.csv \
	> ${DATA_HOME}/shell/uri_ip.csv
}

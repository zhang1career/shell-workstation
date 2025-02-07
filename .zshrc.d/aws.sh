aws_update_machine_ip() {
	aws ec2 describe-instances \
		--filters Name=instance-state-name,Values=running \
		--query 'Reservations[*].Instances[*].{name:Tags[?Key==`Name`]|[0].Value,sip:PrivateIpAddress}' \
		--output text | sed -E 's/\t/,/g' >> ${DATA_HOME}/shell/machine_ip.csv
}

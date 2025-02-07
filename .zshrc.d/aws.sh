aws_update_machine_info() {
	aws ec2 describe-instances \
		--filters Name=instance-state-name,Values=running \
		--query 'Reservations[*].Instances[*].{name:Tags[?Key==`Name`]|[0].Value,sip:PrivateIpAddress,id:InstanceId,type:InstanceType}' \
		--output text | sed -E 's/\t/,/g' >> ${DATA_PATH}/shell/machine_info.csv
}

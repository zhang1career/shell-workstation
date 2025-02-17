jump() {
	# show hint when no parameter
	if [ $# -le 0 ]; then
		echo "$(font_yellow_bold Hint): Targets supported list as follow:"
		map_keys "$DATA_HOME"/shell/machine_ip.csv
		return 0
	fi

	# check param cardinality
	local name="jump"
	local param_num=1
	if [ $# -lt $param_num ]; then
		echo "$(font_red_bold Error): The $(font_bold $name) function requires at least $param_num parameter(s)."
		return 1
	fi

	local target=$1
	# query target user
	local user
	user=$(map_get "$DATA_HOME"/shell/machine_user.csv "$target")
        if [ -z "$user" ]; then
                echo "$(font_red_bold ERROR): The $(font_bold "$target") user is not found."
        fi
	# query target password
	local cred
	cred=$(map_get "$DATA_HOME"/shell/machine_cred.csv "$target")
        if [ -z "$cred" ]; then
                echo "$(font_red_bold ERROR): The $(font_bold "$target") credential is not found."
        fi
	# query target address
	local addr
	addr=$(map_get "$DATA_HOME"/shell/machine_ip.csv "$target")
	if [ -z "$addr" ]; then
		echo "$(font_red_bold ERROR): The $(font_bold "$target") address is not found."
	fi

	ssh -i "$cred" "$user"@"$addr"
}

jump() {
	# show hint when no parameter
	if [ $# -le 0 ]; then
		echo "$(font_yellow_bold Hint): Targets supported list as follow:"
		map_keys ${DATA_HOME}/shell/machine_ip.csv
		return 0
	fi

	# check param cardinality
	NAME="jump"
	PARA_NUM=1
	if [ $# -lt $PARA_NUM ]; then
		echo "$(font_red_bold Error): The $(font_bold $NAME) function requires at least $PARA_NUM parameter(s)."
		return 1
	fi

	TARGET=$1
	# query target user
	USER=$(map_get ${DATA_HOME}/shell/machine_user.csv $TARGET)
        if [ -z $USER ]; then
                echo "$(font_red_bold ERROR): The $(font_bold $TARGET) user is not found."
        fi
	# query target password
	CRED=$(map_get ${DATA_HOME}/shell/machine_cred.csv $TARGET)
        if [ -z $CRED ]; then
                echo "$(font_red_bold ERROR): The $(font_bold $TARGET) credential is not found."
        fi
	# query target address
	ADDR=$(map_get ${DATA_HOME}/shell/machine_ip.csv $TARGET)
	if [ -z $ADDR ]; then
		echo "$(font_red_bold ERROR): The $(font_bold $TARGET) address is not found."
	fi

	ssh -i $CRED ${USER}@${ADDR}
}

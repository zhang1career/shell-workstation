jump() {
	# show hint when no parameter
	if [ $# -le 0 ]; then
		echo "$(font_yellow_bold Hint): Targets supported list as follow:"
		map_keys /data/shell/machine_map.csv
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
	
	# query target address
	ADDR=$(map_get /data/shell/machine_map.csv $TARGET)
	if [ -z $ADDR ]; then
		echo "$(font_red_bold ERROR): The $(font_bold $TARGET) address is not found."
	fi

	$TARGET $ADDR
}

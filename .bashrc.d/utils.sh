map_get() {
	# check arguments cardinality
	local NAME="map_get"
	local ARG_NUM=2
	if [ $# -lt $ARG_NUM ]; then
		echo "Error: The $NAME function requires at least $ARG_NUM parameter(s)."
		return 1
	fi

	# check file existence
	local DATA_PATH=$1
	if [ ! -f "$DATA_PATH" ]; then
		echo "Error: File $DATA_PATH does not exist."
		return 1
	fi

	local KEY=$2

	local RESULT
	RESULT=$(awk -F, -v KEY="$KEY" '$1 == KEY {print $2}' "$DATA_PATH")
	echo "$RESULT"
}


map_keys() {
	# check arguments cardinality
	local NAME="map_keys"
	local ARG_NUM=1
	if [ $# -lt $ARG_NUM ]; then
		echo "Error: The $NAME function requires at least $ARG_NUM parameter(s)."
		return 1
	fi

	# check file existence
	local DATA_PATH=$1
	if [ ! -f "$DATA_PATH" ]; then
		echo "Error: File $DATA_PATH does not exist."
		return 1
	fi

	awk -F ',' '{print $1}' "$DATA_PATH"
}

sha256() {
	echo -n "$1" | openssl dgst -sha256
}

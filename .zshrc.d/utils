map_get() {
	# check param cardinality
        NAME="map_get"
        PARA_NUM=2
        if [ $# -lt $PARA_NUM ]; then
                echo "$(font_red_bold Error): The $(font_bold $NAME) function requires at least $PARA_NUM parameter(s)."
                return 1
        fi

	# check file existance
	DATA_PATH=$1
	if [ ! -f $DATA_PATH ]; then
		echo "$(font_red_bold Error): File $(font_bold $DATA_PATH) does not exist."
		return 1
	fi

	KEY=$2

	value=$(awk -F, -v key="$KEY" '$1 == key {print $2}' $DATA_PATH)
	echo ${value}
}


map_keys() {
        # check param cardinality
        NAME="map_keys"
        PARA_NUM=1
        if [ $# -lt $PARA_NUM ]; then
                echo "$(font_red_bold Error): The $(font_bold $NAME) function requires at least $PARA_NUM parameter(s)."
                return 1
        fi

        # check file existance
        DATA_PATH=$1
        if [ ! -f $DATA_PATH ]; then
                echo "$(font_red_bold Error): File $(font_bold $DATA_PATH) does not exist."
                return 1
        fi

        awk -F ',' '{print $1}' $DATA_PATH
}


sha256() {
	echo -n $1 | openssl dgst -sha256
}

map_get() {
	# check param cardinality
        local name="map_get"
        local param_num=2
        if [ $# -lt $param_num ]; then
                echo "$(font_red_bold Error): The $(font_bold $name) function requires at least $param_num parameter(s)."
                return 1
        fi

	# check file existance
	local data_path=$1
	if [ ! -f $data_path ]; then
		echo "$(font_red_bold Error): File $(font_bold $data_path) does not exist."
		return 1
	fi

	local key=$2

	value=$(awk -F, -v key="$key" '$1 == key {print $2}' $data_path)
	echo ${value}
}


map_keys() {
        # check param cardinality
        local name="map_keys"
        local param_num=1
        if [ $# -lt $param_num ]; then
                echo "$(font_red_bold Error): The $(font_bold $name) function requires at least $param_num parameter(s)."
                return 1
        fi

        # check file existance
        local data_path=$1
        if [ ! -f $data_path ]; then
                echo "$(font_red_bold Error): File $(font_bold $data_path) does not exist."
                return 1
        fi

        awk -F ',' '{print $1}' $data_path
}

sha256() {
	echo -n $1 | openssl dgst -sha256
}

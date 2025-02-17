sdiff() {
	if [ $# -le 0 ]; then
		read "FILEPATH_LOCAL?local filepath: "
		if [ -z "$FILEPATH_LOCAL" ]; then
			echo "Error: The local filepath) is required."
			return 1
		fi
	
		read "INSTANCE_REMOTE?remote instance (blank for tips): "
		if [ -z "$INSTANCE_REMOTE" ]; then
			echo "choose remote instance between followings:"
			map_keys "$DATA_HOME"/shell/machine_ip.csv
			read "INSTANCE_REMOTE?remote instance: "
		fi
		if [ -z "$INSTANCE_REMOTE" ]; then
			echo "Error: The remote instance) is required."
			return 1
		fi
	
		read "FILEPATH_REMOTE?remote filepath ($FILEPATH_LOCAL): "
		if [ -z "$FILEPATH_REMOTE" ]; then
			FILEPATH_REMOTE=$FILEPATH_LOCAL
		fi
	elif [ $# -eq 3 ]; then
		FILEPATH_LOCAL=$1
		INSTANCE_REMOTE=$2
		FILEPATH_REMOTE=$3
	else
		echo "Usage: $0 [local-filepath remote-instance remote-filepath]"
		return 1
	fi
	echo
	
	# query remote instance user
	USER_REMOTE=$(map_get "$DATA_HOME"/shell/machine_user.csv "$INSTANCE_REMOTE")
	if [ -z "$USER_REMOTE" ]; then
		echo "Error: The user $INSTANCE_REMOTE is not found."
		return 1
	fi
	# query remote instance password
	CRED_REMOTE=$(map_get "$DATA_HOME"/shell/machine_cred.csv "$INSTANCE_REMOTE")
	if [ -z "$CRED_REMOTE" ]; then
		echo "Error: The credent $INSTANCE_REMOTE is not found."
		return 1
	fi
	# query remote instance address
	ADDR_REMOTE=$(map_get "$DATA_HOME"/shell/machine_ip.csv "$INSTANCE_REMOTE")
	if [ -z "$ADDR_REMOTE" ]; then
		echo "Error: The ip $INSTANCE_REMOTE is not found."
		return 1
	fi
	
	# file type: f for file, d for directory, n for not found
	FILE_TYPE_REMOTE="n"
	# check file existence
	if [ -d "$FILEPATH_LOCAL" ]; then
		FILE_TYPE_LOCAL="d"	# It's a directory
	elif [ -f "$FILEPATH_LOCAL" ]; then
		FILE_TYPE_LOCAL="f"	# It's a regular file
	else
		FILE_TYPE_LOCAL="n"	# It doesn't exist
	fi
	if [ "$FILE_TYPE_LOCAL" = "n" ]; then
		echo "Error: The $FILEPATH_LOCAL is not found on local."
		return 1
	fi
	
	FILE_TYPE_REMOTE=$(ssh -i "$CRED_REMOTE" "$USER_REMOTE"@"$ADDR_REMOTE" "
		if [ -d \"$FILEPATH_REMOTE\" ]; then
			echo 'd'
		elif [ -f \"$FILEPATH_REMOTE\" ]; then
			echo 'f'
		else
			echo 'n'
		fi
	")
	if [ "$FILE_TYPE_REMOTE" = "n" ]; then
		echo "Error: The $FILEPATH_REMOTE is not found on $INSTANCE_REMOTE."
		return 1
	fi
	
	# compare file type
	if [ "$FILE_TYPE_LOCAL" != "$FILE_TYPE_REMOTE" ]; then
		echo "Error: The local $FILEPATH_LOCAL is a $FILE_TYPE_LOCAL, but remote $FILEPATH_REMOTE is a $FILE_TYPE_REMOTE."
		return 1
	fi

	# compare directory
	if [ "$FILE_TYPE_LOCAL" = "d" ]; then
		diff -y <(ls -1aR "$FILEPATH_LOCAL") <(ssh -i "$CRED_REMOTE" "$USER_REMOTE"@"$ADDR_REMOTE" "ls -1aR $FILEPATH_REMOTE")
	else
		diff -y <(cat "$FILEPATH_LOCAL") <(ssh -i "$CRED_REMOTE" "$USER_REMOTE"@"$ADDR_REMOTE" "cat $FILEPATH_REMOTE")
	fi
}

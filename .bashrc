# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User configuration
if [ -d ~/.bashrc.d ]; then
	if [ "$(ls -A ~/.bashrc.d)" ]; then
		for rc in ~/.bashrc.d/*; do
			if [ -f "$rc" ]; then
				source "$rc"
			fi
		done
	else
		echo "No configurations specified for bash."
	fi
fi

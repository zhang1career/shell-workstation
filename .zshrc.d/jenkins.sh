jenkins_worker() {
	# check param cardinality
        NAME="jenkins_worker"
	PARA_NUM=1
        if [ $# -lt $PARA_NUM ]; then
                echo "$(font_red_bold Error): The $(font_bold $NAME) function requires at least $PARA_NUM parameter(s)."
                return 1
        fi

	KEY="~/.ssh/ec2-user_aws_zhang_jenkinscloud.pem"
	USER="ubuntu"
	ADDR=$1

	ssh -i $KEY $USER@$ADDR
}

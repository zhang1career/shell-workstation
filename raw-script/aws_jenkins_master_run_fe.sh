DEPLOY_ITEM=data-analyzer-fe
DEPLOYEE_HOST=$(/tool/query_service_host.sh $DEPLOY_ITEM)
if [ -z "$DEPLOYEE_HOST" ]; then
  echo "Service $DEPLOY_ITEM is not registered."
  exit 1
fi
ssh -i /home/jenkins/.ssh/ec2-user_aws_zhang_gateway.pem -o StrictHostKeyChecking=no ec2-user@"$DEPLOYEE_HOST" "\
  /home/ec2-user/tool/aws_jenkins_deployee_run_fe.sh \
  13001 \
  3000 \
  zhang1career \
  data-analyzer-fe \
  latest"

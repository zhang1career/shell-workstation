stop slave;

reset slave all;

change master to master_host='172.31.2.15',master_user='sync',master_password='******',master_log_file='master-bin.00000?',master_log_pos=???;

start slave;

show slave status\G

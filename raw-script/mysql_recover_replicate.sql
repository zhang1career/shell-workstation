# Refer: https://cloud.tencent.com/developer/article/1816449

# Method 1.2. skip one error in non-GTID mode
# login in slave node
stop slave;
set sql_slave_skip_counter=1;
start slave;


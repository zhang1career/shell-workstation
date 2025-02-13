1. master

reset and write-lock

```sql
RESET MASTER;
FLUSH TABLES mysql xxx yyy WITH READ LOCK;
SHOW MASTER STATUS;
```

dump master's databases

```sql
mysqldump -uroot -p --databases mysql xxx yyy > dump.sql
```

release write-lock

```sql
UNLOCK TABLES;
```


2. slave

stop slave

```sql
STOP SLAVE;
```

import data

```sh
mysql -uzzzz -p < dump.sql
```


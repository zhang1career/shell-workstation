# The Shell Workstation

The shell workstation provides exports, alias and functions.

## Features
* jump
The jump command supports logging into other running machines in the same VPC. The running machines are recorded in the MACHINE_MAPs.


## Duties
* machine_ip
Maintain data file `${DATA_HOME}/shell/machine_ip.csv`.
Method: run manually on demand.
```shell
aws_update_machine_ip
```

* machine_user
Maintain data file `${DATA_HOME}/shell/machine_user.csv`.
Method: edit manually when create instance.

* machine_cred
Maintain data file `${DATA_HOME}/shell/machine_cred.csv`.
Method: edit manually when create instance.


## Wikis
MACHINE_MAP, a bundle of data files in the path `${DATA_HOME}/shell`, prefixed with 'machine_', and extended with '.csv', i.e. machine_ip.csv, machine_user.csv and machine_cred.csv.

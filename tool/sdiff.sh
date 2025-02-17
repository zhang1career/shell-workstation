#!/bin/bash

echo "SuperDiff: diff local file and remote file"

if [ $# -le 0 ]; then
  read -rp "local filepath: " FILEPATH_LOCAL
  if [ -z "$FILEPATH_LOCAL" ]; then
    echo "$(font_red_bold Error): The $(font_bold local filepath) is required."
    exit 1
  fi

  read -rp "remote instance (blank for tips): " INSTANCE_REMOTE
  if [ -z "$INSTANCE_REMOTE" ]; then
    echo "choose remote instance between followings:"
    map_keys "$DATA_HOME"/shell/machine_ip.csv
    read -rp "remote instance: " INSTANCE_REMOTE
  fi
  if [ -z "$INSTANCE_REMOTE" ]; then
    echo "$(font_red_bold Error): The $(font_bold remote instance) is required."
    exit 1
  fi

  read -rp "remote filepath ($FILEPATH_LOCAL): " FILEPATH_REMOTE
  if [ -z "$FILEPATH_REMOTE" ]; then
    FILEPATH_REMOTE=$FILEPATH_LOCAL
  fi
elif [ $# -eq 3 ]; then
  FILEPATH_LOCAL=$1
  INSTANCE_REMOTE=$2
  FILEPATH_REMOTE=$3
else
  echo "Usage: $0 [local-filepath remote-instance remote-filepath]"
  exit 1
fi
echo ""

# query remote instance user
USER_REMOTE=$(map_get "$DATA_HOME"/shell/machine_user.csv "$INSTANCE_REMOTE")
if [ -z "$USER_REMOTE" ]; then
  echo "$(font_red_bold ERROR): The $(font_bold "$INSTANCE_REMOTE") user is not found."
  exit 1
fi
# query remote instance password
CRED_REMOTE=$(map_get "$DATA_HOME"/shell/machine_cred.csv "$INSTANCE_REMOTE")
if [ -z "$CRED_REMOTE" ]; then
  echo "$(font_red_bold ERROR): The $(font_bold "$INSTANCE_REMOTE") credential is not found."
  exit 1
fi
# query remote instance address
ADDR_REMOTE=$(map_get "$DATA_HOME"/shell/machine_ip.csv "$INSTANCE_REMOTE")
if [ -z "$ADDR_REMOTE" ]; then
  echo "$(font_red_bold ERROR): The $(font_bold "$INSTANCE_REMOTE") address is not found."
  exit 1
fi

# file type: f for file, d for directory, n for not found
FILE_TYPE_LOCAL="n"
FILE_TYPE_REMOTE="n"
# check file existence
test -d "$FILEPATH_LOCAL" && FILE_TYPE_LOCAL='d' || FILE_TYPE_LOCAL='n'
test -f "$FILEPATH_LOCAL" && FILE_TYPE_LOCAL='f' || FILE_TYPE_LOCAL='n'
if [ "$FILE_TYPE_LOCAL" = "n" ]; then
  echo "$(font_red_bold ERROR): The $(font_bold "$FILEPATH_LOCAL") is not found on $(font_bold "$INSTANCE_A")."
  exit 1
fi
ssh -i "$CRED_REMOTE" "$USER_REMOTE"@"$ADDR_REMOTE" "test -d '$FILEPATH_REMOTE' && FILE_TYPE_REMOTE='d' || FILE_TYPE_REMOTE='n'"
ssh -i "$CRED_REMOTE" "$USER_REMOTE"@"$ADDR_REMOTE" "test -f '$FILEPATH_REMOTE' && FILE_TYPE_REMOTE='f' || FILE_TYPE_REMOTE='n'"
if [ "$FILE_TYPE_REMOTE" = "n" ]; then
  echo "$(font_red_bold ERROR): The $(font_bold "$FILEPATH_REMOTE") is not found on $(font_bold "$INSTANCE_REMOTE")."
  exit 1
fi

# compare file type
if [ "$FILE_TYPE_LOCAL" != "$FILE_TYPE_REMOTE" ]; then
  echo "$(font_red_bold ERROR): The $(font_bold "$FILEPATH_LOCAL") is a $FILE_TYPE_LOCAL, but $(font_bold "$FILEPATH_REMOTE") is a $FILE_TYPE_REMOTE."
  exit 1
fi
# compare directory
if [ "$FILE_TYPE_LOCAL" = "d" ]; then
  diff -y <(ls -1aR "$FILEPATH_LOCAL") <(ssh -i "$CRED_A" "$USER_A"@"$ADDR_A" "'ls -1aR $FILEPATH_REMOTE'")
else
  diff -y <(cat "$FILEPATH_LOCAL") <(ssh -i "$CRED_A" "$USER_A"@"$ADDR_A" "'cat $FILEPATH_REMOTE'")
fi

#!/bin/bash

set -e

FILE=/root/installdb.sql

wget https://raw.githubusercontent.com/mysqludf/lib_mysqludf_preg/testing/installdb.sql -O $FILE
sed -i 's/USE mysql;//g' $FILE

MYSQL_CMD="mysql -h $MYSQL_HOST -u root -p$MYSQL_ROOT_PASSWORD"

echo $MYSQL_CMD

until $MYSQL_CMD -e ";"; do
  >&2 echo "MySQL is unavailable - sleeping"
  sleep 1
done

echo "MySQL is available..."

$MYSQL_CMD deltanyc < $FILE

echo "UDFs added successfully"

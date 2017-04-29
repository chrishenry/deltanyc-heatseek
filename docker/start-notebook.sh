#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

set -e

MYSQL_CMD="mysql -h $MYSQL_HOST -u root -p$MYSQL_ROOT_PASSWORD"

until $MYSQL_CMD -e ";"; do
  >&2 echo "MySQL is unavailable - sleeping"
  sleep 1
done

$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE_DATA;"

jupyter notebook $*

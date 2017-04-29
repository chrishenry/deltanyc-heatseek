#!/bin/sh

MYSQL_CMD="mysql -h $MYSQL_HOST -u root -p$MYSQL_ROOT_PASSWORD"

until $MYSQL_CMD -e ";"; do
  >&2 echo "MySQL is unavailable - sleeping"
  sleep 1
done

$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE_RAILS;"
$MYSQL_CMD -e "GRANT ALL PRIVILEGES ON *.* TO $MYSQL_USER;"
$MYSQL_CMD -e "FLUSH PRIVILEGES;"

rake bower:install && \
	bundle exec rails s -p 80 -b '0.0.0.0'

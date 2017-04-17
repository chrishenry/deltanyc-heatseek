#!/bin/sh
rake bower:install && \
	bundle exec rails s -p 80 -b '0.0.0.0'

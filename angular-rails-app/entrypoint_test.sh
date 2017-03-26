#!/bin/bash

rake db:migrate bower:install > /dev/null 2>&1

rake spec

bundle exec teaspoon

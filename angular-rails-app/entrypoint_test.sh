#!/bin/bash

rake db:migrate > /dev/null 2>&1

rake spec

bundle exec teaspoon

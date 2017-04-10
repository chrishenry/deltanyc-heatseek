#!/bin/bash
export PYTHONPATH="$PYTHONPATH:/root/data-imports"
luigi --local-scheduler --no-lock --workers $LUIGI_WORKERS --module luigi_master ImportAll

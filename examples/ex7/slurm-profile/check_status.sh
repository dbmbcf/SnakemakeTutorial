#!/usr/bin/env bash

# Check status of slurm job

jobid="$1"

if [[ "$jobid" == Submitted ]]
then
  echo Invalid job ID: "$jobid" >&2
  exit 1
fi

output=`sacct -j "$jobid" --format State --noheader | head -n 1 | awk '{print $1}'`

if [[ $output =~ ^(COMPLETED).* ]]
then
  echo success
elif [[ $output =~ ^(RUNNING|PENDING|COMPLETING|CONFIGURING|SUSPENDED).* ]]
then
  echo running
elif [[ -z $output ]] # empty, happens if sacct is behind scheduler
then
  echo running
else
  echo failed
fi

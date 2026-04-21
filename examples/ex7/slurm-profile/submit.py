#!/usr/bin/env python3
import os, sys, getpass, pwd, grp

from snakemake.utils import read_job_properties
from snakemake.common.configfile import load_configfile

jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

## set up scicore slurm defaults
sbatch_options = {
    'account' : grp.getgrgid(pwd.getpwnam(getpass.getuser()).pw_gid).gr_name,
    'partition' : 'scicore',
    'qos' : '30min', 
    'mem' : '4G',
    'output' : 'log/{rule}/slurm.%j.%N.out'.format(rule=job_properties["rule"]),
    'job-name' : 'smk.{rule}'.format(rule=job_properties["rule"])
}

# update by job specific resources
res = job_properties["resources"]
for key in sbatch_options.keys():
    if key in res.keys():
        sbatch_options[key] = res[key]

## adjust memory
if "mem_mb" in res.keys():
    sbatch_options["mem"] = res["mem_mb"]
    
## add qos depending on time
def time2qos(time_min):
    if time_min <= 30:
        qos = "30min"
    elif time_min <= 6*60:
        qos = "6hours"
    elif time_min <= 24*60:
        qos = "1day"
    else:
        qos = "1week"
    return(qos)

## check in this order:
for key in ["time","time_min","runtime"]:
    if key in res.keys():
        sbatch_options["qos"] = time2qos(res[key])
        break
    
## adjust threads
sbatch_options["cpus-per-task"] = job_properties["threads"] if "threads" in job_properties.keys() else 1

## create log dir
out = os.path.dirname(sbatch_options['output'])
if not os.path.exists(out):
    os.makedirs(out, exist_ok=True)

## convert to string
options = ""
for k, v in sbatch_options.items():
    val = "" if v is None else f"={v}"
    options += f"--{k}{val} "

os.system("sbatch --parsable {options} {script}".format(options=options, script=jobscript))

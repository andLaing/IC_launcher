import os
import sys

from glob import iglob
from time import sleep

from invisible_cities.core.configure import configure


config          = configure(sys.argv).as_namespace
city            = config.city
conf_template   = config.conf
script_template = config.script
detector        = config.detector
generator       = config.generator
prod_date       = config.date

input_fldrs     = {'detsim'     :       'nexus',
                   'irene'      :     'diomira',
                   'hypathia'   :      'detsim',
                   'diomira'    :      'detsim',
                   'dorothea'   :    'hypathia',
                   'penthesilea':    'hypathia',
                   'esmeralda'  : 'penthesilea'}
file_types      = {'detsim'     : ('nexus'   ,  'buffers'),
                   'irene'      : ('mcrwf'   ,    'pmaps'),
                   'hypathia'   : ('buffers' , 'hypathia'),
                   'diomira'    : ('buffers' ,    'mcrwf'),
                   'dorothea'   : ('hypathia',     'kdst'),
                   'penthesilea': ('hypathia',     'hits'),
                   'esmeralda'  : ('hits'    ,     'cdst')}

with open(conf_template) as conf:
    config_base = conf.read()

with open(script_template) as scrt:
    script_base = scrt.read()

data_fldr  = os.environ['NEXTDATA'] + '/' + detector + '/sim/'
data_fldr += generator + '/' + prod_date + '/{}/'
input_fldr = data_fldr.format(input_fldrs[city])
if hasattr(config, 'other_input'):
    ## This variable set to say that input comes from different folfer
    input_fldr = input_fldr[:-len(prod_date)] + config.other_input

if 'detsim' in city:
    exec_script  = 'python ' + os.environ['NEXTSW']
    exec_script += '/detsim/detsim/position_signal.py'
else:
    exec_script  = 'city ' + city
    input_fldr  += '/output'
config_fldr = data_fldr.format(city) + '/config/'
log_fldr    = data_fldr.format(city) + '/logs/'
output_fldr = data_fldr.format(city) + '/output/'
script_fldr = data_fldr.format(city) + '/scripts/'
os.system('mkdir -p ' + config_fldr)
os.system('mkdir -p ' +    log_fldr)
os.system('mkdir -p ' + output_fldr)
os.system('mkdir -p ' + script_fldr)

for fn in iglob(input_fldr + '/*'):
    #print('fn = ', fn)
    EXECUTE       = 'cd ' + os.environ['WORK_DIR'] + '\n'
    EXECUTE      += 'cp ' + fn + ' /scratch/\n'
    fldr_split_fn = fn.split('/')[-1]
    file_base     = fldr_split_fn.replace(*file_types[city])[:-3]
    if '.gz' in fn:
        EXECUTE   += 'gunzip '   + fldr_split_fn + '\n'
        scratch_in = '/scratch/' + fldr_split_fn[:-3]
        file_base  = file_base[:-3]
    else:
        scratch_in = '/scratch/' + fldr_split_fn
    config_name = config_fldr + file_base + '.conf'
    log_name    = log_fldr    + file_base + '.log'
    script_name = script_fldr + file_base + '.sh'
    scratch_out = '/scratch/' + file_base + '.h5'

    if os.path.isfile(output_fldr + scratch_out.split('/')[-1]):
        print(scratch_out.split('/')[-1], ' already exists, skipping process.')
        continue

    with open(config_name, 'w') as confF:
        conf_info = config_base.replace('INFILE' ,  scratch_in)
        conf_info = conf_info  .replace('OUTFILE', scratch_out)
        confF.write(conf_info)

    EXECUTE += exec_script + ' ' + config_name + ' >& ' + log_name + '\n'
    EXECUTE += 'rm ' + scratch_in  + '\n'
    EXECUTE += 'mv ' + scratch_out + ' ' + output_fldr + '\n'
    with open(script_name, 'w') as scrtF:
        script_info = script_base.replace('EXECUTE', EXECUTE)
        scrtF.write(script_info)

    while int(os.popen('squeue -u alaing | wc -l').read()) > 400:
        sleep(30)

    os.system('sbatch ' + script_name)
    sleep(1)

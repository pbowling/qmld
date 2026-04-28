import os
import numpy as np

# Establishes a working set of precursor info for the interface
info={}
info['name']='14benz'
info['nsubs']=[6,5]
info['nblocks']=np.sum(info['nsubs'])
info['ncentral']=0
info['nreps']=1
info['nnodes']=1
info['cutoff']=.99
info['enginepath']=os.environ['CHARMMEXEC']
info['temp']=298.15
info['engine']='pycharmm'

main_dir = '/home/kaibilal/jupyter/14benz'
prep_dir = f'{main_dir}/vacuum/from_py_prep'
nsubs = info["nsubs"]
from info import *
import re
from DCD_translation import GetLambdas

#LMD/DCD translation (sourced from https://github.com/RyanLeeHayes/ALF/tree/master)
def GetLambdas(alf_info,istep,vac_dir,ndupl=None,begres=None,endres=None): #ADDED ARGUMENT
  """
  Reads alchemical trajectories from binary format

  This routine reads binary alchemical flattening trajectories from
  run[i]/res/[name]_flat.lmd or binary alchemical production trajectories
  from run[i][a]/res/[name]_prod[itt].lmd where [i] is the cycle number,
  [a] is the duplicate letter, [name] is the system name, and [itt] is the
  production chunk, and copies them into human readable trajectories in
  analysis[i]/data/Lambda.[ia].[ir].dat where [ia] is the duplicate index
  and [ir] is the replica index. This routine should be called from the
  analysis[i] directory.

  This routine can be called during flattening or production. Flattening
  versus production is detected by the absence or presence, respectively
  of the three optional parameters.

  This routine formats the filenames appropriately and then passes them to
  the routine GetLambda which does the reading.

  Parameters
  ----------
  alf_info : dict
      Dictionary of variables alf needs to run
  istep : int
      The current cycle of alf being analyzed
  ndupl : int, optional
      The number of independent trials run in production. Leave empty to
      signal this is flattening. (defaul is None)
  begres : int, optional
      The number of chunks of production to discard for equilibration.
      Leave empty for flattening. (default is None)
  endres : int, optional
      The final chunks of production to use for analysis. Leave empty for
      flattening. (default is None)
  """

  # from subprocess import call
  from GetLambda import GetLambda

  if ndupl==None:
    production=False
    # istep=int(sys.argv[1])
    ndupl=1
  else:
    production=True
    # istep=int(sys.argv[1])
    # ndupl=int(sys.argv[2])
    # begres=int(sys.argv[3])
    # endres=int(sys.argv[4])
  # else:
    # print("Error: Need 1 argument for flattening or 4 arguments for production")
    # quit()

  nblocks=alf_info['nblocks']
  nsubs=alf_info['nsubs']
  nreps=alf_info['nreps']
  name=alf_info['name']

  if not os.path.isdir('data'):
    os.mkdir('data')
  DIR="data"

  # ----------------------------------------------------------------------------

  alphabet='abcdefghijklmnopqrstuvwxyz'

  for idupl in range(0,ndupl):

    DDIR=f'{vac_dir}/run'+str(istep) #changed to f-string w vac_dir
    if production:
      DDIR=DDIR+alphabet[idupl]

    for i in range(0,nreps):
      fnmsin=[]
      if nreps>1:
        reptag="_"+str(i)
      else:
        reptag=""
      if production:
        for j in range(begres,endres):
          fnmsin.append(DDIR+'/res/'+name+'_prod'+str(j+1)+'.lmd'+reptag)
      else:
        fnmsin.append(DDIR+'/res/'+name+'_heat.lmd'+reptag)
      fnmout=DIR+("/Lambda.%d.%d.dat" % (idupl,i))
      GetLambda(alf_info,fnmout,fnmsin)

def process_msld() :
    
    # Find number of runs
    runs = []
    for entry in os.listdir(prep_dir) :
        run_match = re.match(r"^run61(\w)$", entry)
        if run_match != None :
            runs.append(run_match.group(1))
    nruns = len(runs)

    outputs = []
    for prod in os.listdir(f"{prep_dir}/run61a"):
        output_match = re.match(r"output_(\d+)", prod)
        if output_match != None :
            outputs.append(output_match.group(1))
    noutputs = len(outputs)

    print(f"runs = {runs} and outputs = {outputs}")


    # For every run, create a set of pdbs for their respective dcd
    for run in runs :
        dcd_path = f"{prep_dir}/run61{run}/dcd"
        os.chdir(dcd_path)
        for output in outputs :
            command = f"processDCD.pl -extract step {prep_dir}/run61{run}/prep/minimized.pdb {dcd_path}/14benz_prod{output}.dcd"
            os.system(command)


    # With the new pdbs, find the number of steps
    nsteps = {}
    for run in runs :
        runsteps = 0
        for entry in os.listdir(f"{prep_dir}/run61{run}/dcd") :
            match = re.match(f"step", entry)
            if match != None :
                runsteps += 1
        nsteps[f"Run {run}"] = runsteps

    # Iterate through every site<site>_sub<sub>_frag.pdb and create dict of {site, sub : ["<atomid>", "<atomid>", "<atomid>"]}
    # Also create all lambda files per run!
    run_pdbs = {}

    for run in range(1, nruns + 1) :
        os.chdir(f"{prep_dir}/run{run}/res")
        GetLambdas(info, run, prep_dir)
        
        for step in range(1, nsteps[f"Run {run}"] + 1) :
            pdb_dir = f"{prep_dir}/run{run}/dcd/step.{step}.pdb"
            with open(pdb_dir, "r") as file:
                pdb = file.read()
                atoms = re.findall(r"ATOM(\s+)(\d+)(\s+)(\w+)", pdb)
            sub_atoms = []
            for entry in atoms :
                sub_atoms.append(entry[3])
            run_pdbs[f"Run {run} Step {step}"] = sub_atoms
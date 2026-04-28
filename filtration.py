from info import *
from process_msld import nruns, nsteps, run_pdbs
import re

def filtration() :
    # For i in range(nsteps), create list of entries in Lambda.dat row step_size * i
    # Create list of elements in first row of Lambda.0.0.dat, store indices of columns with values > .8 in small list
    physical_steps = {}
    for run in range(1, nruns + 1) :
        lmd_path = f"{prep_dir}/run{run}/res/data/Lambda.0.0.dat"
        
        with open(lmd_path, 'r') as file :
            line_count = sum(1 for line in file)
        step_size = line_count / nsteps[f"Run {run}"]
        
        with open(lmd_path, 'r') as file :
            i = 1
            reduced_lmd = {}                   #BIG ISSUE (check slack)!!! In corresponding lambda file, first physical sub changes from 1,1 to 1,3.
            indices = []
            with open(lmd_path, 'r') as file : #Do I treat those as non-physical states because they don't reflect the original 1,1?
                for line in file:              #Potential solution: Account for ignored equilibration steps IN INDICES ARRAY
                    if i % step_size == 0 :
                        if i == 100 :
                            first_line = file.readline()
                            cast_first_line = []
                            for word in first_line.split() :
                                cast_first_line.append(float(word))
                            for col in range(len(cast_first_line)) :
                                if float(cast_first_line[col]) > .8 :
                                    indices.append(col)
                        cast_line = []
                        for word in line.split():
                            cast_line.append(float(word))
                        else : 
                            reduced_lmd[f"Step {int(i / step_size)}"] = cast_line
                    i += 1
    # Check for physical states: if row entries at indices in small list > cutoff, record in new dictionary of physical_steps
    #    storing {step number : physical substituents}
        phys_states = []
        for step in reduced_lmd.keys() :
            physical_state = True
            for physical_i in range(len(indices)) :
                if (reduced_lmd[step][indices[physical_i]] <= info['cutoff']) :
                    physical_state = False
            if physical_state :
                phys_states.append(step)
        physical_steps[f"Run {run}"] = phys_states

    print(f"run_pdbs = {run_pdbs}")
    print(f"physical_steps = {physical_steps}")

    # For each key in physical_steps:
    #     Open related pdb (step.<key>.pdb)
    #     From site and sub, use first dict to get atomIDs
    #     From atomIDs, find atomIDs in step pbd and create string with "<molecule> <xcoord> <ycoord> <zcoord>"
    physical_pdbs = {}
    if os.path.exists(f"{main_dir}/QChemInputs") == False :
        os.mkdir(f"{main_dir}/QChemInputs")
    for run in range(1, nruns + 1) :
        for step_entry in physical_steps[f"Run {run}"] :
            if step_entry :
                step = int(re.findall(r"Step (\d+)", step_entry)[0])        
                fout_dir = f"{main_dir}/QChemInputs/Run{run}_{step_entry}_QC.inp"
                # with open(fout_dir, "w") as fout:
                runstep_mols = run_pdbs[f"Run {run} Step {step}"]
                step_pdb_path = f"{prep_dir}/run{run}/dcd/step.{step}.pdb"
                with open(step_pdb_path, 'r') as pdb:
                    i = 0
                    for line in pdb:
                        if i < len(runstep_mols) :
                            mol = runstep_mols[i]
                            pattern = rf"ATOM(\s+)(\d+)(\s){mol}(\s)LIG(\s+)1(\s+)(\S+)(\s+)(\S+)(\s+)(\S+)"
                            matches = re.findall(pattern, line)
                            xcoord = matches[0][6]
                            ycoord = matches[0][8]
                            zcoord = matches[0][10]
                            physical_pdbs[f"Run {run} Step {step}"] = {mol : [xcoord, ycoord, zcoord]}
                            # fout.write(f"{mol[0]} {xcoord} {ycoord}  {zcoord}")
                            # fout.write("\n")                        
                            i += 1
    print(physical_pdbs)
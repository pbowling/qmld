# qmld Workflow
==========================================
Quantum Mechanics Lambda Dynamics (QMLD) serves as a pipeline for lambda-scaled QM/MM calculations.


## 1. MSLD Sampling (CHARMM)
-------------------------

Run the initial Multi-Site Lambda Dynamics (MSLD) simulation within CHARMM. This step generates the conformational ensemble required for subsequent QM/MM refinement.

**Output:**
- Trajectory files: ``.dcd``
- Lambda log files: ``.lmd``

## 2. Trajectory Processing & Filtering
------------------------------------

Before QM refinement, the raw trajectory must be filtered for "physical" states where the alchemical transition is complete.

**A. Lambda Filtering**

- Parse the ``.lmd`` files.
- Retain only the frames where $\lambda$ > 0.99 for all active sites.
- This ensures the system is in a discrete physical state rather than an intermediate hybrid state.

**B. PDB Generation**

- Use the MMTSB Toolset to extract specific frames from the ``.dcd`` file corresponding to the filtered timestamps.
- Convert the binary trajectory into a series of PDB files for structural analysis.

## 3. QM Region Definition & Input Preparation
-------------------------------------------

Define the subset of atoms to be treated at the QM level.

- **Selection:** Identify residues/atoms for the QM region (e.g., a ligand and nearby catalytic residues).

- **Protonation & Capping:** 
    If the QM/MM boundary bisects a covalent bond, the software will automatically:
    - Truncate the bond.
    - Add a Link Atom (typically hydrogen) to satisfy the valence of the QM atom.

- **Input Generation:** The script generates:
    - Q-Chem input specifying the basis set, functional, and external point charges.
    - CHARMM input for calculating the MM-level energy of the same configuration.

## 4. Single Point Calculations (Q-Chem & CHARMM)
-------------------------------------

The software executes Q-Chem to calculate the electronic energy ($E_{QM}$) & CHARMM ($E_{MM}$) of the defined region.

## 5. Data Aggregation & $\Delta G$ Calculation
--------------------------------------------------

Upon successful completion of all single-point runs, the software parses the output to calculate the Composite Free Energy ($\Delta G_{comp}$):

$$\Delta G_{comp} = \langle E_{QM} - E_{MM} \rangle + \Delta G_{MSLD} $$

**Data Archiving:**
- All intermediate results and energy logs are saved in the ``results/`` directory for final statistical analysis.

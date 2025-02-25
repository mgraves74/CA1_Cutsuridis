# CA1 heteroassociative memory network: Storage and recall
# CA1 PCs, BCs, AACs, BSCs and OLMs (using moderate cell models)
# EC, CA3 (excitatory) and Septal (inhibitory) inputs
# Cycle is: Recall-Storage-Recall etc
# Serial code adapted from Hines' ran3ser.hoc
# VCU & BPG 8-1-09

# Results reported in V. Cutsuridis, S. Cobb and B.P. Graham,
# "Encoding and retrieval in a model of the hippocampal CA1 microcircuit",
# Hippocampus, DOI 10.1002/hipo.20661, 2009.

#%%
#################
# MODULES
#################

# Import modules
from neuron import h 
import numpy as np
import random
import math
import sys
import importlib
import netfcns
from model import cellClasses
import pickle

file_num = 0

### python file to send to bash script
with open("runthis.sh",'w') as f:
    simname = 'guitar'
    celldeath_k = [0]#, 0.15, 0.46, 0.65]
    syn_death_k = [0]#, 0.09, 0.26, 0.35]
    CREB_pop_i = [1] #, 0, 0.2, 0.4, 0.6, 0.8, 1]
    CREBlevel_j = [1] #, 0.125, 0.25, 0.50, 1, 2, 4, 8]
    # CREBtype_h = [1, 2, 3, 4]
    # for hh in range(len(CREBtype_h)):
    #     CREBtype = CREBtype_h[hh]
    for i in range(len(CREB_pop_i)):
        CREB_pop = CREB_pop_i[i]
        for j in range(len(CREBlevel_j)):
            CREBlevel = CREBlevel_j[j]
            for k in range(len(celldeath_k)):
                celldeath = celldeath_k[k]
                syn_death = syn_death_k[k]
                simname = 'guitar' + '_' + str(syn_death) + '_' + str(celldeath) + '_' + str(CREB_pop) + '_' + str(CREBlevel) #+ '_' + str(CREBtype)
                print(f"python main.py {simname} {celldeath} {syn_death} {CREB_pop} {CREBlevel}",file=f) #{CREBtype}
    
h.load_file("stdrun.hoc")
h.load_file("nrngui.hoc") # load_file

#%%

###2c
celldeath = 0

###1e4
CREB_pop = 0

#################
# PARAMETERS
#################
keepoldtypo=0 # 1: rerun the old version of the code, including typos
cellClasses.keepoldtypo = keepoldtypo
usepar = 1 # 1 - use all cores (if mpi installed), 0: run in serial
netfcns.usepar = usepar
printflag = 1 # 0: almost silent, 1: some prints, 2: many prints
netfcns.printflag = printflag

# Set default values for parameters that can be passed in at the command line
plotflag = 0
network_scale = 1 #0.2 # set to 1 for full scale or 0.2 for a quick test with a small network
scaleEScon = 1 # #1 scaling factor for number of excitatory connections in the network, should be set to 1

numCycles = 8 # set to 1 or 2 for a short test network or 8 for a full simulation
simname="guitar"
trial_name = "Normal"
connect_random_low_start_ = 1  # low seed for mcell_ran4_init()

netfile = 'N100S20P5'
electrostim = 0 # 0 = no stimulation, 1 = stimulation according to parameters set farther down in code
percentDeath = celldeath # fraction of pyramidal cells to kill off  ###2c
                  # to represent a disease state

# Check for parameters being passed in via the command line
argadd = 1
startlen = 1
import subprocess
result = subprocess.run('hostname', stdout = subprocess.PIPE)
if (result.stdout.decode('utf-8')[:3] == "scc"): # scc has an odd way of accounting for command line arguments
    argadd = 2
    startlen = 5
    
if len(sys.argv)>(startlen):
    simname = sys.argv[startlen]
    if len(sys.argv)>(argadd+startlen):
        percentDeath = float(sys.argv[argadd+startlen])
        if len(sys.argv)>(2*argadd+startlen):
            syn_death = float(sys.argv[2*argadd+startlen]) ###adds syn_death to command line
            if len(sys.argv)>(3*argadd+startlen):
                CREB_pop = float(sys.argv[3*argadd+startlen])
                if len(sys.argv)>(4*argadd+startlen):
                    CREBlevel = float(sys.argv[4*argadd+startlen])
                    # if len(sys.argv)>(5*argadd+startlen):
                    #     CREBtype = float(sys.argv[5*argadd+startlen])
            #if len(sys.argv)>(2*argadd+startlen):
                #electrostim = float(sys.argv[2*argadd+startlen])
            #if len(sys.argv)>(3*argadd+startlen):
                    #numCycles = int(sys.argv[3*argadd+startlen])
                    #if len(sys.argv)>(4*argadd+startlen):
                        #connect_random_low_start_ = float(sys.argv[4*argadd+startlen])    
            
cellClasses.CREBlevel = CREBlevel #which side is which matters a lot
# cellClasses.CREBtype = CREBtype #so I imported CREBtype from cellClasses but then made CREBtype which are different. Unless I do this, the CREBtype in cellClasses (which is cellClasses.CREBtype) won't be altered when update_biophysics() is called later

rmchars=['"',"'","\\"," "]

for i in rmchars:
    simname = simname.replace(i,"")

fstem = "pyresults/" + simname

# Set Timing Parameters
from model_const import *
from connprops import *

SPATT = calcSPATT(network_scale)

SIMDUR = STARTDEL + (THETA*numCycles)    # simulation duration (msecs)

h.tstop =  SIMDUR
h.celsius = 34


# Save parameters to file:
    
params = {"simname":simname,
          "netfile":netfile,
          "numCycles":numCycles,
          "network_scale":network_scale,
          "SIMDUR":SIMDUR,
          "dt":h.dt,
          "connect_random_low_start_": connect_random_low_start_,
          "scaleEScon": scaleEScon,
          "electrostim": electrostim,
          "percentDeath": percentDeath}

with open('pyresults/' + simname + '.pickle', 'wb') as f:
    pickle.dump(params, f, pickle.HIGHEST_PROTOCOL)

print('checkpoint1') ###checkpoint
#%%

#################
# CREATE CELLS
#################

class CellPop():
    def __init__(self, num=0, gidst=0, gidend=0, order=0, popname="", classtype="", isart=0):
        self.num=num
        self.gidst=gidst
        self.gidend=gidend
        self.core_st=-1
        self.core_en=-1
        self.order=order
        self.popname=popname
        self.classtype=classtype
        self.isart=isart

poplist=[]
poplist.append(CellPop(num=100*network_scale, order=0, classtype="PyramidalCell", popname="PyramidalCell", isart=0))
poplist.append(CellPop(num=2, order=1, popname="BasketCell", classtype="BasketCell", isart=0))
poplist.append(CellPop(num=1, order=2, popname="AACell", classtype="AACell", isart=0))
poplist.append(CellPop(num=1, order=3, popname="BistratifiedCell", classtype="BistratifiedCell", isart=0))
poplist.append(CellPop(num=1, order=4, popname="OLMCell", classtype="OLMCell", isart=0))
poplist.append(CellPop(num=100*network_scale, order=5, popname="CA3Cell", classtype="StimCell", isart=1))
poplist.append(CellPop(num=20*network_scale, order=6, popname="ECCell", classtype="StimCell", isart=1))
poplist.append(CellPop(num=10*network_scale, order=7, popname="SEPCell", classtype="BurstCell", isart=1))

ncell = 0
for p in poplist:
    ncell += p.num
# creates the cells and appends them to a List called cells
cells = []
ranlist = []
nclist = []

h('{load_file("ranstream.hoc")}')  # to give each cell its own sequence generator
h('{load_file("netparmpi.hoc")}')  # to give each cell its own sequence generator

h.nrnmpi_init() 
pnm = h.ParallelNetManager(ncell)	# Set up a parallel net manager for all the cells
pc = pnm.pc # Even if running serially, we can create and use this
                         # in serial, pc.nhost == 1
pc.gid_clear() # If rerunning code, clear old assignments (in case network size got changed)
pnm.round_robin() #Incorporate all processors - cells 0 through ncell-1


if (pc.id()==0 and printflag>0):
    print("simname = {} will run for {} ms, results will be in {}_*.dat".format(simname, SIMDUR, fstem))

# Set GID ranges of cells and Load Cell Class definitions
pop_by_name={}
st=0
i=0
pcst = pc.id()
core_i = 0
newcell = None

CREBrandlist = list(range(100))
for x in range(int(CREB_pop*100)):
    i = random.randint(0,len(CREBrandlist)-1)
    CREBrandlist.pop(i)

for pop in poplist:
    pop_by_name[pop.popname] = pop
    pop.gidst=int(st) 
    pop.gidend=int(pop.gidst + pop.num - 1)
    st = int(pop.gidend + 1)
    pop.core_st = int(core_i)
    coretype_i = 0

#   for j in range(int(pop.num)):    # in serial, make all cells on one core
    for j in range(int(pop.gidst),int(pop.gidend)+1):    # in parallel, make every nth cell on one core                             
        if (pc.gid_exists(j)):
            if (pc.id()==0 and printflag>1):
                print("newcell = cellClasses."+pop.classtype+ "(int("+str(j)+"))")
            exec("newcell = cellClasses."+pop.classtype+ "(int("+str(j)+"))")
            #CREB_rand = random.random() ###1e4 population affected by CREB
            if j in CREBrandlist:
                newcell.update_biophysics(cellClasses.noCREB, cellClasses.noCREB)
                print("noCREB")
                newcell.CREBcell = False
                #print(cellClasses.CREB.mAHP, cellClasses.CREB.sAHP, cellClasses.CREB.AMPA, cellClasses.CREB.NMDA)
            elif pop.gidst == 0:
                newcell.update_biophysics(cellClasses.CREB, cellClasses.CREBlevel)
                newcell.CREBcell = True
                #print(cellClasses.CREB.mAHP, cellClasses.CREB.sAHP, cellClasses.CREB.AMPA, cellClasses.CREB.NMDA)
            if (pop.isart==1):
                newcell.stim.gid = int(j)
                newcell.stim.core_i = int(core_i)
                newcell.stim.coretype_i = int(coretype_i)
            newcell.core_i = int(core_i)
            newcell.coretype_i = int(coretype_i)
            cells.append(newcell)
            if (j==206):
                ranlist.append(h.RandomStream(j+500))  # ranlist.o(i) corresponds to
            else:
                ranlist.append(h.RandomStream(j))  # ranlist.o(i) corresponds to
            i+=1
            pcst +=pc.nhost()
            core_i += 1
            coretype_i += 1
            #pc.set_gid2node(newcell.gid, pc.id())  # associate cell's gid with this host
            nc = newcell.connect2target(None)  # attach spike detector to cell
            pc.cell(newcell.gid, nc)  # associate cell's gid with its spike detector
        
    pop.core_en = core_i-1


# Calculate totals of cells
ncell = sum([o.num for o in poplist if o.isart==0])    # total number of real cells
nstim = sum([o.num for o in poplist if o.isart==1])        # total number of inputs
ntot = ncell+nstim # total number of cells

pc.barrier() # wait for all cores to get to this point before continuing

#%%

#################
# SET STIMULATION
#################

netfcns.mkinputs(cells, ranlist, pop_by_name, pc)

#%%

#################
# SET STORAGE AND RECALL FUNCTIONALITY
#################

# Pattern storage and recall parameters

C_P = 1  # probability of excitatory connections received by each CA1 PC
         # from CA3 inputs (1 gives full connectivity)
         
SPATT = 20*network_scale    # number of active cells per pattern
NPATT = 5    # number of stored patterns
NSTORE = 5    # number of new patterns to store

CPATT = 1    # index of cue pattern
CFRAC = 1    # fraction of active cells in cue


# file name of connection weights and patterns
# (cue and EC patterns taken from FSTORE file to implement storage)
# (use same file for FPATT and FSTORE to test recall only)
if network_scale==1:
    FCONN = "Weights/wgts"+netfile+".dat" #"Weights/wgtsN100S20P5.dat"
    FPATT = "Weights/patts"+netfile+".dat"    # "Weights/pattsN100S20P5.dat"    # already stored patterns
    FSTORE = "Weights/patts"+netfile+".dat"    # "Weights/pattsN100S20P5.dat"    # new patterns to store
else:
    netfile = 'N100S20P5'    
    FCONN = "Weights/wgtsN100S20P5scaled.dat" #"Weights/wgtsN100S20P5.dat"
    FPATT = "Weights/pattsN100S20P5scaled.dat"    # "Weights/pattsN100S20P5.dat"    # already stored patterns
    FSTORE = "Weights/pattsN100S20P5scaled.dat"    # "Weights/pattsN100S20P5.dat"    # new patterns to store
    
print('checkpoint2') ###checkpoint
#%%

#################
# SET CONNECTIVITY
#################

# of connections received by each POSTCELLTYPE from a given PRECELLTYPE
class popConn:
    def __init__(self, popname="", prepop="", prenum=1, type="", weight=0, delay=3, synst=0, synend=0):
        self.popname=popname
        self.prepop=prepop
        self.prenum=prenum
        self.type=type
        self.weight=weight
        self.delay=delay
        self.synst=synst
        self.synend=synend
        self.connsMade=0
        
    def __repr__(self):
        return "Connection {} {} ---> {} of type {} with weight {}".format(int(self.prenum), self.prepop, self.popname, self.type, self.weight)

# Synapse indices
# onto CA1 PCs
E_EC = 0    # EC AMPA excit to medium SLM (2 of)
E_CA3 = 2    # CA3 AMPA excit to medium SR
EN_CA3 = 3    # CA3 NMDA excit to medium SR
EM_CA3 = 23    # CA3 modifiable (STDP) AMPA excit to medium SR
E_PC = 4    # CA1 recurrent AMPA excit to proximal SR
I_BC = 5    # ff&fb inhib via BCs to soma
I_AAC = 6    # ff&fb inhib via AACs to axon initial segment
I_BSC = 11    # ff&fb inhib via BSCs to SR med (12 of: 6 GABAA, 6 GABAB)
I_OLM = 7    # fb inhib via OLMs to SLM (4 of: 2 GABAA, 2 GABAB)

# onto INs (BC, AAC, BSC)
EI_EC = 0    # EC AMPA excit (2 of; not onto BSC)
EI_CA3 = 2    # CA3 AMPA excit (4 of)
EI_PC = 6    # CA1 PC AMPA excit (2 of)
II_SAME = 8    # inhib from neighbouring INs (BC->BC; BSC->BSC)
II_OPP = 9    # inhib from other INs (BSC->BC; BC->BSC)
II_SEP = 10    # inhib from septum (4 of: 2 GABAA, 2 GABAB)

# onto INs (OLM)
EO_PC = 0    # CA1 PC AMPA excit (2 of)
IO_IN = 2    # inhib from INs and septum (2 of: 1 GABAA, 1 GABAB)

###1e5??????

connlist=[]                    # Postsynaptic type      Presynaptic type  number of connections (at least 1)
# connlist.append(popConn(popname="PyramidalCell", prepop="CA3Cell", prenum=max([pop_by_name["CA3Cell"].num * scaleEScon, 1]), type="AMPA", weight=CLWGT, delay=CDEL, synst=E_CA3, synend=E_CA3+EN_CA3)) # CA3_PC. Use EM_CA3 for modifiable synapses
connlist.append(popConn(popname="BasketCell",    prepop="CA3Cell", prenum=max([pop_by_name["CA3Cell"].num * scaleEScon, 1]), type="AMPA", weight=EIWGT, delay=EIDEL, synst=EI_CA3, synend=EI_CA3+3)) # 
connlist.append(popConn(popname="AACell",        prepop="CA3Cell", prenum=max([pop_by_name["CA3Cell"].num * scaleEScon, 1]), type="AMPA", weight=EIWGT, delay=EIDEL, synst=EI_CA3, synend=EI_CA3+3)) # CA3_AAC
connlist.append(popConn(popname="BistratifiedCell", prepop="CA3Cell", prenum=max([pop_by_name["CA3Cell"].num * scaleEScon, 1]), type="AMPA", weight=EIWGT, delay=EIDEL, synst=EI_CA3, synend=EI_CA3+3)) # CA3_BSC

# connlist.append(popConn(popname="PyramidalCell", prepop="ECCell", prenum=max([pop_by_name["ECCell"].num * scaleEScon, 1]), type="AMPA", weight=ECWGT, delay=EIDEL, synst=E_EC, synend=E_EC+2)) # EC_PC
connlist.append(popConn(popname="BasketCell",    prepop="ECCell", prenum=max([pop_by_name["ECCell"].num * scaleEScon, 1]), type="AMPA", weight=EIWGT, delay=EIDEL, synst=EI_EC, synend=EI_EC+1)) # EC_BC
connlist.append(popConn(popname="AACell",        prepop="ECCell", prenum=max([pop_by_name["ECCell"].num * scaleEScon, 1]), type="AMPA", weight=EIWGT, delay=EIDEL, synst=EI_EC, synend=EI_EC+1)) # EC_AAC

connlist.append(popConn(popname="BasketCell",    prepop="SEPCell", prenum=pop_by_name["SEPCell"].num, type="GABAA", weight=SEPWGT, delay=SEPDEL, synst=II_SEP, synend=II_SEP+1)) # SEP_BC
connlist.append(popConn(popname="AACell",        prepop="SEPCell", prenum=pop_by_name["SEPCell"].num, type="GABAA", weight=SEPWGT, delay=SEPDEL, synst=II_SEP, synend=II_SEP+1)) # SEP_AAC

if keepoldtypo:
    connlist.append(popConn(popname="BasketCell", prepop="SEPCell", prenum=pop_by_name["SEPCell"].num, type="GABAA", weight=SEPWGTL, delay=SEPDEL, synst=II_SEP, synend=II_SEP+1)) # SEP_BSC
    connlist.append(popConn(popname="AACell",       prepop="SEPCell", prenum=pop_by_name["SEPCell"].num, type="GABAA", weight=SEPWGTL, delay=SEPDEL, synst=IO_IN, synend=IO_IN)) # SEP_OLM
else:
    connlist.append(popConn(popname="BistratifiedCell", prepop="SEPCell", prenum=pop_by_name["SEPCell"].num, type="GABAA", weight=SEPWGTL, delay=SEPDEL, synst=II_SEP, synend=II_SEP+1)) # SEP_BSC
    connlist.append(popConn(popname="OLMCell",       prepop="SEPCell", prenum=pop_by_name["SEPCell"].num, type="GABAA", weight=SEPWGTL, delay=SEPDEL, synst=IO_IN, synend=IO_IN)) # SEP_OLM

connlist.append(popConn(popname="PyramidalCell", prepop="PyramidalCell", prenum=max([1 * scaleEScon, 1]), type="AMPA", weight=Pcell2Pcell_weight, delay=Pcell2Pcell_delay, synst=E_PC, synend=E_PC)) # PC_PC
connlist.append(popConn(popname="BasketCell",    prepop="PyramidalCell", prenum=max([pop_by_name['PyramidalCell'].num * scaleEScon, 1]), type="AMPA", weight = Pcell2Bcell_weight, delay = Pcell2Bcell_delay, synst=EI_PC, synend=EI_PC+1)) # PC_BC
connlist.append(popConn(popname="BistratifiedCell", prepop="PyramidalCell", prenum=max([pop_by_name['PyramidalCell'].num * scaleEScon, 1]), type="AMPA", weight = Pcell2AAcell_weight, delay = Pcell2AAcell_delay, synst=EI_PC, synend=EI_PC+1)) # PC_BSC
connlist.append(popConn(popname="AACell",        prepop="PyramidalCell", prenum=max([pop_by_name['PyramidalCell'].num * scaleEScon, 1]), type="AMPA", weight = Pcell2BScell_weight, delay = Pcell2BScell_delay, synst=EI_PC, synend=EI_PC+1)) # PC_AAC
connlist.append(popConn(popname="OLMCell",       prepop="PyramidalCell", prenum=max([pop_by_name['PyramidalCell'].num * scaleEScon, 1]), type="AMPA", weight = Pcell2OLMcell_weight, delay = Pcell2OLMcell_delay, synst=EO_PC, synend=EO_PC+1)) # PC_OLM

connlist.append(popConn(popname="PyramidalCell", prepop="BasketCell", prenum=2, type="GABAA", weight = Bcell2Pcell_weight, delay = Bcell2Pcell_delay, synst=I_BC, synend=I_BC)) # BC_PC
connlist.append(popConn(popname="BasketCell",    prepop="BasketCell", prenum=1, type="GABAA", weight = Bcell2Bcell_weight, delay = Bcell2Bcell_delay, synst=II_SAME, synend=II_SAME)) # BC_BC
connlist.append(popConn(popname="BistratifiedCell", prepop="BasketCell", prenum=2, type="GABAA", weight = Bcell2BScell_weight, delay = Bcell2BScell_delay, synst=II_OPP, synend=II_OPP)) # BC_BSC

# The call to make this connection is commented out in hoc code
# connlist.append(popConn(popname="OLMCell",       prepop="BasketCell", prenum=2, type="GABAA", weight = 0.0, delay = 1)) # BC_OLM

connlist.append(popConn(popname="PyramidalCell", prepop="AACell", prenum=1, type="GABAA", weight = AAcell2Pcell_weight, delay = AAcell2Pcell_delay, synst=I_AAC, synend=I_AAC)) # AAC_PC
connlist.append(popConn(popname="PyramidalCell", prepop="BistratifiedCell", prenum=1, type="GABAA", weight = BScell2Pcell_weight, delay = BScell2Pcell_delay, synst=I_BSC, synend=I_BSC+5)) # BSC_PC
connlist.append(popConn(popname="PyramidalCell", prepop="BistratifiedCell", prenum=1, type="GABAB", weight = BScell2Pcell_GABAB_weight, delay = BScell2Pcell_delay, synst=I_BSC+6, synend=I_BSC+11)) # BSC_PC

#connlist.append(popConn(popname="BistratifiedCell",    prepop="BistratifiedCell", prenum=1, type="GABAA", weight = BScell2BScell_weight, delay = BScell2BScell_delay, synst=II_SAME, synend=II_SAME)) # BSC_BC
connlist.append(popConn(popname="BasketCell",    prepop="BistratifiedCell", prenum=1, type="GABAA", weight = BScell2Bcell_weight, delay = BScell2Bcell_delay, synst=II_OPP, synend=II_OPP)) # BSC_BC

connlist.append(popConn(popname="PyramidalCell", prepop="OLMCell", prenum=1, type="GABAA", weight = OLMcell2Pcell_weight, delay = OLMcell2Pcell_delay, synst=I_OLM, synend=I_OLM+1)) # OLM_PC
connlist.append(popConn(popname="PyramidalCell", prepop="OLMCell", prenum=1, type="GABAB", weight =OLMcell2Pcell_GABAB_weight, delay = OLMcell2Pcell_delay, synst=I_OLM+2, synend=I_OLM+3)) # OLM_PC

# In the original Cutsuridis code, this weight is set first to 0.01 and then overwritten a few lines later to 0.0.
# The call to make this conection is commented out in hoc
# connlist.append(popConn(popname="BasketCell",    prepop="OLMCell", prenum=1, type="GABAA", weight = OLMcell2Bcell_weight, delay = OLMcell2Bcell_delay, synst=II_OPP, synend=II_OPP)) # OLM_BC
  
h.mcell_ran4_init(connect_random_low_start_)
nclist = []

# # Make connections with data from above
for conn in connlist: 
    conn.connsMade = netfcns.connectcells(cells,ranlist, nclist, pop_by_name, conn.popname, conn.prepop, synstart=conn.synst, synend=conn.synend, npresyn=conn.prenum, weight=conn.weight, delay= conn.delay, pc = pc, syn_death = syn_death)
    #if (printflag>1):
    #    print("newtar starts with ", pop_by_name[conn.popname].gidst, " and pre starts with ", pop_by_name[conn.prepop].gidst , " and conns made = ", conn.connsMade)

#netfcns.mkinputs(cells, pop_by_name['CA3Cell'].gidst, pop_by_name['ECCell'].gidst, pop_by_name['SEPCell'].gidst, ntot, pop_by_name)
# EC input to PCs
ncelist = netfcns.connectEC(FPATT, ECPATT, NPATT, E_EC, 2, cells,  pop_by_name, pc, syn_death)	#  restore existing pattern
# CA3 input to PCs
print('checkpoint that only takes long in the spyder kernel')
ncslist = netfcns.connectCA3(FCONN, C_P, EM_CA3, EN_CA3, cells, pop_by_name, connect_random_low_start_, pc, syn_death)	# with modifiable synapses
#%%

#################
# SET CUES FOR PATTERNS
#################
netfcns.mkcue(FPATT, CPATT, CFRAC, NPATT, SPATT, cells, ranlist, pop_by_name, pc)	# cue from already stored pattern
#netfcns.mkcue(FSTORE, CPATT, CFRAC, NSTORE)	# cue from new pattern
netfcns.mkEC(cells, ranlist, pop_by_name, pc)

#%%

#################
# SET UP RECORDING OF RESULTS
#################

netfcns.spikerecord(cells,pc)
results = netfcns.vrecord(cells,pop_by_name, iPPC, iNPPC,pc)

#%% Cell Death and Electrostim

num2pick = int(percentDeath*pop_by_name["PyramidalCell"].num) # number of cells

deadlist = []
CREBlist = [] ###1e4

new_random = h.Random(400)
new_random.discunif(pop_by_name["PyramidalCell"].gidst, pop_by_name["PyramidalCell"].gidend)

for x in range(num2pick):
    # pick a random number that corresponds to a specific pyramidal cell
    # append that number to the deadlist
    tmpvar = int(new_random.repick())
    while (deadlist.count(tmpvar)>0):
        tmpvar = int(new_random.repick())
        
    deadlist.append(tmpvar)

###Beginning to attempt CREBlist to aid 1e4 anaylsis
# Cnew_random = h.Random(400)
# Cnew_random.discunif(pop_by_name["PyramidalCell"].gidst, pop_by_name["PyramidalCell"].gidend)

# for x in range(num2pick):
#     Ctmpvar = int(Cnew_random.repick())
#     while (CREBlist.count(Ctmpvar)>0):
#         Ctmpvar = int(Cnew_random.repick())
#     CREBlist.append(Cnew_random)

print('checkpoint_deadlist')
if (pc.id()==0 and percentDeath>0):
    print("List of cells that died:")
list_clamps=[]
for cell2kill in deadlist:
    if (pc.id()==0):
        print(cell2kill)
    if (pc.gid_exists(cell2kill)):
        model_cell = pc.gid2cell(cell2kill)
        # keep remaining lines that add an IClamp and set its properties
    
        stimobj = h.IClamp(model_cell.soma(0.5))
        stimobj.delay = 2
        stimobj.dur = SIMDUR
        stimobj.amp = -.4    
        list_clamps.append(stimobj)

list_of_stims=[]
if (electrostim>0):
    for cell in range(pop_by_name["PyramidalCell"].gidst, pop_by_name["PyramidalCell"].gidend):
        if (deadlist.count(cell)==0 and pc.gid_exists(cell)):        
            model_cell = pc.gid2cell(cell)
        
            electclamp = h.IClamp(model_cell.soma(0.5))
            electclamp.delay = 2
            electclamp.dur = SIMDUR
            electclamp.amp = electrostim # nA .... (1000 pA) 
            list_of_stims.append(electclamp)
            # myvec = h.Vector() 
            # myvec # fill with a pattern
            # myvec.play(electclamp.amp) 
print('checkpoint4')
#%%

#################
# RUN SIMULATION AND WRITE RESULTS
#################


# parallel code functions:
# Do single parallel run
def prun():
    pc.barrier()  # wait for all hosts to get to this point
    pc.set_maxstep(1);
    h.stdinit()
    if (pc.id()==0 and printflag>1):
        print("Parallel run is going to run till",h.tstop)
    pc.psolve(h.tstop);
    pc.barrier()  # wait for all hosts to get to this point

# Do parallel run for each stored pattern
def bpattrun():
    netfcns.erasecue(pop_by_name,pc)
    for i in range(0, NPATT):
        if (pc.id()==0 and printflag>1):
            print("Cue pattern ", i) # print header once
        cuefstem = "{}_{}".format(fstem, i)
        #h.sprint(fstem, "Results/HAM_P5R%", i)
        netfcns.mkcue(FPATT, i, CFRAC, NPATT, pc);	# cue from stored pattern
        pc.barrier()  # wait for all hosts to get to this point
        #{pc.set_maxstep(10)}
        pc.set_maxstep(1);
        h.stdinit()
        pc.psolve(h.tstop);
        netfcns.spikeout(cells,fstem,pc)
        netfcns.vout(cells,results,fstem,pc)
        netfcns.erasecue(pop_by_name,pc)
        
            
# Set a NEURON function (midbal) to run at a specific
# time/event during the simulation:
h('StepBy=100') # ms

h('walltime = startsw()')
h.xopen("midbalfcn.hoc")
h('objref fihw')
h('fihw = new FInitializeHandler(2, "midbal()")')

# run the simulation
# if (batchflag==1):
if (pc.id()==0 and printflag>0):
    print("Now running simulation at scale = ", network_scale, " for time = ", SIMDUR, " with scaleEScon = ", scaleEScon)

print('checkpoint_simulation')

if usepar==1:
    prun() # run and print results
else:
    h.run() 

print('checkpoint_results')

# print out the results
spikeout = netfcns.spikeout(cells,fstem,pc)
vout = netfcns.vout(cells,results,fstem,pc)

if (pc.id()==0 and printflag>0):
    print( "** Finished running sim and printing results **")

import fig9_patternrecall as fig9

perf = fig9.calc_performance(simname,netfile,numCycles, network_scale)   

data2save={'dt':h.dt, 'tstop':h.tstop, 'netfile':netfile, 'simname':simname, 'performance':perf, 'electrostim':electrostim, 'percentDeath':percentDeath, 'network_scale':network_scale}

#%%
# import pickle

# # Save results in a pickle file:
# with open('pyresults/' + simname+'.pkl', 'w') as f:  # Python 3: open(..., 'wb')
#     pickle.dump((spikeout, vout, data2save), f)

if perf is not None:
    with open('pyresults/' + simname+'_performance.txt', 'w') as f:  # Python 3: open(..., 'wb')
        f.write("{:.3f}\n".format(perf))
        f.write("{:.3f}\n".format(electrostim))
        f.write("{:.3f}\n".format(percentDeath))

print('checkpoint7') ###checkpoint
#%%
#################
# PLOT RESULTS
#################
import plotfcns as pf

pf.plotresults(params)

    # if 'cells' in locals():
    #     netfcns.spikeplot(cells,h.tstop,ntot)
    #     netfcns.vplot(cells,results)

if usepar==1 and pc.nhost()>1:
    pc.gid_clear()
    pc.runworker()
    pc.done()
    h.quit()
    quit()  
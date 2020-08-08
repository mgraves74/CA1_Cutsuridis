# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 00:37:03 2020

@author: mbezaire
"""
import numpy as np
import random
from neuron import h
from model_const import *
import matplotlib.pyplot as plt

usepar = 0
printflag = 1
cuelist = []

def connectcells(cells, ranlist, nclist, pop_by_name, post_type, pre_type, synstart, synend,npresyn,weight,delay, pc): # {local i, j, gid, nsyn, r  localobj syn, nc, rs, u
    # initialize the pseudorandom number generator
    ctcons=0
    for i in range(pop_by_name[post_type].core_st,pop_by_name[post_type].core_en+1):
        cell = cells[i]
        rs = ranlist[i]  # RandomStream for cells.object(i)
        rs.start()
        rs.r.discunif(int(pop_by_name[pre_type].gidst),int(pop_by_name[pre_type].gidend))  # pick a random presynaptic cell by gid of presynaptic cell type return source cell index
        u = np.zeros(int(pop_by_name[pre_type].num))  # for sampling without replacement, u[i]==1 means spike source i has already been chosen
        nsyn = 0
        
        while (nsyn < npresyn and nsyn < pop_by_name[pre_type].num):
            r = int(rs.repick())
            # no self-connection and only one connection from any source
            if (r != cell.gid and u[r-int(pop_by_name[pre_type].gidst)] == 0):
                # target synapses
                for j in range(synstart,synend+1) :
                    # set up connection from source to target
                    syn = cell.pre_list[j]
                    #nc = pc.gid_connect(r, syn)
                    if usepar==0:
                        nc = cells[r].connect2target(syn)
                    else:
                        nc = pc.gid_connect(r, syn)
                    
                    nclist.append(nc)
                    nc.delay = delay
                    nc.weight[0] = weight
                
                u[r-int(pop_by_name[pre_type].gidst)] = 1
                nsyn += 1
                ctcons +=1
                
    return ctcons


# connects the EC input layer to PC cells
# read active PCs from pattern file
# all-to-all connectivity between EC and PC pattern cells
# appends the PC NetCons to a List called ncslist
def connectEC(FPATT, ECPATT, NPATT, synstart, numsyn, cells, pop_by_name, pc):# {local i, gid, ncue  localobj cue, cstim, syn, src, nc, fp, target
    ncelist = []
    gids = [cell.gid for cell in cells]
    
    # read pattern file (ECPATT=num rows, NPATT = num columns)
    cue = np.loadtxt(fname = FPATT)
    if (cue.shape != (ECPATT, NPATT) and printflag>1):
        print("The cue data is a different shape than expected:", cue.shape)

    # find active cells in pattern
    for i in range(len(cue)):
        ##if (!pc.gid_exists(i+iPC)) { continue }
        #if (cue[i,0] == 1 ): # TODO added a column index that wouldn't be there usually?

        if (cue[i,0] == 1 and pc.gid_exists(i+pop_by_name["PyramidalCell"].gidst)): # Check if owned by this core
            # print "Pattern cell ", i
            # target = pc.gid2cell(i+iPC)
            target = pc.gid2cell(i+pop_by_name["PyramidalCell"].gidst)
            #target synapses
            for k in range(synstart, synstart+numsyn):
                syn = target.pre_list[k]    # excitatory synapse
                # create pattern stimulus
                for j in range(int(pop_by_name["ECCell"].num)):
                    # set up connection from source to target
                    #nc = pc.gid_connect(j+iEC, syn)
                    if usepar==1:
                        nc = pc.gid_connect(int(j+pop_by_name["ECCell"].gidst), syn)
                    else:
                        src = cells[int(j+pop_by_name["ECCell"].gidst)].stim
                        nc = h.NetCon(src, syn)
                        
                    ncelist.append(nc)
                    nc.delay = ECDEL
                    nc.weight[0] = ECWGT
                    

# connects the CA3 input layer to output cells (PCs and INs)
# read PC connections from a file, with connections to
# a target being a column with index i for target cell i
# appends the PC NetCons to a List called ncslist
                    
def connectCA3(FCONN, C_P, EM_CA3, EN_CA3, cells, pop_by_name, connect_random_low_start_, pc): # {local i, j, cp, gid  localobj src, syn, synN, nc, fc, rs, conns, rc
    cp = C_P    # connection probability
    #mcell_ran4_init(connect_random_low_start_)
    #rc = new Vector(pop_by_name["CA3Cell"].num)  # random physical connectivity
    ncslist = []
    random.seed(connect_random_low_start_)
    #ncilist = new List()
    # inputs to PCs determined by weight matrix
    for i in range(pop_by_name['PyramidalCell'].core_st,pop_by_name['PyramidalCell'].core_en+1):    # loop over possible target cells
        cell = cells[i]
        gid = cell.gid    # id of cell
        syn = cell.pre_list[EM_CA3]    # AMPA synapse with STDP
        syn.wmax = CHWGT
        syn.wmin = CLWGT
        syn.d = STDPDFAC    # depression
        syn.p = STDPPFAC    # potentiation
        syn.gscale = AMPASUPP    # fraction of AMPA during storage
        syn.thresh = STDPTHRESH    # threshold for postsynaptic voltage detection
        syn.gbdel = STDPSTART
        syn.gbint = STDPINT
        syn.gblen = STDPLEN
        synN = cell.pre_list[EN_CA3]    # NMDA synapse
        #rs = ranlist[i]  # the corresponding RandomStream
        #rs.start()
        #rs.r.uniform(0, 1)  # return integer in range 0..1
        #rc.setrand(rs.r)    # generate random connectivity
        
        # open connections file
        # read incoming weights for cell gid
        conns = np.loadtxt(fname = FCONN)

        for j in range(int(pop_by_name["CA3Cell"].num)):
            #for j=0, CA3_PC-1 { # You might need something like this line instead so that it doesn't error out if you are only planning to make a scaled down number of synapses
            # only connection if physical connection exists
            #if (rc[j] <= cp):
            if (random.uniform(0,1) <= cp):
                #print "   src ", j

                if usepar==1:
                    nc = pc.gid_connect(int(j+pop_by_name["CA3Cell"].gidst), synN)
                    nc2 = pc.gid_connect(int(j+pop_by_name["CA3Cell"].gidst), syn)

                else:
                    src = cells[int(j+pop_by_name["CA3Cell"].gidst)].stim
                    nc = h.NetCon(src, synN)
                    nc2 = h.NetCon(src, syn)


                # set up connection from source to target NMDA synapse
                #        nc = pc.gid_connect(j+iCA3, synN)
                ncslist.append(nc)
                nc.delay = CDEL
                nc.weight[0] = CNWGT    # NMDA weight same for all connections
                # high AMPA if weight is 1
                
                ncslist.append(nc2)
                nc2.delay = CDEL

                if (conns[j,0] == 1): # TODO access the correct column
                    # set up connection from source to target
                    #nc = pc.gid_connect(j+iCA3, syn)
                    nc2.weight[0] = CHWGT
                else:
                    # set up connection from source to target
                    #nc = pc.gid_connect(j+iCA3, syn)
                    nc2.weight[0] = CLWGT    # unlearned weight


# sets the CA3, EC and Septal background inputs
def mkinputs(cells, ranlist, pop_by_name, pc): #{local i localobj stim, rs 
    # Configures the stimulation:
    
    for i in range(pop_by_name["CA3Cell"].core_st,pop_by_name["CA3Cell"].core_en+1):
        cells[i].stim.number = ENUM
        cells[i].stim.start = ESTART
        cells[i].stim.interval = EINT
        cells[i].stim.noise = ENOISE
    
    for i in range(pop_by_name["ECCell"].core_st,pop_by_name["ECCell"].core_en+1):
        cells[i].stim.number = ENUM
        cells[i].stim.start = ESTART
        cells[i].stim.interval = EINT
        cells[i].stim.noise = ENOISE
    
    for i in range(pop_by_name["SEPCell"].core_st,pop_by_name["SEPCell"].core_en+1):
        cells[i].stim.number = SEPNUM
        cells[i].stim.start = SEPSTART
        cells[i].stim.interval = SEPINT
        cells[i].stim.noise = SEPNOISE
        cells[i].stim.burstint = SEPBINT
        cells[i].stim.burstlen = SEPBLEN
               
        rs = ranlist[i]
        # Use the gid-specific random generator so random streams are
        # independent of where and how many stims there are.
        cells[i].stim.noiseFromRandom(rs.r)
        rs.r.negexp(1)
        rs.start()
            
#########################
# Instrumentation, i.e. stimulation and recording
#########################

# setup activity in EC stims
def mkEC(cells, ranlist, pop_by_name, pc): # {local i, necs localobj cstim, rs
    EClist = []
    necs = 0
    if (printflag >0):
        print("Make EC input...")
    for i in range(pop_by_name["ECCell"].core_st,pop_by_name["ECCell"].core_en+1):
        cell = cells[i]
        gid = cell.gid    # id of cell
        # create cue stimulus
        cstim = cell.stim
        rs = ranlist[i]
        cstim.number = ECNUM
        cstim.start = ECSTART
        cstim.interval = ECINT
        cstim.noise = ECNOISE
        # Use the gid-specific random generator so random streams are
        # independent of where and how many stims there are.
        cstim.noiseFromRandom(rs.r)
        rs.r.normal(0, 1)
        rs.start()
        EClist.append(i)
        necs += 1

# setup activity pattern in input cue stims
def mkcue(FPATT, CPATT, CFRAC, NPATT, SPATT, cells, ranlist, pop_by_name, pc):
    if (printflag >0):
        print( "Make cue (CA3) input...")
    # open patterns file
    cue = np.loadtxt(fname = FPATT) # read pattern

    ncue = 0
    # find active cells in pattern
    for i in range(len(cue)):
        if (pc.gid_exists(i+pop_by_name["CA3Cell"].gidst)):
            if (ncue <= SPATT*CFRAC):     # fraction of active cells in cue
                if (cue[i,0] == 1): #TODO find the correct column
                    if (printflag >1):
                        print("Cue cell ", i)
                    cstim = pc.gid2cell(i+pop_by_name["CA3Cell"].gidst)
                    rs = ranlist[cells[i+pop_by_name["CA3Cell"].gidst].core_i]
                    # create cue stimulus
                    cstim.number = CNUM
                    cstim.start = CSTART
                    cstim.interval = CINT
                    cstim.noise = CNOISE
                    # Use the gid-specific random generator so random streams are
                    # independent of where and how many stims there are.
                    cstim.noiseFromRandom(rs.r)
                    rs.r.normal(0, 1)
                    rs.start()
                    cuelist.append(i)
                    ncue += 1
                    
                if (printflag >1):  
                    print("  cue size ", ncue)

# remove activity pattern in input cue stims
def erasecue(pop_by_name,pc): # {local i, j localobj cstim
    for i in range(len(cuelist)):
        if (pc.gid_exists(cuelist[i]+pop_by_name["CA3Cell"].gidst)):
            cstim = pc.gid2cell(cuelist[i]+pop_by_name["CA3Cell"].gidst)
            cstim.number = 0

# Spike recording
# tvec, idvec will be Vectors that record all spike times (tvec)
# and the corresponding id numbers of the cells that spiked (idvec)
def spikerecord(cells):
    if (printflag >1):
        print( "Record spikes...")
    for cell in cells:
        if (cell.is_art==0):
            cell._spike_detector = h.NetCon(cell.soma(0.5)._ref_v, None, sec=cell.soma)
            cell.spike_times = h.Vector()
            cell._spike_detector.record(cell.spike_times)
            cell.soma_v = h.Vector().record(cell.soma(0.5)._ref_v)
        #else: # to print stim cell spikes...


# Record cell voltage traces
# Vectors that record voltages from pattern PC
# Vectors that record voltages from non-pattern PC
# Vectors that record voltages from INs

def vrecord(cells,pop_by_name, iPPC, iNPPC):    
    if (printflag >1):
        print( "Record example voltage traces...")
    results = {}
    for cell in cells:	# loop over possible target cells
        gid = cell.gid	# id of cell
        if (gid==iPPC):
            results["pvsoma"] = h.Vector().record(cell.soma(0.5)._ref_v)
            results["pvsr"] = h.Vector().record(cell.radTmed(0.5)._ref_v)
            results["pvslm"] = h.Vector().record(cell.lm_thick1(0.5)._ref_v)

        if (gid==iNPPC):
            results["npvsoma"] = h.Vector().record(cell.soma(0.5)._ref_v)
            results["npvsr"] = h.Vector().record(cell.radTmed(0.5)._ref_v)
            results["npvslm"] = h.Vector().record(cell.lm_thick1(0.5)._ref_v)

        if (gid==pop_by_name['BasketCell'].gidst):
            results["vBC"] = h.Vector().record(cell.soma(0.5)._ref_v)
            #print("Recording results into vBC from ", cell)

        if (gid==pop_by_name['AACell'].gidst):
            results["vAAC"] = h.Vector().record(cell.soma(0.5)._ref_v)
            #print("Recording results into vAAC from ", cell)

        if (gid==pop_by_name['BistratifiedCell'].gidst):
            results["vBSC"] = h.Vector().record(cell.soma(0.5)._ref_v)
            #print("Recording results into vBSC from ", cell)

        if (gid==pop_by_name['OLMCell'].gidst):
            results["vOLM"] = h.Vector().record(cell.soma(0.5)._ref_v)
            #print("Recording results into vOLM from ", cell)

    return results

def spikeout(cells,fstem,pc):
    if (pc.id()==0):
        with open("{}_spt.dat".format(fstem), 'w') as f:
            f.write("time\t cell\n")
            for cell in cells:
                if (cell.is_art==0):
                    for spk in cell.spike_times:
                        f.write("{}\t{}\n".format(spk, cell.gid))
    
    pc.barrier()  # wait for all hosts to get to this point
    for rank in range(1,pc.nhost()):
        if (rank==pc.id()):
            with open("{}_spt.dat".format(fstem), 'a') as f:
                for cell in cells:
                    if (cell.is_art==0):
                        for spk in cell.spike_times:
                            f.write("{}\t{}\n".format(spk, cell.gid))

def vout(cells,results,fstem, pc):  
    for key in results:
        with open("{}_{}_{}.dat".format(fstem, key, pc.id()), 'w') as f:
            for v in results[key]:
                f.write("{}\n".format(v))


# produce raster plot of spiking activity
def spikeplot(cells,tstop,ntot):
    plt.figure()
    for i, cell in enumerate(cells):
        if (cell.is_art==0 and cell.spike_times.size()>0):
            plt.vlines(cell.spike_times, i + 0.5, i + 1.5)
    plt.xlabel('Time (ms)')
    plt.ylabel('Neuron (gid)')
    plt.show()
    
def vplot(cells,results):
    plt.figure()
        
    for key in results:
        t = np.arange(0,h.t+h.dt,h.dt)
        if (len(t)!=len(results[key])):
            t = np.arange(0,h.t,h.dt)
        plt.plot(t,results[key],label=key)
        
    plt.xlabel('Time (ms)')
    plt.ylabel('Membrane Potential (mV)')
    plt.legend(loc="upper right")
    plt.show()

# panel for simulation results
def xspikeres():
    h.xpanel("Spike results")
    h.xbutton("Write out", "spikeout()")
    h.xbutton("Plot", "spikeplot()")
    h.xpanel()




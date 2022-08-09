# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 08:41:29 2020

@author: mbezaire
"""

import matplotlib.pyplot as plt
import numpy as np
from neuron import h
import time
# Plot voltage traces from example PC and INs
# Summary diagram for Hippocampus paper
# BPG 23-1-09

def plot_voltages(simname = 'par', STIME = 200, ETIME = 2050, dt=.025):
    
    plt.figure()
    # ms=8
    # lw=1
    nr = 5
    
    VMIN = -90
    VMAX = 50
    
    plt.subplot(nr,1,1);
    FV = 'pyresults/'+ simname +  '_pvsoma.dat'  #graph3/ # voltage file ### remember to change folder
    v = np.loadtxt(FV)  # load spike times
    t = np.arange(0,ETIME+dt,dt)       # extract times
    plt.plot(t, v, 'k-');   # voltage trace
    plt.title('Membrane Potential Traces');
    plt.ylabel('Pyr\n V (mV)');
    plt.xlim([STIME, ETIME])
    plt.ylim([VMIN+10, VMAX-30])
    ax = plt.gca()
    ax.axes.xaxis.set_ticklabels([])
    
    plt.subplot(nr,1,2);
    FV = 'pyresults/'+ simname +  '_vAAC.dat'  #graph3/ # voltage file ### remember to change folder
    v = np.loadtxt(FV)  # load spike times
    t = np.arange(0,ETIME+dt,dt)       # extract times
    plt.plot(t, v, 'k-');   # voltage trace
    plt.ylabel('AA\nV (mV)');
    plt.xlim([STIME, ETIME])
    plt.ylim([VMIN, VMAX+10])
    ax1 = plt.gca()
    ax1.axes.xaxis.set_ticklabels([])
    
    plt.subplot(nr,1,3);
    FV = 'pyresults/'+ simname +  '_vBC.dat'  #graph3/ # voltage file ### remember to change folder
    v = np.loadtxt(FV)  # load spike times
    t = np.arange(0,ETIME+dt,dt)       # extract times
    plt.plot(t, v, 'k-');   # voltage trace
    plt.ylabel('B\nV (mV)');
    plt.xlim([STIME, ETIME])
    plt.ylim([VMIN, VMAX+10])
    ax2 = plt.gca()
    ax2.axes.xaxis.set_ticklabels([])
    
    
    plt.subplot(nr,1,4);
    FV = 'pyresults/'+ simname +  '_vBSC.dat'  #graph3/ # voltage file ### remember to change folder
    v = np.loadtxt(FV)  # load spike times
    t = np.arange(0,ETIME+dt,dt)       # extract times
    plt.plot(t, v, 'k-');   # voltage trace
    plt.ylabel('Bis\nV (mV)');
    plt.xlim([STIME, ETIME])
    plt.ylim([VMIN, VMAX+10])
    ax3 = plt.gca()
    ax3.axes.xaxis.set_ticklabels([])
    
    
    plt.subplot(nr,1,5);
    FV = 'pyresults/'+ simname +  '_vOLM.dat'  #graph3/ # voltage file ### remember to change folder
    v = np.loadtxt(FV)  # load spike times
    t = np.arange(0,ETIME+dt,dt)       # extract times
    plt.plot(t, v, 'k-');   # voltage trace
    plt.ylabel('OLM\nV (mV)');
    plt.xlabel('Time (ms)');
    plt.xlim([STIME, ETIME])
    plt.ylim([VMIN, VMAX])
    plt.savefig("official_plots/membrane_potential_traces" + '_' + str(simname) + '_' + str(time.time()) + ".png") #ANDY - saved plot in folder, marked with timestamp\
    plt.savefig('Images/' + simname + 'v.png')
    #plt.show()
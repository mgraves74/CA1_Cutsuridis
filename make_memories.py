# -*- coding: utf-8 -*-
"""
Created on Tue Aug 10 16:27:39 2021

@author: maria


Make new netfiles!!

Usage is to load this file, then:
baseline = read_patt(netfile = 'N100S20P5')

# then
# to make a memory that is part of another one
# and part random
memfile = two_memories(baseline, X=.75)

# OR

memfile = two_memories(baseline, X=.25, Y=.25)
# to make hybrid memories - mashup of 2 other memories

# then 
write_patt(memfile,"N100S20P5combined")
"""

import numpy as np

def read_patt(netfile = 'N100S20P5'):
    baseline = np.loadtxt('Weights/patts' +netfile+'.dat')
    return baseline

def write_patt(memfile,netfile = 'N100S20P5combined'):
    np.savetext('Weights/patts' +netfile+'.dat', memfile)
    
def two_memories(memfile, X=.5, mems2use = [0, 1]):
    # Make a netfile that has X percentage of one memory
    # and 1-X of another
    if (max(mems2use)-1)>memfile.shape[1]:
        print('Error, trying to access a memory that doesnt exist')
    if X>.99 or X<.01:
        print('Error, choose a fraction between 0 and 1')
    swap_index = int(memfile.shape[0]*X)   
    
    memfile[swap_index:,0] = memfile[swap_index:,1]
        
    return memfile
    



def memory_pieces(memfile, X=.25, Y=.25, mems2use = [0, 1]):
    # Make a netfile that has X percentage of one memory
    # and Y percentage of another
    if (max(mems2use)-1)>memfile.shape[1]:
        print('Error, trying to access a memory that doesnt exist')

    if X>.99 or X<.01:
        print('Error, choose a fraction between 0 and 1 for X')

    if Y>.99 or Y<.01:
        print('Error, choose a fraction between 0 and 1 for X')
 
    if (X+Y)>1:
        print('X and Y together must be 1 or less')
        
    swapX_index = int(memfile.shape[0]*X)   
    swapY_index = int(memfile.shape[0]*Y)   
    # memfile[:swapX_index,0] stays the same
    
    # middle part is now 0s
    memfile[swapX_index:swapY_index,0] = np.zeros((swapY_index-swapX_index,))
    
    # last part is Y memory
    memfile[swapY_index:,0] = memfile[swapY_index:,1]

    return memfile




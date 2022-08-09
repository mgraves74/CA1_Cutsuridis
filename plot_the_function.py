# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 23:21:30 2022

@author: mgrav
"""

# =============================================================================
# import plotfcns as pf
# celldeath_k = [0, 0.15, 0.65]
# syn_death_k = [0, 0.09, 0.35]
# CREB_pop_i = [1]#0, 0.2, 0.4, 0.6, 0.8, 1]
# CREBlevel_j = [0.125, 0.25, 0.50, 1, 2, 4, 8]
# for i in range(len(CREB_pop_i)):
#     CREB_pop = CREB_pop_i[i]
#     for j in range(len(CREBlevel_j)):
#         CREBlevel = CREBlevel_j[j]
#         for k in range(len(celldeath_k)):
#             celldeath = celldeath_k[k]
#             syn_death = syn_death_k[k]
#             simname = 'guitar' + '-' + str(syn_death) + '-' + str(celldeath) + '-' + str(CREB_pop) + '-' +str(CREBlevel)
#             pf.plotresults(simname)
# =============================================================================

# this should loop through and generate plots from downloaded zip folder
import plotfcns as pf
pf.plotresults("guitar")

### note that this won't work for repeat files so just don't repeat files
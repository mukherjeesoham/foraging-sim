#==============================================================================
# Code for understanding when butterflies leave a patch.
# Soham M, 1/2015
#==============================================================================

import numpy as np 
from numpy import linalg as LA
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
import matplotlib

goldenratio = 2. / (1 + 5**.5)
matplotlib.rcParams.update({
"font.size"       : 12.0,
"axes.titlesize"  : 12.0,
"axes.labelsize"  : 12.0,
"xtick.labelsize" : 12.0,
"ytick.labelsize" : 12.0,
"legend.fontsize" : 12.0,
"figure.figsize"  : (10.3, 10.3*goldenratio),
"figure.dpi"  : 300,
"savefig.dpi" : 300,
"text.usetex" : True
})

#------------------------------------------------------------------------------
# Setting up the grid -- initial conditions
#------------------------------------------------------------------------------

#TEST CASE
"""
SP    = 5 
NF    = 3
MAXIT = 6
REP   = 50
"""
#------------------------------------------
# Things you should play with
#------------------------------------------
SP    = 50 		#path size
NF    = 100 	#number of foragers
MAXIT = 200		#how many time steps would you want to take?
REP   = 10 		#After how many time steps do the flowers that were
				#emptied, replenish?

GENERATE_PATH_EVOLUTION = 0

PATCH    = np.random.randint(2, size=(SP, SP)) 
FORAGERS = np.zeros((NF, 3))	

for BF in FORAGERS:
	BF[1:] = np.random.randint(SP, size=2)
	BF[0]  = 0.5

FORAGERS = np.dstack((np.zeros(np.shape(FORAGERS)), FORAGERS))

#------------------------------------------------------------------------------
# Evolving the system
#------------------------------------------------------------------------------

def UPDATE(FORAGERS, PATCH, IT):
	
	POS0 = FORAGERS[:, 1:, -1]
	

	if IT%REP == 0:
		POSM3 = FORAGERS[:, 1:, -REP]
		for _XY in POSM3:
			PATCH[int(_XY[0]), int(_XY[1])] = 1.0

	POS1 = np.random.randint(SP, size=(np.shape(FORAGERS)[0], 2))

	NFORAGERS = np.zeros((np.shape(FORAGERS)[0], 3))
	
	for _BTFY in range(np.shape(FORAGERS)[0]):
		DT = LA.norm(POS0[_BTFY] - POS1[_BTFY])*(0.1/SP**2.0)
		PE = PATCH[POS1[_BTFY, 0], POS1[_BTFY, 1]]
		
		if PE == 1.0:
			PC = 0.1
		else:
			PC = 0.0
		
		TC = PE - DT - PC

		NFORAGERS[_BTFY][0]  = FORAGERS[_BTFY][0][-1] + TC

		print "Forager: ", _BTFY
		print "Old Positon: ", POS0[_BTFY]
		print "New Positon: ", POS1[_BTFY]
		print "Resource at new Positon: ", PATCH[POS1[_BTFY, 0], POS1[_BTFY, 1]]
		print "Travel cost to new Positon: ", LA.norm(POS0[_BTFY] - POS1[_BTFY])*0.01
		print "Proceesing cost of nectar: ", PC
		print "Total Energy gained: ", TC
		print "Old Resource: ",  FORAGERS[_BTFY][0][-1]
		print "New Resource: ",  FORAGERS[_BTFY][0][-1] + TC
		print 40*'.'

		NFORAGERS[_BTFY, 1:] = POS1[_BTFY]
		PATCH[POS1[_BTFY, 0], POS1[_BTFY, 1]] = 0

	return NFORAGERS, PATCH

def ANALYZE_FORAGERS(FORAGERS):
	DATA = FORAGERS[:, 0, :]
	print "Foragers = %r \t Iterations = %r"%(DATA.shape[0], DATA.shape[1])
	EVOL = np.diff(DATA, axis = 1)
	EXIT_CANDIDATES = []

	for index, _forager in enumerate(EVOL):
		print _forager[-4:]
		if _forager[-1] < 0  and _forager[-2] < 0 and _forager[-3] < 0 and _forager[-4] < 0:
			print "Potential exit candidate: %r. Checking futher."%index
			if np.abs(_forager[-1]) >  np.abs(_forager[-2]) > np.abs(_forager[-3]) > _forager[-4]:
				print "Candidate confirmed. Forager %r will exit."%index
				EXIT_CANDIDATES.append(index)

	if np.size(np.array(EXIT_CANDIDATES)) > 0:
		return np.array(EXIT_CANDIDATES)
	else:
		return [0]

def ANALYZE_PATCH(PATCH):
	print "Average Patch Density:", np.mean(PATCH)
	return np.mean(PATCH)

def EVOLVE(FORAGERS, PATCH, ITMAX):

	print "\n"
	print 40*"-"
	print "Size of PATCH = ", SP
	print 40*"-"
	
	PATCH_DENSITY = []
	NUM_FORAGERS  = []
	ITERATION     = []
	
	# NUM_FORAGERS.append(FORAGERS.shape[0])
	# PATCH_DENSITY.append(ANALYZE_PATCH(PATCH))
	# ITERATION.append(0)

	for _iter in range(101, ITMAX + 100):
		print 75*"="
		print "Iteration : ", _iter-100

		print "Number of foragers = ", FORAGERS.shape[0]
		print 75*"="
		NFORAGERS, PATCH = UPDATE(FORAGERS, PATCH, _iter)
		if GENERATE_PATH_EVOLUTION == 1 and MAXIT < 50:
			plt.imshow(PATCH, cmap='viridis', interpolation='nearest')
			plt.savefig("../output/patch_evolution/patch_evolution_%r.pdf"%(_iter))

		FORAGERS = np.dstack((FORAGERS, NFORAGERS))

		if _iter-100 > 5:
			EXCAN = ANALYZE_FORAGERS(FORAGERS)
			if np.size(EXCAN) > 0:
				FORAGERS = np.delete(FORAGERS, EXCAN, axis=0)
				
				PATCH_DENSITY.append(ANALYZE_PATCH(PATCH))
				NUM_FORAGERS.append(FORAGERS.shape[0])
				ITERATION.append(_iter)
				
				if FORAGERS.shape[0] == 0:
					print 75*"="
					print "Exiting simulation. All foragers have left."		
					print 75*"="
					return np.array(NUM_FORAGERS),  np.array(PATCH_DENSITY), np.array(ITERATION)
	return FORAGERS


#------------------------------------------------------------------------------
# Call function
#------------------------------------------------------------------------------

num_foragers, patch_density, Iteration = EVOLVE(FORAGERS, PATCH, MAXIT)

#---------------------------
# Some basic visualization
#---------------------------

plt.figure(1)
plt.plot(NF - num_foragers, patch_density, 'r-.', linewidth=2.2)
plt.ylabel("Patch Density")
plt.xlabel("Number of foragers that have left")
plt.grid()
plt.savefig("./immediate/num_foragers_patch_density.pdf")
plt.close()

plt.figure(2)
plt.plot(Iteration, patch_density, 'b.-', linewidth=2.2)
plt.xlabel("Iteration")
plt.ylabel("Patch density")
plt.grid()
plt.savefig("./immediate/iteration_patch_density.pdf")
plt.close()

plt.figure(3)
plt.plot(Iteration, NF - num_foragers, 'r.-', linewidth=2.2)
plt.xlabel("Iteration")
plt.ylabel("Number of foragers that have left")
plt.grid()
plt.savefig("./immediate/iteration_num_foragers.pdf")
plt.close()

# %% [markdown]
"""
Bootstrapped distributions of fit parameters
============================================

This example shows how to generate probability density functions of
values for fit parameters using bootstrapping, showcased for 5pDEER.
"""

import numpy as np
import matplotlib.pyplot as plt
from deerlab import *

# %% [markdown]
# Generate data
# -------------

t = np.linspace(-0.1,6.5,100)      # time axis, us
r = np.linspace(1.5,6,100)         # distance axis, ns
param0 = [3, 0.3, 0.2, 3.5, 0.3, 0.65, 3.8, 0.2, 0.15] # parameters for three-Gaussian model
P = dd_gauss3(r,param0)         # model distance distribution
B = lambda t,lam: bg_hom3d(t,300,lam) # background decay
exparam = [0.6, 0.3, 0.1, 3.2]     # parameters for 5pDEER experiment
pathinfo = ex_5pdeer(exparam)   # pathways information

np.random.seed(0)
K = dipolarkernel(t,r,pathinfo,B)
Vexp = K@P + whitegaussnoise(t,0.01)

# %% [markdown]
# Analysis
# --------
#

def fit(V):

    # Set boundaries for the fit parameters (see DL_fitting_5pdeer.m)
    ex_lb   = [ 0,   0,   0,  max(t)/2-1] # lower bounds
    ex_ub   = [10,  10,  10,  max(t)/2+1] # upper bounds
    ex_par0 = [0.5, 0.5, 0.5, max(t)/2  ] # start values
    ub = [[],[],ex_ub]
    lb = [[],[],ex_lb]
    par0 = [[],[],ex_par0]
    # When running the fit, since we are only interested in the parameters we'll ignore
    # the rest (otherwise the ``Bfit``,``Pfit``,etc. could be bootstrapped as well) 
    # We need the Vfit to pass it to bootan as well, so we'll request that one too.
    Vfit,_,_,parfit,_,_,_ = fitsignal(V,t,r,'P',bg_hom3d,ex_5pdeer,par0,lb,ub,uqanalysis=False)

    # Unpack the parameters, since bootan() requires the outputs to be arrays
    # of numerical values, not structures
    exparam = parfit['ex']
    exparam[0:3] /=sum(exparam[0:3])
    bgparam = parfit['bg']

    return exparam,bgparam,Vfit


# Run the fit once as usual, to check that the model fits the data
exparfit,bgparfit,Vfit = fit(Vexp)

# Bootstrapping with 100 samples
bootuq = bootan(fit,Vexp,Vfit,50)

# Extract the uncertainty quantification for the parameters
exparam_uq = bootuq[0]
bgparam_uq = bootuq[1]

# Extract distributions for the experiment parameters
Lam0_values,Lam0_pdf = exparam_uq.pardist(0)
lam1_values,lam1_pdf = exparam_uq.pardist(1)
lam2_values,lam2_pdf = exparam_uq.pardist(2)
T02_values,T02_pdf     = exparam_uq.pardist(3)

# Extract distributions for the background parameters
conc_values,conc_pdf = bgparam_uq.pardist(0)

# %% [markdown]
# Plot
# --------

plt.figure(figsize=(15,11))

plt.subplot(321)
plt.fill_between(Lam0_values,Lam0_pdf,color='b',alpha=0.4)
plt.vlines(exparfit[0],0,max(Lam0_pdf),colors='k',linestyles='dashed',linewidth=2)
plt.vlines(exparam[0],0,max(Lam0_pdf),colors='r',linestyles='dashed',linewidth=2)
plt.xlabel('$\Lambda_0$')
plt.ylabel('PDF')
plt.legend(['Bootstrapped','Fit','Truth'])

plt.subplot(322)
plt.fill_between(lam1_values,lam1_pdf,color='b',alpha=0.4)
plt.vlines(exparfit[1],0,max(lam1_pdf),colors='k',linestyles='dashed',linewidth=2)
plt.vlines(exparam[1],0,max(lam1_pdf),colors='r',linestyles='dashed',linewidth=2)
plt.xlabel('$\lambda_1$')
plt.ylabel('PDF')

plt.subplot(323)
plt.fill_between(lam2_values,lam2_pdf,color='b',alpha=0.4)
plt.vlines(exparfit[2],0,max(lam2_pdf),colors='k',linestyles='dashed',linewidth=2)
plt.vlines(exparam[2],0,max(lam2_pdf),colors='r',linestyles='dashed',linewidth=2)
plt.xlabel('$\lambda_2$')
plt.ylabel('PDF')

plt.subplot(324)
plt.fill_between(T02_values,T02_pdf,color='b',alpha=0.4)
plt.vlines(exparfit[3],0,max(T02_pdf),colors='k',linestyles='dashed',linewidth=2)
plt.vlines(exparam[3],0,max(T02_pdf),colors='r',linestyles='dashed',linewidth=2)
plt.xlabel('$T_{0,2}$ [$\mu s$]')
plt.ylabel('PDF')

plt.subplot(325)
plt.fill_between(conc_values,conc_pdf,color='b',alpha=0.4)
plt.vlines(bgparfit[0],0,max(conc_pdf),colors='k',linestyles='dashed',linewidth=2)
plt.vlines(300,0,max(conc_pdf),colors='r',linestyles='dashed',linewidth=2)
plt.xlabel('Spin conc. [$\mu M$]')
plt.ylabel('PDF')


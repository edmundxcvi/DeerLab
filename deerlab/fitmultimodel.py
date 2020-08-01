# fitmultimodel.py - Multi-component distributions SNNLS fit function
# --------------------------------------------------------------------
# This file is a part of DeerLab. License is MIT (see LICENSE.md).
# Copyright(c) 2019-2020: Luis Fabregas, Stefan Stoll and other contributors.

import numpy as np
import copy
import deerlab as dl
from deerlab.utils import isempty, jacobianest, hccm, goodness_of_fit
from types import FunctionType

def fitmultimodel(V,Kmodel,r,model,maxModels,method='aic',lb=[],ub=[],lbK=[],ubK=[],
                 weights=1, normP = True, uqanalysis=True,**kwargs):
    """ Fits a multi-model parametric distance distribution model to a dipolar signal using separable 
    non-linear least-squares (SNLLS).

    Parameters
    ----------
    V : array_like or list of array_like
        Dipolar signal(s) to be fitted.
    Kmodel : callable or 2D-array_like
        Dipolar kernel model. If no kernel parameters must be fitted, it can be specified as a matrix array 
        (or a list thereof if multiple signals are globally fitted). 
        Otherwise, it is a callable function that accepts an array of kernel parameters and returns
        a kernel matrix array or a list thereof.
    r : array_like 
        Distance axis, in nanometers.
    model : callable 
        Basis component of the multi-component distance distribution. 
        Must be a callable DeerLab model function (e.g. dd_gauss or dd_rice).
    maxModels : scalar 
        Maximal number of components in the multi-component distance distribution.
    method : string
        Functional metric used for the selection of the optimal number of components:

        * ``'aic'``  Akaike information criterion
        * ``'aicc'`` corrected Akaike information criterion
        * ``'bic'``  Bayesian information criterion
        * ``'rmsd'`` Root-mean squared deviation
        The default is ``'aic'``.
        
    lb : array_like
        Lower bounds for the distribution basis model parameters. If not specified, parameters are unbounded.
    ub : array_like
        Upper bounds for the distribution basis model parameters. If not specified, parameters are unbounded.
    ubK : array_like
        Lower bounds for the kernel model parameters. If not specified, parameters are unbounded.
    ubK : array_like
        Upper bounds for the kernel model parameters. If not specified, parameters are unbounded.

    Returns
    -------
    Pfit : ndarray
        Fitted distance distribution with optimal number of components.
    parfit : list of ndarray
        Fitted model parameters. The different subsets can be accessed as follows:
        
        * ``parfit[0]`` - Array of fitted kernel parameters
        * ``parfit[1]`` - Array of fitted distance distribution components parameters
        * ``parfit[2]`` - Array of fitted components amplitudes

    Puq : :ref:`UncertQuant`
        Covariance-based uncertainty quantification of the fitted distance distribution
    paramuq : :ref:`UncertQuant`
        Covariance-based uncertainty quantification of the fitted parameters
    stats : dict
        Goodness of fit statistical estimators:

        * ``stats['chi2red']`` - Reduced \chi^2 test
        * ``stats['r2']`` - R^2 test
        * ``stats['rmsd']`` - Root-mean squared deviation (RMSD)
        * ``stats['aic']`` - Akaike information criterion
        * ``stats['aicc']`` - Corrected Akaike information criterion
        * ``stats['bic']`` - Bayesian information criterion

    Additional keyword arguments:
    -----------------------------
    weights : array_like 
        Array of weighting coefficients for the individual signals in global fitting, the default is all weighted equally.
    normP : boolean
        Enable/disable renormalization of the fitted distribution, by default it is enabled.
    uqanalysis : boolean
        Enable/disable the uncertainty quantification analysis, by default it is enabled.    

    Further keywords corresponding to the snlls() function can be passed as well.

    Notes
    -----
    This function takes advantage of the special structure of a multi-component model, i.e. the separability 
    of the component amplitudes as linear parameters from the rest of the non-linear parameters. This makes it
    suitable to be solved as a SNLLS problem.

    Examples
    --------
    A classical example involves the fit of a multi-Gauss distance distribution to a 4-pulse DEER dipolar signal. 
    Since the signal requires additional parameters  (e.g. modulation depth, background parameters,…) a kernel model 
    can be defined to account for these::
    
        def K4pdeer(Kpar):
            # Unpack parameters
            lam,conc = Kpar
            # Construct kernel
            K = dipolarkernel(t,r,lam,bg_hom3d(t,conc,lam))
            return K
        
        Pfit,parfit,Puq,paruq,stats = fitmultimodel(V,Kmodel,r,dd_model,Nmax,'aicc')


    If multiple signals are to be fitted globally the example abova can be easily adapted by passing multiple 
    signals to the fit function and by returning multiple kernels with the kernel model function::
    
        def K4pdeer(Kpar):
            # Unpack parameters
            lam,conc = Kpar
            # Construct kernels for both signals
            K1 = dipolarkernel(t1,r,lam,bg_hom3d(t1,conc,lam))
            K2 = dipolarkernel(t2,r,lam,bg_hom3d(t2,conc,lam))
            return K1,K2
        
        Pfit,parfit,Puq,paruq,stats = fitmultimodel([V1,V2],Kmodel,r,dd_model,Nmax,'aicc')


    """
    # Ensure that all arrays are numpy.nparray
    lb,ub,r = np.atleast_1d(lb,ub,r)
    
    # Parse multiple datsets and non-linear operators into a single concatenated vector/matrix
    V, Kmodel, weights, Vsubsets = dl.utils.parse_multidatasets(V, Kmodel, weights)

    # Check kernel model
    if type(Kmodel) is FunctionType:
        # If callable, determine how many parameters the model requires
        nKparam = 0
        notEnoughParam = True
        while notEnoughParam:
            nKparam = nKparam + 1
            try:
                Kmodel(np.random.uniform(size=nKparam))
                notEnoughParam = False
            except:
                notEnoughParam = True
    else:
        # If the kernel is just a matrix make it a callable without parameters
        nKparam = 0
        K = copy.deepcopy(Kmodel) # need a copy to avoid infite recursion on next step
        Kmodel = lambda _: K
    
    # Parse boundaries
    lb0, ub0 = np.atleast_1d(lb, ub)
    if len(lbK) is not nKparam or len(ubK) is not nKparam:
        raise ValueError('The upper/lower bounds of the kernel parameters must be ',nKparam,'-element arrays')

    # Extract information about the model
    info = model()
    nparam = len(info['Start'])
    if isempty(lb0):
        lb0 = info['Lower']
    if isempty(ub0):
        ub0 = info['Upper']
    paramnames = info['Parameters']

    areCenterDistances = [str in ['Center','Location'] for str in paramnames]
    if any(areCenterDistances):
        # If the center of the basis function is a parameter limit it 
        # to the distance axis range (stabilizes parameter search)
        ub0[areCenterDistances] = max(r)
        lb0[areCenterDistances] = min(r)

    # Ensure that all arrays are numpy.nparray
    lb0,ub0,lbK,ubK = np.atleast_1d(lb0,ub0,lbK,ubK)

    def nonlinmodel(par,Nmodels):
    #===============================================================================
        """
        Non-linear augmented kernel model
        ----------------------------------
        This function constructs the actual non-linear function which is 
        passed to the SNLLS problem. The full signal is obtained by multiplication
        of this matrix by a vector of amplitudes. 
        """
        # Get kernel with current non-linear parameters
        K = Kmodel(par[np.arange(0,nKparam)])
        paramsused = nKparam
        Knonlin = np.zeros((K.shape[0],Nmodels))
        for iModel in range(Nmodels):
            subset = np.arange(paramsused, paramsused+nparam)
            paramsused = paramsused + nparam
            # Get basis functions
            Pbasis = model(r,par[subset])
            # Combine all non-linear functions into one
            Knonlin[:,iModel] = K@Pbasis
        return Knonlin
    #===============================================================================

    def Pmodel(nlinpar,linpar):
    #===============================================================================
        """
        Multi-component distribution model
        ----------------------------------
        This function constructs the distance distribution from a set of
        non-linear and linear parameters given certain number of components and
        their basis function.
        """
        paramsused = nKparam
        Pfit = 0
        for amp in linpar:
            subset = np.arange(paramsused, paramsused+nparam)
            paramsused = paramsused + nparam
            # Add basis functions
            Pfit = Pfit + amp*model(r,nlinpar[subset])
        return Pfit
    #===============================================================================

    def logestimators(V,Vfit,plin,pnonlin,functionals):
    #===============================================================================
        """
            Log-Likelihood Estimators
        ---------------------------
        Computes the estimated likelihood of a multi-component model being the
        optimal choice.
        """
        if type(functionals) is not dict:
            functionals = {'rmsd':[],'aic':[],'aicc':[],'bic':[]}
        nParams = len(pnonlin) + len(plin)
        Q = nParams + 1
        N = len(V)
        SquaredSumRes = np.sum((V - Vfit)**2)
        logprob = weights*N*np.log(SquaredSumRes/N)
        # Compute the estimators
        rmsd = weights*np.sqrt(1/N*SquaredSumRes)
        aic = logprob + 2*Q
        aicc = logprob + 2*Q + 2*Q*(Q+1)/(N-Q-1)
        bic =  logprob + Q*np.log(N)

        # Append results to existing dictionary
        functionals['rmsd'].append(rmsd)
        functionals['aic'].append(aic)
        functionals['aicc'].append(aicc)
        functionals['bic'].append(bic)
        return functionals
    #===============================================================================

    # Pre-allocate containers
    Vfit,Pfit,plin_,pnonlin_,nlin_ub_,nlin_lb_,lin_ub_,lin_lb_ = ([] for _ in range(8))
    logest = []

    # Loop over number of components in model
    # =======================================
    for Nmodels in np.arange(1,maxModels+1):
        
        # Prepare non-linear model with N-components
        # ===========================================
        Knonlin = lambda par: nonlinmodel(par,Nmodels)
        
        # Box constraints for the model parameters (non-linear parameters)
        nlin_lb = np.matlib.repmat(lb0,1,Nmodels)
        nlin_ub = np.matlib.repmat(ub0,1,Nmodels)

        # Add the box constraints on the non-linear kernel parameters
        nlin_lb = np.concatenate((lbK, nlin_lb),axis=None)
        nlin_ub = np.concatenate((ubK, nlin_ub),axis=None)
        
        # Start values of non-linear parameters
        np.random.seed(1)
        par0 = np.random.uniform(size=(len(nlin_lb)),low=nlin_lb, high=nlin_ub)

        # Box constraints for the components amplitudes (linear parameters)
        lin_lb = np.ones(Nmodels)        
        lin_ub = np.full(Nmodels,np.inf)
        
        # Separable non-linear least-squares (SNLLS) fit
        scale = 1e2
        pnonlin,plin,_,stats = dl.snlls(V*scale,Knonlin,par0,nlin_lb,nlin_ub,lin_lb,lin_ub, penalty=False, uqanalysis=False,linTolFun=[], linMaxIter=[],**kwargs)
        plin = plin/scale

        # Store the fitted parameters
        pnonlin_.append(pnonlin)
        plin_.append(plin)

        # Get fitted kernel
        Kfit = nonlinmodel(pnonlin,Nmodels)
        
        # Get fitted signal
        Vfit.append(Kfit@plin)
        
        # Get fitted distribution
        Pfit.append(Pmodel(pnonlin,plin))

        # Likelihood estimators
        # =====================
        logest = logestimators(V,Vfit[Nmodels-1],plin,pnonlin,logest)

        # Store other parameters for later
        nlin_ub_.append(nlin_ub)
        nlin_lb_.append(nlin_lb)   
        lin_ub_.append(lin_ub)
        lin_lb_.append(lin_lb)

    # Select the optimal model
    # ========================
    Peval = Pfit
    fcnals = logest[method]
    idx = np.argmin(fcnals)
    Nopt = idx+1
    Pfit = Pfit[idx]
    Vfit = Vfit[idx]
    pnonlin = pnonlin_[idx]
    plin = plin_[idx]
    nlin_lb = nlin_lb_[idx]
    nlin_ub = nlin_ub_[idx]
    lin_lb = lin_lb_[idx]
    lin_ub = lin_ub_[idx]

    # Package the fitted parameters
    # =============================
    fitparam = [[],[],[]]
    fitparam[0] = pnonlin[0:nKparam] # Kernel parameters
    fitparam[1] = pnonlin[nKparam:nKparam+nparam] # Components parameters
    fitparam[2] = plin # Components amplitudes

    # Uncertainty quantification analysis (if requested)
    # ==================================================
    if uqanalysis:
        # Compute the residual vector
        Knonlin = lambda par: nonlinmodel(par,Nopt)
        res = weights*(Vfit - V)

        # Compute the Jacobian
        Jnonlin,_ = jacobianest(lambda p: weights*Knonlin(p)@plin, pnonlin)
        Jlin = weights*Knonlin(pnonlin)
        J = np.concatenate((Jnonlin, Jlin),1)
        
        # Estimate the heteroscedasticity-consistent covariance matrix
        covmatrix = hccm(J,res,'HC1')
        
        # Construct uncertainty quantification structure for fitted parameters
        paramuq = dl.UncertQuant('covariance',np.concatenate((pnonlin, plin)),covmatrix,np.concatenate((nlin_lb, lin_lb)),np.concatenate((nlin_ub, lin_ub)))
        
        P_subset = np.arange(0, nKparam+nparam*Nopt)
        amps_subset = np.arange(P_subset[-1]+1, P_subset[-1]+1+Nopt)
        Puq = paramuq.propagate(lambda p: Pmodel(p[P_subset],p[amps_subset]), np.zeros(len(r)))
    else: 
        Puq = []
        paramuq = []

    # Goodness of fit
    stats = []
    for subset in Vsubsets: 
        Ndof = len(V[subset]) - (nKparam + nparam + Nopt)
        stats.append(goodness_of_fit(V[subset],Vfit[subset],Ndof))
    if len(stats)==1: 
        stats = stats[0]

    # If requested re-normalize the distribution
    if normP:
        Pnorm = np.trapz(Pfit,r)
        Pfit = Pfit/Pnorm
        if uqanalysis:
            Puq_ = copy.deepcopy(Puq) # need a copy to avoid infite recursion on next step
            Puq.ci = lambda p: Puq_.ci(p)/Pnorm

    return Pfit, fitparam, Puq, paramuq, fcnals, Peval, stats
    # =========================================================================
.. _changelog:


--------------
Release Notes
--------------


.. rubric:: Legend

- |feature| : Features something new which could not be done before
- |efficiency| : A change which improves the performance or memory usage.
- |enhancement| : An improvement to a previously existing feature.
- |fix| : Something which was not working as expected or leading to errors has been fixed.
- |api| : This will require changes in your scripts or code.

Release v0.14.0 - April 2022
---------------------------------

.. rubric:: Overall changes

- |feature| |api| Complete overhaul of the DeerLab modelling and fitting interface. Check the new documentation for help and details. (:pr:`218`, :pr:`223`, :pr:`228`, :pr:`237`, :pr:`225`, :pr:`243`). 
  
  * A new modelling system has been introduced. DeerLab main interface runs on a new ``Model`` object class. Models implement and provide the distinction between linear and non-linear parameters.
  * Model parameters are no longer (solely) identified by their indexing inside a parameter vector, but are referenced by name. This avoids the need for a user to recall the ordering of the parameters. This is now all handled internally. For example, before ``paramA = parameters[idxA]`` is now ``model.paramA``.   
  * Any model parameter is accessible from the model object and its boundaries, start values and other properties can be easily modified. For example, to change the lower boundary of a parameter: ``model.paramA.lb = 0``.  
  * A new general ``fit`` function that fits arbitrary ``Model`` objects to single or multiple datasets has been implemented. The function automatically handles the selection of solvers to optimally fit the data to the model. 
  * Implemented a new function ``link`` to link model parameters (setting equality constraints in models). 
  * Implemented a new function ``merge`` to create a model returning more than one response (allowing the creation of global models). 
  * Implemented a new function ``relate`` to define functional relationships between model parameters.
  * Implemented a new function ``lincombine`` to create a model whose response is a linear combination of the inputs' model responses. 
  * Model parameters can now be frozen (set to a constant value and ignored during optimization) in the ``Model`` object and on the back-end ``snlls`` solver. For examples, to fix a parameter to a certain value: ``model.paramA.freeze(0.5)``.
  * Arbitrary normalization conditions can be imposed to the linear parameters.
  * Bootstrapping can now be requested directly from the ``fit`` function via the ``bootstrap`` keyword argument. The function will then return the bootstrap uncertainty quantification of all model parameters and of the model's response instead of the covariance-based uncertainty.
  * Implemented a new function ``dipolarmodel``, which generates models based on the dipolar EPR multi-pathway theoretical model. 
  * Added new examples, adapted existing ones, and removed unneeded examples. 
  * Add many new tests and removed tests related to deprecated functionality. 
  * All the built-in parametric models are now pre-compiled ``Model`` objects instead of just functions.
  * The function ``fitmodel`` has been deprecated and removed. The original has been substituted (and greatly expanded) by the new    ``dipolarmodel`` and ``fit`` functions. 
  * The function ``fitmultimodel`` has been deprecated and removed. The original functionality can be easily scripted with the new modelling system. An example of has been added, describing how to script the same functionality. 

- |feature| Introduced the profile-likelihood methodology both for uncertainty quantification based on likelihood-confidence intervals, and for identifiability analysis (:pr:`222`).

  * Added a new function ``profile_analysis`` to calculate the objective function profiles from model object parameters.
  * Implemented a new uncertainty quantification ``UQResult`` object type ``'profile'`` for results obtained from profile_analysis.
- |feature| Implemented a system to specify arbitrary penalty functions to be included in the non-linear part of the objective function during optimization. The penalties can be custom-defined and constructed into a ``Penalty`` object that can be passed to the ``fit`` function. Outer optimization of the penalty weights can also be included based on certain information-based criteria (:pr:`197`, :pr:`218`, :pr:`225`). 

  * Implemented a new object ``Penalty`` that includes the penalty function, weight parameter (and its boundaries), and the selection functional for optimization.
  * Adds new outer optimization options for the penalty weights, based on hard-coded model selection functionals. For now, the ICC, AIC, AICc, and BIC functionals are available.
  * Implemented a new function ``dipolarpenalty`` that generates dipolar-EPR-specific penalties, e.g. to induce compactness and/or smoothness.
- |feature| Implemented masking of datasets during optimization (:pr:`250`).
- |feature| Added a ``verbose`` option to display progress of the fit routines (:pr:`250`).
- |feature| Added support for analyzing and fitting complex-valued models and data (:issue:`127`, :pr:`218`).
- |feature| Orientation selection in dipolar signals can now be simulated for arbitrary orientation weights distributions via the ``orisel`` keyword argument in the new ``dipolarmodel`` or the ``dipolarkernel`` functions (:pr:`183`, :pr:`203`). 
- |feature| Re-purposed the ``ex_`` models. Each of these function represents a specific dipolar EPR experiment. These now take the experimental time delays as input, and return a new ``ExperimentInfo`` object. This can be passed to ``dipolarmodel`` via the optional keyword argument ``experiment`` to refine the boundaries and start values of the dipolar pathway refocusing times and amplitudes based on the experimental setup (:pr:`225`). 
- |feature| Implemented masking of datasets during optimization (:pr:`250`).
- |enhancement| Overhaul of the DeerLab documentation website (:pr:`235`).

  * Full HTML/CSS overhaul. The new web design based on the PyData theme has a clearer design, with more readable pages and code blocks.
  * Deprecates the use of the RTD theme. This removes the hard constraint of using Sphinx 1.8.0. Now the documentation builds with the latest Sphinx release.
  * Add a user-guide for the new modelling and fitting system.
  * Re-organize all of the website content.
  * Improved the dipolar EPR starting guide, and adapted it to the new system.
  * Fixed some minor errors in the examples.
  * Redesigned all examples towards the use of actual experimental data files in BES3T format. Examples can now be taken and easily adapted by users to their experiment data files (:pr:`304`).
- |enhancement| Added the functionality to print a ``FitResult`` object to display a summary of the fit goodness-of-fit statistics and a table of all estimated parameters and their uncertainties (:pr:`234`). 
- |enhancement| Added a new keyword argument ``regparamrange`` to ``snlls`` and ``fit`` to specify the search range of the optimal regularization parameter (:pr:`225`).
- |enhancement| Noise levels of the datasets can be optionally specified in all functions taking datasets (:pr:`213`).
- |enhancement| Added the option to include or exclude the edges of vector in ``regoperator`` via a new keyword argument ``includeedges`` (:pr:`204`). The default for all functions in DeerLab has been set to ``includeedges=False`` (:issue:`205`, :pr:`230`).  
- |enhancement| Generalized the regularization operator. Related functions no longer take ``regorder`` (regularization operator order) as an argument. Instead they now take ``regop`` (the full regularization operator) as an argument (:pr:`216`).
- |enhancement| Generalized the regularized linear least-squares functionality. Now it can handle arbitrary bounds on linear parameters and adapts the linear LSQ solver back end accordingly (:pr:`216`).
- |efficiency| Improved performance of post-optimization model evaluation/propagation for large datasets (:issue:`200`, :pr:`238`).  
- |efficiency| Implemented (adaptable) memory limits for potentially memory-intense functions (:issue:`201`, :pr:`239`). 
- |api| The function ``correctscale`` has been deprecated (:pr:`293`). Its limited functionality is included in the now broader functionality provided by the new modelling and fitting system.
- |api| The functions ``fitregmodel`` and ``fitparamodel`` have been deprecated and their core functionality merged into ``snlls``. The ``snlls`` function now handles any kind of least-squares problem and automatically employs optimal combinations of solvers to find the solution to the problems (:pr:`218`). 
- |api| Renamed the function ``bootan`` to ``bootstrap_analysis`` (:pr:`227`).
- |api| Deprecated TV and Huber regularization. Accordingly the keyword arguments ``regtype``, ``huberparameter`` have been removed throughout (:pr:`216`).
- |api| Deprecated the ``nnlsbpp`` NNLS solver (:pr:`231`).
- |api| Deprecated the ``regparamrange`` function (:pr:`232`). It depended on home-written code for the GSVD, which (as shown in previous issues) was prone to LAPACK backend problems and other bugs. This function was still a derelict from DeerAnalysis methodology.
- |api| The function ``time2dist`` has been renamed to ``distancerange`` (:issue:`273`, :pr:`274`).- |api| The function ``time2dist`` has been renamed to ``distancerange`` (:issue:`273`, :pr:`274`).
- |api| The convergence control arguments of the fit functions have now been renamed for consistency with the ``least_squares`` function of the SciPy package (:pr:`296`).
- |api| Changed the name of the parameter ``width`` to ``std`` in the ``dd_gauss``, ``dd_gauss2``, ``dd_gauss3``, and ``dd_skewgauss``models (:issue:`278`, :pr:`280`).
- |fix| When using the ``multistart`` keyword argument, no longer includes the parameter boundaries in the set of multiple start values (:pr:`218`). 
- |fix| Fixed error (manifesting as ``nan`` values in the confidence intervals) caused by a division-by-zero in the covariance matrix estimation (:pr:`218`).
- |fix| Fix encoding error during installation (:pr:`252`). This error could disrupt the installation in OS with default encoding different from CP-1252.
- |fix| Implement a new function to ensure that estimated Jacobians are positive semi-definite matrices. This fixes the appearance of warnings and bugs when calculating confidence intervals (:pr:`216`).
- |fix| Corrected the scale invariance behavior of the covariance-based uncertainty estimates (:pr:`218`).
- |fix| Fixed multiple ``numpy.VisibleDeprecationWarning`` and ``RunTime`` warnings (:issue:`207`, :pr:`212`).
- |fix| Corrected the math in the documentation of some distance distribution models (:pr:`215`).
- |fix| Corrected the behavior of dataset weights. These are no longer normalized at runtime and kept as specified by the users (:issue:`248`, :pr:`250`).
- |fix| While testing, now skips a unit test if an error with the Tk backend of Matplotlib occurs (:pr:`211`).
- |fix| Fix multiple bugs and errors related to the new modelling and fitting system (:pr:`226`, :issue:`233`, :pr:`235`, :issue:`241`, :pr:`242`, :issue:`244`, :pr:`245`, :pr:`246`, :pr:`249`).
- |fix| Correct behavior of multistart optimization for one-sided parameter boundaries (:pr:`252`).
- |fix| Fix bug when globally fitting multiple datasets. The global weights were not being manipulated correctly in the estimation of the linear parameters leading to incorrect results (:pr:`302`)

.. rubric:: ``bootstrap_analysis``
- |efficiency| Added a new keyword argument ``memorylimit`` to specify the maximal memory used by the bootstrap analysis (by default 8GB). If the total analysis is expected to exceed the memory limit, the function will abort the execution (:issue:`200`, :pr:`238`).

.. rubric:: ``dipolarkernel``
- |feature| Added a new option `complex` to request the complex-valued dipolar kernel to simulate the out-of-phase contributions to the dipolar signals (:pr:`258`).
- |efficiency| Added a new keyword argument ``memorylimit`` to specify the maximal memory used by the dipolar kernel (by default 8GB). If the dipolar kernel is expected to exceed the memory limit, the function will abort the execution (:issue:`200`, :pr:`238`).
- |fix| Prompts error if wrong method is selected when specifying a limited excitation bandwidth (:issue:`181`, :pr:`183`). 

.. rubric:: ``bg_models``
- |feature| Implemented the time-dependent phase shifts for all the built-in physical background models, namely ``bg_hon3d_phase``, ``bg_hom3dex_phase``, and ``bg_homfractal_phase`` (:pr:`258`).   
- |enhancement| Changed the implementation of ``bg_hom3dex`` (:pr:`258`). This avoids the use of tabulated pre-calculated values. Accordingly the utility functions ``calculate_exvolume_redfactor`` and ``load_exvolume_redfactor`` have been removed.
- |fix| Improved the implementation and behavior of the ``bg_homfractal`` model (:pr:`258`).

.. rubric:: ``diststats``
- |fix| Fixed the behavior when dealing with distributions with arbitrary integral values

.. rubric:: ``selregparam``
- |enhancement| Implemented a general LSQ solver as backend to adapt to different regularized optimization problem structures.
- |enhancement| Generalized the linear least-squares solver. (:pr:`216`).
- |enhancement| In the ``brent`` mode, the search range is no longer selected from the min/max of ``regparamrange`` output, but from a new keyword argument ``searchrange`` set by default to ``[1e-8,1e2]``. The default values were chosen as the statistical means of Monte-Carlo simulations of the min/max values of ``regparamrange``'s output for typical 4-pulse DEER kernels (:pr:`232`).
- |enhancement|  In the ``grid`` mode, the grid-values are passed by the pre-existing keyword argument ``candidates``. By default, if not specified, a grid will be generated from the ``searchrange`` argument (:pr:`232`).

.. rubric:: ``UQResult``
- |fix| Ensures non-negativity of estimated parameter uncertainty probability density functions.
- |enhancement| Improve the behavior of ``UQresult.propagate()`` for bootstrapped uncertainty results. Now, instead of propagating bootstrapped uncertainty via the estimated covariance matrix, the uncertainty is propagated by bootstrapping from the bootstrapped uncertainty distributions (:pr:`218`). 
- |fix| Fix behavior of the bootstrap median (:pr:`254`).
- |fix| Suppress multiple ``DeprecationWarning`` warnings during uncertainty calculations (:pr:`255`).
- |fix| Fix error prompt when requesting private methods such as ``__deepcopy__`` (:issue:`301`, :pr:`303`).

.. rubric:: ``correctphase``
- |fix| Implement a fully vectorized analytical solution, resulting in a 30-150x speedup (:pr:`256`, :pr:`279`). 
- |api| Eliminate the ``phase='posrealint'`` and ``phase='negrealint'`` options (:pr:`279`).

.. rubric:: ``deerload``
- |fix| Raise warning instead of exception when parsing lines without key-value pairs (:pr:`256`). This avoid errors when trying to load BES3T files with PulseSPEL scripts edited in different OS systems.

.. rubric:: ``whitegaussnoise``
- |api| Renamed the argument ``level`` to ``std`` for clarity (:pr:`276`).
- |api| Make the argument ``std`` a required positional argument and no longer provide a default value (:pr:`276`).

Release v0.13.2 - July 2021
---------------------------------

.. rubric:: Overall changes

- |fix| Fixed an error appearing during installation in Windows systems. If during installation a  ``python`` executable alias was not created, the call to the ``pipwin`` manager returned an error and the installation failed to download and install Numpy, SciPy and CVXOpt (:pr:`187`).
- |fix| Fixed the rendering of certain code-blocks in the documentation examples which were appearing as plain text (:issue:`179`, :pr:`184`). 
- |fix| Fixed the execution and rendering of the model examples in the documentation (:issue:`189`, :pr:`190`). 
- |fix| Fixed a bug in ``snlls`` where one of the linear least-squares solvers can return results that violate the boundary conditions due to float-point round-off errors (:issue:`177`, :pr:`188`).


Release v0.13.1 - May 2021
---------------------------------

.. rubric:: Overall changes

- |fix| Fixed the behavior of global weights throughout DeerLab fit functions. The keyword argument ``weights`` was not having any or the expected effect in the results in some fit functions. Also fixes the behavior of built-in plots for global fits (:issue:`168`, :pr:`171`). 
- |enhancement| Optimize default weights in global fitting according to the datasets noise levels (:issue:`169`, :pr:`174`).
- |fix| Fixed a bug in ``snlls`` that was causing the confidence intervals in ``snlls``, ``fitmodel`` and ``fitmultimodel`` to vanish for large signal scales (:issue:`165`, :pr:`166`). 

.. rubric:: ``deerload`` 

- |fix| Corrected a bug that happened in certain BES3T Bruker spectrometer files, when there are entries under the ``MANIPULATION HISTORY LAYER`` section at the end of the descriptor file. Also fixed the reading of ``.XGF`` partner files (:pr:`164`). 

.. rubric:: ``snlls``

- |enhancement| The keyword argument ``extrapenalty`` now requires a function that takes both non-linear and linear parameters. Corrected the name of the keyword in the documentation (:pr:`175`). 

.. rubric:: ``fitparamodel``

- |fix| Fixed the scaling of the output ``FitResult.model`` and ``FitResult.modelUncert`` (:pr:`173`).

.. rubric:: ``ex_pseudotitration_parameter_free``:

- |fix| Removed ``Ctot`` from second order term in the ``chemicalequalibrium`` polynomial (:pr:`163`).

---------------------------------

Release v0.13.0 - April 2021
---------------------------------

.. rubric:: Overall changes

- |feature| DeerLab is now distributed via the Anaconda repository and can be installed with the ``conda`` package manager (:issue:`12`, :pr:`157`). The installation instructions have been expanded to describe the Anaconda installation (:pr:`155`).
- |feature| DeerLab now supports Python 3.9.
- |enhancement| The function ``fitsignal`` has been re-named to ``fitmodel`` for correctness and consistency with other functions (:pr:`102`).
- |feature| Added new experiment models for RIDME on systems with one to seven harmonic pathways (S=1/2 to S=7/2) to include all higher harmonics (overtones) (:pr:`79`). 
- |enhancement| Bootstrapping is now embedded into ``fitmodel`` to automatically bootstrap all output quantities without the need to write additional script lines (:issue:`55`). In ``fitmodel`` a new option ``uq`` allows to switch between covariance or bootstrapping uncertainty quantification (:pr:`88`). 
- |feature| The function ``fitmodel`` now returns ``Vmod`` and ``Vunmod``, the modulated and unmodulated contributions to the fitted dipolar signal, respectively, along their uncertainties as additional outputs (:pr:`78`).
- |feature| Implemented several initialization strategies in ``fitmultimodel`` for multi-model components (:pr:`67`). Three different new strategies ``'spread'``, ``'split'`` and ``'merge'`` will initialize the parameter values of the N-component fit based on the results of the N-1/N+1 component fit to improve quality of results and speed.  
- |feature| Added contribution guidelines to the documentation and automated list of DeerLab contributors. 
- |feature| The function ``snlls`` now accepts additional custom penalties to include in the optimization (:issue:`76`, :pr:`112`).
- |feature| All fit functions now return the fit of the data along its uncertainty automatically as part of the ``FitResult`` object(:issue:`130`, :pr:`134`).
- |feature| Implemented a new method ``UQResult.join()`` to merge multiple uncertainty quantification objects (:pr:`154`). This permits error propagation from multiple uncertainty sources to a common function.
- |efficiency| The performance of all fit functions has been considerably accelerated by removing call overheads in built-in DeerLab models (:issue:`100`, :pr:`101`, :pr:`143`).
- |fix| Improved robustness of the installation from PyPI (:pr:`65`):
- |fix| The installer no longer assumes the alias ``pip`` to be setup on the system. 
- |fix| The installation will now handle cases when system-wide privileges are not available (:issue:`52`).
- |fix| Improved robustness of the installation in Windows systems to avoid missing DLL errors (:issue:`64`).
- |fix| The installer will now get the latest Numpy/Scipy releases in Windows systems available at the [Gohlke repository](https://www.lfd.uci.edu/~gohlke/pythonlibs/). 
- |fix| Adapted piece of code leading to a ``VisibleDeprecationWarning`` visible during execution of certain DeerLab functions.
- |enhancement| Improved interface of built-in plots in ``FitResult.plot()``. The method now returns a Matplotlib figure object (``matplotlib.figure.Figure``) instead of an axes object (``matplotlib.axes._subplots.AxesSubplot``) which can be modified more freely to adjust graphical elements (:issue:`85`). The method now takes an optional keyword ``FitResult.plot(show=True\False)`` to enable/disable rendering of the graphics upon calling the method (:pr:`87`).
- |fix| The fit objective values returned in ``FitResult.cost`` are now correct (previous versions had an erroneous 1/2 factor) (:issue:`80`). The value is now returned as a scalar value instead of a single-element list (:issue:`81`).
- |enhancement| Removed the re-normalization conventions ``K(t=0,r)=1`` and ``B(t=0)=1`` and associated options ``renormalize`` and ``renormpaths`` in the ``dipolarkernel`` and ``dipolarbackground`` functions (:pr:`99`) to avoid identifiability issues between dipolar pathway amplitudes and signal scales during fitting (:issue:`76`). 
- |enhancement| The fit convergence criteria ``tol`` (objective function tolerance) and ``maxiter`` (iteration limit) are now exposed as keyword argument in all fit functions (:issue:`111`, :pr:`112`). 
- |enhancement| Multiple improvements and corrections to the documentation (:pr:`95`, :pr:`96`, :pr:`104`, :pr:`106`, :pr:`107`, :pr:`115`, :pr:`122`)
- |fix| Corrections in the metadata of multiple ``dd_models``. The key ``Parameters`` of some models contained the wrong names.
- |enhancement| The metadata of the built-in models is now accessible and manipulable via function attributes (e.g. ``dd_gauss.parameters``) rather than trought a returned dictionary (e.g. ``dd_gauss()['Parameters']``) (:pr:`143`).
- |enhancement| The keyword argument to request uncertainty quantification has been unified across all fitting functions. It is now ``uq`` (:pr:`120`).
- |api| The ``UncertQuant`` class has been renamed into ``UQResult`` (:pr:`123`).
- |enhancement| Uncertainty quantification is now tested numerically against an external package (``lmfit``) to ensue quality and accuracy(:pr:`121`).
- |enhancement| Expanded the collection of examples in the documentation, and improved existing ones (:pr:`144`, :pr:`148`, :pr:`153`).

.. rubric:: ``deerload`` 

- |fix| Fixed behavior of the function when loading certain 2D-datasets in the BES3T format (:issue:`82`, :pr:`83`).
- |fix| In 2D-datasets, the abscissas are now returned as a list of abscissas instead of a single 2D-matrix (:pr:`83`). 

.. rubric:: ``fitmodel``

- |fix| Corrected the scaling behaviour of all outputs related to components of the dipolar signal to match the scaling of the original experimental data (:pr:`78`). 
- |enhancement| The built-in plot method ``FitResult.plot()`` now plots the unmodulated component fit as well with its uncertainty (:pr:`78`).
- |enhancement| When plotting bootstrapped results with ``FitResult.plot()``, the fit is substituted with the median of the bootstrapped distribution (:pr:`148`).
- |enhancement| Extended information included in the verbose summary (:pr:`78`). 
- |enhancement| Simplified the interface for defining initial values and boundaries of parameters in ``fitsignal`` (:pr:`71`). Now instead of defining, e.g., ``fitsignal(..., lb = [[],[50],[0.2, 0.5]])`` one can define the individual vales/boundaries ``fitsignal(..., bg_lb = 50, ex_lb = [0.2,0.5])`` by using the new keywords. 
- |api| Removed the keyword argument ``uqanalysis=True/False``. The uncertainty quantification can now be disabled via the new keyword ``uq=None`` (:pr:`98`).
- |fix| Corrected the behaviour of built-in start values when manually specifying boundaries (:pr:`73`). If the built-in start values are outside of the user-specified boundaries the program will now automatically set the start values in the middle of the boundaries to avoid errors (:issue:`72`)).
- |enhancement| Implemented the constraint ``Lam0+sum(lam)<=1`` to ensure the structural-identifiability of ``Lam0`` and ``V0`` during SNLLS optimization of experiment models with more than one modulated dipolar pathway (i.e. does not affect ``ex_4pdeer``) (:issue:`76`, :pr:`108`).
- |enhancement| The function now accepts any sequence input (lists, arrays, tuples, etc.) instead of just lists (:pr:`152`). 
- |api| Removed the optional keyword argument ``regtype`` (:pr:`137`).
- |fix| Fixed a bug in the scaling of the distance distribution uncertainty quantification (:pr:`148`).

.. rubric:: ``fitregmodel``

- |fix| Corrected the behaviour of the uncertainty quantification when disabling the non-negativity constraint (:pr:`121`).

.. rubric:: ``fitparamodel`` 

- |fix| Made ``par0`` a positional argument instead of an optional keyword (:issue:`70`). to avoid errors when not defined (:issue:`69`).
- |api| Keyword argument ``rescale`` has been renamed to ``fitscale`` (:issue:`128`, pr:`129`).

.. rubric:: ``snlls``

- |fix| Corrected bug that was leading to the smoothness penalty being accounted for twice in the least-squares residual during optimization (:issue:`103`).
- |enhancement| Now returns the uncertainty quantification of linear and nonlinear parts as separate objects ``nonlinUncert`` and ``linUncert`` (:pr:`108`).
- |enhancement| Improved the covariance-based uncertainty analysis by including correlations between linear and non-linear parameters(:pr:`108`).
- |fix| Improved the behavior of signal scale determination (:pr:`108`).
- |fix| Enabled prescaling of the data to avoid scaling issues during uncertainty quantification (:issue:`132`, :pr:`133`).
- |fix| Corrected the behaviour of the uncertainty quantification when disabling the regularization penalty (:pr:`121`).

.. rubric:: ``diststats`` 

- |fix| Now compatible with non-uniformly defined distance distributions (:issue:`92`, :pr:`94`)). 
- |fix| Added internal validation step to avoid non-sensical results when confounding the syntax (:pr:`91`).

.. rubric:: ``dipolarkernel`` 

- |enhancement| Now allows defining pathways without unmodulated components.
- |fix| All optional keyword arguments can only be passed as named and not positional arguments (:pr:`138`)). 
- |api| The keyword ``pathways`` now only takes lists of pathways and not modulation depth parameters. A new separate keyword ``mod`` takes the modulation depth parameter for the simplified 4-pulse DEER kernel (:issue:`118`, :pr:`138`).
- |api| Renamed the background argument keyword ``B`` into ``bg`` (:pr:`138`).

.. rubric:: ``regparamrange``

- |fix| Implemented new CSD algorithm to avoid LAPACK library crashes encountered when using multiple DeerLab functions calling ``regparamrange`` internally (:pr:`68`).

.. rubric:: ``correctphase`` 

- |feature| Implement new keyword ``phase`` to select the criterion for optimizing the phase for correction (:issue:`114`, :pr:`131`).
- |api| Deprecated imaginary offset fitting (:pr:`131`). 
- |api| Deprecated manual phase correction. Manual correction can be done by the user and is now described in the beginner's guide (:pr:`131`). 

-------------------------------

Release v0.12.2 - October 2020
---------------------------------

.. rubric::  Overall changes

- |fix| Fit functions using the ``multistart`` option are now fully deterministic. The functions was using now a random generator to define the different start points, this is now deterministic. 

- |enhancement| Documentation UI has been re-designed for a more confortable reading. Minor errors and outdated information have been corrected throughout. Expanded reference documentation of several functions for better understanding. 


.. rubric:: ``regparamrange``

- |fix| The exception handling introduced in the previous release was still too specific. The function kept crashing due to SVD non-convergence errors during the GSVD. This has been fixed and the error will not lead to a crash. (:issue:`42`).   

.. rubric:: ``dd_skewgauss``

- |fix| Corrected an error in the implementation that was leading to wrong distributions (:issue:`61`).  

.. rubric:: ``dd_models``, ``ex_models``

-  |enhancement| Adapted numerical boundaries and start values of some built-in models to reflect better the physical reality. Afected models: ``dd_skewgauss``, ``dd_triangle``, ``dd_gengauss``, ``ex_5pdeer``, ``ex_ovl4pdeer``. 

-------------------------------

Release v0.12.1 - October 2020
---------------------------------

.. rubric::  Overall changes

- |efficiency| The calculation of the Jacobian for covariance-based uncertainty analysis has been simplified providing a significant boost in performance for all fit functions (:pr:`55`). 

- |fix| The Jacobian computation is more robust, now taking into consideration parameter boundaries (:pr:`58`). This solves errors such as the ones reported in (:issue:`50`).

- |fix| Broken examples in the documentation have been corrected (:pr:`57`).

- |enhancement| When requesting attributes or method of a UncertQuant object under disabled uncertainty analysis (``uqanalysis=False``) now it will prompt an explanatory error instead of just crashing (:issue:`56`). 

.. rubric:: ``fitsignal``

- |fix| Corrected the behaviour of the scaling output (``fit.scale``). Now all fitted dipolar signals (``fit.V``) have the same scaling as the input signal (:issue:`53`). 

.. rubric::  ``regparamrange``

- |fix| Relaxed the exception handling to catch errors occuring under certain conditions. The function seems to crash due to LAPACK or SVD non-convergence errors during the GSVD, now these are catched and the alpha-range is estimated using simple SVD as an approximation. This function might be deprecated in a future release (:issue:`42`).   

-------------------------------


Release v0.12.0 - October 2020
---------------------------------

.. rubric::  Overall changes

- |feature| Added new function ``diststats`` to calculate different statistical quantities of the distance distribution and their corresponding uncertainties (:pr:`37`).

- |feature| Introduced the option ``cores`` to ``bootan`` parallelize the bootstrapping using multiple CPUs (:pr:`35`). 

- |enhancement| The regularization operator matrices ``regoperator`` now include the edges of the distribution (:pr:`38`). Now the smoothness penalty is imposed on the distribution edges avoiding the accumulation of distribution mass at the edges of ``r``. 

- |enhancement| The interface for defining dipolar pathways has been simplified (:pr:`41`). For example, a signal with two dipolar pathways had to be defined as ``pathways = [[Lam0,np.nan], [lam1,T0]]``. Now the unmodulated pathway must be defined by its amplitude and does not accept the use of ``np.nan``, e.g. ``pathways = [Lam0, [lam1,T0]]``.

- |api| The project version control has been switched from the Git-flow to the GitHub-flow design. The default branch has been switched from ``master`` to ``main``, which is now always production-ready. All new contributions are merged into ``main`` exclusively by pull requests.

- |enhancement| The dependency on the ``lambda`` parameter has been removed from all phenomenological background models, and kept only for physical models (:pr:`43`). Their interface with ``dipolarbackground`` and ``dipolarkernel`` have been updated accordingly. 
 
.. rubric::  ``bg_homfractal`` 

-  |fix| Corrected behavior of the model. For ``d=3`` the model returned wrong values, and for ``d~=3`` the model resulted in an error.

.. rubric::  ``UncertQuant``

- |fix| Fixed bug when propagating uncertainty to scalar functions.

.. rubric::  ``deerload``

- |fix| Fixed UTF-8 error when loading certain spectrometer files in MacOS (:pr:`30`)

.. rubric::  ``fitsignal``

- |fix| The fitted scale of the signal is now properly calculated when fitting fully parametric signals. 
- |fix| Fixed error occuring when fitting a dipolar evolution function with a non-parametric distribution.

.. rubric::  ``selregparam``

- |fix| Fixed bug occuring when requesting the ``lc`` or ``lr`` selection methods.

.. rubric::  ``regparamange``

- |fix| An error occuring at the BLAS/LAPLACK error ocurring under certain conditions in MacOS and Ubuntu is now handled to avoid a crash. 

-------------------------------


Release v0.11.0 - September 2020
---------------------------------

.. rubric::  Overall changes

* |enhancement| All Gauss models (``dd_gauss``,etc.) now use the standard deviation ``sigma`` instead of the FWHM as the width parameter for consistency with other method such as Rice distributions (:pr:`19`).

* |fix| All hard-wired random seeds have been removed. 

* |feature| A new method ``plot()`` has been added to the ``FitResult`` class returned by all fit functions. This will create a basic plot of the fit results (:pr:`7`).

.. rubric::  ``snlls``

- |api| Renamed option ``penalty`` as ``reg`` and improved its interface (:pr:`13`).
- |enhancement| The regularization parameter of the optimal solution is returned now (:pr:`20`).

.. rubric::  ``whitegaussnoise``

- |enhancement| Added a ``seed`` option to select static noise realizations.

.. rubric::  ``correctzerotime`` 

- |fix| Fixed bug when zero-time is at start/end of array (:pr:`24`).
- |fix| Function no longer rescales the experimental data passed on to the function. 

.. rubric::  ``fitsignal``  

- |enhancement| The regularization parameter of the optimal solution is returned now (:pr:`20`).
- |fix| Bug fixed when fitting dipolar evolution functions (no background and no experiment models) with a parametric distance distribution. 

.. rubric::  ``fitmultimodel``

- |enhancement| Start points are now spread over constrained parameter space grid instead of being randomble initiated(:pr:`22`).

.. rubric::  ``deerload`` 

- |fix| Now returns the time axis in microseconds instead of nanoseconds (:pr:`21`).
- |fix| The bug appearing when loading certain BES3T files has been fixed (:pr:`14`).

.. rubric::  ``fitregmodel``

- |enhancement| Now returns the fitted dipolar signal in the ``FitResult`` output

.. rubric::  ``correctscale``

- |fix| The parameter fit ranges have been adjusted.


-------------------------------

Release v0.10.0 - August 2020
-----------------------------

As of this version, DeerLab is based on Python in contrast to older versions based on MATLAB found [here](https://github.com/JeschkeLab/DeerLab-Matlab).

.. rubric:: Overall changes

- |api| The following functions have been deprecated due to limited usability or due to functionality overlap with other DeerLab functions: ``aptkernel``, ``backgroundstart``, ``fitbackground``, ``paramodel``, and ``time2freq``. 

- |feature| All fit functions now return a single ``FitResult`` output which will contain all results. 

- |feature| All functions are now compatible with non-uniformly increasing distance axes. 

- |feature| All fit functions are completely agnostic with respect of the abolute values of the signal amplitude. This is automatically fitted by all function and return as part of the results.

- |feature| Uncertainty quantification for all fit functions is returned as a ``UncertQuant`` object from which confidence intervals, parameter distributions, etc. can be generated generalizing the uncertainty interface for all DeerLab. Uncertainty can now be propagated to arbitrary functions.

.. rubric:: ``fitparamodel``

- |enhancement| The functionality has been streamlined. Function now fits arbitrary parametric models using non-linear leas-squares without consideration of whether it is a time-domain or distance-domain model. The models no longer need to take two inputs (axis+parameters) and now only tk the parameters as input. 

.. rubric:: ``fitregmodel``

- |fix| Goodness-of-fit estimators are now computed using the proper estimation the degrees of freedom.

.. rubric:: ``fitmultimodel``

- |fix| Added internal measures to avoid situations where one or several components are suppressed by fitting zero-amplitudes making the method more stable. 

.. rubric:: ``uqst``

- |fix| The uncertainty distributions of the parameters are now returned as properly normalized probability density functions.

.. rubric:: ``fftspec``

- |fix| Frequency axis construction has been corrected.

.. rubric:: ``regoperator``

- |feature| Now calculates the numerically exact finite-difference matrix using Fornberg's method.

.. rubric:: ``correctphase``

- |feature| Now can handle 2D-datasets.



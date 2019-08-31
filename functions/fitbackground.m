%
% FITBACKGROUND Fit the background function in a signal
%
%   [B,lambda,param] = FITBACKGROUND(V,t,@model)
%   Fits the background (B) and the modulation depth (lambda) to a
%   time-domain signal (V) and time-axis (t) based on a given time-domain
%   parametric model (@model). The fitted parameters of the model are
%   returned as a last output argument.
%
%   [B,lambda,param] = FITBACKGROUND(V,t,@model,tstart)
%   The time at which the background starts to be fitted can be passed as a
%   an additional argument. 
%   
%   [B,lambda,param] = FITBACKGROUND(V,t,@model,[tstart tend])
%   The start and end times of the fitting can be specified by passing a
%   two-element array as the argument. If tend is not specified, the end of
%   the signal is selected as the default.
%
%   [B,lambda,param] = FITBACKGROUND(...,'Property',Value)
%   Additional (optional) arguments can be passed as property-value pairs.
%
% The properties to be passed as options can be set in any order.
%
%   'LogFit' - Specifies whether to fit the log of the signal (default: false)
%
% Copyright(C) 2019  Luis Fabregas, DeerAnalysis2
%
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License 3.0 as published by
% the Free Software Foundation.

function [B,ModDepth,FitParam] = fitbackground(Data,t,BckgModel,FitDelimiter,varargin)


[LogFit,InitialGuess] = parseoptional({'LogFit','InitialGuess'},varargin);


if nargin<3
    error('Not enough input arguments.')
end

if nargin<4
    FitDelimiter = minmax(t);
elseif length(FitDelimiter) == 1
    FitDelimiter(2) = max(t);
elseif length(FitDelimiter) > 2
    error('The 4th argument cannot exceed two elements.')
end

if FitDelimiter(2)<FitDelimiter(1)
    error('The fit start time cannot exceed the fit end time.')
end

if ~isa(BckgModel,'function_handle')
   error('The background model must be a valid function handle.') 
end

if ~iscolumn(t)
    t = t.';
end

if isempty(LogFit)
   LogFit = false; 
end

DataIsColumn = iscolumn(Data);
if ~DataIsColumn
    Data = Data.';
end

validateattributes(FitDelimiter,{'numeric'},{'2d','nonempty'},mfilename,'FitDelimiter')
validateattributes(Data,{'numeric'},{'2d','nonempty'},mfilename,'Data')
validateattributes(t,{'numeric'},{'2d','nonempty','increasing'},mfilename,'t')

%--------------------------------------------------------------------------
%Memoization
%--------------------------------------------------------------------------

persistent cachedData
if isempty(cachedData)
    cachedData =  java.util.LinkedHashMap;
end
hashKey = datahash({Data,t,BckgModel(),FitDelimiter});
if cachedData.containsKey(hashKey)
    Output = cachedData.get(hashKey);
    [B,ModDepth,FitParam] = java2mat(Output);
    %Java does not recognize columns
    B = B(:);
    if DataIsColumn && ~iscolumn(B)
        B = B.';
    end
    return
end

%--------------------------------------------------------------------------
%--------------------------------------------------------------------------

%Find the position to limit fit
FitStartTime = FitDelimiter(1);
FitEndTime = FitDelimiter(2);
[~,FitStartPos] = min(abs(t - FitStartTime)); 
[~,FitEndPos] = min(abs(t - FitEndTime));

%Limit the time axis and the data to fit
Fitt = t(FitStartPos:FitEndPos);
FitData = Data(FitStartPos:FitEndPos);

%Use absolute time scale to ensure proper fitting of negative-time data
Fitt = abs(Fitt);

%Prepare minimization problem solver
solveropts = optimoptions(@lsqnonlin,'Algorithm','trust-region-reflective','Display','off',...
    'MaxIter',8000,'MaxFunEvals',8000,...
    'TolFun',1e-10,'DiffMinChange',1e-8,'DiffMaxChange',0.1);

%Construct cost functional for minimization
if LogFit
    CostFcn = @(param)(sqrt(1/2)*(log((1 - param(1) + eps)*BckgModel(Fitt,param(2:end))) - log(FitData)));
else
    CostFcn = @(param)(sqrt(1/2)*((1 - param(1))*BckgModel(Fitt,param(2:end)) - FitData));
end

%Initiallize StartParameters (1st element is modulation depth)
LowerBounds(1) = 0;
UpperBounds(1) = 1;

%Get information about the time-domain parametric model
Info = BckgModel();
Ranges =  [Info.parameters(:).range];
LowerBounds(2:1 + Info.nParam) = Ranges(1:2:end-1);
UpperBounds(2:1 + Info.nParam) = Ranges(2:2:end);
if ~isempty(InitialGuess)
    StartParameters = InitialGuess;
else
    StartParameters(1) = 0.5;
    StartParameters(2:1 + Info.nParam) =  [Info.parameters(:).default];
end

FitParam = lsqnonlin(CostFcn,StartParameters,LowerBounds,UpperBounds,solveropts);

%Get the fitted modulation depth
ModDepth = FitParam(1);

%Extrapolate fitted background to whole time axis
B = BckgModel(abs(t),FitParam(2:end));

%Ensure data is real
B = real(B);
if ~DataIsColumn
    B = B';
end

%Store output result in the cache
Output = {B,ModDepth,FitParam};
cachedData = addcache(cachedData,hashKey,Output);

end

% Load the Simulink model
model = 'faulttest';
load_system(model);

% Set the simulation parameters if needed
set_param(model, 'StopTime', '5');  % Example of setting stop time

% Run the simulation
simOut = sim(model);

% Extract data from simOut
% Assuming you have signals logged in simOut

% For example, if you have a signal logged as 'yout'
loggedData = simOut.get('yout');



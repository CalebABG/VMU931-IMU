delete(instrfindall);
close all;
clear all;
clc;


%% User defined variables
comPort = 'COM10';


%% VMU931
% Data
data.Timestamp  = 0;
data.AccelX     = [];
data.AccelY     = [];
data.AccelZ     = [];
data.GyroX      = [];
data.GyroY      = [];
data.GyroZ      = [];
data.CompassX   = [];
data.CompassY   = [];
data.CompassZ   = [];
data.q0         = [];
data.q1         = [];
data.q2         = [];
data.q3         = [];
data.EulerX     = [];
data.EulerY     = [];
data.EulerZ     = [];
data.Heading    = [];
dataArray       = data;

% Serial
vmu                         = serial(comPort);
vmu.ByteOrder               = 'bigEndian';
vmu.BytesAvailableFcnMode   = 'byte';
vmu.OutputBufferSize        = 4;
vmu.InputBufferSize         = 10000;
vmu.UserData                = dataArray;
vmu.BytesAvailableFcnCount  = 40;
vmu.BytesAvailableFcnMode   = 'byte';
vmu.BytesavailableFcn       = @vmuCallback;


%% Main loop
fopen(vmu);

while (1)
    % Use Ctrl + C to stop the infinite loop
    % Run the last section of the script manually (Ctrl + Enter)
    display(vmu.BytesAvailable);
    
end


%% ***RUN MANUALLY***
vmu.UserData(end) = [];
dataTable = struct2table(vmu.UserData);
fclose (vmu);

djb=table2array(dataTable(:,2:4))
plot(cell2mat(djb))










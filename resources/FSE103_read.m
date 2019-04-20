delete(instrfindall);
close all;
clear;
clc;

raw = uint8('r');
force =  uint8('f');


%% Setup variables
saveData = 1;               %% Save to file? (0 or 1)
dataType = force;     		%% Choose the data you want to receive (raw or force)
s = serial('COM4');         %% Pick the correct port ('COM#')
stopCount = 100;            %% You can either stop recording after a certain number of data,
stopTime = '04/19 16:10';   %% or at a specific time (you also need to change some comments below)

timestamp = [];
if (dataType == raw)
    raw1 = [];
    raw2 = [];
    raw3 = [];
elseif (dataType == force)
    forceX = [];
    forceY = [];
    forceZ = [];
else
    return;
end


%% Setup serial
s.ByteOrder = 'bigEndian';
s.BytesAvailableFcnMode = 'byte';
s.OutputBufferSize = 1;
fopen(s);


%% Request data type
fwrite(s, dataType);
pause(0.01);


%% Read from serial
i = 0;
    % Comment either one of the next two lines to choose how you want to stop recording.
% while ~isequal(datestr(now,'mm/DD HH:MM'),stopTime)
while (i < stopCount)

    i = i+1;
    wrongMessage = 0;
    
    %% First byte (0x0D)
    while (fread(s, 1, 'uint8') ~= hex2dec('0d'))
    end

    %% Size of message
    size = fread(s, 1, 'uint8');

    %% Type of message
    if (fread(s, 1, 'uint8') ~= dataType)
        display('Wrong type of message');
        fread(s, size-3, 'uint8');
        wrongMessage = 1;
    end

    %% Content of message
    if (~wrongMessage)
        timestamp = [timestamp; fread(s, 1, 'uint32')];
        if (dataType == raw) % RAW
            raw1 = [raw1; fread(s, 1, 'float')];
            raw2 = [raw2; fread(s, 1, 'float')];
            raw3 = [raw3; fread(s, 1, 'float')];
            
        elseif (dataType == force) % FORCE
            forceX = [forceX; fread(s, 1, 'float')];
            forceY = [forceY; fread(s, 1, 'float')];
            forceZ = [forceZ; fread(s, 1, 'float')];
			
        end
    end
    
    %% Last byte (0xFF)
    if (fread(s, 1, 'uint8') ~= hex2dec('ff') && ~wrongMessage)
        display('Wrong last byte');
        timestamp = timestamp(1:end-1);
        if (dataType == raw) % RAW
            raw1 = raw1(1:end-1);
            raw2 = raw2(1:end-1);
            raw3 = raw3(1:end-1);

        elseif (dataType == force) % FORCE
            forceX = forceX(1:end-1);
            forceY = forceY(1:end-1);
            forceZ = forceZ(1:end-1);
        
        end
    end
    
    %% You can do whatever you want in real time HERE.
	
	%%
    
end


%% Create table with data
if saveData
    if (dataType == raw) % RAW
        data = table(timestamp, raw1, raw2, raw3, 'VariableNames', {'time', 'raw1', 'raw2', 'raw3'});
        save(['FSE103_rawData_' datestr(datevec(now), 'yyyy-mm-dd_HH-MM')], 'data');
    elseif (dataType == force) % FORCE
        data = table(timestamp, forceX, forceY, forceZ, 'VariableNames', {'time', 'x', 'y', 'z'});
        save(['FSE103_forceData_' datestr(datevec(now), 'yyyy-mm-dd_HH-MM')], 'data');
    end
end


%% Clean up
fclose(s);
delete(s);
return;
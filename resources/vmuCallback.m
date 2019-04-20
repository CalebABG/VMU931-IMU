function vmuCallback( vmu, event )
%% Read from serial
% Start byte (0x01)
while (fread(vmu, 1, 'uint8') ~= hex2dec('01'))
end

% Size of message
size = fread(vmu, 1, 'uint8');

% Type of message
type = fread(vmu, 1, 'uint8');

% Content of message
timestamp = fread(vmu, 1, 'uint32');
if (type == uint8('a'))
    var1 = fread(vmu, 1, 'float');
    var2 = fread(vmu, 1, 'float');
    var3 = fread(vmu, 1, 'float');
    
elseif (type == uint8('g'))
    var1 = fread(vmu, 1, 'float');
    var2 = fread(vmu, 1, 'float');
    var3 = fread(vmu, 1, 'float');
    
elseif (type == uint8('c'))
    var1 = fread(vmu, 1, 'float');
    var2 = fread(vmu, 1, 'float');
    var3 = fread(vmu, 1, 'float');
    
elseif (type == uint8('q'))
    var1 = fread(vmu, 1, 'float');
    var2 = fread(vmu, 1, 'float');
    var3 = fread(vmu, 1, 'float');
    var4 = fread(vmu, 1, 'float');
    
elseif (type == uint8('e'))
    var1 = fread(vmu, 1, 'float');
    var2 = fread(vmu, 1, 'float');
    var3 = fread(vmu, 1, 'float');
    
elseif (type == uint8('h'))
    var1 = fread(vmu, 1, 'float');
    
else
    return;
end

% End byte (0x04)
if (fread(vmu, 1, 'uint8') ~= hex2dec('04'))
    return;
end


%% Fill user data
if (vmu.UserData(end).Timestamp ~= timestamp)
    vmu.UserData(end+1).Timestamp = timestamp;
end

if (type == uint8('a'))
    vmu.UserData(end).AccelX = var1;
    vmu.UserData(end).AccelY = var2;
    vmu.UserData(end).AccelZ = var3;

elseif (type == uint8('g'))
    vmu.UserData(end).GyroX = var1;
    vmu.UserData(end).GyroY = var2;
    vmu.UserData(end).GyroZ = var3;

elseif (type == uint8('c'))
    vmu.UserData(end).CompassX = var1;
    vmu.UserData(end).CompassY = var2;
    vmu.UserData(end).CompassZ = var3;

elseif (type == uint8('q'))
    vmu.UserData(end).q0 = var1;
    vmu.UserData(end).q1 = var2;
    vmu.UserData(end).q2 = var3;
    vmu.UserData(end).q3 = var4;

elseif (type == uint8('e'))
    vmu.UserData(end).EulerX = var1;
    vmu.UserData(end).EulerY = var2;
    vmu.UserData(end).EulerZ = var3;

elseif (type == uint8('h'))
    vmu.UserData(end).Heading = var1;
end


%% End of function
return;










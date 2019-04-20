import struct
import sys
from collections import namedtuple

"""
VMU931 Ref Guide: http://variense.com/Docs/VMU931/VMU931_UserGuide.pdf
Adapted from: https://github.com/JosephRedfern/PyVMU
"""


# VMU931 Terminal/Command Prompt instructions
IMU_Instructions = """\nCommands to send to the IMU:
Stop program:
    exit

Set Commands:
    set <'accel'|'mag'|'gyro'|'euler'|'quat'|'heading'> <on|off>
    res <'accel'|'gyro'> <'accel'=[2, 4, 8 or 18] | 'gyro'=[250, 500, 1000 or 2000]>

Get Commands:
    get <'status'>

Debug Commands:
    debug <'on'|'off'>
    errors <'on'|'off'>
"""


# Debug flag and Device Status obj
ShowErrors = True    # type: bool
Debug = False         # type: bool
Device_Status = None  # type: Status

# Mappings for commands to send to imu
GyroResolutionMapping = {250: 0, 500: 1, 1000: 2, 2000: 3}
AccelerometerResolutionMapping = {2: 4, 4: 5, 8: 6, 16: 7}

# Commands which can be sent to imu
ToggleCommandMap = {
    'accel': b'vara',
    'mag': b'varc',
    'gyro': b'varg',
    'euler': b'vare',
    'quat': b'varq',
    'heading': b'varh'
}

# Named tuples for getting data from imu
Accelerometer = namedtuple('Accelerometer', ["timestamp", "x", "y", "z"])
Magnetometer = namedtuple('Magnetometer', ['timestamp', 'x', 'y', 'z'])
Gyroscope = namedtuple('Gyroscope', ['timestamp', 'x', 'y', 'z'])
Euler = namedtuple('Euler', ['timestamp', 'x', 'y', 'z'])
Quaternion = namedtuple('Quaternion', ['timestamp', 'w', 'x', 'y', 'z'])
Heading = namedtuple('Heading', ['timestamp', 'h'])
Status = namedtuple('Status', ['magnetometer_enabled',
                               'gyroscope_enabled',
                               'accelerometer_enabled',
                               'gyroscope_resolution',
                               'accelerometer_resolution',
                               'low_output_rate',
                               'heading_streaming',
                               'euler_streaming',
                               'magnetometer_streaming',
                               'quaternions_streaming',
                               'gyroscope_streaming',
                               'accelerometer_streaming'])


# Message methods
def get_imu_status(serial_device):
    # We don't want to update the status again after sending the message, otherwise we'd be in an infinite loop.
    print("Getting IMU Status: Update Request")
    send_message(serial_device, message=b"vars", update_status=False)


def send_message(serial_device, message, update_status=True):
    serial_device.write(message)
    if update_status:
        get_imu_status(serial_device)


# Set methods
def set_imu_interface(serial_device, interface,  # type: str
                      state  # type: bool
                      ):

    interface = interface.lower()
    assert Device_Status is not None, "Device Status is not Set"
    assert interface in ToggleCommandMap.keys(), "Interface is invalid"

    if interface == 'accel':
        if Device_Status.accelerometer_streaming != state:
            toggle_imu_interface(serial_device, interface)

    elif interface == 'mag':
        if Device_Status.magnetometer_streaming != state:
            toggle_imu_interface(serial_device, interface)

    elif interface == 'gyro':
        if Device_Status.gyroscope_streaming != state:
            toggle_imu_interface(serial_device, interface)

    elif interface == 'euler':
        if Device_Status.euler_streaming != state:
            toggle_imu_interface(serial_device, interface)

    elif interface == 'quat':
        if Device_Status.quaternions_streaming != state:
            toggle_imu_interface(serial_device, interface)

    elif interface == 'heading':
        if Device_Status.heading_streaming != state:
            toggle_imu_interface(serial_device, interface)


def toggle_imu_interface(serial_device, interface  # type: str
                         ):
    interface = interface.lower()
    assert interface in ToggleCommandMap.keys(), "IMU interface invalid"

    send_message(serial_device, message=ToggleCommandMap[interface], update_status=False)


def can_set_imu_interface_resolution():
    assert Device_Status is not None, "Device Status is None"

    if Device_Status.quaternions_streaming == True or \
            Device_Status.euler_streaming == True or Device_Status.heading_streaming == True:
        return False
    else:
        return True


def set_gyro_resolution(serial_device, resolution):
    if can_set_imu_interface_resolution():
        print("Cannot set a custom resolution while Quaternions, Euler Angles or Heading is streaming data")
        return

    assert resolution in GyroResolutionMapping.keys(), \
        "Invalid gyroscope resolution, must be 250, 500, 1000 or 2000"

    if sys.version_info[0] < 3:
        command = b"var{}".format(GyroResolutionMapping[resolution])
    else:
        command = "var{}".format(GyroResolutionMapping[resolution]).encode()

    send_message(serial_device, command)


def set_accelerometer_resolution(serial_device, resolution):
    if not can_set_imu_interface_resolution():
        print("Cannot set a custom resolution while Quaternions, Euler Angles or Heading is streaming data")
        return

    assert resolution in AccelerometerResolutionMapping.keys(), \
        "Invalid accelerometer resolution, must be 2, 4, 8 or 18"

    if sys.version_info[0] < 3:
        command = b"var{}".format(AccelerometerResolutionMapping[resolution])
    else:
        command = "var{}".format(AccelerometerResolutionMapping[resolution]).encode()

    send_message(serial_device, command)


# Get methods
def get_status(data):
    status, res, low_output, data = struct.unpack(">3BI", data)

    mag_status = status & 0b00000100 != 0
    gyro_status = status & 0b00000010 != 0
    acc_status = status & 0b00000001 != 0

    gyro_res = None

    if res & 0b10000000 != 0:
        gyro_res = 2000
    elif res & 0b01000000 != 0:
        gyro_res = 1000
    elif res & 0b00100000 != 0:
        gyro_res = 500
    elif res & 0b00010000 != 0:
        gyro_res = 250

    acc_res = None

    if res & 0b00001000 != 0:
        acc_res = 16
    elif res & 0b000000100 != 0:
        acc_res = 8
    elif res & 0b00000010 != 0:
        acc_res = 4
    elif res & 0b00000001 != 0:
        acc_res = 2

    low_output_rate = low_output & 0b00000001 != 0

    heading_streaming = data & 0b01000000 != 0
    euler_streaming   = data & 0b00010000 != 0
    mag_streaming     = data & 0b00001000 != 0
    quat_streaming    = data & 0b00000100 != 0
    gyro_streaming    = data & 0b00000010 != 0
    acc_streaming     = data & 0b00000001 != 0

    return Status(
        magnetometer_enabled=mag_status,
        gyroscope_enabled=gyro_status,
        accelerometer_enabled=acc_status,
        gyroscope_resolution=gyro_res,
        accelerometer_resolution=acc_res,
        low_output_rate=low_output_rate,
        heading_streaming=heading_streaming,
        euler_streaming=euler_streaming,
        magnetometer_streaming=mag_streaming,
        quaternions_streaming=quat_streaming,
        gyroscope_streaming=gyro_streaming,
        accelerometer_streaming=acc_streaming
    )


def get_quat(data):
    ts, w, x, y, z = struct.unpack(">I4f", data)
    return Quaternion(timestamp=ts, w=w, x=x, y=y, z=z)


def get_euler(data):
    ts, x, y, z = struct.unpack(">I3f", data)
    return Euler(timestamp=ts, x=x, y=y, z=z)


def get_accel(data):
    ts, x, y, z = struct.unpack(">I3f", data)
    return Accelerometer(timestamp=ts, x=x, y=y, z=z)


def get_magnet(data):
    ts, x, y, z = struct.unpack(">I3f", data)
    return Magnetometer(timestamp=ts, x=x, y=y, z=z)


def get_gyro(data):
    ts, x, y, z = struct.unpack(">I3f", data)
    return Gyroscope(timestamp=ts, x=x, y=y, z=z)


def get_heading(data):
    ts, h = struct.unpack(">If", data)
    return Heading(timestamp=ts, h=h)


# Get data from IMU
def get_imu_data(serial_device):
    global Device_Status, Debug

    try:
        message_start = serial_device.read(1)
        message_start = struct.unpack("B", message_start)[0]

        if message_start == 0x01:
            # Unsure why we have to subtract 4bytes from this... but we do.
            message_size = serial_device.read(1)
            message_size = (struct.unpack("B", message_size)[0]) - 4

            message_type = serial_device.read(1)
            message_type = struct.unpack("c", message_type)[0]

            message_data = serial_device.read(message_size)

            message_end = serial_device.read(1)
            message_end = struct.unpack("B", message_end)[0]

            # If we have an invalid footer, skip this packet, otherwise continue.
            if message_end != 0x04:
                if ShowErrors:
                    print("Invalid footer, skipping packet: {}".format(message_end))
            else:
                data = None

                if message_type == b'e':
                    data = get_euler(message_data)

                elif message_type == b'q':
                    data = get_quat(message_data)

                elif message_type == b'h':
                    data = get_heading(message_data)

                elif message_type == b'a':
                    data = get_accel(message_data)

                elif message_type == b'g':
                    data = get_gyro(message_data)

                elif message_type == b'c':
                    data = get_magnet(message_data)

                elif message_type == b's':
                    data = get_status(message_data)
                    Device_Status = data

                else:
                    if ShowErrors:
                        print("Couldn't Get for {}".format(message_type))

                if Debug:
                    # print("Start Message")
                    # print("Message Type: {}".format(message_type))
                    # print("Message Text: {}".format(message_data))
                    print("Data: {}".format(data))
                    # print("Message Data: {}".format(data))
                    # print("End Message\n")

                return data

    except() as err:
        print(err)
        sys.exit(-1)

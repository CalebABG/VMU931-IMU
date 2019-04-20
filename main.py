#!/usr/bin/python

# Please note that this project relies on PySerial package
# Install PySerial if errors arise when trying to execute script

from __future__ import print_function
import serial
import vmu931_utils
import signal
import sys
import time

OLD_PYTHON = sys.version_info[0] < 3

running = True

imuPort = 'COM8'
execute_command = False
command = None

millis = lambda: int(time.time() * 1000.0)
time_now = millis()
time_duration = 200  # milliseconds

# serial.Serial(port='COM8', baudrate=115200, timeout=1, rtscts=1)
imuSerial = serial.Serial(port='COM8', baudrate=115200)


# Ctrl+C command handler
def imu_command_handler(signum, frame):
    global execute_command, command

    execute_command = True
    print(vmu931_utils.IMU_Instructions)

    if OLD_PYTHON:
        command = raw_input("Please Enter One of the Listed Commands: ")
    else:
        command = input("Please Enter One of the Listed Commands: ")

    if command is not None:
        command = command.lower()


# Handle ctrl+C
signal.signal(signal.SIGINT, imu_command_handler)

if __name__ == "__main__":
    if imuSerial.inWaiting():
        print("Device is in Waiting...\n Please Restart Program or Unplug IMU (Serial Device)")
    else:
        # Always request the status first, DON'T try to 'set' interfaces without first
        # getting the status from the IMU
        vmu931_utils.get_imu_status(imuSerial)

        print("Waiting to Get Device Status: ")

        while vmu931_utils.Device_Status is None:
            if millis() > time_now + time_duration:
                time_now = millis()
                print(".", end='')

            vmu931_utils.get_imu_data(imuSerial)
            if vmu931_utils.Device_Status is not None:
                break

        print("\n\nGot Device Status, Setting IMU Interface Values")
        vmu931_utils.set_imu_interface(imuSerial, 'accel', True)
        vmu931_utils.set_imu_interface(imuSerial, 'gyro', True)
        vmu931_utils.set_imu_interface(imuSerial, 'quat', False)
        vmu931_utils.set_imu_interface(imuSerial, 'mag', False)
        vmu931_utils.set_imu_interface(imuSerial, 'euler', False)
        print("IMU Interface Values Set, Grabbing IMU Data")

        while running:
            if execute_command == False:
                data = vmu931_utils.get_imu_data(imuSerial)
            else:
                if command == 'exit':
                    break

                elif command.startswith('set'):
                    args = command.split(" ")

                    if len(args) == 3:
                        vmu931_utils.set_imu_interface(imuSerial, args[1],
                                                       True if args[2].lower() == 'on' else False)

                elif command.startswith('res'):
                    args = command.split(" ")

                    if len(args) == 3:
                        if args[1] == 'accel':
                            vmu931_utils.set_accelerometer_resolution(imuSerial, int(args[2]))

                        elif args[1] == 'gyro':
                            vmu931_utils.set_gyro_resolution(imuSerial, int(args[2]))

                elif command.startswith('get'):
                    args = command.split(" ")

                    if len(args) == 2 and args[1].lower() == 'status':
                        vmu931_utils.get_imu_status(imuSerial)

                elif command.startswith('debug'):
                    args = command.split(" ")

                    if len(args) == 2:
                        vmu931_utils.Debug = True if args[1].lower() == 'on' else False

                elif command.startswith('errors'):
                    args = command.split(" ")

                    if len(args) == 2:
                        vmu931_utils.ShowErrors = True if args[1].lower() == 'on' else False

                execute_command = False

    print("\nProgram Finished :D")

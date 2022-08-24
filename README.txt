----ROBOT ARM INTERFACE INSTRUCTIONS----
This application is created for assistance in controlling the robot arm as part of the Biobox project.
--FEATURES--
-Allows opening, editing and saving of text files by using the 'Open File' and 'Save File' buttons

-Clear text by using the 'Clear' button

-Built-in compiler with simple programming language

-Compile & execute program files via arduino serial communication using the 'Execute' button

--INSTRUCTIONS--
Upon creating or opening a program file you can check the syntax is correct by using the 'Compile' button
(See Arm Programming Help).
If the syntax is recognised, the compiler will convert the program into serial-ready format and save to 'filename_cmd.txt'.
Do not try to compile or execute this new file as the compiler will not recognise it.

Once you are happy with your program you can execute your file. This will first compile the program, then send the _cmd.txt file
to the arduino via serial which will then interpret each command and execute it.
During this process a popup will show asking for you to wait until the arm has fully calibrated, which should take a few seconds.
Pressing 'cancel' will cancel the start of the execution of the program.

--BUGS--
Most bugs occur when the arduino has not been set up properly.

1. [Errno 2] could not open port portname: [Errno 2] No such file or directory: 'portname'
- The arduino is not connected to the specified port. Ensure the arduino is connected to this computer.
If the error still persists, open the arduino IDE and connect the arduino via tools->port. 
Port should be set to 'COM4' on windows or '/dev/cu.usbmodem1101' on mac (number suffixes will vary).
Copy this port name and replace the arduinoPort attribute with this value within RobotArmInterface.py.
Save the file and restart the editor.
(Note this error usually occurs each time the arduino is unplugged as the port tends to change)

2. [Errno 16] could not open port portname: [Errno 16] Resource busy: 'portname'
- The selected port is busy. This generally is due to the serial monitor being open when the python script is trying to access it.
Close the serial monitor and try again.

3. Unable to open/save file: 'NoneType' object has no attribute 'name'
- The open/save file dialog was cancelled meaning it was unable to open a file. This can be safely ignored.

4. Unrecognised command: command[...] See 'README.txt' for help
- Invalid syntax. See below to identify the problem.


----ARM PROGRAMMING HELP----
(not to be confused with the assembly language)

The robot arm can be programmed using a series of commands:
move(<servo_no>,<angle>);
do(<delay>);
bit(<pin_no>,<value>);
pump(<pump_no>,<steps>);
spin(<speed>);
irrd(<irrd_time>);

offset(<x>,<y>,<z>);
moveall(<x>,<y>,<z>,<tilt>);
shift(<x>,<y>,<z>,<tilt>);
dispense(<pump_no>,<vol>); ---not currently implemented
learnas(<position_name>);
takepose(<position_name>);

repeat(<i>,<command>);
macro(<filename>);

More details about each command are given below.

--MOVE COMMAND--
-Format-
move(<servo_no>,<angle>);
-Description-
Queues a servo to move to a desired angle in degrees, represented by # and ### respectively.
-Constraints-
Argument one accepts one parameter with range 0-4, which selects the desired servo.
Argument two accepts one three-digit parameter with range 000-180, which selects the desired angle.
Note angles must be given in three digit form e.g. an angle of 10 degrees would be represented as 010.

--DO COMMAND--
-Format-
do(<delay>);
-Description-
Executes all queued move commands simultaneously, followed by a time delay represented by #.
-Constraints-
do() accepts one integer parameter with range 0+, which selects the delay time in milliseconds before the next command is executed.
Note a minimum delay time is added to this value (~4 seconds) to allow the arm to move into its requested position before reading the next command.
i.e. 'do(0);' would actually execute a delay of 4050 milliseconds, 'do(100);' would wait 4150ms etc.
This delay is executed python-side.

--BIT COMMAND--
-Format-
bit(<pin_no>,<value>);
-Description-
Sets a pin on the arduino to a value of high/1 or low/0.
-Constraints-
bit() accepts two parameters.
Argument one accepts a positive integer value which refers to the pin number.
Argument two accepts one of HIGH, LOW, 1, 0, which sets the selected pin to a high or low voltage.
i.e. 'bit(3,HIGH);' or 'bit(3,1);' would set pin 3 to a high voltage.

--PUMP COMMAND--
-Format-
pump(<pump_no>,<steps>);
-Description-
Selects a syringe pump and moves it a given number of steps.
-Constraints-
pump() accepts two parameters.
Argument one accepts a positive integer value which selects the pump.
Argument two accepts a signed integer value which selects the number of steps the pump will move.
If argument two is negative the pump will move in the opposite direction.
i.e. 'pump(2,300);' will move pump 2 a total of 300 steps.

--SPIN COMMAND--
-Format-
spin(<speed>);
-Description-
Sets the speed of the wineglass motor.
-Constraints-
spin() accepts one positive integer parameter, which is translated to a voltage applied to the wineglass motor.
This controls the speed at which the wineglass spins.
i.e. 'spin(1000);' would set the wineglass to a speed of 1000 rpm.

--IRRADIATE COMMAND--
-Format-
irrd(<irrd_time>);
-Description-
Requests irradiation time from the ion beam.
-Constraints-
irrd() accepts one integer parameter, which is the irradiation time in minutes.
i.e. 'irrd(45);' would request a beam time of 45 minutes.

--OFFSET COMMAND--
-Format-
offset(<x>,<y>,<z>);
-Description-
Intended to be used at the start of a file. Adds an offset to all coordinates in case of misalignment.
-Constraints-
offset() accepts three signed parameters, for the x, y and z axes.
i.e. 'offset(0,-4,1.5);' would adjust all coordinates programmed in the file by -4cm in the y axis and 1.5cm in the z axis.

--MOVEALL COMMAND--
-Format-
moveall(<x>,<y>,<z>,<tilt>);
-Description-
Moves end effector of robot to the specified coordinates with a given tilt relative to the horizontal.
-Constraints-
moveall() accepts four signed float parameters, for the x, y and z axes, and a tilt angle.
i.e. 'moveall(0,24.5,0,90);' would move the end effector to coordinates (0,24.5,0) with an angle of 90 degrees to the horizontal.

--SHIFT COMMAND--
-Format-
shift(<x>,<y>,<z>,<tilt>);
-Description-
Shifts end effector of robot from current position by specified coordinates and a given angle.
-Constraints-
shift() accepts four signed float parameters, for the x, y and z axes, and a tilt angle.
i.e. 'shift(0,1.5,-1,0);' would move the end effector by 1.5cm in the y axis and -1cm in the z axis.

--DISPENSE COMMAND-- ******(NOT CURRENTLY IMPLEMENTED)******
-Format-
dispense(<pump_no>,<vol>);
-Description-
Dispenses a volume of sample from specified syringe pump. 
-Constraints-
dispense() accepts two parameters.
Argument one accepts an integer which selects the pump number.
Argument two accepts a float which selcts the volume to be dispensed from the selected pump.
i.e. 'dispense(2,5);' would dispense 5 microlitres from pump 2.

--LEARNAS COMMAND--
-Format-
learnas(<position_name>);
-Description-
Saves the robot's current end effector coordinates as a named position file to be reused later.
-Constraints-
learnas() accepts one string parameter of length 3+ which specifies the name to be designated to the end effector's position.
i.e. 'learnas(IRRD_POS);' would save the robot's position as IRRD_POS which can be referenced using takepose().

--TAKEPOSE COMMAND--
-Format-
takepose(<position_name>);
-Description-
Moves the end effector to the saved coordinates specified by <position_name>.
-Constraints-
takepose() accepts one string parameter of length 3+ which specifies the saved position for the robot to move to.
i.e. 'takepose(IRRD_POS);' would move the end effector to the previously saved IRRD_POS position.

--REPEAT COMMAND--
-Format-
repeat(<i>,<command>);
-Description-
Repeats the specified command a total of i times.
-Constraints-
repeat() accepts two parameters.
Argument one accepts a positive integer parameter which specifies the number of repetitions.
Argument two accepts string containing any command recognised in the syntax WITHOUT including the semicolon. THe second argument specifies the command to be repeated.
i.e. 'repeat(4,shift(0,0,1,0));' would repeat the command 'shift(0,0,1,0);' a total of 4 times.

--MACRO COMMAND--
-Format-
macro(<filename>);
-Description-
Executes an external command file stored in COMMANDS/MACROS under the name <filename>.txt
-Constraints-
macro() accepts one string parameter which must match the prefix of a file in ./COMMANDS/MACROS
All commands within this file must also accepted by syntax in order for execution to begin.
i.e. 'macro(TEST_MACRO);' would execute the file 'TEST_MACRO.txt'

--SYNTAX--
The syntax ignores whitespace and is not case sensitive. I recommend spacing out the commands with whitespace to make them more readable.
Commands must be separated by a semicolon.


If you are still having issues feel free to email me at joseph.percival-2@student.manchester.ac.uk.
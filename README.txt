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
Port should be set to 'COM4' on windows or '/dev/cu.usbmodem1101' on mac (numbers will vary).
Copy this port name and replace the arduinoPort attribute with this value within execute_code.py.
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

--MOVE COMMAND--
-Format-
s(#)a(###);
-Description-
Queues a servo to move to a desired angle in degrees, represented by s() and a() respectively.
-Constraints-
s() accepts one parameter with range 0-3, which selects the desired servo.
a() accepts one three-digit parameter with range 000-180, which selects the desired angle.
Note angles must be given in three digit form e.g. an angle of 10 degrees would be represented as 010.

--DO COMMAND--
-Format-
do(#);
-Description-
Executes all queued move commands simultaneously, followed by a time delay represented by #.
-Constraints-
do() accepts one integer parameter with range 0+, which selects the delay time in milliseconds before the next command is executed.
Note a minimum delay time is added to this value (~4 seconds) to allow the arm to move into its requested position before reading the next command.
i.e. 'do(0);' would actually execute a delay of 4050 milliseconds, 'do(100);' would wait 4150ms etc.
This delay is executed python-side.

--SYNTAX--
The syntax ignores whitespace and is not case sensitive. I recommend spacing out the commands with whitespace to make them more readable.
Commands must be separated by a semicolon.

If you are still having issues feel free to email me at joseph.percival-2@student.manchester.ac.uk.
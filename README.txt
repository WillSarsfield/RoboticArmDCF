----ARM PROGRAMMING HELP----

The robot arm can be programmed using a series of commands:

--MOVE COMMAND--
s(#)a(###);
-Description-
Queues a servo to move to a desired angle in degrees, represented by s() and a() respectively.
-Constraints-
s() accepts one parameter with range 0-3, which selects the desired servo.
a() accepts one three-digit parameter with range 000-180, which selects the desired angle.
Note angles must be given in three digit form e.g. an angle of 10 degrees would be represented as 010.

--DO COMMAND--
do(#);
-Description-
Executes all queued move commands simultaneously, followed by a time delay represented by do().
-Constraints-
do() accepts one parameter with range 0-inf, which selects the delay time in milliseconds before the next command is executed.
Note a minimum delay time is added to this value (~4 seconds) to allow the arm to move into its requested position before reading the next command.
i.e. do(0); would actually execute a delay of 4050 milliseconds.

The syntax ignores whitespace and is case insensitive.
Commands must be separated by a semicolon.
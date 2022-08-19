import re
import math

length = [10.5,9,5]
tilt = 90.0
x= 0.0
y = 24.5
x2 = (-(length[2]) * (math.cos((tilt*math.pi)/180))) + x
y2 = (-(length[2]) * (math.sin((tilt*math.pi)/180))) + y
print(x2,y2)
import re

class CommandInterpreter:
    max_angle=180           #refers to the maximum range of motion the servo has in degrees
    def __init__(self):
        pass

    def get_encoded_command(self,command=None,type=''):
        paramList=re.findall(r'\d+',command)
        # ...-ve        |0      | +ve...
        # do cmd        | move cmd              | bit cmd | pump cmd | spin cmd             |
        if type=='move':
            servo_num,angle=int(paramList[0]),int(paramList[1]) # gets all numbers from the move command
            encoded_val= servo_num*(max_angle+1)+angle      # maps (RxR)->R i.e. there is a unique positive encoded_val for each combination of servo&angle
            encoded_val+=1                                  # need to reserve zero for a separate commmand 
            # print(servo_num,angle,'encoded as',encoded_val)
        elif type=='do':
            waitTime=int(paramList[0]) # gets the wait time from the do command
            encoded_val= -waitTime-1                        #wait command is encoded as the negative numbers (1 is subtracted as the value 0 is already used)
            # print(waitTime,'encoded as',encoded_val)
        elif type=='bit':
            if len(paramList)==1:
                bit=paramList[0]
            elif len(paramList)==2:
                bit,value = int(paramList[0]),int(paramList[1])

            #convert bit and value here
        elif type=='pump':
            pump_num,steps=int(paramList[0]),int(paramList[1])
        elif type=='spin':
            pass

        return encoded_val
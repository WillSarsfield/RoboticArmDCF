import re

class CommandInterpreter:
    max_angle=180           #refers to the maximum range of motion each servo has in degrees
    num_servos=5

    def __init__(self,x_ofst=0,y_ofst=0,z_ofst=0):
        self.x_ofst=x_ofst
        self.y_ofst=y_ofst
        self.z_ofst=z_ofst
        self.x_pos=0
        self.y_pos=0
        self.z_pos=0

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
                if re.match('high',command):
                    value = 1
                elif re.match('low',command):
                    value = 0
            elif len(paramList)==2:
                bit,value = int(paramList[0]),int(paramList[1])

            #convert bit and value here
        elif type=='pump':
            pump_num,steps=int(paramList[0]),int(paramList[1])
        elif type=='spin':
            speed=int(paramList[0])
        elif type=='irrd':
            pass
        elif type=='mckirrd':
            pass
        elif type=='offset':
            self.x_ofst,self.y_ofst,self.z_ofst=[paramList[i] for i in (0,1,2)]
        elif type=='moveall':
            x,y,z=[paramList[i] for i in (0,1,2)]
            #eff_ang=paramList[3]
            angles=self.get_angle_from_coords(x, y, z)
            decomp_cmds=[]
            for i in range(len(angles)):
                decomp_cmds.append(self.get_encoded_command(command='move('+i+','+angles[i]+')',type='move'))
            
            decomp_cmds.append(self.get_encoded_command(command='do(0)',type='do'))
            self.x_pos,self.y_pos,self.z_pos=x,y,z
            encoded_val=decomp_cmds



        elif type=='shift':
            pass
        elif type=='dispense':
            pass
        elif type=='learnas':
            pass
        elif type=='takepose':
            pass

        return encoded_val

    def get_angle_from_coords(self,x,y,z):
        return None
        return angles

    def get_steps_from_vol(self,vol):
        return None
        return steps
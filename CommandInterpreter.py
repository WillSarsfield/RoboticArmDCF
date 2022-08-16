import re
import math

class CommandInterpreter:
    max_angle=180           #refers to the maximum range of motion each servo has in degrees
    num_servos=5

    def __init__(self,x_ofst=0,y_ofst=0,z_ofst=0):
        self.x_ofst=x_ofst
        self.y_ofst=y_ofst
        self.z_ofst=z_ofst
        self.tilt=0
        self.x_pos=0
        self.y_pos=0
        self.z_pos=0
        

    def get_encoded_command(self,command=None,type=''):
        paramList=re.findall(r'\d+',command)
        encoded_val=None
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
        # elif type=='mckirrd':
        #     pass
        elif type=='offset':
            self.x_ofst,self.y_ofst,self.z_ofst=[int(paramList[i]) for i in (0,1,2)]
        elif type=='moveall':
            print(command)
            x,y,z=[int(paramList[i]) for i in (0,1,2)]
            x,y,z=x+self.x_ofst,y+self.y_ofst,z+self.z_ofst
            eff_ang=paramList[3]
            angles=self.get_angle_from_coords(x, y, z, tilt=eff_ang)
            decomp_cmds=[]
            for i in range(len(angles)):
                decomp_cmds.append(self.get_encoded_command(command='move(%s,%s)'%(i,angles[i]),type='move'))
            
            decomp_cmds.append(self.get_encoded_command(command='do(0)',type='do'))
            self.x_pos,self.y_pos,self.z_pos,self.tilt=x,y,z,eff_ang
            encoded_val=decomp_cmds

        elif type=='shift':
            x_diff,y_diff,z_diff=[int(paramList[i]) for i in (0,1,2)]
            x,y,z=x_diff+self.x_pos,y_diff+self.y_pos,z_diff+self.z_pos
            eff_ang=int(paramList[3])+self.tilt
            encoded_val=self.get_encoded_command(command='moveall(%s,%s,%s,%s)'%(x,y,z,eff_ang),type='moveall')

        elif type=='dispense':
            pump_no,vol=paramList[0],paramList[1]
            steps=self.get_steps_from_vol(vol)
            encoded_val=self.get_encoded_command(command='pump(%s,%s)'%(pump_no,steps),type='pump')
            
        elif type=='learnas':
            pos_name = command[8:-1]
            with open('./SAVED_POSITIONS'+pos_name.upper()+'.txt','w') as pos_file:
                pos_file.write(self.x_pos+','+self.y_pos+','+self.z_pos)
                pos_file.close()

        elif type=='takepose':
            file_name = command[9:-1]
            with open('./SAVED_POSITIONS'+file_name.upper()+'.txt','r') as pos_file:
                coords=''.join(pos_file.readline().split())
                pos_file.close()
            x,y,z=[int(coords.split(',')[i]) for i in (0,1,2)]
            encoded_val=self.get_encoded_command(command='moveall(%s,%s,%s,%s)'%(x,y,z,eff_ang),type='moveall')

        elif type=='repeat':
            args = command[7:-1].split(',',2) #splits at the first & second comma
            encoded_vals=[]
            encoded_command=self.get_encoded_command(command=args[-1],type=args[0]) #get encoded value(s) of desired repeated command
            if type(encoded_cmd)==type(0):
                encoded_vals.append(encoded_cmd)
            elif type(encoded_cmd)==type([]):
                encoded_vals.append(int(encoded_cmd[i]) for i in range(len(encoded_cmd)))
            encoded_vals*args[1] #repeats commands specified number of times

        return encoded_val

    def get_angle_from_coords(self,x,y,z,tilt=0):
        angle = []
        length = [10.5,9,5]
        angle.append(180 - ((math.atan(z/x)*180)/math.pi))
        if angle[0] > 180:
            angle[0] -= 180
        if (x<0 and z<0) or (x>0 and z<0):
            x = math.sqrt(x**2 + z**2)
        else:
            x = -math.sqrt(x**2 + z**2)
        x2 = (-length[2]) * math.cos((tilt*math.pi)/180) + x
        y2 = (-length[2]) * math.sin((tilt*math.pi)/180) + x
        d = math.sqrt(x2**2 + y2**2)
        a = ((math.atan(-y2/-x2)*180)/math.pi)
        if x2 <= 0:
            angle.append((((math.acos((length[0]**2 + d**2 - length[1]**2)/(2*length[0]/d))*180)/math.pi) + a) + 180)
        else:
            angle.append(((math.acos((length[0]**2 + d**2 - length[1]**2)/(2*length[0]/d))*180)/math.pi) + a)
        angle.append(((math.acos((length[0]**2 + length[1]**2 - d**2)/(2*length[0]/d))*180)/math.pi) + 180)
        angle.append(360 - math.fmod(angle[1] + angle[2] - tilt, 360))
        angle[1] = 180 - angle[1]
        angle[2] -= 270
        if angle[3] < 180:
            angle[3] += 90
        else:
            angle[3] -= 270
        if angle[2] > 180 or angle[2] < 0:
            angle[2] = math.fmod(angle[2],180)
        if angle[3] > 180 or angle[3] < 0:
            angle[3] = math.fmod(angle[3],180)
        return angle

    def get_steps_from_vol(self,vol):
        return None
        return steps
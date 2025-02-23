import re
import math
import socket
import time

class CommandInterpreter:
    #refers to the maximum range of motion each servo has in degrees

    def __init__(self,x_ofst=0.0,y_ofst=0.0,z_ofst=0.0):
        self.x_ofst=x_ofst
        self.y_ofst=y_ofst
        self.z_ofst=z_ofst
        self.tilt=90.0
        self.x_pos=0.0
        self.y_pos=0.0
        self.z_pos=0.0
        self.max_angle=180
        self.num_servos=5
        self.pump_ofst = self.num_servos*(self.max_angle+1)
        self.num_pumps = 4
        self.max_steps = 3000
        self.num_switches = 2
        self.bit_ofst = self.num_pumps*(self.max_steps+1)+self.pump_ofst
        self.spin_ofst = self.bit_ofst + (self.num_switches*2)
        

    def get_encoded_command(self,command=None,cmd_type=''):
        signed_float = re.compile('(-?\d+\.?\d*)')
        paramList=re.findall(signed_float,command)
        encoded_val=[]
        # ...-ve        |0      | +ve...
        # do cmd        | move cmd              | pump cmd | bit cmd | spin cmd             |
        if cmd_type=='move':
            servo_num,angle=int(paramList[0]),float(paramList[1]) # gets all numbers from the move command
            encoded_val= servo_num*(self.max_angle + 1)+angle      # maps (RxR)->R i.e. there is a unique positive encoded_val for each combination of servo&angle
            encoded_val+=1                                  # need to reserve zero for a separate commmand 
            # print(servo_num,angle,'encoded as',encoded_val)
        elif cmd_type=='do':
            waitTime=int(paramList[0]) # gets the wait time from the do command
            encoded_val= -waitTime-1                        #wait command is encoded as the negative numbers (1 is subtracted as the value 0 is already used)
            # print(waitTime,'encoded as',encoded_val)
            
        elif cmd_type=='bit':
            bit,value = int(paramList[0]),int(paramList[1])
            encoded_val = self.bit_ofst + bit*2 + value

            #convert bit and value here
        elif cmd_type=='pump':
            pump_num,steps=int(paramList[0]),int(paramList[1])
            steps += 1500 #needs to convert to number in range -1500 -> 1500 to 0 -> 3000
            encoded_val = self.pump_ofst + pump_num*(self.max_steps+1) + steps
        elif cmd_type=='spin':
            encoded_val = self.spin_ofst + int(paramList[0]) + 1
        elif cmd_type=='irrd':
            encoded_val = 15000 + int(paramList[0])
        # elif cmd_type=='mckirrd':
             #pass   
        elif cmd_type=='offset':
            self.x_ofst,self.y_ofst,self.z_ofst=[int(paramList[i]) for i in (0,1,2)]

        elif cmd_type=='moveall':
            x,y,z=[float(paramList[i]) for i in (0,1,2)]
            x,y,z=x+self.x_ofst,y+self.y_ofst,z+self.z_ofst
            eff_ang=paramList[3]
            self.x_pos,self.y_pos,self.z_pos,self.tilt=x,y,z,eff_ang
            angles=self.get_angle_from_coords(x, y, z, tilt=eff_ang)
            decomp_cmds=[]
            for i in range(len(angles)):
                decomp_cmds.append(self.get_encoded_command(command='move(%s,%s)'%(i,angles[3-i]),cmd_type='move'))
            
            decomp_cmds.append(self.get_encoded_command(command='do(0)',cmd_type='do'))
            encoded_val=decomp_cmds

        elif cmd_type=='shift':
            x_diff,y_diff,z_diff=[float(paramList[i]) for i in (0,1,2)]
            x,y,z=x_diff+self.x_pos,y_diff+self.y_pos,z_diff+self.z_pos
            eff_ang=float(paramList[3])+float(self.tilt)
            encoded_val=self.get_encoded_command(command='moveall(%s,%s,%s,%s)'%(x,y,z,eff_ang),cmd_type='moveall')

        elif cmd_type=='dispense':
            pump_no,vol=paramList[0],paramList[1]
            steps=self.get_steps_from_vol(vol)
            encoded_val=self.get_encoded_command(command='pump(%s,%s)'%(pump_no,steps),cmd_type='pump')
            
        elif cmd_type=='learnas':
            pos_name = command[8:-1]
            with open('./SAVED_POSITIONS/'+pos_name.upper()+'.txt','w') as pos_file:
                pos_file.write(self.x_pos+','+self.y_pos+','+self.z_pos)
                pos_file.close()

        elif cmd_type=='takepose':
            file_name = command[9:-1]
            print(file_name)
            with open('./SAVED_POSITIONS/'+file_name.upper()+'.txt','r') as pos_file:
                coords=''.join(pos_file.readline().split())
                pos_file.close()
            x,y,z,eff_ang=[float(coords.split(',')[i]) for i in (0,1,2,3)]
            encoded_val=self.get_encoded_command(command='moveall(%s,%s,%s,%s)'%(x,y,z,eff_ang),cmd_type='moveall')

        elif cmd_type=='repeat':
            args = command[7:-1].split(',',1) #splits at the first & second comma
            sub_type=args[-1].split('(',1)[0]
            encoded_val=[]
            encoded_cmd=self.get_encoded_command(command=args[-1],cmd_type=sub_type) #get encoded value(s) of desired repeated command
            if type(encoded_cmd)==type(0):
                encoded_val.append(encoded_cmd)
            elif type(encoded_cmd)==type([]):
                encoded_val.extend(encoded_cmd)
            encoded_val=encoded_val*int(args[0]) #repeats commands specified number of times

        elif cmd_type=='macro':
            filename=command[6:-1]
            with open('./COMMANDS/MACROS/'+filename.upper()+'.txt','r') as macro_file:
                text = macro_file.read()
                macro_file.close()
            text=''.join(text.split()).lower()
            command_list=text.split(';')
            for command in command_list:
                cmd_type=command.split('(',1)[0]
                sub_cmd_list = self.get_encoded_command(command=command,cmd_type=cmd_type)
                for i, cmd in enumerate(sub_cmd_list):
                    encoded_val.append(cmd)
        else:
            print('no commands recognised')

        # print(encoded_val)
        return encoded_val

    def get_angle_from_coords(self,x,y,z,tilt=0.0):
        angle = []
        tilt = float(tilt)
        length = [10.5, 9.0, 10.3 ,8]
        if x == 0 and z != 0:
            angle.append(90)
            if z<=0:
                x = -(math.sqrt(x**2 + z**2))
            elif z>=0:
                x = math.sqrt(x**2 + z**2)
        elif z == 0:
            angle.append(0)
        else:
            angle.append(math.fmod((math.atan(z/x)*180)/math.pi,180))
            if angle[0] < 0:
                angle[0] += 180
            if x>=0 and z<=0:
                x = -(math.sqrt(x**2 + z**2))
            elif x<=0 and z>=0:
                x = math.sqrt(x**2 + z**2)
            elif x<=0 and z<=0:
                x = -(math.sqrt(x**2 + z**2))
            elif x >= 0 and z >= 0:
                x = math.sqrt(x**2 + z**2)
        x = x + length[3]*(math.sin((tilt/180)*math.pi))
        y = y - length[3]*(math.cos((tilt/180)*math.pi))
        x2 = (-(length[2]) * (math.cos((tilt*math.pi)/180))) + x
        y2 = (-(length[2]) * (math.sin((tilt*math.pi)/180))) + y
        d = math.sqrt((x2**2) + (y2**2))
        if x2 == 0:
            a = -90
        else:
            a = ((math.atan(-y2/-x2)*180)/math.pi)
        if x2 <= 0:
            angle.append((((math.acos(((length[0]**2) + (d**2) - (length[1]**2))/(2*length[0]*d))*180)/math.pi) + a) + 180)
        else:
            angle.append(((math.acos(((length[0]**2) + (d**2) - (length[1]**2))/(2*length[0]*d))*180)/math.pi) + a)
        angle.append(((math.acos(((length[0]**2) + (length[1]**2) - (d**2))/(2*length[0]*length[1]))*180)/math.pi) + 180)
        angle.append(360 - math.fmod(angle[1] + angle[2] - tilt, 360))
        angle[1] = 180 - angle[1]
        angle[2] -= 270
        if angle[3] < 180:
            angle[3] += 90
        else:
            angle[3] -= 270
        for i in range(4):
            if angle[i] > 180 or angle[i] < 0:
                return None   
        return angle

    def get_steps_from_vol(self,vol):
        return None
        return steps
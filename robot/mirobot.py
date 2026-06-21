#coding=utf-8
from pprint import pprint
from enum import Enum
import re
import sys
import os
import PythonCallBack

class MirobotJoint(Enum):
    Joint1 = 1
    Joint2 = 2
    Joint3 = 3
    Joint4 = 4
    Joint5 = 5
    Joint6 = 6
    
class RevolveDirection(Enum):
    cw = 1
    ccw = 2
    
class MoveDirection(Enum):
    forward = 1
    backward = 2
    up = 3
    down = 4 
    right = 5
    left = 6
    
class MoveMode(Enum):
     relative = 1  #相对位置 G91
     absolute =2   #绝对位置 G90
     
class Motion(Enum):
    MOVJ = 1  #关节运动
    MOVL = 2  #直线运动
    JUMP = 3  #门型轨迹运动
    
class Mirobot:
    def __init__(self, receive_callback=None, debug=False):
        self.debug = debug
        self.receive_callback = receive_callback
        self.get_status_callback = None

    # COMMUNICATION #

    # 直接发送GCode
    # send a message
    def send_msg(self, msg):
        PythonCallBack.sendMessage(msg)
        if self.debug:
            print('Message send: %s' % msg)

    # 接受串口返回--未实现
    # message receive handler
    def receive_msg(self, msg):
        msg = msg.decode('utf-8')
        if self.receive_callback is not None:
            try:
                self.receive_callback(msg)
            except Exception as e:
                print(e)
                print('Receive callback error: ', sys.exc_info()[0])

        if msg.startswith('<'):
            self.update_status(msg)

    def isColorSensor(self, color):
       cc = PythonCallBack.getColorSensor(color)
       return cc;
       
    def setIOADOValue(self, address, value):
       PythonCallBack.setIOADOValue(address, value)
       
    def setIOAFOValue(self, address, value):
       PythonCallBack.setIOAFOValue(address, value)
       
    def getIOADIValue(self, address):
       vv = PythonCallBack.getIOADIValue(address)
       return vv;
       
    def getIOAFIValue(self, address):
       vv = PythonCallBack.getIOAFIValue(address)
       return vv;  
       
    #每个轴复位
    # home each axis individually
    def home_individual(self):
        msg = '$HH'
        self.send_msg(msg)

    # 复位
    def home_simultaneous(self, n=0):
        msg = '$H'
        if 1 == n:
          msg = '$H7'
        elif 2 == n:
          msg = '$H0'
        self.send_msg(msg)
        
    # 解锁
    # unlock the shaft
    def unlock_shaft(self):
        msg = 'M50'
        self.send_msg(msg)

    #设定运动速度
    def set_speed(self, speed):
        msg = 'F'+ str(speed)
        self.send_msg(msg)
    
    # 初始位置
    def go_to_zero(self):
        self.go_to_axis(0, 0, 0, 0, 0, 0)

    #关节旋转到
    # send all axes to a specific position
    def go_to_axis(self, a1, a2, a3, a4, a5, a6):
        msg = 'M21 G90 G1'
        msg += ' X' + str(a1)
        msg += ' Y' + str(a2)
        msg += ' Z' + str(a3)
        msg += ' A' + str(a4)
        msg += ' B' + str(a5)
        msg += ' C' + str(a6)
        self.send_msg(msg)
        return

    #G1参数速度
    #G0最大速度
    # increment all axes a specified amount
    def increment_axis(self, a1, a2, a3, a4, a5, a6):
        msg = 'M21 G91 G1'
        msg += ' X' + str(a1)
        msg += ' Y' + str(a2)
        msg += ' Z' + str(a3)
        msg += ' A' + str(a4)
        msg += ' B' + str(a5)
        msg += ' C' + str(a6)
        self.send_msg(msg)
        return
    
    #移动到坐标位置
    # linear move to a cartesian position
    def go_to_cartesian_lin(self, m, x, y, z, a, b, c):
        msg = 'M20 G90'
        if Motion.MOVJ == m:
          msg += ' G01'
        elif Motion.MOVL == m:
          msg += ' G00'
        elif Motion.JUMP == m:
          msg += ' G05'
        else:
          return
        msg += ' X' + str(x)
        msg += ' Y' + str(y)
        msg += ' Z' + str(z)
        msg += ' A' + str(a)
        msg += ' B' + str(b)
        msg += ' C' + str(c)
        self.send_msg(msg)
        return
    
    #笛卡尔空间中的线性增量
    # linear increment in cartesian space
    def increment_cartesian_lin(self, m, x, y, z, a, b, c):
        msg = 'M20 G91'
        if Motion.MOVJ == m:
          msg += ' G01'
        elif Motion.MOVL == m:
          msg += ' G00'
        elif Motion.JUMP == m:
          msg += ' G05'
        else:
          return
        msg += ' X' + str(x)
        msg += ' Y' + str(y)
        msg += ' Z' + str(z)
        msg += ' A' + str(a)
        msg += ' B' + str(b)
        msg += ' C' + str(c)
        self.send_msg(msg)
        return

    #吸盘开
    def suction_cup_on(self):
        self.send_msg('M3S1000')
    
    #吸盘关
    def suction_cup_off(self):
        self.send_msg('M3S0')
        
    #吸盘吹
    def suction_cup_blow(self):
        self.send_msg('M3S500')
    
    #夹具开    
    def gripper_on(self):
        self.send_msg('M3S40\nM4E45')
    
    #夹具关    
    def gripper_off(self):
        self.send_msg('M3S60\nM4E65')
        
    # set the pwm of the air pump
    def set_air_pump(self, pwm):
        msg = 'M3S' + str(pwm)
        self.send_msg(msg)

    # set the pwm of the gripper
    def set_gripper(self, pwm):
        msg = 'M4E' + str(pwm)
        self.send_msg(msg)
    
    #延时执行 秒
    # set the pwm of the gripper
    def set_delay_time(self, t):
        msg = 'G4 P'+str(t)
        self.send_msg(msg)
        
    #滑轨移动到
    def slider_move_to(self, x, speed):
       msg = 'G90 G01' + ' D' + str(x) + ' F' + str(speed)
       self.send_msg(msg)
       
    #传送带移动到  
    def conveyor_move_to(self, c, n, speed):
       msg = ''
       if MoveMode.relative == c:
         msg += 'G91 G01'
       elif MoveMode.absolute == c:
         msg += 'G90 G01'
       else:
         return
       msg += ' D' + str(n) + ' F' + str(speed)
       self.send_msg(msg)
     
    #关节移动
    def move_to_axis(self, joint, revolve, n):
        msg = 'M21 G91 G01 '
        if RevolveDirection.ccw == revolve:
          n = -n;
        if MirobotJoint.Joint1 == joint:
          msg += 'X' + str(n)
        elif MirobotJoint.Joint2 == joint:
          msg += 'Y' + str(n)
        elif MirobotJoint.Joint3 == joint:
          msg += 'Z' + str(n) 
        elif MirobotJoint.Joint4 == joint:
          msg += 'A' + str(n) 
        elif MirobotJoint.Joint5 == joint:
          msg += 'B' + str(n) 
        elif MirobotJoint.Joint6 == joint:
          msg += 'C' + str(n)
        else:
          return
        self.send_msg(msg)
     
    #定向移动
    def direction_mobility(self, d, n):
       msg = 'M20 G91 G01 '
       if   MoveDirection.forward == d:
         msg += 'Y'+ str(n)
       elif MoveDirection.backward == d:
         msg += 'Y'+ str(-n)
       elif MoveDirection.up == d:
         msg += 'Z'+ str(n)
       elif MoveDirection.down == d:
         msg += 'Z'+ str(-n)
       elif MoveDirection.right == d:
         msg += 'X'+ str(n)
       elif MoveDirection.left == d:
         msg += 'X'+ str(-n)
       else:
         return
       self.send_msg(msg)

    #门型轨迹移动 只用于笛卡尔模式
    def jump_move(self, m, x, y, z, a, b, c):
      msg = 'M20 '
      if MoveMode.relative == m:
        msg += 'G91 G05'
      elif MoveMode.absolute == m:
        msg += 'G90 G05'
      else:
        return
      msg += ' X' + str(x) + ' Y' + str(y)+' Z'+ str(z) + ' A' + str(a) + ' B' + str(b)+' C'+ str(c)
      self.send_msg(msg)
      
    def set_arc_move(self, mode, revolve, x, y, z, r):
      msg = 'M20 '
      if MoveMode.relative == mode:
        msg += 'G91 '
      elif MoveMode.absolute == mode:
        msg += 'G90 '
      else:
        return
      if RevolveDirection.cw == revolve:
          msg += 'G2 '
      elif RevolveDirection.ccw == revolve:
          msg += 'G3 '
      else:
          return
      msg += 'X'+str(x)+' Y'+str(y)+' Z'+str(z)+' R'+str(r)
      self.send_msg(msg);
      
    def custom_tool_offset(self, x, y, z):
      msg = '$46='+str(x)+'\n$47='+str(y)+'\n$48='+str(y)
      self.send_msg(msg);
      
    def transfer_string(self, ss=''):
      self.send_msg(ss);
    

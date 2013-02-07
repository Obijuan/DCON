#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import time

#-- Registros de la DCON
DIRC_ADDR = 0x00
DINS_ADDR = 0x01
AIN0_ADDR = 0x02
AIN1_ADDR = 0x03
DOUS_ADDR = 0x04
AOUT_ADDR = 0x05
PWM0_ADDR = 0x06
PWM1_ADDR = 0x07

#--- Modos de las tramas
READ = 3
WRITE = 6

#-- Salidas digitales
T0 = 1   #-- DO0: Transistor 0
DO0 = T0 #-- DO0 y T0 son sinonimos

T1 = 2   #-- DO1: Transistor 1
DO1 = T1 #-- DO1 y T1 son sinonimos

R0 = 4  #-- Rele 0
R1 = 8  #-- Rele 1


class IncorrectFrame(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class TimeOut(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


def Frame(tupla = (0, READ, 0, 0)):
  """Construir una trama para la dcon"""
  dir, mode, reg, value = tupla
  return ":{0:02X}{1}{2:02X}{3:04X}".format(dir, mode, reg, value)


def Parse(frame):
  """Analisis de la trama. Se devuelven los 4 campos
  El formato de la trama es
     
        :aafddvvvv
        
     donde:
     
       :  --> Cabecera
       aa --> Direccion del DCON: 0 -  8
       f  --> Funcion: 3 (READ), 6 (WRITE)
       dd --> Registro: 00 - 0x14
       vvvv -> Valor"""
       
  ##-- Campo 1: Direccion ---------     
  try:
    dir = int(frame[1] + frame[2], 16)
  except IndexError:
    print "  ** ERROR: Direccion no dada"
    raise IncorrectFrame(1)
  except ValueError:
    print "  ** ERROR: Direccion incorrecta"
    raise IncorrectFrame(2)
  
  ##-- Campo 2: Funcion ----------
  try:
    mode = int(frame[3], 16)
  except IndexError:
    print "  ** ERROR: Funcion de la trama no dada"
    raise IncorrectFrame(3)
  except ValueError:
    print "  ** ERROR: La funcion de la trama es incorrecta"
    raise IncorrectFrame(4)
  
  if mode!=READ and mode!=WRITE:
    print "  ** ERROR: La funcion de la trama es incorrecta"
    raise IncorrectFrame(4)
  
  #-- Campo 3: Registro
  try:
    reg = int(frame[4] + frame[5], 16)
  except IndexError:
    print "  ** ERROR: Registro no dado"
    raise IncorrectFrame(5)
  except ValueError:
    print "  ** ERROR: Registro incorrecto"
    raise IncorrectFrame(6)
  
  if reg<0 or reg>0x1A:
    print "  ** ERROR: Registro incorrecto"
    raise IncorrectFrame(6)
  
  #-- Campo 4: Valor
  try:
    value = int(frame[6] + frame[7] + frame[8] + frame[9], 16)
  except IndexError:
    print "  ** ERROR: Valor no dado"
    raise IncorrecFrame(7)
  except ValueError:
    print "  ** ERROR: Valor incorrecto"
    raise IncorrectFrame(8)
  
  ##-- Devolver una tupla con los datos recibidos
  return dir, mode, reg, value


class Dcon(object):
  """Dcon class. For accessing to all the dcon resources"""
  
  def __init__(self, sp, dir = 0):
    """Arguments: serial port and dcon address"""
    self.sp = sp
    self.dir = dir

  def __str__(self):
    str1 = "DCON. Dir: {0}\n".format(self.dir)
    str2 = "Puerto serie: {0}".format(self.sp.name)
    return str1 + str2

  def send_frame(self, frame):
    """Send a frame to the DCON. The frame is a string"""
    #-- Switch to Transmiting mode
    self.sp.setRTS(False)
    time.sleep(0.0002)

    #-- Send the frame
    print "<-- (out) " + frame
    self.sp.write(frame);

    #-- Switch to receiving mode
    time.sleep(0.001)
    self.sp.setRTS(True)
    
    #-- Wait for the frame response
    #-- or... for a timeout
    rx_frame = self.sp.read(len(frame));
    
    #-- Check the received frame
    if len(rx_frame)!=0:
      
      #--Frame received. Print it!
      print "--> (in)  " + rx_frame
      
    else:
      #-- No response! timeout!
      print "TIMEOUT";
      raise TimeOut(1)
      
    return rx_frame

#------------------ ACCESS TO THE DCON REGISTERS!!! -----------------------
  @property
  def DIRC(self):
    """DCON current dir. register"""
    frame = Frame((self.dir, READ, DIRC_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1
      
    return dir

  @DIRC.setter
  def DIRC(self, value):
    frame = Frame((self.dir, WRITE, DIRC_ADDR, value))
    frame_rx = self.send_frame(frame)
    

  @property
  def DINS(self):
    """Digital INPUTS. It returns the state of the 2 digital inputs"""
    frame = Frame((self.dir, READ, DINS_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1,-1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1,-1
    
    #-- Get the state of the inputs
    di0 = value & 0x0001
    di1 = (value & 0x0002) >> 1
    
    #-- Return the inputs
    return di0, di1
    
  @property
  def AIN0(self):
    """Analog input 0"""
    frame = Frame((self.dir, READ, AIN0_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1
      
    return value
  
  @property
  def AIN1(self):
    """Analog input 1"""
    frame = Frame((self.dir, READ, AIN1_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1
      
    return value
  
  @property
  def DOUS(self):
    """Digital outputs"""
    frame = Frame((self.dir, READ, DOUS_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1
      
    return value
  
  @DOUS.setter
  def DOUS(self, value):
    frame = Frame((self.dir, WRITE, DOUS_ADDR, value))
    frame_rx = self.send_frame(frame)
  
  @property
  def AOUT(self):
    """Digital outputs"""
    frame = Frame((self.dir, READ, AOUT_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1
      
    return value
  
  @AOUT.setter
  def AOUT(self, value):
    frame = Frame((self.dir, WRITE, AOUT_ADDR, value))
    frame_rx = self.send_frame(frame)
  
  @property
  def PWM0(self):
    """Digital outputs"""
    frame = Frame((self.dir, READ, PWM0_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1
      
    return value
  
  @PWM0.setter
  def PWM0(self, value):
    frame = Frame((self.dir, WRITE, PWM0_ADDR, value))
    frame_rx = self.send_frame(frame)
    
  @property
  def PWM1(self):
    """Digital outputs"""
    frame = Frame((self.dir, READ, PWM1_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1
      
    return value
  
  @PWM1.setter
  def PWM1(self, value):
    frame = Frame((self.dir, WRITE, PWM1_ADDR, value))
    frame_rx = self.send_frame(frame)  
    
    
    
    
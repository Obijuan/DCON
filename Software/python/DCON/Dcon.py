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
COND_ADDR = 0x08
CONA_ADDR = 0x09
CPID_ADDR = 0x0A
PPID_ADDR = 0x0B
IPID_ADDR = 0x0C
DPID_ADDR = 0x0D
SPLC_ADDR = 0x0E
UAA0_ADDR = 0x0F
UAA1_ADDR = 0x10
CIAL_ADDR = 0x11
COAL_ADDR = 0x12
VIDA_ADDR = 0x13
ALMO_ADDR = 0x14

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

#-- E/S digitales
ON = 1
OFF = 0

def DIG_str(bit):
  """Interpretacion de los bits de E/S digital"""
  DIG_str_table = ["OFF", "ON"]
  try:
    cad = DIG_str_table[bit]
  except IndexError:
    return "Invalido"
  
  return cad

#-- Modos config. salidas digitales
DIG = 0   #--- Salida digital normal
PWM = 1   #--- Salida PWM

def COND_val(cdo1, cdo0):
  value = (cdo1 << 1) | cdo0
  return value

#-- Interpretacion de los bits del reg. COND
#--                    0              1
COND_str_table = ["Digital normal", "PWM"]

def COND_str(bit):
  try:
    cad = COND_str_table[bit]
  except IndexError:
    return "Invalido"
  
  return cad


#-- Modos de configuracion entradas/salidas analógicas
M0_20 = 0  #-- Modo 0 - 20 ma
M4_20 = 1  #-- Modo 4 - 20 ma
M0_5  = 2  #-- Modo 0 - 5 v
TERMO = 3  #-- Modo Termopar (solo entradas)

def CONA_val(cao, cain1, cain0):
  """Construir el valor para el registro CONA segun el modo de configuracion"""
  value = (cao << 8) | (cain1 << 4) | cain0
  return value

#-- Interpretacion digitos del reg. CONA
#--                   0         1       2         3
CONA_str_table = ["0-20mA", "4-20mA", "0-5v","Termopar"]

def CONA_str(digit):
  """Devolver la cadena asociada a un modo de configuracion"""
  try:
    cad = CONA_str_table[digit]
  except IndexError:
    return "Invalido"
    
  return cad


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
      return -16,-16
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -16,-16
    
    #-- Get the state of the inputs
    di0 = value & 0x0001
    di1 = (value & 0x0002) >> 1
    
    #-- Debug:
    #print ""
    #print "DI0: ({0}) {1}".format(di0, DIG_str(di0))
    #print "DI1: ({0}) {1}".format(di0, DIG_str(di1))
    #print ""
    
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
      return -16, -16, -16, -16
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -16, -16, -16, -16
        
    #-- Get the state of the outputs
    do0 = value & 0x0001              #-- Transitor 0
    do1 = (value & 0x0002) >> 1       #-- Transitor 1
    r0  = (value & 0x0004) >> 2       #-- Rele 0
    r1  = (value & 0x0008) >> 3       #-- Rele 1
      
    return do0, do1, r0, r1
  
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
      
    return valueinputs
  
  @PWM1.setter
  def PWM1(self, value):
    frame = Frame((self.dir, WRITE, PWM1_ADDR, value))
    frame_rx = self.send_frame(frame)  
    
  @property
  def COND(self):
    """Configuration of digital outputs"""
    frame = Frame((self.dir, READ, COND_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1, -1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1, -1
    
    #-- Get the state of the configuration bits
    cdo0 = value & 0x0001
    cdo1 = (value & 0x0002) >> 1
    
    #-- Debug...
    print ""
    print "DO0: ({0}) {1}".format(cdo0, COND_str(cdo0))
    print "DO1: ({0}) {1}".format(cdo1, COND_str(cdo1))
    print ""
    
    #-- Return the inputs
    return cdo0, cdo1
      
    return value  
    
  @COND.setter
  def COND(self, value):
    frame = Frame((self.dir, WRITE, COND_ADDR, value))
    frame_rx = self.send_frame(frame)  
    
  @property
  def CONA(self):
    """Configuration of analog inputs/outputs"""
    frame = Frame((self.dir, READ, CONA_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1, -1, -1
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1, -1, -1
    
    #-- Get the state of the configuration bits
    cao = (value & 0x0F00) >> 8
    cain1 = (value & 0x00F0) >> 4
    cain0 = (value & 0x000F)
    
    #-- Debug: show the digits
    print ""
    print "AO:   ({0}), {1} ".format(cao, CONA_str(cao))
    print "AIN1: ({0}), {1} ".format(cain1, CONA_str(cain1))
    print "AIN0: ({0}), {1} ".format(cain0, CONA_str(cain0))
    print ""
    
    #-- Return the inputs
    return cao, cain1, cain0

  
  @CONA.setter
  def CONA(self, value):
    frame = Frame((self.dir, WRITE, CONA_ADDR, value))
    frame_rx = self.send_frame(frame) 
  
  @property
  def CPID(self):
    """Configuration of CPID inputs/outputs"""
    frame = Frame((self.dir, READ, CPID_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -16
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -16
    
    #-- Get the state of the configuration bits
    cpid = (value & 0x000F)
    
    #-- Debug: 

    #-- Return the value
    return cpid  
  
  @CPID.setter
  def CPID(self, value):
    frame = Frame((self.dir, WRITE, CPID_ADDR, value))
    frame_rx = self.send_frame(frame) 
  
  @property
  def PPID(self):
    """Configuration of CPID inputs/outputs"""
    frame = Frame((self.dir, READ, PPID_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1024
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1024

    #-- Return the value
    return value

  @PPID.setter
  def PPID(self, value):
    frame = Frame((self.dir, WRITE, PPID_ADDR, value))
    frame_rx = self.send_frame(frame)
    

  @property
  def IPID(self):
    """Configuration of CPID inputs/outputs"""
    frame = Frame((self.dir, READ, IPID_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1024
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1024
    
    #-- Return the value
    return value

  @IPID.setter
  def IPID(self, value):
    frame = Frame((self.dir, WRITE, IPID_ADDR, value))
    frame_rx = self.send_frame(frame)

  @property
  def DPID(self):
    """Configuration of CPID inputs/outputs"""
    frame = Frame((self.dir, READ, DPID_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1024
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1024
    
    #-- Return the value
    return value

  @DPID.setter
  def DPID(self, value):
    frame = Frame((self.dir, WRITE, DPID_ADDR, value))
    frame_rx = self.send_frame(frame)

  @property
  def SPLC(self):
    """Configuration of CPID inputs/outputs"""
    frame = Frame((self.dir, READ, SPLC_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1024
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1024
    
    #-- Return the value
    return value

  @SPLC.setter
  def SPLC(self, value):
    frame = Frame((self.dir, WRITE, SPLC_ADDR, value))
    frame_rx = self.send_frame(frame)


  @property
  def UAA0(self):
    """Configuration of CPID inputs/outputs"""
    frame = Frame((self.dir, READ, UAA0_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1024
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1024
    
    #-- Return the value
    return value

  @UAA0.setter
  def UAA0(self, value):
    frame = Frame((self.dir, WRITE, UAA0_ADDR, value))
    frame_rx = self.send_frame(frame)

  @property
  def UAA1(self):
    """Configuration of CPID inputs/outputs"""
    frame = Frame((self.dir, READ, UAA1_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1024
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1024
    
    #-- Return the value
    return value

  @UAA1.setter
  def UAA1(self, value):
    frame = Frame((self.dir, WRITE, UAA1_ADDR, value))
    frame_rx = self.send_frame(frame)


  @property
  def CIAL(self):
    """Configuration of input alarms"""
    frame = Frame((self.dir, READ, CIAL_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -16, -16, -16, -16
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -16, -16, -16, -16
    
    #-- Get the state of the configuration bits
    adi0 = (value & 0x000F)
    adi1 = (value & 0x00F0) >> 4
    aai0 = (value & 0x0F00) >> 8
    aai1 = (value & 0xF000) >> 12
    
    #-- Debug: show the digits
    #print ""
    #print "AO:   ({0}), {1} ".format(cao, CONA_str(cao))
    #print "AIN1: ({0}), {1} ".format(cain1, CONA_str(cain1))
    #print "AIN0: ({0}), {1} ".format(cain0, CONA_str(cain0))
    #print ""
    
    #-- Return the inputs
    return adi0, adi1, aai0, aai1  

  @CIAL.setter
  def CIAL(self, value):
    frame = Frame((self.dir, WRITE, CIAL_ADDR, value))
    frame_rx = self.send_frame(frame) 

  @property
  def COAL(self):
    """Configuration of input alarms"""
    frame = Frame((self.dir, READ, COAL_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -16, -16, -16, -16
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -16, -16, -16, -16
    
    #-- Get the state of the configuration bits
    adi0 = (value & 0x000F)
    adi1 = (value & 0x00F0) >> 4
    aai0 = (value & 0x0F00) >> 8
    aai1 = (value & 0xF000) >> 12
    
    #-- Debug: show the digits
    #print ""
    #print "AO:   ({0}), {1} ".format(cao, CONA_str(cao))
    #print "AIN1: ({0}), {1} ".format(cain1, CONA_str(cain1))
    #print "AIN0: ({0}), {1} ".format(cain0, CONA_str(cain0))
    #print ""
    
    #-- Return the inputs
    return adi0, adi1, aai0, aai1

  @COAL.setter
  def COAL(self, value):
    frame = Frame((self.dir, WRITE, COAL_ADDR, value))
    frame_rx = self.send_frame(frame)     

  @property
  def VIDA(self):
    """Life!"""
    frame = Frame((self.dir, READ, VIDA_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -1024
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -1024
    
    #-- Return the value
    return value

  @VIDA.setter
  def VIDA(self, value):
    frame = Frame((self.dir, WRITE, VIDA_ADDR, value))
    frame_rx = self.send_frame(frame)

  @property
  def ALMO(self):
    """Configuration of Alarmas"""
    frame = Frame((self.dir, READ, ALMO_ADDR, 0));
    try:
      frame_rx = self.send_frame(frame)
    except TimeOut:
      return -16, -16
    
    #-- Parse the received frame
    try:
      dir, mode, reg, value = Parse(frame_rx)
    except IncorrectFrame:
      print "ERROR EN COMUNICACIONES"
      return -16, -16
    
    #-- Get the state of the configuration bits
    mode = (value & 0x000F)
    alm = (value & 0x00F0) >> 4
    
    #-- Debug: show the digits
    print "----"
    #print "AO:   ({0}), {1} ".format(cao, CONA_str(cao))
    #print "AIN1: ({0}), {1} ".format(cain1, CONA_str(cain1))
    #print "AIN0: ({0}), {1} ".format(cain0, CONA_str(cain0))
    #print ""
    
    #-- Return the inputs
    return mode, alm


  @ALMO.setter
  def ALMO(self, value):
    frame = Frame((self.dir, WRITE, ALMO_ADDR, value))
    frame_rx = self.send_frame(frame) 










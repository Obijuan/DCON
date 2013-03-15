#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""Pruebas del modulo DCON para la tarjeta DCON

Forma de uso:

test  [puerto serie]

Ej. en Linux:

./test /dev/ttyUSB0

Si no se especifica ningún puerto, se toma /dev/ttyUSB0 por defecto
"""
import sys
import getopt
import serial
import time
from Dcon import *

def probar_entradas():
  print "Prueba 1:  SALIDA EN VOLTAJE"
  print "Configuracion:"
  print " AO:  0-5v"
  print " AI0: 0-5v"
  print " AI1: 0-5v"
  d.CONA = 0x222
  d.AOUT = 0;
  print "Unir AO con AI0"
  print "Pulsa ENTER para empezar"
  raw_input();
  
  #-- Valores de aout a probar
  aout_val = [0x0, 0x100, 0x200, 0x300, 0x3FF];
  for aout in aout_val:
    d.AOUT = aout;   #-- Enviar senal por AOUT
    time.sleep(0.4);
    ai0 = d.AIN0      #-- Leer entrada 0
    print "SALIDA: AOUT --> {0:0X}, RECIBIDO: AIN0 <-- {1:0X}".format(aout, ai0) 
  
  print "Unir AO con AI1"
  print "Pulsa ENTER para empezar"
  raw_input();
  
  for aout in aout_val:
    d.AOUT = aout;   #-- Enviar senal por AOUT
    time.sleep(0.4);
    ai1 = d.AIN1      #-- Leer entrada 1
    print "SALIDA: AOUT --> {0:0X}, RECIBIDO: AIN1 <-- {1:0X}".format(aout, ai1) 
  


def info_di(d):
  """Mostrar informacion sobre las entradas digitales"""
  
  #-- Read digital inputs
  di0,di1 = d.DINS
  
  print ""
  print "---- ENTRADAS DIGITALES ----"
  print "DI0: ({0}) {1}".format(di0, DIG_str(di0))
  print "DI1: ({0}) {1}".format(di0, DIG_str(di1))
  print ""
  
def info_do(d):
  """Mostrar informacion sobre las salidas digitales"""
  
  #-- Read digital outputs
  do0,do1,r0,r1 = d.DOUS
  
  #-- Read the configuration
  cdo0, cdo1 = d.COND
  
  print ""
  print "----- SALIDAS DIGITALES ----"
  print "DO0: ({0}) {1},  TIPO: {2}".format(do0, DIG_str(do0),COND_str(cdo0))
  print "DO1: ({0}) {1},  TIPO: {2}".format(do1, DIG_str(do1),COND_str(cdo1))
  print ""

def motor_move(pos):
  frame = "JSGP 4,2,{0}\r".format(pos)
  print "<-- (out) " + frame
  s.write('\r'+frame)
  frame_in = s.read(20)
  print "--> (in) " + frame_in

def motor_disable():
  frame = "JSAP 204,0,1\r"
  print "<-- (out) " + frame
  s.write('\r'+frame)
  frame_in = s.read(20)
  print "--> (in) " + frame_in

def alarmas_off():
  d1.CIAL = 0x0000
  d2.CIAL = 0x0000
  d3.CIAL = 0
  d4.CIAL = 0
  d5.CIAL = 0
  d6.CIAL = 0
  d7.CIAL = 0
  d8.CIAL = 0
  
  
  d1.DOUS = 0x0000
  d2.DOUS = 0x0000
  
  d1.ALMO = 0x0001
  d2.ALMO = 0x0001
  d3.ALMO = 0x0001
  d4.ALMO = 0x0001
  d5.ALMO = 0x0001
  
  d1.COAL = 0
  d2.COAL = 0 
  d3.COAL = 0
  d4.COAl = 0
  d5.COAL = 0
  d6.COAL = 0
  d7.COAL = 0
  d8.COAL = 0
  
def rearme():
  d1.CIAL = 0x0000
  d2.CIAL = 0x0000
  
  d1.DOUS = 0x0000
  d2.DOUS = 0x0000
  
  d1.ALMO = 0x0001
  d2.ALMO = 0x0001
  d3.ALMO = 0x0001
  d4.ALMO = 0x0001
  d5.ALMO = 0x0001
  
  d1.CIAL = 0x1112
  d2.CIAL = 0x1102

def monitor_oven(n, sec=60):
  for i in xrange(n):
    print "({3}) {2} --> Temp: {0}, Salida: {1}".format(d1.AIN1, d1.AOUT, time.asctime(), i)
    #print "y-: {2}, e0:{3},  e1: {0}, e2:{1}".format(d.PWM0,d.PWM1, d.UAA0, d.UAA1)
    time.sleep(sec)

def show_regs():
  print "DIRC: 0x{0:0X}".format(d.DIRC)
  print "COND: {0}".format(d.COND)
  print "CONA: 0X{0}".format(d.CONA)
  print "CPID: 0X{0:0X}".format(d.CPID)
  print "PPID: 0X{0:0X}".format(d.PPID)
  print "IPID: 0X{0:0X}".format(d.IPID)
  print "DPID: 0X{0:0X}".format(d.DPID)
  print "SPLC: 0X{0:0X}".format(d.SPLC)
  print "UAA0: 0X{0:0X}".format(d.UAA0)
  print "UAA1: 0X{0:0X}".format(d.UAA1)
  print "CIAL: 0X{0}".format(d.CIAL)
  print "COAL: 0X{0}".format(d.COAL)
  print "VIDA: 0X{0:0X}".format(d.VIDA)
  print "ALMO: 0X{0}".format(d.ALMO)

#------  MAIN -------------------

# parse command line options
try:
  opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
except getopt.error, msg:
  print msg
  print "for help use --help"
  sys.exit(2)
  
# process options
for o, a in opts:
  if o in ("-h", "--help"):
    print __doc__
    sys.exit(0)

#-- Default serial port (if none is given in the arguments)
serial_name = "/dev/ttyUSB0"

#-- If there are arguments...
if (len(args) > 0) :
    
  #-- The first arg. is the serial port
  serial_name = args[0]

#print "Puerto serie: {0}".format(serial_name)

#-- Open the serial port
#--------------------------------------------------------
#-- Abrir el puerto serie. Si hay algun error se termina
#--------------------------------------------------------
try:
  s = serial.Serial(serial_name, 115200)
  
  #-- Timeout: 100 ms
  s.timeout=0.1;

except serial.SerialException:
  #-- Error al abrir el puerto serie
  sys.stderr.write("Error opening the port {0}".format(serial_name))
  sys.exit(1)

#-- Mostrar el nombre del dispositivo
print "Puerto serie abierto: {0}\n".format(s.name)

#-- Conectar con las DCONes
d = Dcon(s,0)
d1 = Dcon(s, 1)
d2 = Dcon(s, 2)
d3 = Dcon(s, 3)
d4 = Dcon(s, 4)
d5 = Dcon(s, 5)
d6 = Dcon(s, 6)
d7 = Dcon(s, 7)
d8 = Dcon(s, 8)
d9 = Dcon(s, 9)

#d2.DIRC




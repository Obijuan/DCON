#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import console_io
import sys
import getopt
import serial
import time

DO0_state = 0
DO1_state = 0
Rele0_state = 0
Rele1_state = 0

#-- Analog outputs in three states: min (0v), middle (2.5v) and max (5v)
AO_state = 0
AO_value = ["0000", "01FF", "03FF"]

def send_frame(frame):
  #-- Switch to Transmiting mode
  s.setRTS(False)
  time.sleep(0.0002)

  #-- Send the frame
  print "<-- (out) " + frame
  s.write(frame);

  #-- Switch to receiving mode
  time.sleep(0.001)
  s.setRTS(True)
  
  #-- Wait for the frame response
  #-- or... for a timeout
  rx_frame = s.read(len(frame));
  
  #-- Check the received frame
  if len(rx_frame)!=0:
    
    #--Frame received. Print it!
    print "--> (in)  " + rx_frame
    
  else:
    #-- No response! timeout!
    print "TIMEOUT"; 

def digital_output_frame():
  #-- Send a digital output frame according to the current outputs state
  value = Rele1_state<<3 | Rele0_state<<2 | DO1_state<<1 | DO0_state
  value_digit = "{0:X}".format(value)
  send_frame(FRAME_DOUS_WRITE+"000"+value_digit)
    
#-----------------
#-- Sacar el menu
#-----------------
def menu():
  print """
  
     Pruebas del DCON
     ----------------
     
     1.- Lectura de la dirección del DCON
     2.- Cambiar la dirección del DCON a 0x01
     3.- Cambiar la dirección del DCON a 0x02
     4.- Lectura de entradas digitales (DINS)
     5.- Lectura de entrada analógica 0 (AIN0)
     6.- Lectura de entrada analógica 1 (AIN1)
     7.- Salida Digital 0 on/off (DOUS)
     8.- Salida Digital 1 on/off (DOUS)
     9.- Rele 0 on/off (DOUS)
     0.- Rele 1 on/off (DOUS)
     a.- Salida Analógica 0 / 2.5 / 5v (AOUT)
     
  SP.- Volver a sacar el menu
  ESC.- Terminar
  """

#----------------------
#   MAIN
#----------------------

serial_port = "/dev/ttyACM0"

#-- Tecla ESC
ESC = '\x1B'


#-- Frames
FRAME_DIRC_READ    = ":003000000"
FRAME_DIRC_WRITE_1 = ":006000001" 
FRAME_DIRC_WRITE_2 = ":006000002"
FRAME_DINS_READ    = ":013010000"
FRAME_AIN0_READ    = ":013020000"
FRAME_AIN1_READ    = ":013030000"
FRAME_DOUS_WRITE   = ":01604"
FRAME_AOUT_WRITE   = ":01605"

FRAME_RELE1_ON  = ":016040008"
FRAME_RELE2_ON  = ":016040004"

#--------------------------------------------------------
#-- Abrir el puerto serie. Si hay algun error se termina
#--------------------------------------------------------
try:
  s = serial.Serial(serial_port, 115200)
  
  #-- Timeout: 100 ms
  s.timeout=0.1;
  
except serial.SerialException:
  #-- Error al abrir el puerto serie
  sys.stderr.write("Error opening the port {0}".format(serial_port))
  sys.exit(1)

#-- Mostrar el nombre del dispositivo
print "Serial port: {0}\n".format(s.name)


#-- Sacar menu
menu()

#-- bucle principal
while True:

  #-- Leer tecla
  c = console_io.getkey()
  
  #-- Procesar tecla
  if c=='1': 
    send_frame(FRAME_DIRC_READ)
    
  elif c=='2': 
    send_frame(FRAME_DIRC_WRITE_1)
    
  elif c=='3': 
    digital_output_frame()
    send_frame(FRAME_DIRC_WRITE_2)
    
  elif c=='4': 
    send_frame(FRAME_DINS_READ)
    
  elif c=='5': 
    send_frame(FRAME_AIN0_READ)
    
  elif c=='6': 
    send_frame(FRAME_AIN1_READ)
    
  elif c=='7': 
    DO0_state = (DO0_state + 1) % 2
    digital_output_frame()
    
  elif c=='8': 
    DO1_state = (DO1_state + 1) % 2
    digital_output_frame()
 
  elif c=='9': 
    Rele0_state = (Rele0_state + 1) % 2
    digital_output_frame()
    
  elif c=='0': 
    Rele1_state = (Rele1_state + 1) % 2
    digital_output_frame()
    
  elif c=='a': 
    AO_state = (AO_state + 1) % 3
    send_frame(FRAME_AOUT_WRITE + AO_value[AO_state])
    
  elif c==' ': menu()
  elif c==ESC: break   #-- Salir del bucle
 
#-- Terminar 
print "-- FIN --"

#--- The end....
s.close()


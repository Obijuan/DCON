#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import console_io
import sys
import getopt
import serial
import time


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
    send_frame(FRAME_DIRC_WRITE_2)
    
  elif c==' ': menu()
  elif c==ESC: break   #-- Salir del bucle
 
#-- Terminar 
print "-- FIN --"

#--- The end....
s.close()


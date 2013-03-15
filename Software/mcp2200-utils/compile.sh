#!/bin/bash

echo "compiling..."

#-- Reading the config settings of the mcp2200 chip
gcc mcp2200.c read_config.c  -I/usr/include/libusb-1.0 -I. -lusb-1.0 -lrt -lpthread  -o read_config

#-- Configuring the mcp2200 chip for the DCON board
gcc mcp2200.c mcp2200-config.c -I/usr/include/libusb-1.0 -I. -lusb-1.0 -lrt -lpthread  -o mcp2200-config



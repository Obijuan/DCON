#!/bin/bash

echo "compiling..."


gcc mcp2200.c mcp2200-config.c -I/usr/include/libusb-1.0 -I. -lusb-1.0 -lrt -lpthread  -o mcp2200-config



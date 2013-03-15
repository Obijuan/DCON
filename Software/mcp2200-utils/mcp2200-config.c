#include <stdio.h>
#include <sys/types.h>
#include <string.h>

#include <mcp2200.h>

int connectionID;


int DCON_init(char* serial_dev)
{
  //--- Manage the MC2200 chip. Detect and configure. 

  //Init MCP2200 library
  int r = mcp2200_init();
  if (r < 0)
	  return r;

  //Count currently connected devices.
  int cnt = mcp2200_list_devices(MCP2200_VENDOR_ID, MCP2200_PRODUCT_ID);
  if (cnt < 0) return cnt;

  if (cnt == 0){
	  printf("No device found!");
	  return 0;
  }

  if (cnt > 1) {
    printf("Multiple devices, couldn't choose..");
    return 0;
  }
  
  //Connect to the only available device
  //The address of the device denotes the USB bus/port to which the device is connected
  int address = mcp2200_get_address(0);
  printf("Opening at address 0x%x\n", address);

  int connectionID = mcp2200_connect(0);

  if (connectionID < 0){
	  printf("Connection failed! Error code: %d\n", connectionID);
	  if (connectionID == -3) 
	    printf ("No rights to open!!");
	    
	  return 0;
  }

  //Configure device
  r = mcp2200_hid_configure(connectionID, 0, 0, 0, 0, 1000);
  if (r != 0){
	  printf("Configure error: %d\n", r);
  }
  
  //-- Everything is ok!!
  return 1;
}


int main(int argc, char** argv)
{
  
  
  int i;
  
  //-- Init the DCON
  int iok = DCON_init("/dev/ttyACM0");
  if (iok) {
    printf("--> CHIP MCP2200 de la DCON correctamente configurado");
  }  else {
    printf("ERROR. Chip NO configurado");
  }

  //-- END
  usleep(300000); 
  
  //Dispose driver before quitting
  mcp2200_close();
  
  return 0;
}

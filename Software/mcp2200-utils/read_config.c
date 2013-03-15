#include <stdio.h>
#include <sys/types.h>
#include <mcp2200.h>

int main(int argc, char** argv){

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
	
	if (cnt>1) {
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
		  printf ("You do not have permissions to access the device\n");
		return 0;
	}

	//-- Read the MCP2200 config
	uint8_t test;
	r = mcp2200_hid_read_io(connectionID, &test);
	if (r == 0)
	    printf ("Config READ...\n");
	else
            printf ("ERROR! reading config!");


	//Dispose driver before quitting
	mcp2200_close();
	return 0;
}
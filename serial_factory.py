import time
import usb.core
import usb.util
import serial

class SerialBase(serial.Serial):
    def __init__(self, *args, **kwargs):
        self.current_port = None
        self.N_PORTS = 7
        PID = 0xea60
        VID = 0x10c4

        self.dev = usb.core.find(idVendor=VID, idProduct=PID)
        assert self.dev, "No device found, aborting..."


        super().__init__(*args, **kwargs)

    def set_port(self, port):
        assert 0 <= port <= self.N_PORTS
        if port == self.current_port:
            print("No muxing needed")
            return
        self.current_port = port
        self.flush()

        # GPIOs are in reverse order LSB/MSB
        g_1 = (port // 4) % 2 == 1
        g_2 = (port // 2) % 2 == 1
        g_3 = port % 2 == 1
    
        reg = (g_1 << 1) | (g_2 << 2) | (g_3 << 3)
        reg = (reg << 8) | 0xff

        reqType = 0x41
        bReq = 0xff
        wVal = 0x37e1
        self.dev.ctrl_transfer(reqType, bReq, wVal, reg, [])


class MuxedSerial():
    def __init__(self, serial: SerialBase, index: int):
        self.serial = serial
        self.index = index
    
    def write(self, *args, **kwargs):
        self.serial.set_port(self.index)
        self.serial.write(*args, **kwargs)

    def read(self, *args, **kwargs):
        self.serial.set_port(self.index)
        self.serial.read(*args, **kwargs)

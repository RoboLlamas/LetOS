import serial

class TX2i:
    #TTY device string and serial connection
    tty = ""
    ser = None

    #Constructor
    #Establishes connection to TX2i over UART
    #Params: String device name
    def __init__(self, device):
        self.tty = device
        ser = serial.Serial(self.tty)

    #Init, Public
    #Initializes connection to TX2i and does SoH check
    #Returns: string response from TX2i for logging    
    #Function calls: Comm, passing 'STOP' and response legnth of 8
    def init(self):
        msg = b"STAT"
        response = self.__comm(msg, 8)
        return response

    #Start, Public
    #Sends command to TX2i to begin image capture and proccessing
    #Returns: string response from TX2i for logging
    #Function calls: Comm, passing 'STOP' and response legnth of 6
    def start(self):
        msg = b"STRT"
        response = self.__comm(msg, 6)
        return response
    
    #Stop, Public
    #Sends command to TX2i to stop image capture and processing
    #Returns: string response from TX2i for logging
    #Function calls: Comm, passing 'STOP' and response legnth of 6
    def stop(self):
        msg = b"STOP"
        response = self.__comm(msg, 6)
        return response

    #Comm, Private
    #Sends the message over the serial port
    #Params: string message, int length of expected response
    #Returns: string response from TX2i
    #Exception: returns exception if error occured
    def __comm(self, message, length):
        try:
            self.ser.write(message)
            response = self.ser.read(length)
            return response
        except Exception as e:
            return e
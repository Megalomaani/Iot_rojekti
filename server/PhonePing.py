import subprocess
import threading
import time
import datetime
import logging

LOG_FILENAME = "pinger.log"

def pingDevice(ip, pingAmount):
    #ip = '192.168.86.219'
    arg1 = '-c' + str(pingAmount)
    retval = subprocess.call(['ping', arg1 , ip], stdout=subprocess.DEVNULL, shell=False)

    return retval == 0

class wifiPinger():

    def __init__(self, ip, trigger_function, *args, pingAmount=3, pingInterval=0):
        self.phoneConnected = False
        self.pingAmount = pingAmount
        self.ip = ip#'192.168.86.219'
        self.pingInterval = pingInterval
        self.trigger_function = trigger_function
        self.trigger_args = args

        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

        pingThread = threading.Thread(target=self.phone_ping, name="PingerThread")
        pingThread.start()


    def isPhoneConnected(self):
        return self.phoneConnected

    def phone_ping(self):
        #Mihis tän nyt laittais :D
        while True:
            #print("thread")
            now = datetime.datetime.now()
            now_str = "{:02d}.{:02d} - {:02d}:{:02d}:{:02d} ".format(now.day, now.month, now.hour, now.minute, now.second)
            if pingDevice(self.ip,self.pingAmount) == True:
                if self.phoneConnected != True:
                    print("Phone connected")
                    logging.debug(now_str + "Phone connected")
                    self.run_trigger()
                self.phoneConnected = True
            else:
                if self.phoneConnected != False:
                    print("Phone disconnected")
                    logging.debug(now_str +"Phone disconnected")
                    self.run_trigger()
                self.phoneConnected = False
            time.sleep(self.pingInterval)

    def run_trigger(self):

        #todo: purkka
        str = "self.trigger_function("
        if len(self.trigger_args) != 0:
            for i in range(len(self.trigger_args)):
                str += "self.trigger_args[{}]".format(i) + ","
                #print(i)

            str = str[:-1]

        str += ")"
        try:
            eval(str)
        except TypeError:
            print("Error: Too many arguments given for trigger_function in constructor")


if __name__ == '__main__':

    def trig():
        print("Trigger")


    pinger = wifiPinger("192.168.10.33", trig)



    while True:

        print("Main loop")
        time.sleep(3)

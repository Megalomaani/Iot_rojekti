import time
import datetime
from dateutil.rrule import *
import sys
import json
import threading


class Alarm():

    def __init__(self, trigger_function, *args):

        self.currentTime = datetime.datetime.now()
        self.timer = 0
        self.trigger_function = trigger_function
        self.args = args
        self.alarms = {}

        self.readAlarms()


    def prnt(self):

        print(self.currentTime)
        for a in self.alarms.keys():
            print(self.alarms[a])


    def triggerAlarm(self, id):

        self.readAlarms()

        #todo: purkka
        str = "self.trigger_function("
        for i in range(len(self.args)):
            str += "self.args[{}]".format(i) + ","
            #print(i)

        str = str[:-1]
        str += ")"

        try:
            eval(str)
        except TypeError:
            print("Error: Too many arguments given for trigger_function in constructor")



        if self.alarms[id]["repeat"] == "no":
            self.deleteAlarm(id)
        else:
            self.startTimer()


    def setAlarm(self, name, wdays, hour, minute, repeat):

        self.readAlarms()
        self.stopTimer()

        alarm = {
            "name" : name,
            "wdays" : list(set(wdays)),
            "hour" : hour,
            "minute" : minute,
            "repeat" : repeat
        }

        alarmID = 0
        while str(alarmID) in self.alarms.keys():
            alarmID += 1
            #print(alarmID)


        self.alarms[str(alarmID)] = alarm

        #save alarms
        self.saveAlarms()
        self.startTimer()


    def readAlarms(self):
        with open("alarms.json", 'r') as infile:
            try:
                self.alarms = json.load(infile)
                return True
            except json.JSONDecodeError:
                self.alarms = {}
                #print("alarms.json empty")
                return False

    def saveAlarms(self):
        with open('alarms.json', 'w') as outfile:
            json.dump(self.alarms, outfile)

    def deleteAlarm(self,alarmID):

        self.readAlarms()
        self.stopTimer()

        if alarmID in self.alarms.keys():
            del self.alarms[alarmID]
        else:
            print("Error: Alarm ID not found!")

        self.saveAlarms()
        self.startTimer()


    def clearAlarms(self):

        self.alarms = {}
        self.saveAlarms()
        self.stopTimer()


    def startTimer(self):

        self.readAlarms()
        self.stopTimer()
        self.currentTime = datetime.datetime.now()

        nextAlarmDelta = datetime.timedelta.max
        #tim = time.time()

        if len(self.alarms) == 0:
            self.timer = 0
            return
        alarmID = 0
        for id, alarm in self.alarms.items():
            daysList = list( rrule(WEEKLY, count = len(alarm["wdays"] * 2), byweekday=tuple(alarm["wdays"])) )
            i = 0
            for day in daysList:
                day = day.replace(hour = alarm["hour"])
                day = day.replace(minute = alarm["minute"])
                day = day.replace(second = 0)
                delta = day - self.currentTime
                if delta < nextAlarmDelta and delta.days >= 0:
                    nextAlarmDelta = delta
                    alarmID = id

                #print(daysList)

        #print time until next alarm
        s = nextAlarmDelta.total_seconds()
        days, remainder = divmod(s, 3600*24)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        print("Timer start, {:02} days, {:02} hours, {:02} minutes, {:02} seconds until next alarm".format(int(days),int(hours), int(minutes), int(seconds)))
        #print(time.time()-tim)
        #todo: args to correct alarm id
        self.timer = threading.Timer(nextAlarmDelta.total_seconds(), self.triggerAlarm, args=str(alarmID))
        self.timer.name = "AlarmTimerThread"
        self.timer.start()


    def stopTimer(self):
        if self.timer != 0:
            self.timer.cancel()


def foo(a,b):
    print("a: ",a)
    b()

def bar():
    print("bar")

def debug():

    a = [1,2]
    b = bar
    alarm = Alarm(foo, a, b)
    #alarm.prnt()
    alarm.clearAlarms()
    alarm.setAlarm("ac", [0,1], 20, 26, "no")
    alarm.setAlarm("ab", [4,2], 18, 22, "weekly")
    #alarm.deleteAlarm("0")
    #alarm.prnt()
    alarm.triggerAlarm("0")
    i = 1
    while i < 60:
        print(i)
        i += 1
        if  i == 4:
            alarm.clearAlarms()
            alarm.setAlarm("ac", [0,1], 20, 25, "weekly")
        time.sleep(1)


#for debugging
if __name__ == '__main__':
    globals()[sys.argv[1]]()

# ServerUtilities - all the useful stuff

from datetime import datetime


class ServerUtilities:

    def __init__(self, mlock):
        self.masterLock = mlock
        print("ServerUtils started")

    def log(self, logEntry):
        now = datetime.now()
        stamped_logEntry = "{}: {}".format(now, logEntry)
        print("Logged: ", stamped_logEntry)

    def get_lock(self):
        return self.masterLock


import os
import os.path
from datetime import datetime
from _thread import start_new_thread

class Logger:
    def __init__(self, task_name : str):
        self.task_name = task_name
        self.root = os.path.split(__file__)[0].split(os.sep)[0:-1]
        temp = ""
        for i in self.root:
            temp += i+os.sep
        self.root = temp
        del temp
        self.error_logs = os.path.join(str(self.root),"error_logs")
        self.logs = os.path.join(self.root,"logs")
        if (not (os.path.isdir(self.error_logs) and os.path.isdir(self.logs))): self.initiator()

    def initiator(self):
        """
        Permit to generate the two log folder
        """
        if not os.path.exists(self.error_logs): os.mkdir(self.error_logs)
        if not os.path.exists(self.logs): os.mkdir(self.logs)

    def insert_error(self, error = "", code = 0, time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        start_new_thread(self.__write_error, (error, code, time,))

    def __write_error(self, error : str, code : int, time : str):
        with open(os.path.join(self.error_logs,f"TASK ERROR {self.task_name} {time.split(" ")[0]}.txt"),"a") as file:
            file.write(f"{time} -- CODE ERROR [{code}]:`\n\t")
            temp = error.split(" ")
            count = 0
            for i in range(len(temp)):
                file.write(str(temp[i])+" ")
                count += 1
                if count > 15:
                    file.write("\n\t")
                    count = 0
            separator = "###########################################################\n"
            file.write('\n\n'+separator*3+"\n")

    def insert_logs(self, msg = "", code = 0, time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        start_new_thread(self.__write_logs, (msg, code, time,))

    def __write_logs(self, msg : str, code : int, time : str):
        with open(os.path.join(self.logs,f"TASK LOGS {self.task_name} {time.split(" ")[0]}.txt"),"a") as file:
            file.write(f"{time} -- CODE LOGS [{code}]:`\n\t")
            temp = msg.split(" ")
            count = 0
            for i in range(len(temp)):
                file.write(str(temp[i])+" ")
                count += 1
                if count > 15:
                    file.write("\n\t")
                    count = 0
            separator = "###########################################################\n"
            file.write('\n\n'+separator*3+"\n")
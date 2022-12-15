"""
forwarding traffic for bouncing host to host 
assessing network-based software 

for understanding - 
unknown protocols, 
modify traffic being sent to an application
create test cases for fuzzers.

How we going to implement
4 main functions 
1. communication between local and remote machines to the console(hexdump)
2. Recieve data from socket either local or remote machine (recieve_from)
3. Manage traffic direction between remote and local machines (proxy_hanlder).
4. Set up listenning socket and pass it to proxy_hanlder(server_loop)

USAGEs 
test against FTP server:
port 21 is previlige port need sudo 
sudo python proxy.py <local ip> 21 ftp.sun.ac.za 21 True

Another terminal we start FTP session with default port 21 
ftp <local IP>

we can use command like ls, and bye for quiting from ftp server.
We can send in username and password and exit cleanly. 
"""
import sys 
import socket 
import threading 

# ASCII char printables or (.) if doesn't exist.
# list comprehension is use here and repr for formatting 
# we join back from list to string 
# boolean short shortcirut technique is use here ASCCI number between 0 -255
# if length is 3 we get chr(i) otherwise '.'
HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])



def hexdump(src, length=16, show=True):
    """
    1. communication between local and remote machines to the console(hexdump)
    # test hexdump('python rocks\n and proxies roll\n')
    """
    # make sure we got string. If we get bytes string then decode them 
    if isinstance(src, bytes):
        # decodes from bytes to string 
        src = src.decode()
        
    # initialize a default empty list ds
    results = list()
    
    
    for i in range(0, len(src), length):
        # use piece of string to dump and put it into the word variable 
        word = str(src[i:i+length])
        
        # use built-in function translate to substitute the string representation of each character for raw string
        printable = word.translate(HEX_FILTER)
        
        # subsit hex representation of integer value to raw string (hexa)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        
        # create new array to hold the strings, result, hex value of the index of the first byte in the word, and its printable representation.
        # calculate the width of hex
        hexwidth = length * 3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    # if show is True then print the hexdump 
    if show:
        for line in results:
            print(line)
    else:
        # otherwise return the hexdump as string 
        return results 

def receive_from(connection):
    """
    receive data for local and remote data to be use.
    timeout is set to 5 seconds and might be aggresive for proxy traffic to other countries or over lossy networks. 
    timeout can be increase for better performance 
    set while loop until no more data to recieve or we time out. 
    """
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data 
            
                
    except Exception as e:
        pass 
    return buffer 

"""
request_handler and response_handler methods can be use for modifying response and request packets 
perform fuzing tasks, 
test for authentication issues,
If find plaintext user credentials being sent and want to try to elevate privileges by passing in admin instead of your own username.

"""
def request_handler(buffer):
    
    # perform packet omdifications 
    return buffer 

def response_handler(buffer):
    #perform packet modifications 
    return buffer 

"""
This function contains logic of our proxy
"""
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # connect to remote hosst 
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    
    # check to make sure we don't need to first initiate a connection to 
    # the remote side and request data before going into the main loop
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        
    remote_buffer = response_handler(remote_buffer) 
    
    # send back to client if there is remote buffer 
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)
    
    while True:
        """
        receive_from is use for both sides communications. 
        It accepts connected socket object and performs a receive. 
        
        rest is straight forward: we set up our loop to continually read from the local client, 
        process the data, send it to the remote client,  
        read from remote client, process the data, and send it to the local client until we no longer detect any data.
        when local and remote are done sending data we breakout of the loop.
        """
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] Received %d bytes from localhost." % len(local_buffer)
            print(line)
            
            # dump the contes of the packet for inspection 
            hexdump(local_buffer)
            
            # hand output to request handler 
            local_buffer = request_handler(local_buffer)
            
            # send the local buffer to remote 
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")
        
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Rreceived %d bytes from remote." % len(remote_buffer))
            
            # dump the contes of the packet for inspection 
            hexdump(remote_buffer)
            
            # hand output to response handler 
            remote_buffer = response_handler(remote_buffer)
            
            # send the recieve buffer to local 
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")
        
        # no more data to send oh either side then we close remote and local and break out of the loop.
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break 
        

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    """
    
    """
    # create a socket 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # bind localhost and port then listen 
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' % e)
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit() 
        
    # start listening up to 5 clients 
    print("[*] Listening oncommand %s:%d" % (local_host, local_port))
    server.listen(5)
    
    while True:
        # start accepting connection 
        client_socket, addr = server.accept()
        # print out the local connection information 
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # start a thread to talk to the remote host 
        # fresh connection request are hand it off to the proxy_handler and create new thread 
        # proxy_handler handle sending and receiving of juicy bits to either side of data stream. 
        proxy_thread = threading.Thread(target = proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    """
    command line arguments are parse and start using server loop that listens for connections. 
    """
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]") 
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]
    
    # convert the string commandline arguments is translated to boolean value 
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False 
        
    # start the server loop 
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
    
if __name__ == '__main__':
    main() 
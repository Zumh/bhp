# we build our own tcp server because we want to use 
# build command shell or proxy server 

"""
we going to build tcp multi threaded server 
"""

import socket 
import threading 

IP = '0.0.0.0'
#IP = '127.0.0.1'

PORT = 9998

def main():
    
    # create the tcp server object 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # pass IP and PORT that we want to start listen
    server.bind((IP, PORT)) 
    
    # start listening 
    server.listen(5)
    
    # print the connection when client connect to the server 
    print(f"[*] Listening on {IP}:{PORT}")
    
    while True: 
        # get the client socket and remote connection details 
        client, address = server.accept()
        
        print(f"[*] Accepted connection from {address[0]}:{address[1]}")
        
        # let the thread handle clients 
        client_handler = threading.Thread(target = handle_client, args = (client,))
        # start the thread
        client_handler.start()

def handle_client(client_socket):
    """
    send, recieve data from a client
    """
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')
    
# start executing from __main__ and our first function will main()
if __name__ == '__main__':
    main()

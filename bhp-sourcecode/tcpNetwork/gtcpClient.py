import socket 

"""
3 assumptions
This code snippet makes some serious assumptions about sockets that you definitely want to be aware of. 
The first assumption is that our connection will always succeed, and 
The second is that the server expects us to send data first (some servers expect to send data to you first and await your response). 
Our third assumption is that the server will always return data to us in a timely fashion. 
We make these assumptions largely for simplicity’s sake.
"""
target_host = "www.google.com"
target_port = 80

# create a socket object 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client 
client.connect((target_host, target_port))
# data encode 
data = b"GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n"
# send some data
client.send(data)

# receive some data 
response = client.recv(4096)

print(response.decode())

client.close()

#print(response)

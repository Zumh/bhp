
"""
Why? build ssh_command 

Pivoting with BHNET, the netcat replacement we built, is pretty handy, but 
sometimes it’s wise to encrypt your traffic to avoid detection. A common 
means of doing so is to tunnel the traffic using Secure Shell (SSH). But 
what if your target doesn’t have an SSH client, just like 99.81943 percent 
of Windows systems?

How? 
To learn about how this library works, we’ll use Paramiko to make a 
connection and run a command on an SSH system, configure an SSH 
server and SSH client to run remote commands on a Windows machine, and 
finally puzzle out the reverse tunnel demo file included with Paramiko to 
duplicate the proxy option of BHNET.

Paramiko supports athentication with keys instead of password.
In real world SSH key authentication should be use in real engagement.

"""
import paramiko 

def ssh_command(ip, port, user, passwd, cmd):
    
    # ssh_command make connection to SSH server and rungs a single command. 
    client = paramiko.SSHClient()
    
    # Because we're controlling both ends we set policy to accept the SSH key for SSH server and make the connection. 
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # We will be using username and password. 
    client.connect(ip, port=port, username=user, password=passwd)
    
    # Assuming the connection is made, we run the command that we passed in the call to the ssh_command func. 
    # If command produce output, we print each line of the output. 
    _, stdout, stdeer = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('--- Output ---')
        for line in output:
            print(line.strip())
    
if __name__ == '__main__':
    # In the main block, we use a new module, getpass
    import getpass 
    
    """
    You can use it to get the username from the current environment, 
    but since our username is different on the two machines, 
    we explicitly ask for the username on the command line. 
    """
    # user = getpass.getuser()
    user = input('Username: ')
    
    # We then use the getpass function to request the password
    password = getpass.getpass()
    
    # Then we get the IP, port, and command (cmd) to run and send it to be executed
    ip = input('Enter server IP: ') or '192.168.190.133'
    port = input('Enter port or <CR>: ') or 2222
    cmd = input('Enter command or <CR>: ') or 'id'
    ssh_command(ip, port, user, password, cmd)
    
    
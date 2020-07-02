import socket
import select
import errno
import threading
import sys

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
my_username = input("Username: ")

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

######################################################################

"""
from tkinter import *

window= Tk()

window.geometry("1024x1024")

scrollbar = Scrollbar(window)

scrollbar.pack( side = RIGHT, fill = Y ) 

mylist = Listbox(window, yscrollcommand = scrollbar.set, width=100, height=50 ) 

def clicked():
	global mylist
	for line in range(100): 
		mylist.insert(END, 'This is line number ' + str(line))
		#return

def chat(str):
	mylist.insert(END, str) 


button=Button(text="SEND",command=clicked).place(x=720, y=900)
#button.pack()


mylist.pack( side = LEFT, fill = BOTH ) 

scrollbar.config( command = mylist.yview ) 

#window.mainloop()


"""

######################################################################


def send_msg(client_socket):
	while True:
		# Wait for user to input a message
	    message = input(f'{my_username} > ')

	    # If message is not empty - send it
	    if message:

	        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
	        message = message.encode('utf-8')
	        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
	        client_socket.send(message_header + message)
	        #print("sent,",message_header,message)


def recv_msg(client_socket):
	while True:
		try:
		    try:
		        # Now we want to loop over received messages (there might be more than one) and print them
		        while True:
		            #print("trying to receive message")

		            # Receive our "header" containing username length, it's size is defined and constant
		            username_header = client_socket.recv(HEADER_LENGTH)
		            #print("trying to receive message 2")

		            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
		            if not len(username_header):
		                print('Connection closed by the server')
		                sys.exit()

		            # Convert header to int value
		            username_length = int(username_header.decode('utf-8').strip())

		            # Receive and decode username
		            username = client_socket.recv(username_length).decode('utf-8')

		            # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
		            message_header = client_socket.recv(HEADER_LENGTH)
		            message_length = int(message_header.decode('utf-8').strip())
		            message = client_socket.recv(message_length).decode('utf-8')

		            # Print message
		            #print("Reading for messages")
		            print(f'\n\n{username} > {message}\n\n{my_username} > {}',end='')
		            #gui.mylist.insert(f'\n\n{username} > {message}\n\n{my_username} > ')

		    except IOError as e:
		        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
		        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
		        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
		        # If we got different error code - something happened
		        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
		            print('Reading error: {}'.format(str(e)))
		            return

		        # We just did not receive anything
		        #print("reached continue")
		        #continue

		    except Exception as e:
		        # Any other exception - something happened, exit
		        print('Reading error: '.format(str(e)))
		        sys.exit()
		except KeyboardInterrupt:
		    return


t1=threading.Thread(target=send_msg,args=(client_socket,))
t2=threading.Thread(target=recv_msg,args=(client_socket,))
#t3=threading.Thread(target=loop)

t1.start()
t2.start()
#t3.start()


t1.join()
t2.join()
#t3.join()

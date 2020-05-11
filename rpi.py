#Importing Libraries
import cv2
import socket
import freenect
import RPi.GPIO as GPIO

#Function to make a soft left turn
def forward(server):
	#Setting GPIO pins
	#Motor 1
	GPIO.output(3, GPIO.HIGH)
	GPIO.output(5,GPIO.LOW)

	#Motor2
	GPIO.output(11, GPIO.HIGH)
	GPIO.output(13, GPIO.LOW)

    #Running the command for 1 second
    time.sleep(1)

    #Sending Feedback
    server.send('done')

#Function to make a soft left turn
def soft_left(server):
	#Setting GPIO pins
	#Motor 1
	GPIO.output(3, GPIO.LOW)
	GPIO.output(5,GPIO.LOW)

	#Motor2
	GPIO.output(11, GPIO.HIGH)
	GPIO.output(13, GPIO.LOW)

    #Running the command for 1 second
    time.sleep(1)

    #Sending Feedback
    server.send('done')

#Function to make a soft right turn
def soft_right(server):
	#Setting GPIO pins
	#Motor 1
	GPIO.output(3, GPIO.HIGH)
	GPIO.output(5,GPIO.LOW)

	#Motor2
	GPIO.output(11, GPIO.LOW)
	GPIO.output(13, GPIO.LOW)

    #Running the command for 1 second
    time.sleep(1)

    #Sending Feedback
    server.send('done')

#Function to make a left turn
def left(server):
	#Setting GPIO pins
	#Motor 1
	GPIO.output(3, GPIO.LOW)
	GPIO.output(5,GPIO.HIGH)

	#Motor2
	GPIO.output(11, GPIO.HIGH)
	GPIO.output(13, GPIO.LOW)

    #Running the command for 1 second
    time.sleep(1)

    #Sending Feedback
    server.send('done')

#Function to make a right turn
def right(server):
	#Setting GPIO pins
	#Motor 1
	GPIO.output(3, GPIO.HIGH)
	GPIO.output(5,GPIO.LOW)

	#Motor2
	GPIO.output(11, GPIO.LOW)
	GPIO.output(13, GPIO.HIGH)

    #Running the command for 1 second
    time.sleep(1)

    #Sending Feedback
    server.send('done')

#Function to stop
def stop(server):
	#Setting GPIO pins
	#Motor 1
	GPIO.output(3, GPIO.LOW)
	GPIO.output(5,GPIO.LOW)

	#Motor2
	GPIO.output(11, GPIO.LOW)
	GPIO.output(13, GPIO.LOW)

    #Running the command for 1 second
    time.sleep(1)

    #Sending Feedback
    server.send('done')

#Function to send image
def send_img(type):

    if type == 'image':
        frame = freenect.sync_get_video()[0]
    elif type == 'depth':
        frame = freenect.sync_get_depth()[0]

    #Saving Image
    cv2.imwrite('send.jpg', frame)
	file_name = "test.jpg"
    # Send The File name to the recieve function
	server.send(file_name.encode())
    # open The Selected File
	file = open(file_path,'rb')
	for i in file:
	    server.send(i) # send the data to the reciever

	file.close()
	server.close()

#Main function
def main():
    # Intialising TCP server AF_NET is used For TCP Network
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Getting Host Name
    host = server.gethostname()

    #Using any random port number
    #Port Number used for both client and server should be same
    port = 12345

    #Connecting to server using host address and port
    server.connect((host, port))

    while True:
        msg = server.recv(1024)
        #If recieved msg is image
        if msg == 'image':
            send_img('image', server)
        #If recieved msg is depth
        elif msg == 'depth':
            send_img('depth', server)
        #If recieved msg is forward
        elif msg == 'forward':
            forward(server)

if __name__ == "__main__":
    main()

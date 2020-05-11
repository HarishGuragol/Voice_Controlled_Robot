#Importing Libraries
import os
import cv2
import time
import struct
import socket
import pyaudio
import freenect
import wikipedia
import playsound
import numpy as np
from gtts import gTTS
from scripts.rhino.rhino import *
from scripts.porcupine.porcupine import *

#Fucntion to get images
def get_image(type, client):     #'type' to tell about RGB image/depth image

	path = ""
	file = open(path,'w')
	file.write(IPaddr)
	file.close()

	#Sending the type of Image
	client.send(type)

	# It will wait until it gets the file name which is passed from the send function
	file_name = client.recv(1024).decode()
	print(file_name)
	# This will open a new file in your python Dir with same file name
	file = open(file_name,'wb')
	# It will recieve the starting 10 bytes
	data = client.recv(10)
	while data:
	    #print(data)
	    file.write(data)
	    data = client.recv(1024)

	print("Data Recieved Succesfully")
	client.close()

	#returning RGB or depth image
	image = cv2.imread(file_name)
	return image

#Function to check if center cit ent
def co_incident():
	pass

#Function to go to an object
def goTo(slots, net, LABELS, ln, client):

	#Getting the Value of the Key in Dictonary-Slots
	obj = str(slots['ob1'])

	#Initializing the variables
	x = y = z = None

	#Getting the coordinated of the object
	(x,y,z) = getCoordinates(obj, net, LABELS, ln, client)

	#Checking if the object was found or not
	if x == None or y == None or z == None:

		#Speaking that object was not found
		print("None here")
		playsound.playsound('not_found.mp3')

	else:
		#Ensuring the centers co-incident
		co_incident()

		print(x,y,z)
		#Move towards the object
		while z>=0.0:

			#Move forward and check the distance again
			send(client, "forward")
			time.sleep(1)
			(x,y,z) = getCoordinates(obj, net, LABELS, ln, client)


#Function to get the coordinated of the given object
def getCoordinates(obj, net, LABELS, ln, client):

	while True:

		#Get Images from Rpi
		frame = get_image("image", client)

		#Get Depth Image from Rpi
		depth = get_image("depth", client)

		#Fetting Shape of the frame
		(H, W) = frame.shape[:2]

		#Creating blob from image
		blob = cv2.dnn.blobFromImage(frame, 1/255.0, (224, 224), swapRB = True, crop = False)
		net.setInput(blob)
		layerOutputs = net.forward(ln)

		#Initializing lists for displaying the output
		boxes = []
		confidences = []
		classIds = []

		#Looping over each layer's output
		for output in layerOutputs:

			#Looping over each detection
			for detect in output:

				#Extracting ClassID and confidence
				score = detect[5:]
				classID = np.argmax(score)
				confidence = score[classID]

				#Filtering weak detection
				if confidence > 0.5:

					#Getting bounding rectangle
					box = detect[:4] * np.array([W, H, W, H])
					(centerX, centerY, Width, Height) = box.astype("int")

					#Getting Top and Left Points
					x = int(centerX - (Width/2))
					y = int(centerY - (Height/2))

					#Adding to lists
					boxes.append([x, y, int(Width), int(Height)])
					classIds.append(classID)
					confidences.append(float(confidence))

				#Non-Maxia Suppression
				idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)

				#Checking Minimum Detection
				if len(idxs) > 0:

					#Looping over indexs
					for i in idxs.flatten():

						x = boxes[i][0]
						y = boxes[i][1]
						w1 = boxes[i][2]
						h1 = boxes[i][3]

						if LABELS[classIds[i]] == obj:
							#Calculating the coordinates
							print("Here")
							cx = int(x + (w1/2))
							cy = int(y + (h1/2))
							cz = 0.1236 * np.tan(depth[cy][cx] / 2842.5 + 1.1863)
							return (cx,cy,cz)


#Function to speak/interact
def speak(slots):

	#Getting the Value of the Key in Dictonary-Slots
	keyword = str(slots['p1'])

	#If the keyword in known
	if keyword == "yourself":

		#Declaring the text
		splitted = ["Hey, my name is groooot. I am a cute, cute robooooo. I am designed by Gaurav, Harish and Swati, and I work for them. Nice meeting you. I am here to help you, just spell groooooot."]

	#If keyword is not known
	else:

		#Searching
		search_result = wikipedia.summary(keyword)

		#Spliting
		splitted = search_result.split("\n")


	#Speech to text model
	speech = gTTS(text = splitted[0], lang = 'en-in' , slow = False)

	#Saving Audio File
	speech.save("speak.mp3")

	#Running Audio file
	playsound.playsound('speak.mp3')



def send(client, dir):

	#Sending data to server
	client.send(dir)

	#Waiting for feedback
	while client.recv(1024)!= 'done':
		pass

	client.close()

#Main Function
def main():

	#Initializing Variables
	awake = False
	intent_extraction_is_finalized = False

	#Loading Picovoice Models
	rhino_wakeword = Porcupine(library_path = "/home/garima/Gaurav/Blog_2/Integrated/res/libpv_porcupine.so",
								model_file_path = "/home/garima/Gaurav/Blog_2/Integrated/res/porcupine_params.pv",
								keyword_file_paths = ["/home/garima/Gaurav/Blog_2/Integrated/res/hey_groot.ppn"],
								sensitivities = [0.5])

	rhino_commands = Rhino(library_path = "/home/garima/Gaurav/Blog_2/Integrated/res/libpv_rhino.so",
							model_path = "/home/garima/Gaurav/Blog_2/Integrated/res/rhino_params.pv",
							context_path = "/home/garima/Gaurav/Blog_2/Integrated/res/robo.rhn")

	# setup audio
	pa = pyaudio.PyAudio()
	audio_stream = pa.open(rate = rhino_commands.sample_rate,
							channels = 1,
							format = pyaudio.paInt16,
							input = True, frames_per_buffer=rhino_commands.frame_length)

	#Loading label, weight and configuration model paths for YOLO
	labelPath = os.path.sep.join(["yolo-coco","coco.names"])
	weightPath = os.path.sep.join(["yolo-coco", "yolov3.weights"])
	configPath = os.path.sep.join(["yolo-coco", "yolov3.cfg"])

	#Loading Labels
	LABELS = open(labelPath).read().strip().split("\n")

	#Loading YOLO
	net = cv2.dnn.readNetFromDarknet(configPath, weightPath)

	#Determining YOLO output layer
	ln = net.getLayerNames()
	ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

	#Setting up Rpi GPIO pins numbering
	#GPIO.setmode(GPIO.BOARD)

	#Declaring Pin modes
	#GPIO.setup(3, GPIO.OUT)
	#GPIO.setup(5, GPIO.OUT)
	#GPIO.setup(11, GPIO.OUT)
	#GPIO.setup(13, GPIO.OUT)

	#Making Commonly used Audio Files
	#Speech to Text
	wake = gTTS(text = "At your service friend!", lang = "en-in", slow = False)
	error = gTTS(text = "I'm tired! I will take a nap.", lang = "en-in", slow = False)
	not_found = gTTS(text = "Object not found!", lang = "en-in", slow = False)
	not_understood = gTTS(text = "I understand your order friend", lang = "en-in", slow = False)

	#Saving Audio File
	wake.save("wake.mp3")
	error.save("error.mp3")
	not_found.save("not_found.mp3")
	not_understood.save("unclear.mp3")

	#Sockets Initializing
	network = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	# Intialising the Port
	port = 12345
	network.bind(('',port))

	hostname = socket.gethostname()
	IPaddr = socket.gethostbyname(hostname)

	network.listen(5)

	# Geting Client host name and the IP address Details
	client, addr = network.accept()

	print("Start")

	# detect commands in continuous loop
	while True:

		#Reading Input
			pcm = audio_stream.read(rhino_commands.frame_length)
			pcm = struct.unpack_from("h" * rhino_commands.frame_length, pcm)

			try:
				#If wake word is not spoken
				if not awake:

					#Processing the voice input
					result = rhino_wakeword.process(pcm)

					#If wake word is the input, result is true
					if result:

						#Wake Word detected
						awake = True
						time.sleep(0.1)
						print("awake")
						#playsound.playsound('wake.mp3')
						#os.system('mpg321 wake.mp3')
						#time.sleep(5)
						print("Speak More")

				elif not intent_extraction_is_finalized:

					#Getting Intent Extraction
					intent_extraction_is_finalized = rhino_commands.process(pcm)

				else:

					#If the command is detected
					if rhino_commands.is_understood():

						#Getting Intent and Slots
						intent, slots = rhino_commands.get_intent()
						print(intent)
						playsound.playsound('wake.mp3')
						#os.system('mpg321 wake.mp3')

						#Checking Intent and doing Neccessary Action
						#If going to an object is an intent
						if intent == "goTo":
							#Shift the control to goTo function
							goTo(slots, net, LABELS, ln, client)

						#If speaking is the intent
						elif intent == "speak":
							#Shift the control to speak function
							speak(slots)

						#If coming back in the intent
						#elif intent == "comeBack":
							#Shift the control to comeBack function
							#comeBack(slots)

						#If Stop is the intent
						elif intent == "stop":
							#Shift the control to stop function
							stop()

						#No match
						else:
							#Command not found
							time.sleep(0.1)
							print("1")
							playsound.playsound('unclear.mp3')

					#Command not understood
					else:
						#print("Command not understood")
						time.sleep(0.1)
						playsound.playsound('unclear.mp3')

					#Resetting Rhino to detect new command
					rhino_commands.reset()
					awake = False
					intent_extraction_is_finalized = False

			except Exception as e:
				print(e)
				time.sleep(0.1)
				playsound.playsound('error.mp3')
				exit()
				#os.system('python3 try_1.py')

#Calling Main Funciton
if __name__ == "__main__":
	main()

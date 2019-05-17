import time
import grovepi
import cv2
import firebase_admin
from firebase_admin import credentials, firestore, storage
from firebase_admin import db

relay = 4
fb_credentials = credentials.Certificate('deets.json')

firebase_admin.initialize_app(fb_credentials, {
'storageBucket': 'iotproject-bbb12.appspot.com',
'databaseURL' : 'https://iotproject-bbb12.firebaseio.com/'
})
def upload():

    db = firestore.client()
    bucket = storage.bucket()
    blob = bucket.blob('door.png')
    outfile='door.png'
    global picurl
    with open(outfile, 'rb') as my_file:
        blob.upload_from_file(my_file)
        blob.make_public()
        picurl = blob.public_url
        return (blob.public_url)
def dblisten():

    ref = db.reference('users')
    doorval = db.reference('users/doorOpen').get()

    #doorval =  (next(iter(data.items())))
    #print(data)
    if "true" in  doorval:
        grovepi.digitalWrite(relay,0)
        time.sleep(5)
        grovepi.digitalWrite(relay,1)


def dbUpload():
    try:
        print (picurl)
        print("Success")
        global ref
        # root
        ref = db.reference()
        ref.set(
                {
                'users':{
                    'url': 'false',
                    'doorOpen': 'false'
                    }

                    }
                )
        ref = db.reference('users')
        ref.update({
                'url': picurl
                })
    except IOError as e:
        print("Something went wrong" + e)
def takepic():
    cam = cv2.VideoCapture(0)
    retval, frame = cam.read()
    if retval != True:
        raise ValueError("Can't read frame")

    cv2.imwrite('door.png', frame)
    cv2.waitKey()
    cam.release()
def lightsen():
    # Connect the Grove Light Sensor to analog port A0
    # SIG,NC,VCC,GND
    light_sensor = 0



    # Turn on LED once sensor exceeds threshold resistance
    threshold = 10

    grovepi.pinMode(light_sensor,"INPUT")


    while True:
        try:
            # Get sensor value
            sensor_value = grovepi.analogRead(light_sensor)

            # Calculate resistance of sensor in K
            resistance = (float)(1023 - sensor_value) * 10 / sensor_value

            if resistance > threshold:
                # Send HIGH to switch on LED
                dblisten()

            else:
                # Send LOW to switch off LED
                takepic()
                upload()
                dbUpload()





                print("picture has been taken")

            #print("sensor_value = %d resistance = %.2f" %(sensor_value,  resistance))
            time.sleep(.5)

        except IOError:
            print ("Error")
lightsen()

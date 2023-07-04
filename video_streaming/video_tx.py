import socket
import cv2
import numpy as np
import threading
import time
import json

TCP_IP = "192.168.50.36"
TCP_PORT = 8002
sock = socket.socket()
sock.connect((TCP_IP, TCP_PORT))
quality=90
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),quality]


def calculate_psnr(img1, img2):
    # Read the images
    #img1 = cv2.imread(img1)
    #img2 = cv2.imread(img2)
    #print(img1.shape)
    #print(img2.shape)
    height, width, channels = img1.shape
    height2, width2, channels = img2.shape
    if height!=height2 or width!=width2:
        img2= cv2.resize(img2, (width, height))
    # Calculate the MSE (Mean Squared Error)
    #img1=np.asarray(img1)
    #img2=np.asarray(img2)
    mse = np.mean((img1 - img2) ** 2)
    #print((img1-img2).shape)
    
    # Calculate the maximum pixel value
    max_pixel = 255.0

    # Calculate the PSNR using the MSE and maximum pixel value
    psnr = 10 * np.log10(max_pixel**2 / mse)

    return psnr

class CamThread(threading.Thread):
    def run(self):
        global frame
        global cam
        #cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cam = cv2.VideoCapture(0)
        while True:
            if cv2.waitKey(1) & 0xFF == ord('w'):
                if quality<=90:
                    quality+=5
                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),quality]
                print("quality:{}".format(quality))
            if cv2.waitKey(1) & 0xFF == ord('s'):
                if quality>=10:
                    quality-=5
                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),quality]
                print("quality:{}".format(quality))

            ret, frame = cam.read()
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            #-----calculate psnr-----
            new_image = np.frombuffer(imgencode, np.uint8)
            new_image=cv2.imdecode(new_image,1)
            psnr=calculate_psnr(frame, new_image)
            print("PSNR:{:.2f}dB".format(psnr))
            #-----calculate psnr end------
            data = np.array(imgencode)
            stringData = data.tostring()

            #-------PSNR、frame size to json-----
            json_msg={"PSNR":psnr, "size":len(stringData),'time': time.time()}
            json_msg=json.dumps(json_msg)
            sock.send(json_msg.ljust(200).encode('utf-8'))
            #sock.send( (str(len(stringData)).ljust(16)).encode('utf-8'))
            sock.send( stringData )
        sock.close()
        cam.release()
        cv2.destroyAllWindows()





cam_t=CamThread()
cam_t.start()



    






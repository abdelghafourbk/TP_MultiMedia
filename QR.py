from ast import keyword
from random import random
from turtle import end_fill
from typing import List
from PIL import Image
from cv2 import imread
import numpy as np
import cv2
import warnings
import pyqrcode 
from pyqrcode import QRCode 
import qrcode
import itertools

#----------------------------------------------------Fonctions de la prof ---------------------------------#
#codage rle 
def encode(image, file_name='compressed_image.txt', bits=15):

    count_list = []
    count = 0
    prev = None
    fimage = image.flatten()
    size = 2**(bits+1) - 2**bits #32768 = 8000H
    
    for pixel in fimage:
        
        if prev == None:
            prev = pixel # first pixel 
            count += 1
        else:
            if prev != pixel: # The current pixel is different from the previous one
                if count >= 3:
                    count_list.append((size+count, [prev]))
                else:
                    if  count_list == []:
                        count_list.append((count, [prev]*count)) 
                    else: 
                        c, color = count_list[-1]
                        if c > size: 
                            count_list.append((count, [prev]*count))
                        else:
                            if c+count <= (2**bits)-1: # Make sure that we didn't use all of the 15 bits reserved for the color's sequence length 
                                count_list[-1] = (c+count, color+[prev]*count)
                            else:
                                count_list.append((count, [prev]*count))
                prev = pixel
                count = 1
            else: # The current pixel is like the previous one
                if count < (2**bits)-1: # Make sure that we didn't use all of the 15 bits reserved for the number of repetitions 
                    count += 1                    
                else:
                    count_list.append((size+count, [prev]))
                    prev = pixel
                    count = 1

    if count >= 3:
        count_list.append((size+count, [prev]))
    else:
        c, color = count_list[-1]
        if c > size:
            count_list.append((count, [prev]*count))
        else:
            if c+count <= (2**bits)-1:
                count_list[-1] = (c+count, color+[prev]*count)
            else:
                count_list.append((count, [prev]*count))

    # Hexa encoding
    with open(file_name,"w") as file:
        hexa_encoded = "".join(map(lambda x: "{0:04x}".format(x[0])+"".join(map(lambda y: "{0:02x}".format(y), x[1])), count_list))
        """ hexa_encoded = ""
        for count, colors in count_list:
            hexa_encoded += "{0:04x}".format(count)
            for color in colors:
                hexa_encoded += "{0:02x}".format(color) """
        file.write(hexa_encoded)
        
    # Compression rate
    rate = (1-(len(hexa_encoded)/2)/len(fimage))*100
    
    return hexa_encoded, rate

def decode(height, width, file_name='compressed_image.txt', bits=15):

    # Read the entire code from the file
    with open(file_name, "r") as file:
        code = file.readlines()[0]
        
    # Loop through the code and get the color of the pixels
    size = 2**(bits+1) - 2**bits  #32768 
    i = 0
    data = []
    while i < len(code):
        count = code[i:i+4]
        count = int(count, 16)
        i += 4
        if count > size: 
            # Here the color is repeated 3 times or more
            count -= size
            color = code[i:i+2]
            color = int(color, 16)            
            data += [color]*count
            i += 2
        else: 
            # Here each color is repeated less than 3 times
            color_seq = code[i:i+count*2]
            colors = [int(color_seq[idx:idx+2], 16) for idx in range(0, len(color_seq), 2)]
            data += colors
            i += count*2

    image = np.zeros((height, width)).astype(np.uint8)
    for k, (i, j) in enumerate(itertools.product(range(height), range(width))):
        image[i, j] = data[k]

    return image

#------------------------------------------------------------Fonctions code QR ------------------------------#
#creer le qr code a partir d'une image 
def create_qr(image):
   #image=cv2.imread(image)
   list=[] 
   list_img=[]
   encoded, rate = encode(image, file_name='compressed.txt', bits=15)
   taille=len(encoded)
   s=""
   for i in range (taille):
    #pour ne pas avoir ne overflow on decoupe la grande chaine 
    if len(s)<2200:
       s=s+encoded[i]
    else:
        list.append(s)
        s=""
   # la derniere chaine soit ajouté dans la liste 
   list.append(s)
   k=0
   #parcourir la liste des chaines decouper  
   for j in list: 
      qr = qrcode.make(j)
      qr.save('img'+str(k)+'.png')
      #garder les noms des images pour le decodage  
      list_img.append('img'+str(k)+'.png')
      k=k+1
 
   return list_img
     
     
def decode_qr(list_img):

    val_final=""
    detecteur = cv2.QRCodeDetector()
    #parcourir la liste des noms des images 
    for i in  list_img:      
        imageqr = cv2.imread(i)
        val,b,c=detecteur.detectAndDecode(imageqr)
        #rassembler toutes les valeurs des chaines decouper 
        val_final=val_final+val

    fdecodeqr = open("data.txt", "a")
    #ecrire la chaine final dans un fichier 
    fdecodeqr.write(val_final)
    #decodage 
    imgdecqr= decode(12,12, file_name='data.txt', bits=15)    
    return imgdecqr

# --------------------utiliser resize au lieu de plusieur qr code ----------------#
def create_qr_resize(image):
    imageR=cv2.resize(image,(16,16),interpolation = cv2.INTER_AREA)
    encoded, rate = encode(imageR, file_name='compressed.txt', bits=15)
    qr = qrcode.make(encoded)
    qr.save('img.png')

def decode_qr_resize(image):
    detecteur = cv2.QRCodeDetector()
    imageqr = cv2.imread(image)
    val,b,c=detecteur.detectAndDecode(imageqr)
    fdecodeqr = open("data.txt", "a")
    #ecrire la chaine final dans un fichier 
    fdecodeqr.write(val)
    #decodage 
    imgdecqr= decode(12,12, file_name='data.txt', bits=15)    
    return imgdecqr


#---------------------------------------------main code --------------------------------------------------------#

image1=cv2.imread("16x16.png")
encoded, rate = encode(image1, file_name='compressed.txt', bits=15)
print(encoded)

#taut de  compression 
encoded, rate = encode(image1, file_name='compressed1.txt', bits=15)
print (f'Compression rate :{rate:.02f}%') 

#creer qrcode 
list_img=create_qr(image1)
print (decode_qr(list_img))

#decode 
data= decode_qr(list_img)

#creer image 
compressed_image = Image.fromarray(data, mode='L')
compressed_image.show()
compressed_image.save('decompressed.png')

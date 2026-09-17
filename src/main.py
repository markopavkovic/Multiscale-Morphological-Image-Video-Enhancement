import plotly.express as px
from skimage import io
import numpy as np
from skimage.transform import rescale,resize
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from skimage import exposure

from scipy import signal
from scipy import ndimage

import math

from skimage import color

from skimage import morphology
from skimage import img_as_float32, img_as_ubyte


def multiscale_morphological_contrast_enhancement(input_data, alfa, lista_velicina_se):
    if isinstance(input_data, str):
        img = io.imread(input_data, as_gray=True)
    else:
        img = input_data

    f = img.astype(np.float32)
    if f.max() > 1.0:
        f /= 255.0

    suma_wth = np.zeros_like(f)
    suma_bth = np.zeros_like(f)
    for k in lista_velicina_se:
        se = morphology.disk(k)
        wth = morphology.white_tophat(f, se)
        bth = morphology.black_tophat(f, se)
        suma_wth += alfa * wth
        suma_bth += alfa * bth

    f_out = f + suma_wth - suma_bth
    f_out = np.clip(f_out, 0, 1)
    gama = 0.7
    f_out = np.power(f_out, gama)
    return img_as_ubyte(f_out)


def enhancement_rgb(slika_rgb, alfa, lista_se):
    img_hsv = color.rgb2hsv(slika_rgb)

    v_kanal = img_hsv[:, :, 2]
    v_enhanced = multiscale_morphological_contrast_enhancement(v_kanal, alfa, lista_se)

    img_hsv[:, :, 2] = v_enhanced.astype(np.float32) / 255.0

    return color.hsv2rgb(img_hsv)



#Prikaz RGB slike
#img_kolor = io.imread('lena_color.png')
#rezultat_kolor = enhancement_rgb(img_kolor, 100, [5,25,50])

#plt.figure(figsize=(15,7))
#plt.subplot(1,2,1)
#plt.title('Original')
#plt.imshow(img_kolor)
#plt.subplot(1,2,2)
#plt.title("Multiscale Enhancement (RGB)")
#plt.imshow(rezultat_kolor)
#plt.show()


#Prikaz sive slike
#img_original=io.imread('lisbon.jpg',as_gray=True)

#rezultat = multiscale_morphological_contrast_enhancement('lisbon.jpg', 50, [3, 7, 15])

#plt.figure(figsize=(15,7))
#plt.subplot(1,2,1)
#plt.title('Original')
#plt.imshow(img_original,cmap='gray')
#plt.subplot(1,2,2)
#plt.title('Morfološka Top-Hat transformacija')
#plt.imshow(rezultat,cmap='gray')
#plt.show()

import os
import cv2


def enhancement_rgb_video(slika_rgb, alfa, lista_se):
    img_hsv = color.rgb2hsv(slika_rgb)
    v_kanal = img_hsv[:, :, 2]
    v_enhanced = multiscale_morphological_contrast_enhancement(v_kanal, alfa, lista_se)
    img_hsv[:, :, 2] = v_enhanced.astype(np.float32) / 255.0
    rgb_out = color.hsv2rgb(img_hsv)

    return (np.clip(rgb_out, 0, 1) * 255).astype(np.uint8)



def obradi_video(putanja_ulaz, putanja_izlaz, alfa=1, lista_se=[3, 7, 15]):
    cap = cv2.VideoCapture(putanja_ulaz)
    if not cap.isOpened():
        print(f"GRESKA: Video nije pronadjen na lokaciji: {putanja_ulaz}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(putanja_izlaz, fourcc, fps, (width, height))

    print("---------------------------------------")
    print("OBRADA VIDEA JE POCELA...")
    print("Pritisni 'q' na tastaturi da prekines.")
    print("---------------------------------------")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        processed_rgb = enhancement_rgb_video(frame_rgb, alfa, lista_se)


        final_frame = cv2.cvtColor(processed_rgb, cv2.COLOR_RGB2BGR)


        out.write(final_frame)

        cv2.imshow('Obrada Videa (Q za kraj)', final_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("---------------------------------------")
    print(f"ZAVRSENO! Video je sacuvan: {putanja_izlaz}")
    print("---------------------------------------")


korisnik = os.getlogin()
putanja_ulaz = f"C:\\Users\\{korisnik}\\Documents\\Traffic.mp4"
putanja_izlaz = f"C:\\Users\\{korisnik}\\Documents\\Traffic_Poboljsan.avi"

obradi_video(putanja_ulaz, putanja_izlaz)

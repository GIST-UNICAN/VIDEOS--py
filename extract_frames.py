import cv2
import argparse
import os
import glob
from datetime import datetime
from zipfile import ZipFile
from ftplib import FTP
from contextlib import closing
from os.path import basename

def extractImages(pathIn, pathOut, fps):
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    success,image = vidcap.read()
    success = True
    while success:
      vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*(1000/fps)))    # added this line 
      success,image = vidcap.read()
#      print ('Read a new frame: ', success)
      nombre=basename(pathIn)[:-4]
      cv2.imwrite( pathOut + f"/{nombre}-"+str(int(fps))+"-" + str(count).zfill(8)+".jpg", image)     # save frame as JPEG file
      count = count + 1

if __name__ == "__main__":
    datos_ftp = {"host":"rampillas.synology.me", "user":"rampillas", 'passwd':"roma2014" }
    hoy = datetime.now()
    dia, mes, año = map(lambda x: getattr(hoy,x), ("day", "month", "year"))
    ruta_actual=os.getcwd()
    # sacar rutas
    rutas=glob.glob(ruta_actual+r'\*.mov')
    # procesar
    directorio_imagenes = ruta_actual + f"\\{año}-{mes}-{dia}"
    if not os.path.isdir(directorio_imagenes):
        os.mkdir(directorio_imagenes)
    
    for ruta in rutas:
        extractImages(ruta, directorio_imagenes, 0.5)
    ruta_zip = directorio_imagenes + ".zip"
    with ZipFile(ruta_zip, "w") as archivo_zip:
        archivo_zip.write(directorio_imagenes)
    with closing(FTP(**datos_ftp)) as sesion, open(ruta_zip,
                "rb") as archivo:
        sesion.storbinary("STOR {}".format(basename(ruta_zip)), archivo)
        sesion.quit()
        
    
    
    
            
    # comprimir
#    # enviar ftp 
#    ruta
#    lista_videos
#    extractImages(r"D:\Users\Andres\Escritorio\20180417_0630_0930\0 - 2018-04-17 06-30-00-709.mov",
#                  r"D:\Users\Andres\Escritorio\20180417_0630_0930\out", 
#                  0.5)
#    parser = argparse.ArgumentParser(description='Extract frames from a video')
#    parser.add_argument('--video', type=str, required=True, help='Video path')
#    parser.add_argument('--dest', type=str, required=True, help='Destination folder')
#    parser.add_argument('--fps', type=float, required=True, help='Frame rate')
#    args = parser.parse_args()
   
#    extractImages(args.video, args.dest, args.fps)


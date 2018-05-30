import argparse
import os
import glob
from datetime import datetime
from zipfile import ZipFile
from ftplib import FTP, error_perm
from contextlib import closing
from os.path import basename
import urllib.request
import time
from persistqueue import Queue
from threading import Thread
import traceback
import logging
import pysftp


def descarga_camaras(cola,salva_cada):
    def crea_foto(ruta_archivo,camara):
        with open(ruta_archivo,'wb') as foto:
            foto.write(urllib.request.urlopen('http://192.168.0.{}/snap.jpg?JpegSize=M&JpegCam={}'.format(camara[0],camara[1])).read())
        
    print(datetime.now())
    ip_camaras=((120,1),(120,2),(120,4),(120,8),(120,5),(120,6),(120,7),(120,9),(121,10),(122,14),(122,15),(122,1),(122,2),(122,3),(122,4),(122,5),(122,6),(122,7),(122,8),(122,9),(122,13))
    while True:
        inicio=datetime.now()
        inicio_str=datetime.strftime(inicio,'%H_%M_%S')
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
        for camara in ip_camaras: 
            ruta_archivo=r'camaras_web/{}_{}_{}.jpg'.format(inicio_str,camara[0],camara[1])
            try:
                crea_foto(ruta_archivo,camara)         
            except Exception as e:
                logging.exception('Error al crear el archivo {}'.format(ruta_archivo))
                pass
            else:
                try:
                    cola.put(ruta_archivo)
                except:
                    logging.exception('Error al poner en cola el archivo {}'.format(ruta_archivo))
                    time.sleep(2)
        fin=datetime.now()
        time.sleep(salva_cada-((fin-inicio).seconds+(fin-inicio).microseconds)/1000000)

def sube_ftp(cola,cola_borrar):  
    datos_ftp = {"host":"193.144.208.142", "user":"camaras_kml", 'passwd':"kfahjdlkj78908+-" }
    while True:
        try:
            with closing(FTP(**datos_ftp)) as sesion:
                sesion.cwd('camaras')
                while True:
                    ruta=cola.get()
                    with open(ruta, "rb") as archivo:
                        try:
                            sesion.storbinary("STOR {}".format('/'+ruta[21:]), archivo)                          
                        except Exception as e:
                            logging.exception('Error al subir el archivo {} msg'.format(ruta[11:]))
                            cola.put(ruta)
                            sesion.quit()
                            break
                        else:
                            cola_borrar.put(ruta)

                                
        except Exception as e:
            time.sleep(5)
            logging.exception('Error FTP ')
            pass

        
def borra_viejos(cola_borrar):
    while True:
        ruta=cola_borrar.get()
        try:
            os.remove(ruta)
##            print('borrado')
        except FileNotFoundError:
            pass
        except Exception as e:
##            print('error {}'.format(str(e)))
            cola_borrar.put(ruta)
            logging.exception('Error borrando {}'.format(ruta))
            time.sleep(5)
                

     
if __name__ == "__main__":
    salva_cada=2
    logging.basicConfig(filename='sube_videos_web.log',level=logging.WARNING)
    cola = Queue('sube_web')
    cola_borrar = Queue('borra_web')
    Thread(target=descarga_camaras, args=(cola,salva_cada)).start()
    Thread(target=sube_ftp, args=(cola,cola_borrar)).start()
    Thread(target=borra_viejos, args=(cola_borrar,)).start()

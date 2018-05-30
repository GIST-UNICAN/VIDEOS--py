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

def upload_file(directorio,file):
    options=pysftp.CnOpts()
    options.hostkeys=None
    with pysftp.Connection('212.123.203.86', username='seta', password='q2+zpx2kayOKKO7z',cnopts=options) as sftp:
        try:
            with sftp.cd('data/cameras/{}'.format(directorio)):
                sftp.put(file)  
        except FileNotFoundError:
            sftp.mkdir('data/cameras/{}'.format(directorio))
            with sftp.cd('data/cameras/{}'.format(directorio)):
                sftp.put(file) 

def descarga_camaras(cola,salva_cada):
    def crea_foto(ruta_archivo,camara):
        with open(ruta_archivo,'wb') as foto:
            foto.write(urllib.request.urlopen('http://192.168.0.{}/snap.jpg?JpegSize=M&JpegCam={}'.format(camara[0],camara[1])).read())
        
    print(datetime.now())
##    ip_camaras=((122,14),(122,4),(122,6),(122,9),(122,10),(121,4),(121,10),(120,1),(120,8),(120,10),(120,2))
    ip_camaras=((122,14),(122,4))
    while True:
        inicio=datetime.now()
        inicio_str=datetime.strftime(inicio,'%H_%M_%S_%f')
        directorio=datetime.strftime(inicio,r'%Y_%m_%d')
        for camara in ip_camaras: 
            ruta_archivo=r'camaras/{}/{}_ip_{}_cam_{}.jpg'.format(directorio,inicio_str,camara[0],camara[1])
            try:
                crea_foto(ruta_archivo,camara)         
            except FileNotFoundError:
                os.mkdir(r'camaras/{}'.format(directorio))
                logging.warning('El directorio {} ha sido creado'.format(desktop,directorio))
                try:     
                    crea_foto(ruta_archivo,camara)
                except:
                    raise
                else:
                    try:
                        cola.put((ruta_archivo,directorio))
                    except Exception as e:
                        logging.exception('Error al manipular la cola con archivo {}'.format(ruta))
            except Exception as e:
                logging.exception('Error al crear el archivo {}'.format(ruta_archivo))
                pass
            else:
                try:
                    cola.put((ruta_archivo,directorio))
                except:
                    logging.exception('Error al poner en cola el archivo {}'.format(ruta_archivo))
                    time.sleep(2)
        fin=datetime.now()
        time.sleep(salva_cada-((fin-inicio).seconds+(fin-inicio).microseconds)/1000000)

def sube_ftp(cola,cola_borrar):  
    datos_ftp = {"host":"193.144.208.142", "user":"ftpserver", 'passwd':"kjgbhr867kk,m-+`" }
    while True:
        try:
            with closing(FTP(**datos_ftp)) as sesion:
                options=pysftp.CnOpts()
                options.hostkeys=None
                with pysftp.Connection('212.123.203.86', username='seta', password='q2+zpx2kayOKKO7z',cnopts=options) as sftp:
                    sesion.cwd('camaras')
                    while True:
                        ruta, directorio=cola.get()
                        with open(ruta, "rb") as archivo:
                            try:
                                sesion.storbinary("STOR {}".format(ruta[8:]), archivo)
                                try:
                                    with sftp.cd('data/cameras/{}'.format(directorio)):
                                        sftp.put(ruta)  
                                except FileNotFoundError:
                                    sftp.mkdir('data/cameras/{}'.format(directorio))
                                    with sftp.cd('data/cameras/{}'.format(directorio)):
                                        sftp.put(ruta)
                            except error_perm:
                                logging.warning('INTENTANDO CREAR directorio  remoto {}'.format(directorio))
                                sesion.mkd(directorio)
                                logging.warning('El directorio  remoto {} ha sido creado'.format(directorio))
                            except Exception as e:
                                logging.exception('Error al subir el archivo {} msg'.format(ruta[8:]))
                                cola.put((ruta,directorio))
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
    logging.basicConfig(filename='sube_videos.log',level=logging.WARNING)
    cola = Queue('sube')
    cola_borrar = Queue('borra')
    Thread(target=descarga_camaras, args=(cola,salva_cada)).start()
    Thread(target=sube_ftp, args=(cola,cola_borrar)).start()
    Thread(target=borra_viejos, args=(cola_borrar,)).start()

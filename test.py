# -*- coding: utf-8 -*-
"""
Created on Wed May 30 10:22:27 2018

@author: Andres
"""
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

datos_ftp = {"host":"193.144.208.142", "user":"camaras_kml", 'passwd':"kfahjdlkj78908+-" }
while True:
    try:
        with closing(FTP(**datos_ftp)) as sesion:
            sesion.cwd('camaras')
            print(sesion.dir())
            time.sleep(15)
#            while True:
#                ruta=cola.get()
#                with open(ruta, "rb") as archivo:
#                    try:
#                        print(ruta[12:])
#                        sesion.storbinary("STOR {}".format(ruta[12:]), archivo)
#                        
#                    except Exception as e:
#                        logging.exception('Error al subir el archivo {} msg'.format(ruta[12:]))
#                        cola.put(ruta)
#                        sesion.quit()
#                        break
#                    else:
#                        cola_borrar.put(ruta)

                            
    except Exception as e:
        time.sleep(5)
        
        pass
# -*- coding: utf-8 -*-
"""
Created on Tue May 29 08:52:16 2018

@author: Andres
"""
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
            
 
upload_file('23',r"D:\Users\Andres\OneDrive\OneDrive - Universidad de Cantabria\Recordar GIST - VARIOS\Parsear datos recorridos MetroTus\ALMACÉN_INFORMES\2018528_bis\2018-5-28.pdf")          
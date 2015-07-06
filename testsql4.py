#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

"""
projet tuteuré 2014-2015
repris par LW
"""

# Importation des bibliotheques
from __future__ import print_function, division
import RPi.GPIO as GPIO
import time
import nxppy
import sqlite3
import logging

# CONFIGURATION DES LOGS
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# create a file handler
HANDLER = logging.FileHandler('/home/pi/LOGS/debug_raspAccess.log')
HANDLER.setLevel(logging.INFO)
# create a logging format
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
# add the handlers to the logger
LOGGER.addHandler(HANDLER)

LOGGER.info('Start script')

# Definition des ports en entre/sortie
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.IN)
GPIO.setup(25, GPIO.IN)

MASTER = '04F1D561EE0280'

def lecture():
    """ Lecture d'une carte NFC """
    mifare = nxppy.Mifare()
    data = ""
    try:
        data = mifare.select()
        print("UID=", data)
    except nxppy.SelectError:
        pass
    return data

def main():
    """ Fonction principale """
    # Connexion a la base de donnee
    conn = sqlite3.connect('nfc2.db')
    curs = conn.cursor()

    # Debut du programme
    while True:

        uid = lecture()
        
        #************************************
        #*** Detection de la carte MASTER ***
        #************************************
        if uid == MASTER:                  # Si la carte maitre est detectee

            # Condition pour l'AJOUT d une carte
            if (GPIO.input(22)==0):        # Si le bouton poussoir noir est appuye
                print("Presente la carte a ajouter")
                # Clignotement LED
                GPIO.output(17, GPIO.HIGH)    
                time.sleep(0.4)
                GPIO.output(17, GPIO.LOW)
                time.sleep(0.4)
                GPIO.output(17, GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(17, GPIO.LOW)
                time.sleep(0.4)
                GPIO.output(17, GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(17, GPIO.LOW)
                time.sleep(0.4)
                GPIO.output(17, GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(17, GPIO.LOW)
                time.sleep(0.4)
                # Fin clignotement

                curs.execute('SELECT * FROM carte')    # Lecture de la base de donnee
                listebdd = curs.fetchall()        # Insertion BDD dans la variable listebdd

                if str(uid) in str(listebdd):    # Si la carte est dans la BDD
                    print('la carte ' + str(uid) + ' est deja autorisee')
                    GPIO.output(18, GPIO.HIGH)    # Allumer LED rouge
                elif str(uid) == "None":        # Si pas de carte detectee
                    print("Aucune carte detectee")
                    GPIO.output(18, GPIO.HIGH)    # Allumer LED rouge
                else:
                    curs.execute("INSERT INTO carte (card) values (?)", (uid,))    # Ajout dans la BDD
                    print('la carte ' + str(uid) + ' a ete ajoute')
                    conn.commit()        # Enregistrement des modifications dans la BDD
                    GPIO.output(17, GPIO.HIGH)    # Allumer LED verte
                    time.sleep(1)
                    GPIO.output(17, GPIO.LOW)    # Eteindre LED verte

                time.sleep(1)
                GPIO.output(18, GPIO.LOW)    # Eteindre LED rouge

            #Condition pour la SUPPRESSION d une carte
            elif GPIO.input(25) == 0:        # Si le bouton poussoir rouge est appuye
                print("Presente la carte a supprimer")
                GPIO.output(18, GPIO.HIGH)        # Clignotement LED rouge
                time.sleep(0.4)
                GPIO.output(18, GPIO.LOW)
                time.sleep(0.4)
                GPIO.output(18, GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(18, GPIO.LOW)
                time.sleep(0.4)
                GPIO.output(18, GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(18, GPIO.LOW)
                time.sleep(0.4)
                GPIO.output(18, GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(18, GPIO.LOW)

                curs.execute('SELECT * FROM carte')    # Lecture de la base de donnee
                bas = curs.fetchall()                  # Insertion BDD dans la variable bas

                if uid == MASTER:        # Si on presente la carte maitre
                    print("la carte maitre ne peut pas etre suprimmee")
                    GPIO.output(18, GPIO.HIGH)    # Allumer LED rouge
                    time.sleep(1)
                    GPIO.output(18, GPIO.LOW)    # Eteindre LED rouge
                elif str(uid) in str(bas):         # Si la carte est dans la BDD
                    curs.execute("delete from carte where card=(?)", (uid,))    # Suppression dans la BDD
                    print('la carte ' + str(uid) + ' a ete supprime')
                    conn.commit()        # Enregistrement des modifications dans la BDD
                    GPIO.output(17, GPIO.HIGH)    # Allumer LED verte
                    time.sleep(1)
                    GPIO.output(17, GPIO.LOW)    # Eteindre LED verte
                else:
                    print("La carte n est pas dans la base de donnee")
                    GPIO.output(18, GPIO.HIGH)    # Allumer LED rouge
                    time.sleep(1)
                    GPIO.output(18, GPIO.LOW)    # Eteindre LED rouge

            if GPIO.input(22) == 1 and GPIO.input(25) == 1:            # Si aucun bouton poussoir n est presse
                curs.execute('SELECT * FROM carte') # Lecture de la base de donnee
                base = curs.fetchall()              # Insertion BDD dans la variable base
                if str(uid) in str(base):          # Si la carte est dans la BDD
                    print("allumer, c'est ouvert")
                    GPIO.output(17, GPIO.HIGH)      # Allumer LED verte
                    GPIO.output(4, GPIO.HIGH)       # Declencher relais
                    time.sleep(5)
                    GPIO.output(17, GPIO.LOW)       # Eteindre LED verte
                    GPIO.output(4, GPIO.LOW)        # Arret du declenchement du relais
                    print("on ferme")
                    time.sleep(1)
 
    conn.close()        # Fermeture de la connection avec la BDD

if __name__ == "__main__":
    main()
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

import pingo
from pingo.parts.led import Led
#from pingo.parts.button import Switch

#import time
from time import sleep
import nxppy
import sqlite3
import logging
from logging.handlers import RotatingFileHandler

# CONFIGURATION DES LOGS
# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger()
# on met le niveau du logger à DEBUG, comme ça il écrit tout
logger.setLevel(logging.DEBUG)

# création d'un formateur qui va ajouter le temps, le niveau
# de chaque message quand on écrira un message dans le log
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# création d'un handler qui va rediriger une écriture du log vers
# un fichier en mode 'append', avec 1 backup et une taille max de 10Mo
file_handler = RotatingFileHandler('/home/pi/LOGS/LOG_raspAccess.log', 'a', 10000000, 1)
# on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
# créé précédement et on ajoute ce handler au logger
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# création d'un second handler qui va rediriger chaque écriture de log
# sur la console
steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
logger.addHandler(steam_handler)

logger.info('Start script')



def lecture():
    """ Lecture d'une carte NFC """
    mifare = nxppy.Mifare()
    data = ""
    try:
        data = mifare.select()
        logger.debug("UID=" + str(data))
    except nxppy.SelectError:
        pass
    return data
    
def createTable(db):
    try:
        cursor = db.cursor()
        cursor.execute(''' CREATE TABLE IF NOT EXISTS carte(
                              id INTEGER PRIMARY KEY, 
                              card TEXT,
                              m INTEGER) ''')
        db.commit()
        
    except Exception as e:
        # Roll back any change if something goes wrong
        print("exception")
        db.rollback()
        raise e
    
    finally:
        #db.close()
        pass

def main():
    """ Fonction principale """
    MASTER = '04F1D561EE0280'
    
    # Definition des ports en entre/sortie
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(4, GPIO.OUT) #Sortie relais

    board = pingo.detect.get_board()

    red_led_pin = board.pins[12]   #GPIO18
    r_led = Led(red_led_pin)
    green_led_pin = board.pins[11] #GPIO17
    g_led = Led(green_led_pin)
    
    r_led.off()
    g_led.off()
    
    black_btn_pin = board.pins[15] #GPIO22
    red_btn_pin = board.pins[22]   #GPIO25
    black_btn_pin.mode = pingo.IN
    red_btn_pin.mode = pingo.IN
    
    #Test leds
    g_led.on()
    r_led.on()
    sleep(1)
    g_led.off()
    r_led.off()
    
    # Connexion a la base de donnee
    conn = sqlite3.connect('nfc2.db')
    createTable(conn)
    
    curs = conn.cursor()
    

    # Debut du programme
    while True:

        uid = lecture()
        
        
        #************************************
        #*** Detection de la carte MASTER ***
        #************************************
        if uid == MASTER:                  # Si la carte maitre est detectee

        # Condition pour l'AJOUT d une carte
            if (black_btn_pin.state == pingo.LOW):        # Si le bouton poussoir noir est appuye
                logger.debug("Presente la carte a ajouter")

                # Clignotement LED verte
                # Donne aussi le temps de présenter la carte a enregistrer
                for i in range(4):
                    g_led.on()    
                    sleep(0.4)
                    g_led.off()
                    sleep(0.4)
                #g_led.blink(times=5, on_delay=0.4, off_delay=0.4) # blink
                # Fin clignotement
                
                uid = lecture()
                
                curs.execute('SELECT * FROM carte')    # Lecture de la base de donnee
                listebdd = curs.fetchall()        # Insertion BDD dans la variable listebdd

                if str(uid) in str(listebdd):    # Si la carte est dans la BDD
                    logger.debug('la carte ' + str(uid) + ' est deja autorisee')
                    r_led.on()    # Allumer LED rouge
                elif str(uid) == "None":        # Si pas de carte detectee
                    logger.debug("Aucune carte detectee")
                    r_led.on()    # Allumer LED rouge
                else:
                    curs.execute("INSERT INTO carte (card) values (?)", (uid,))    # Ajout dans la BDD
                    logger.info('la carte ' + str(uid) + ' a ete ajoute')
                    conn.commit()        # Enregistrement des modifications dans la BDD
                    g_led.on()    # Allumer LED verte
                    sleep(1)
                    g_led.off()    # Eteindre LED verte
                    

                sleep(1)
                r_led.off()    # Eteindre LED rouge

        #Condition pour la SUPPRESSION d une carte
            elif red_btn_pin.state == pingo.LOW:        # Si le bouton poussoir rouge est appuye
                logger.debug("Presente la carte a supprimer")
                
                
                # Clignotement LED rouge
                # Donne aussi le temps de présenter la carte
                for i in range(4):
                    r_led.on()        
                    sleep(0.4)
                    r_led.off()
                    sleep(0.4)
                #r_led.blink(times=4, on_delay=0.4, off_delay=0.4) # blink forever
                
                uid = lecture()
                
                curs.execute('SELECT * FROM carte')    # Lecture de la base de donnee
                bas = curs.fetchall()                  # Insertion BDD dans la variable bas

                if uid == MASTER:        # Si on presente la carte maitre
                    logger.warning("Tentative de suppression de la carte MAITRE")
                    r_led.on()    # Allumer LED rouge
                    sleep(1)
                    r_led.off()    # Eteindre LED rouge
                elif str(uid) in str(bas):         # Si la carte est dans la BDD
                    curs.execute("delete from carte where card=(?)", (uid,))    # Suppression dans la BDD
                    logger.info('la carte ' + str(uid) + ' a ete supprime')
                    conn.commit()        # Enregistrement des modifications dans la BDD
                    g_led.on()    # Allumer LED verte
                    sleep(1)
                    g_led.off()    # Eteindre LED verte
                else:
                    logger.debug("La carte n est pas dans la base de donnee")
                    r_led.on()    # Allumer LED rouge
                    sleep(1)
                    r_led.off()    # Eteindre LED rouge

        if uid != "" and red_btn_pin.state == pingo.HIGH and black_btn_pin.state == pingo.HIGH:            # Si aucun bouton poussoir n est presse
            curs.execute('SELECT * FROM carte') # Lecture de la base de donnee
            base = curs.fetchall()              # Insertion BDD dans la variable base
            if str(uid) in str(base):          # Si la carte est dans la BDD
                logger.info("Ouverture de la porte")
                g_led.on()      # Allumer LED verte
                GPIO.output(4, GPIO.HIGH)       # Declencher relais
                sleep(5)
                g_led.off()       # Eteindre LED verte
                GPIO.output(4, GPIO.LOW)        # Arret du declenchement du relais
                logger.debug("Verrouillage de la porte")
                sleep(1)
 
    conn.close()        # Fermeture de la connection avec la BDD

if __name__ == "__main__":
    main()

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

# Definition des ports en entre/sortie
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.IN)
GPIO.setup(25, GPIO.IN)

MASTER = '04F1D561EE0280'

def main():
    # Connexion a la base de donnee
    conn = sqlite3.connect('nfc2.db')
    curs = conn.cursor()
    mifare = nxppy.Mifare()
    
    # Debut du programme
    while True:
        uid = ""
        try:
            uid = mifare.select()              # Lecture et insertion dans une variable du numero de la carte NCF presentee
            print("UID=", uid)
        
            if uid == MASTER:                  # Si la carte maitre est detectee

                #Condition pour l'ajout d une carte
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

                    ajou = ""
                    try:
                        ajou = mifare.select()        # Lecture et insertion dans une variable de la carte NCF presentee
                        curs.execute('SELECT * FROM carte')    # Lecture de la base de donnee
                        listebdd = curs.fetchall()        # Insertion BDD dans la variable listebdd

                        if str(ajou) in str(listebdd):    # Si la carte est dans la BDD
                            print('la carte ' + str(ajou) + ' est deja autorisee')
                            GPIO.output(18, GPIO.HIGH)    # Allumer LED rouge

                        elif str(ajou) == "None":        # Si pas de carte detectee
                            print("Aucune carte detectee")
                            GPIO.output(18, GPIO.HIGH)    # Allumer LED rouge

                        else:
                            curs.execute("INSERT INTO carte (card) values (?)", (ajou,))    # Ajout dans la BDD
                            print('la carte ' + str(ajou) + ' a ete ajoute')
                            conn.commit()        # Enregistrement des modifications dans la BDD
                            GPIO.output(17, GPIO.HIGH)    # Allumer LED verte
                            time.sleep(1)
                            GPIO.output(17, GPIO.LOW)    # Eteindre LED verte
                    except:
                        pass

                    time.sleep(1)
                    GPIO.output(18, GPIO.LOW)    # Eteindre LED rouge


                #Condition pour la suppression d une carte
                if GPIO.input(25) == 0:        # Si le bouton poussoir rouge est appuye
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

                    suppr = ""
                    try:
                        suppr = mifare.select()        # Lecture et insertion dans une variable du numero de la carte NCF presentee
                        curs.execute('SELECT * FROM carte')    # Lecture de la base de donnee
                        bas = curs.fetchall()            # Insertion BDD dans la variable bas

                        if suppr == MASTER:        # Si on presente la carte maitre
                            print("la carte maitre ne peut pas etre suprimmee")
                            GPIO.output(18, GPIO.HIGH)    # Allumer LED rouge
                            time.sleep(1)
                            GPIO.output(18, GPIO.LOW)    # Eteindre LED rouge

                        elif str(suppr) in str(bas):         # Si la carte est dans la BDD
                            curs.execute("delete from carte where card=(?)", (suppr,))    # Suppression dans la BDD
                            print('la carte ' + str(suppr) + ' a ete supprime')
                            conn.commit()        # Enregistrement des modifications dans la BDD
                            GPIO.output(17, GPIO.HIGH)    # Allumer LED verte
                            time.sleep(1)
                            GPIO.output(17, GPIO.LOW)    # Eteindre LED verte

                        else:
                            print("La carte n est pas dans la base de donnee")
                            GPIO.output(18, GPIO.HIGH)    # Allumer LED rouge
                            time.sleep(1)
                            GPIO.output(18, GPIO.LOW)    # Eteindre LED rouge
                    except:
                        pass
            
        except:
            pass

        lect = ""
        try:
            lect = mifare.select()         # Lecture et insertion dans une variable du numero de la carte NCF presentee
            print("LECT=", lect)

            if GPIO.input(22) == 1:            # Si aucun bouton poussoir n est presse
                if GPIO.input(25) == 1:
                    curs.execute('SELECT * FROM carte') # Lecture de la base de donnee
                    base = curs.fetchall()              # Insertion BDD dans la variable base
                    if str(lect) in str(base):          # Si la carte est dans la BDD
                        print("allumer, c'est ouvert")
                        GPIO.output(17, GPIO.HIGH)      # Allumer LED verte
                        GPIO.output(4, GPIO.HIGH)       # Declencher relais
                        time.sleep(5)
                        GPIO.output(17, GPIO.LOW)       # Eteindre LED verte
                        GPIO.output(4, GPIO.LOW)        # Arret du declenchement du relais
                        print("on ferme")
                        time.sleep(1)
                    
        except:
            pass
            
        

    conn.close()        # Fermeture de la connection avec la BDD

if __name__ == "__main__":
    main()
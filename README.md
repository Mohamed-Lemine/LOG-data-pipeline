
# Projet de traitement et calibration de données spectrales

Ce projet a pour objectif de gérer, calibrer, analyser et visualiser des mesures spectrales issues d’instruments scientifiques, dans le cadre du laboratoire LOG.




---

# Structure des dossiers du projet

## core

Ce dossier contient les modules Python principaux organisés en classes (programmation orientée objet).Exemples de fichiers :\

- data_manager.py : pour la gestion des lectures et écritures de données - calibration_manager.py : pour la calibration des mesures - filter_manager.py, processing_manager.py, etc.

---

## gui

Ce dossier (optionnel) contiendra le code source de l’interface graphique du projet, si une interface utilisateur est développée (ex : Tkinter, PyQt).
Exemple : main_window.py

---

## scripts

Ce dossier contient les scripts principaux pour lancer le traitement complet, la calibration ou la génération de résultats, ainsi que des exemples d’utilisation.
Exemple : main.py

---

## config

Ce dossier contient les fichiers de configuration qui servent de référence ou de paramètres pour les traitements.Exemples :\

- absorption_totale_trios.xlsx : table d’absorption - param_model_ku.xlsx : paramètres de calibration

---

## data

Ce dossier contient toutes les données d’entrée du projet, organisées par type : - raw/ : données brutes (.dat, .xlsx…) directement issues de l’instrument - calibration/ : fichiers de calibration instrument - distance/ : fichiers liés à la distance

---

## output

Ce dossier regroupe tous les fichiers de sortie générés par les traitements du projet : - calibrated/ : mesures calibrées (pkl, xlsx, etc.) - plots/ : graphiques générés - netcdf/ : exports NetCDF - autres sous-dossiers selon besoins

---

## tests

Ce dossier (optionnel) contient des scripts et jeux de données pour tester et valider les différentes fonctionnalités du code (tests unitaires).

---

## docs

Ce dossier contient la documentation utilisateur ou technique, les schémas d’architecture, tutoriels ou tout document d’accompagnement utile au projet.

---




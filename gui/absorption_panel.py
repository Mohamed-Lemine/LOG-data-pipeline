#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 10:52:13 2025

@author: mdlemineahmedou
"""

import tkinter as tk
from tkinter import filedialog
import os
from gui.logs_panel import LogsPanel
from core.absorption_manager import AbsorptionManager

class AbsorptionPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # Zone de logs tout en bas
        self.logs_panel = LogsPanel(self)

        # Frame du formulaire (en haut)
        self.form_frame = tk.Frame(self)
        self.form_frame.pack(fill='x', padx=10, pady=(10, 0))

        # Variables d’état pour les chemins de fichiers
        self.bilan_tagge_path = tk.StringVar()
        self.absorption_path = tk.StringVar()
        self.distance_path = tk.StringVar()  # Optionnel, tu peux ne pas l'afficher si inutile

        # Fichier bilan taggé
        tk.Label(self.form_frame, text="Fichier bilan_radeau_tagged.xlsx:").grid(row=0, column=0, sticky="e")
        tk.Entry(self.form_frame, textvariable=self.bilan_tagge_path, width=40).grid(row=0, column=1)
        tk.Button(self.form_frame, text="Parcourir", command=self.choose_bilan_tagge).grid(row=0, column=2)
        tk.Button(self.form_frame, text="Par défaut", command=self.set_default_bilan_tagge).grid(row=0, column=3)

        # Fichier absorption totale
        tk.Label(self.form_frame, text="Fichier absorption_totale_trios.xlsx:").grid(row=1, column=0, sticky="e")
        tk.Entry(self.form_frame, textvariable=self.absorption_path, width=40).grid(row=1, column=1)
        tk.Button(self.form_frame, text="Parcourir", command=self.choose_absorption).grid(row=1, column=2)
        tk.Button(self.form_frame, text="Par défaut", command=self.set_default_absorption).grid(row=1, column=3)

        tk.Label(self.form_frame, text="Dossier fichiers distance LU :").grid(row=2, column=0, sticky="e")
        tk.Entry(self.form_frame, textvariable=self.distance_path, width=40).grid(row=2, column=1)
        tk.Button(self.form_frame, text="Parcourir", command=self.choose_distance).grid(row=2, column=2)
        tk.Button(self.form_frame, text="Raccourci", command=self.set_distance_shortcut).grid(row=2, column=3)
        tk.Label(
            self.form_frame,
            text="(laisser vide pour distance par défaut de 4 cm)",
            font=("Arial", 9, "italic"),
            fg="gray"
        ).grid(row=2, column=4, sticky="w", padx=(5, 0))




        # Bouton lancer traitement
        tk.Button(self.form_frame, text="Lancer traitement Absorption/PKL", command=self.run_absorption).grid(row=4, column=1, pady=10)
        tk.Button(self.form_frame, text="Réinitialiser", command=self.reset_fields).grid(row=4, column=2)

        # Affichage zone logs en bas (sur toute la largeur)
        self.logs_panel = LogsPanel(self)
        self.logs_panel.pack(fill='x', padx=10, pady=10, side='bottom')

    # Fonctions de parcours de fichiers/dossiers
    def choose_bilan_tagge(self):
        path = filedialog.askopenfilename(title="Choisir bilan taggé", filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.bilan_tagge_path.set(path)
            self.logs_panel.log(f"Fichier bilan taggé sélectionné : {path}")

    def choose_absorption(self):
        path = filedialog.askopenfilename(title="Choisir absorption totale", filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.absorption_path.set(path)
            self.logs_panel.log(f"Fichier absorption sélectionné : {path}")

    def choose_distance(self):
        path = filedialog.askdirectory(title="Choisir le dossier de fichiers distance")
        if path:
            self.distance_path.set(path)
            self.logs_panel.log(f"Dossier de fichiers distance sélectionné : {path}")
    

    # Fonctions Par défaut (adapter les chemins selon l’orga du projet)
    def set_default_bilan_tagge(self):
        default_path = os.path.join(self.project_root, "output","bilan_tagge" , "bilan_tagge_mission.xlsx")
        self.bilan_tagge_path.set(default_path)
        self.logs_panel.log(f"Fichier bilan taggé par défaut sélectionné : {default_path}")

    def set_default_absorption(self):
        default_path = os.path.join(self.project_root, "data", "absorption" , "absorption_default.xlsx")
        self.absorption_path.set(default_path)
        self.logs_panel.log(f"Fichier absorption par défaut sélectionné : {default_path}")

    def set_distance_shortcut(self):
        # Raccourci : renseigne directement data/distance
        default_path = os.path.join(self.project_root, "data", "distance")
        self.distance_path.set(default_path)
        self.logs_panel.log(f"Dossier distance (raccourci) sélectionné : {default_path}")

    
    def run_absorption(self):
        try:
            self.logs_panel.log("Début du traitement absorption/PKL...")
    
            # Toujours travailler avec des chemins absolus et cwd correct
            BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            os.chdir(BASE_DIR)
    
            # Chemins d'entrée (tu peux adapter les .get())
            path_bilan_tagge = self.bilan_tagge_path.get()
            path_absorption = self.absorption_path.get()
            path_distance = self.distance_path.get() if self.distance_path.get() else None
    
            # Création et lancement du pipeline
            manager = AbsorptionManager(
                path_bilan_tagge=path_bilan_tagge,
                path_absorption=path_absorption,
                path_distance=path_distance
            )
            manager.process_station_spectra()
            manager.save_pkl_files()
    
            # Logs
            mission = getattr(manager, "mission", None)
            n_stations = len(getattr(manager, "df_Lu_shadow", {}))
            self.logs_panel.log(f"Mission : {mission if mission else '(inconnu)'}")
            self.logs_panel.log(f"Nombre de stations traitées : {n_stations}")
            for tag, df in getattr(manager, "df_Lu_shadow", {}).items():
                self.logs_panel.log(f"  - {tag} : {len(df)} mesures LU")
    
            dist_used = manager.path_distance if getattr(manager, "path_distance", None) else "(valeur par défaut 4.0 cm)"
            self.logs_panel.log(f"Distance LU : {dist_used}")
    
            out_dir = os.path.join("output", "pkl_by_station", getattr(manager, "mission", "inconnu"))
            self.logs_panel.log(f"PKL sauvegardés dans : {out_dir}")
    
            self.logs_panel.log("Traitement absorption terminé avec succès.")
    
        except Exception as e:
            self.logs_panel.log(f"Erreur lors du traitement absorption : {e}")


    def reset_fields(self):
        self.bilan_tagge_path.set("")
        self.absorption_path.set("")
        self.distance_path.set("")
        self.logs_panel.log("Champs réinitialisés.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 10:21:05 2025

@author: mdlemineahmedou
"""

import os
import tkinter as tk
from tkinter import filedialog
from gui.logs_panel import LogsPanel
from core.bilan_radeau_manager import BilanRadeauBuilder

class BilanTaggePanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # --- 1. Formulaire (en haut)
        self.form_frame = tk.Frame(self)
        self.form_frame.pack(fill='x', padx=10, pady=(10, 0))

        self.calibrated_dir = tk.StringVar()
        self.station_metadata = tk.StringVar()
        self.output_file = tk.StringVar()

        # Chemin dossier calibrated
        tk.Label(self.form_frame, text="Dossier fichiers calibrés:").grid(row=0, column=0, sticky="e")
        tk.Entry(self.form_frame, textvariable=self.calibrated_dir, width=40).grid(row=0, column=1)
        tk.Button(self.form_frame, text="Parcourir", command=self.choose_calibrated_dir).grid(row=0, column=2)
        tk.Button(self.form_frame, text="Par défaut", command=self.set_default_calibrated_dir).grid(row=0, column=3)

        # Chemin métadonnées stations
        tk.Label(self.form_frame, text="Fichier métadonnées stations:").grid(row=1, column=0, sticky="e")
        tk.Entry(self.form_frame, textvariable=self.station_metadata, width=40).grid(row=1, column=1)
        tk.Button(self.form_frame, text="Parcourir", command=self.choose_station_metadata).grid(row=1, column=2)
        tk.Button(self.form_frame, text="Par défaut", command=self.set_default_station_metadata).grid(row=1, column=3)

        # Fichier de sortie
        tk.Label(self.form_frame, text="Dossier de sortie bilan:").grid(row=2, column=0, sticky="e")
        tk.Entry(self.form_frame, textvariable=self.output_file, width=40).grid(row=2, column=1)
        tk.Button(self.form_frame, text="Parcourir", command=self.choose_output_file).grid(row=2, column=2)
        tk.Button(self.form_frame, text="Par défaut", command=self.set_default_output_file).grid(row=2, column=3)

        # Boutons action
        tk.Button(self.form_frame, text="Lancer le bilan taggé", command=self.on_run_bilan).grid(row=3, column=1, pady=10)
        tk.Button(self.form_frame, text="Réinitialiser", command=self.reset_fields).grid(row=3, column=2)

        # --- 2. Logs en bas
        self.logs_panel = LogsPanel(self)
        self.logs_panel.pack(fill='x', padx=10, pady=10, side='bottom')

    # Méthodes de choix/defaut chemins (analogue à CalibrationPanel)
    def choose_calibrated_dir(self):
        path = filedialog.askdirectory(title="Choisir dossier calibrated")
        if path:
            self.calibrated_dir.set(path)
            self.logs_panel.log(f"Dossier calibrated sélectionné : {path}")

    def set_default_calibrated_dir(self):
        default_path = os.path.join(self.project_root, "output", "calibrated")
        self.calibrated_dir.set(default_path)
        self.logs_panel.log(f"Dossier calibrated par défaut sélectionné : {default_path}")

    def choose_station_metadata(self):
        path = filedialog.askopenfilename(title="Choisir métadonnées stations", filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.station_metadata.set(path)
            self.logs_panel.log(f"Fichier métadonnées sélectionné : {path}")

    def set_default_station_metadata(self):
        default_path = os.path.join(self.project_root, "data", "stations_metadata" , "santa_cruz_metadata.xlsx")
        self.station_metadata.set(default_path)
        self.logs_panel.log(f"Fichier métadonnées par défaut sélectionné : {default_path}")

    def choose_output_file(self):
        path = filedialog.asksaveasfilename(title="Fichier de sortie bilan", defaultextension=".xlsx")
        if path:
            self.output_file.set(path)
            self.logs_panel.log(f"Fichier de sortie sélectionné : {path}")

    def set_default_output_file(self):
        default_path = os.path.join(self.project_root, "output", "bilan_tagge" )
        self.output_file.set(default_path)
        self.logs_panel.log(f"Fichier de sortie bilan par défaut : {default_path}")

    def on_run_bilan(self):
        try:
            self.logs_panel.log("Lancement du pipeline de bilan taggé...")
            builder = BilanRadeauBuilder(self.calibrated_dir.get(), self.station_metadata.get())
            df_final = builder.build_bilan(self.output_file.get())
            self.logs_panel.log(f"Bilan taggé généré et sauvegardé dans : {self.output_file.get()}")
            self.logs_panel.log("")  # Espace
            self.logs_panel.log(f"Nombre de couples traités : {len(df_final)}")
            
            self.logs_panel.log("")  # Espace
            # === 1. Capteurs Lu / Ref détectés ===
            roles = builder.get_lu_and_ref_capteurs()
            lu_caps = [k for k, v in roles.items() if v == "Lu"]
            ref_caps = [k for k, v in roles.items() if v == "Ref"]
            self.logs_panel.log("Capteurs LU détectés : " + ", ".join(lu_caps))
            self.logs_panel.log("Capteurs REF détectés : " + ", ".join(ref_caps))
    
            self.logs_panel.log("")  # Espace
    
            # === 2. Nombre de couples par station ===
            couples_by_station = df_final.groupby("Tag").size()
            for station, nb in couples_by_station.items():
                self.logs_panel.log(f"Station {station} : {nb} couples LU/REF")
    
            self.logs_panel.log("")  # Espace
    
            # === 3. Liste des stations ===
            stations = sorted(df_final["Tag"].unique())
            self.logs_panel.log("Stations détectées : " + ", ".join(stations))
    
        except Exception as e:
            self.logs_panel.log(f"Erreur lors du bilan : {e}")




    def reset_fields(self):
        self.calibrated_dir.set("")
        self.station_metadata.set("")
        self.output_file.set("")
        self.logs_panel.log("Champs réinitialisés.")


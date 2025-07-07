#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:32:25 2025

@author: mdlemineahmedou
"""

import os
import tkinter as tk
from tkinter import filedialog, ttk
from gui.logs_panel import LogsPanel  # Import important !
from core.calibration_manager import CalibrationManager

class CalibrationPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Helper : racine du projet (calculée dynamiquement)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # --- 1. Frame du formulaire (haut)
        self.form_frame = tk.Frame(self)
        self.form_frame.pack(fill='x', padx=10, pady=(10, 0))

        self.dat_path = tk.StringVar()
        self.calib_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.interpolation_mode = tk.StringVar(value="UV_Vis")

        # Fichier .dat à traiter
        tk.Label(self.form_frame, text="Fichier .dat à traiter:").grid(row=0, column=0, sticky="e")
        tk.Entry(self.form_frame, textvariable=self.dat_path, width=40).grid(row=0, column=1)
        tk.Button(self.form_frame, text="Parcourir", command=self.choose_dat_file).grid(row=0, column=2)

        # Dossier calibration
        tk.Label(self.form_frame, text="Dossier calibration:").grid(row=1, column=0, sticky="e")
        tk.Entry(self.form_frame, textvariable=self.calib_dir, width=40).grid(row=1, column=1)
        tk.Button(self.form_frame, text="Parcourir", command=self.choose_calib_dir).grid(row=1, column=2)
        tk.Button(self.form_frame, text="Par défaut", command=self.set_default_calib_dir).grid(row=1, column=3)

        # Dossier de sortie
        tk.Label(self.form_frame, text="Dossier de sortie:").grid(row=2, column=0, sticky="e")
        tk.Entry(self.form_frame, textvariable=self.output_dir, width=40).grid(row=2, column=1)
        tk.Button(self.form_frame, text="Parcourir", command=self.choose_output_dir).grid(row=2, column=2)
        tk.Button(self.form_frame, text="Par défaut", command=self.set_default_output_dir).grid(row=2, column=3)

        # Mode d'interpolation
        tk.Label(self.form_frame, text="Mode d'interpolation:").grid(row=3, column=0, sticky="e")
        mode_menu = ttk.Combobox(self.form_frame, textvariable=self.interpolation_mode, values=["UV_Vis", "UV"])
        mode_menu.grid(row=3, column=1, sticky="w")
        mode_menu.bind("<<ComboboxSelected>>", self.update_mode)

        # Boutons d'action
        tk.Button(self.form_frame, text="Lancer la calibration", command=self.on_run_calibration).grid(row=4, column=1, pady=10)
        tk.Button(self.form_frame, text="Réinitialiser", command=self.reset_fields).grid(row=4, column=2)

        # --- 2. Zone de logs (en bas, toute largeur, toujours présente)
        self.logs_panel = LogsPanel(self)
        self.logs_panel.pack(fill='x', padx=10, pady=10, side='bottom')

    # --- Fonctions pour boutons "Par défaut"
    def set_default_calib_dir(self):
        default_path = os.path.join(self.project_root, "data", "calibration", "ALL_2023")
        self.calib_dir.set(default_path)
        self.logs_panel.log(f"Dossier calibration par défaut sélectionné : {default_path}")

    def set_default_output_dir(self):
        default_path = os.path.join(self.project_root, "output", "calibrated")
        self.output_dir.set(default_path)
        self.logs_panel.log(f"Dossier de sortie par défaut sélectionné : {default_path}")

    # ... Le reste de tes méthodes habituelles (choose_dat_file, on_run_calibration, etc.) ...



    # --- Le reste ne change pas (choose_dat_file, choose_calib_dir, ...)
    # ... (reprends exactement tes méthodes existantes)

    def choose_dat_file(self):
        """
        Ouvre une boîte de dialogue pour choisir le fichier .dat brut à calibrer.
        """
        path = filedialog.askopenfilename(title="Choisir fichier .dat", filetypes=[("DAT files", "*.dat")])
        if path:
            self.dat_path.set(path)
            self.logs_panel.log(f"Fichier .dat sélectionné : {path}")

    def choose_calib_dir(self):
        """
        Ouvre une boîte de dialogue pour choisir le dossier de calibration.
        """
        path = filedialog.askdirectory(title="Choisir dossier calibration")
        if path:
            self.calib_dir.set(path)
            self.logs_panel.log(f"Dossier calibration sélectionné : {path}")

    def choose_output_dir(self):
        """
        Ouvre une boîte de dialogue pour choisir le dossier de sortie.
        """
        path = filedialog.askdirectory(title="Choisir dossier sortie")
        if path:
            self.output_dir.set(path)
            self.logs_panel.log(f"Dossier de sortie sélectionné : {path}")

    def update_mode(self, *args):
        """
        Met à jour le mode d'interpolation sélectionné.
        """
        mode = self.interpolation_mode.get()
        self.logs_panel.log(f"Mode d'interpolation changé en : {mode}")

    def on_run_calibration(self):
        """
        Lance le pipeline de calibration et affiche la progression dans les logs.
        """
        try:
            self.logs_panel.log("Début de la calibration...")
            manager = CalibrationManager(path_calib_dir=self.calib_dir.get())
            nb = manager.run_full_calibration_pipeline(
                path_data=self.dat_path.get(),
                output_dir=self.output_dir.get(),
                interpolation_mode=self.interpolation_mode.get()
            )
            self.logs_panel.log(f"Calibration terminée avec succès. {nb} fichiers calibrés exportés.")
        except Exception as e:
            self.logs_panel.log(f"Erreur lors de la calibration : {e}")

    def reset_fields(self):
        """
        Réinitialise les champs de saisie et les variables.
        """
        self.dat_path.set("")
        self.calib_dir.set("")
        self.output_dir.set("")
        self.interpolation_mode.set("UV_Vis")
        self.logs_panel.log("Champs réinitialisés.")

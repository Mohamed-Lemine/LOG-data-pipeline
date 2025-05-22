#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:32:25 2025

@author: mdlemineahmedou
"""

import tkinter as tk
from tkinter import filedialog, ttk
from core.calibration_manager import CalibrationManager

class CalibrationPanel(tk.Frame):
    def __init__(self, master, logs_panel):
        """
        Initialise les widgets du panneau de calibration.
        - master : fenêtre parente (MainWindow)
        - logs_panel : référence à la zone de logs pour afficher les messages
        """
        super().__init__(master)
        self.logs_panel = logs_panel

        # Variables d'état
        self.dat_path = tk.StringVar()
        self.calib_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.interpolation_mode = tk.StringVar(value="UV_Vis")

        # Widgets
        tk.Label(self, text="Fichier .dat à traiter:").grid(row=0, column=0, sticky="e")
        tk.Entry(self, textvariable=self.dat_path, width=40).grid(row=0, column=1)
        tk.Button(self, text="Parcourir", command=self.choose_dat_file).grid(row=0, column=2)

        tk.Label(self, text="Dossier calibration:").grid(row=1, column=0, sticky="e")
        tk.Entry(self, textvariable=self.calib_dir, width=40).grid(row=1, column=1)
        tk.Button(self, text="Parcourir", command=self.choose_calib_dir).grid(row=1, column=2)

        tk.Label(self, text="Dossier de sortie:").grid(row=2, column=0, sticky="e")
        tk.Entry(self, textvariable=self.output_dir, width=40).grid(row=2, column=1)
        tk.Button(self, text="Parcourir", command=self.choose_output_dir).grid(row=2, column=2)

        tk.Label(self, text="Mode d'interpolation:").grid(row=3, column=0, sticky="e")
        mode_menu = ttk.Combobox(self, textvariable=self.interpolation_mode, values=["UV_Vis", "UV"])
        mode_menu.grid(row=3, column=1, sticky="w")
        mode_menu.bind("<<ComboboxSelected>>", self.update_mode)

        tk.Button(self, text="Lancer la calibration", command=self.on_run_calibration).grid(row=4, column=1, pady=10)
        tk.Button(self, text="Réinitialiser", command=self.reset_fields).grid(row=4, column=2)

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
            manager.run_full_calibration_pipeline(
                path_data=self.dat_path.get(),
                output_dir=self.output_dir.get(),
                interpolation_mode=self.interpolation_mode.get()
            )
            self.logs_panel.log("Calibration terminée avec succès.")
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

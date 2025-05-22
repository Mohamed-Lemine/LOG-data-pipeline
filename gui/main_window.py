#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:49:14 2025

@author: mdlemineahmedou
"""

import tkinter as tk
from gui.calibration_panel import CalibrationPanel
from gui.logs_panel import LogsPanel

class MainWindow(tk.Tk):
    def __init__(self):
        """
        Initialise la fenêtre principale de l'application graphique.
        Cette fenêtre assemble les panneaux Calibration et Logs.
        """
        super().__init__()

        # Configuration fenêtre principale
        self.title("Application de Calibration des Spectres")
        self.geometry("750x500")

        # Initialiser LogsPanel en premier
        self.logs_panel = LogsPanel(self)
        self.logs_panel.pack(pady=10, padx=10, fill='both', expand=True)

        # Initialiser CalibrationPanel, avec référence vers LogsPanel
        self.calibration_panel = CalibrationPanel(self, logs_panel=self.logs_panel)
        self.calibration_panel.pack(pady=10, padx=10, fill='x')

        # Log initialisation terminée
        self.logs_panel.log("Application démarrée avec succès.")


# Pour lancer l'application depuis ce fichier directement (test rapide)
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

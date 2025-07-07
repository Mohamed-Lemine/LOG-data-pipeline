#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:49:14 2025

@author: mdlemineahmedou
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

from gui.calibration_panel import CalibrationPanel
from gui.bilan_tagge_panel import BilanTaggePanel
from gui.absorption_panel import AbsorptionPanel
from gui.visualisation_panel import VisualisationPanel

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Projet Spectres - Traitement complet")
        self.geometry("1300x1150")
        self.configure(bg='white')

        # Header en haut (logo + nom du projet)
        header = tk.Frame(self, height=60, bg='#1c305c')
        header.pack(side='top', fill='x')
        
        logo_path = os.path.join(os.path.dirname(__file__), "resources", "logo_LOG.jpg")
        logo_img_pil = Image.open(logo_path)
        logo_img_pil = logo_img_pil.resize((90, 80 ))
        logo_img = ImageTk.PhotoImage(logo_img_pil)
        self.logo_img = logo_img
        logo = tk.Label(header, image=self.logo_img, bg='#1c305c')
        logo.pack(side='left', padx=40, pady=3)
        title = tk.Label(
            header, text="Application de Traitement Spectres",
            font=("Arial", 22, 'bold'), bg='#1c305c', fg='white'
        )
        title.pack(side='left', padx=50)

        # Sidebar à gauche (navigation étapes)
        sidebar = tk.Frame(self, width=180, bg='#e9eef6')
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        # Zone centrale principale
        self.central_frame = tk.Frame(self, bg='white')
        self.central_frame.pack(side='left', fill='both', expand=True)

        # Initialisation panels
        self.panels = {
            'Calibration': CalibrationPanel(self.central_frame),
            'Bilan Taggé': BilanTaggePanel(self.central_frame),
            'Absorption/PKL': AbsorptionPanel(self.central_frame),
            'Visualisation': VisualisationPanel(self.central_frame),
        }
        for panel in self.panels.values():
            panel.pack_forget()
        self.panels['Calibration'].pack(fill='both', expand=True)
        self.current_panel = 'Calibration'

        # --- Styles ttk pour la sidebar ---
        self.style = ttk.Style()
        self.style.configure("Sidebar.TButton", font=("Arial", 12), padding=6)
        self.style.configure("Sidebar.Selected.TButton", background="#bacbf5", foreground="#1c305c")
        self.style.map("Sidebar.TButton",
            background=[('active', '#bacbf5')],
            foreground=[('active', '#1c305c')]
        )

        # --- Boutons navigation ---
        self.nav_keys = ["Calibration", "Bilan Taggé", "Absorption/PKL", "Visualisation"]
        self.sidebar_buttons = []
        for key in self.nav_keys:
            btn = ttk.Button(
                sidebar, text=key,
                style="Sidebar.TButton",
                command=lambda k=key: self.show_panel(k),
                width=20
            )
            pady = (30, 10) if key == "Calibration" else 10
            btn.pack(fill='x', pady=pady, padx=15)
            self.sidebar_buttons.append(btn)

        # Affiche le bouton actif au démarrage
        self.sidebar_buttons[0].configure(style="Sidebar.Selected.TButton")

    def show_panel(self, key):
        # Cache le panel courant
        self.panels[self.current_panel].pack_forget()
        # Affiche le nouveau
        self.panels[key].pack(fill='both', expand=True)
        self.current_panel = key

        # Update styles pour navigation
        for btn, nav_key in zip(self.sidebar_buttons, self.nav_keys):
            if nav_key == key:
                btn.configure(style="Sidebar.Selected.TButton")
            else:
                btn.configure(style="Sidebar.TButton")


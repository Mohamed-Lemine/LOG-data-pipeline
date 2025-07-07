#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 28 15:37:00 2025

@author: mdlemineahmedou
"""

import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure



class VisualisationPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        # 1. Champ dossier PKL + bouton
        self.path_pkl_dir = tk.StringVar()
        frame_top = tk.Frame(self)
        frame_top.pack(fill='x', padx=10, pady=10)
    
        tk.Label(frame_top, text="Dossier PKL par station :").pack(side='left')
        tk.Entry(frame_top, textvariable=self.path_pkl_dir, width=50).pack(side='left', padx=5)
        tk.Button(frame_top, text="Parcourir", command=self.browse_pkl_folder).pack(side='left', padx=5)
        
        tk.Button(
            frame_top,
            text="Raccourci",
            command=self.goto_pkl_by_station
        ).pack(side='left', padx=5)
                
        # Frame contenant le Canvas + Scrollbar horizontale + label de scroll
        self.stations_frame = tk.Frame(self)
        self.stations_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Canvas pour les boutons station
        self.stations_canvas = tk.Canvas(self.stations_frame, height=60)
        self.stations_canvas.pack(side='left', fill='x', expand=True)
        
        # Scrollbar horizontale sous le canvas
        self.stations_scroll = tk.Scrollbar(self.stations_frame, orient='horizontal', command=self.stations_canvas.xview)
        self.stations_scroll.pack(side='bottom', fill='x')
        self.stations_canvas.configure(xscrollcommand=self.stations_scroll.set)

        # Indicateur visuel pour le scroll
        self.scroll_hint = tk.Label(self.stations_frame, text="⟶", fg="grey", font=("Arial", 18))
        self.scroll_hint.pack(side='right', padx=6)
        
        # Sous-frame pour les boutons
        self.stations_buttons_frame = tk.Frame(self.stations_canvas)
        self.stations_canvas.create_window((0, 0), window=self.stations_buttons_frame, anchor='nw')

        # Bind mousewheel (shift+scroll) pour scroll horizontal
        self.stations_canvas.bind("<Shift-MouseWheel>", self._on_mousewheel)

        # Update scrollregion après chaque ajout de bouton
        self.stations_buttons_frame.bind("<Configure>", lambda e: self.stations_canvas.configure(scrollregion=self.stations_canvas.bbox("all")))
        
        # Frame pour les graphes 2x2
        self.plots_frame = tk.Frame(self)
        self.plots_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Placeholders pour la gestion interne
        self.station_buttons = []
        self.plot_canvases = []
        self.visualisation_manager = None
        self.current_tag = None
    
    def goto_pkl_by_station(self):
        # Change directement le champ de texte pour pointer sur le dossier de base
        import os
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        shortcut_path = os.path.join(BASE_DIR, "output", "pkl_by_station")
        self.path_pkl_dir.set(shortcut_path)
        # Ouvre tout de suite le navigateur de dossiers si tu veux sélectionner une mission
        folder = filedialog.askdirectory(
            title="Choisir une mission dans pkl_by_station",
            initialdir=shortcut_path
        )
        if folder:
            self.path_pkl_dir.set(folder)
            from core.visualisation_manager import VisualisationManager
            self.visualisation_manager = VisualisationManager(folder)
            self.load_stations(folder)

    
    def _on_mousewheel(self, event):
        # Scroll horizontal avec Shift + Molette
        self.stations_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")


        
    def browse_pkl_folder(self):
        """Permet à l'utilisateur de choisir le dossier PKL à visualiser."""
        folder = filedialog.askdirectory(title="Choisir dossier PKL par station")
        if folder:
            self.path_pkl_dir.set(folder)
            # Ici, tu importes/initialises VisualisationManager sur ce dossier
            from core.visualisation_manager import VisualisationManager  # adapte si besoin
            self.visualisation_manager = VisualisationManager(folder)
            
            # Rafraîchis la liste de stations
            self.load_stations(folder)


    def load_stations(self, path_pkl_dir):
        """Charge les fichiers PKL et affiche les boutons horizontaux pour chaque station."""
        # 1. Efface les boutons précédents
        for btn in self.station_buttons:
            btn.destroy()
        self.station_buttons.clear()
    
        # 2. Récupère la liste des stations via VisualisationManager
        tags = []
        if self.visualisation_manager is not None:
            tags = self.visualisation_manager.get_stations()
    
        # 3. Pour chaque station, crée un bouton dans self.stations_buttons_frame (et non self.stations_frame !)
        for idx, tag in enumerate(tags):
            btn = tk.Button(self.stations_buttons_frame, text=tag, width=10,
                            command=lambda t=tag: self.on_station_selected(t))
            btn.pack(side='left', padx=3, pady=2)
            self.station_buttons.append(btn)
    
        # 4. Mise à jour du scroll du canvas
        self.stations_buttons_frame.update_idletasks()
        self.stations_canvas.config(scrollregion=self.stations_canvas.bbox("all"))
    
        # 5. Sélectionne la première station par défaut (s'il y en a)
        if tags:
            self.on_station_selected(tags[0])



    def on_station_selected(self, tag):
        """Affiche les 4 graphes de la station sélectionnée (petit format, en grille 2x2)."""
        self.current_tag = tag
        # Nettoyage du frame des subplots
        for widget in self.plots_frame.winfo_children():
            widget.destroy()
    
        # Crée une nouvelle Figure matplotlib avec 2x2 subplots
        fig = Figure(figsize=(10, 10))
        axs = fig.subplots(2, 2)
        plot_types = ['lu', 'edref', 'rrs', 'distance']
    
        # Trace les 4 graphes dans la grille
        for idx, plot_type in enumerate(plot_types):
            ax = axs[idx // 2, idx % 2]
            if plot_type == 'lu':
                self.visualisation_manager.plot_lu_all(tag, ax=ax, show=False)
                ax.set_title('LU')
            elif plot_type == 'edref':
                self.visualisation_manager.plot_edref_all(tag, ax=ax, show=False)
                ax.set_title('EDREF')
            elif plot_type == 'rrs':
                self.visualisation_manager.plot_rrs_all(tag, ax=ax, show=False)
                ax.set_title('RRS')
            elif plot_type == 'distance':
                self.visualisation_manager.plot_distance(tag, ax=ax, show=False)
                ax.set_title('Distance')
            # Ajoute un listener pour le clic sur chaque subplot
            def _onclick(event, plot_type=plot_type):
                # Vérifie qu’on clique dans ce subplot
                if event.inaxes == ax:
                    self.on_subplot_click(plot_type)
            fig.canvas.mpl_connect('button_press_event', _onclick)
    
        # Affiche la figure dans le frame
        canvas = FigureCanvasTkAgg(fig, master=self.plots_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        





    def on_subplot_click(self, plot_type):
        """
        Affiche le graphe demandé (plot_type : 'lu', 'edref', 'rrs', 'distance') en grand dans une popup.
        plot_type : str parmi ['lu', 'edref', 'rrs', 'distance']
        """
        if self.current_tag is None or self.visualisation_manager is None:
            return
    
        # Prépare une nouvelle fenêtre popup
        popup = tk.Toplevel(self)
        popup.title(f"Graphe {plot_type.upper()} — Station {self.current_tag}")
    
        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)
    
        # Sélection du plot à afficher
        if plot_type == 'lu':
            self.visualisation_manager.plot_lu_all(self.current_tag, ax=ax)
        elif plot_type == 'edref':
            self.visualisation_manager.plot_edref_all(self.current_tag, ax=ax)
        elif plot_type == 'rrs':
            self.visualisation_manager.plot_rrs_all(self.current_tag, ax=ax)
        elif plot_type == 'distance':
            self.visualisation_manager.plot_distance(self.current_tag, ax=ax)
        else:
            popup.destroy()
            return
    
        # Ajustement du layout pour éviter chevauchement
        fig.tight_layout(pad=2)
        fig.subplots_adjust(bottom=0.45, left=0.50, right=0.97, top=0.9)
    
        # Affiche le plot dans le popup
        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)



    def update_all_subplots(self, tag):
        """
        Rafraîchit les 4 sous-graphes matplotlib pour la station sélectionnée.
        """
        # Nettoyage de l’ancienne frame de subplots
        for widget in self.plots_frame.winfo_children():
            widget.destroy()
    
        fig = Figure(figsize=(13, 8))
        axs = fig.subplots(2, 2)  # matrice 2x2
    
        # --- Remplissage des 4 plots par VisualisationManager (en passant axs)
        self.visualisation_manager.plot_lu_all(tag, ax=axs[0, 0])
        self.visualisation_manager.plot_edref_all(tag, ax=axs[0, 1])
        self.visualisation_manager.plot_rrs_all(tag, ax=axs[1, 0])
        self.visualisation_manager.plot_distance(tag, ax=axs[1, 1])
    
        # --- Ajustements de layout APRÈS le tracé de tous les plots
        fig.tight_layout(pad=3.5)
        fig.subplots_adjust(left=0.07, right=0.97, top=0.93, bottom=0.11, wspace=0.33, hspace=0.45)
    
        # Rotation des labels X du graphe Distance (en bas à droite)
        ax4 = axs[1, 1]
        for label in ax4.get_xticklabels():
            label.set_rotation(30)
            label.set_ha('right')
    
        # Canvas Matplotlib → Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plots_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
        # Stockage pour popup éventuelle
        self.current_figure = fig
        self.current_canvas = canvas

    
    
    
    
    
    
    
    
    
    
    
    
    

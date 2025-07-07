#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 10:32:35 2025

@author: mdlemineahmedou
"""

import os 
import re 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class VisualisationManager:
    def __init__(self, path_pkl_dir):
        """
        Initialise le manager de visualisation.
        - path_pkl_dir : chemin du dossier des fichiers PKL par station (ex: output/pkl_by_station/recife_2024)
        """
        self.path_pkl_dir = path_pkl_dir

    def get_stations(self) -> list:
        """
        Retourne la liste des stations disponibles dans le dossier PKL,
        en détectant tous les fichiers commençant par 'df_Lu_shadow_'.
        """
        tags = []
        pattern = re.compile(r"df_Lu_shadow_(.+)\.pkl")
        for fname in os.listdir(self.path_pkl_dir):
            match = pattern.match(fname)
            if match:
                tags.append(match.group(1))
        tags = sorted(tags)
        return tags

    def plot_rrs_all(self, tag, ax=None, show=True):
        """
        Affiche toutes les courbes Rrs (lambda 310–950nm) pour la station <tag>.
        Si ax est fourni, dessine dessus. Sinon crée une nouvelle figure.
        """
        path_rrs = os.path.join(self.path_pkl_dir, f"df_Rrs_{tag}.pkl")
        df_rrs = pd.read_pickle(path_rrs)
        lo_spectre = np.arange(310, 951)
    
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 5))
        for idx in df_rrs.index:
            y = df_rrs.loc[idx, lo_spectre].values
            ax.plot(lo_spectre, y, alpha=0.4)
        ax.set_title(f"Rrs — {tag}")
        ax.set_xlabel("Longueur d'onde (nm)")
        ax.set_ylabel("Rrs")
        ax.grid(True, alpha=0.2)
        if show:
            plt.tight_layout()
            plt.show()
    
    
    def plot_lu_all(self, tag, ax=None, show=True):
        """
        Affiche toutes les courbes Lu (lambda 310–950nm) pour la station <tag>.
        Si ax est fourni, dessine dessus. Sinon crée une nouvelle figure.
        """
        path_lu = os.path.join(self.path_pkl_dir, f"df_Lu_shadow_{tag}.pkl")
        df_lu = pd.read_pickle(path_lu)
        lo_spectre = np.arange(310, 951)
    
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 5))
        for idx in df_lu.index:
            y = df_lu.loc[idx, lo_spectre].values
            ax.plot(lo_spectre, y, alpha=0.4)
        ax.set_title(f"Lu corrigé (shadow+absorption) — {tag}")
        ax.set_xlabel("Longueur d'onde (nm)")
        ax.set_ylabel("Lu")
        ax.grid(True, alpha=0.2)
        if show:
            plt.tight_layout()
            plt.show()

    def plot_edref_all(self, tag, ax=None, show=True):
        """
        Trace toutes les courbes Edref (spectres complets) pour chaque mesure de la station <tag>.
        Si ax fourni, trace dessus ; sinon crée une nouvelle figure.
        """
        path_pkl = os.path.join(self.path_pkl_dir, f"df_Edref_{tag}.pkl")
        if not os.path.isfile(path_pkl):
            print(f"[ERREUR] Fichier PKL introuvable : {path_pkl}")
            return
    
        df = pd.read_pickle(path_pkl)
        lambdas = np.arange(310, 951)
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 5))
        for idx in df.index:
            y = df.loc[idx, lambdas].values
            ax.plot(lambdas, y, alpha=0.4)
        ax.set_title(f"Edref – Station {tag} ({len(df)} mesures)")
        ax.set_xlabel("Longueur d'onde (nm)")
        ax.set_ylabel("Edref")
        if show:
            plt.tight_layout()
            plt.show()
    
    def plot_distance(self, tag, ax=None, show=True):
        """
        Affiche la distance (en cm) de chaque mesure pour la station <tag>.
        Si ax fourni, trace dessus ; sinon crée une nouvelle figure.
        """
        filename = f"df_Distance_{tag}.pkl"
        filepath = os.path.join(self.path_pkl_dir, filename)
        if not os.path.isfile(filepath):
            print(f"[ERREUR] Fichier de distance non trouvé pour la station {tag} : {filepath}")
            return
    
        df_dist = pd.read_pickle(filepath)
        if "Distance_cm" not in df_dist.columns:
            print(f"[ERREUR] Colonne 'Distance_cm' absente dans {filepath}")
            return
    
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df_dist.index, df_dist["Distance_cm"], marker='o', linestyle='-')
        ax.set_xlabel("Date / Heure")
        ax.set_ylabel("Distance LU (cm)")
        ax.set_title(f"Distance LU – Station {tag}")
        ax.grid(True)
        if show:
            plt.tight_layout()
            plt.show()

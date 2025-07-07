#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 28 14:57:26 2025

@author: mdlemineahmedou
"""

import os
from core.visualisation_manager import VisualisationManager

def main():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(BASE_DIR)
    mission_name = "recife_2024"  # adapte le nom selon ton dossier
    path_pkl_dir = os.path.join(BASE_DIR, "output", "pkl_by_station", mission_name)
    viz = VisualisationManager(path_pkl_dir)
    stations = viz.get_stations()
    print("Stations disponibles :", stations)
    if not stations:
        print("Aucune station trouvée pour cette mission.")
        return
    tag = stations[10]  # Change ici pour une autre station si tu veux
    print(f"\n--- Affichage des graphes pour la station : {tag} ---")
    viz.plot_rrs_all(tag)
    viz.plot_lu_all(tag)
    viz.plot_edref_all(tag)
    viz.plot_distance(tag)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 00:42:13 2025

@author: mdlemineahmedou
"""
import os
from core.absorption_manager import AbsorptionManager

def main():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(BASE_DIR)  # Toujours à la racine projet

    # Chemins d'entrée
    path_bilan_tagge = os.path.join(BASE_DIR, 'output', 'bilan_tagge', 'bilan_tagge_recife_2024.xlsx')
    path_absorption  = os.path.join(BASE_DIR, 'data', 'absorption', 'absorption_totale_trios.xlsx')
    path_distance = os.path.join(BASE_DIR, 'data', 'distance', 'distanceJuin2016')  # (optionnel)

    # Création du manager
    manager = AbsorptionManager(
        path_bilan_tagge=path_bilan_tagge,
        path_absorption=path_absorption,
        #path_distance=path_distance,
    )

    # Lancement du pipeline
    manager.process_station_spectra()
    manager.save_pkl_files()  # <-- Le manager gère le dossier cible et le nom de mission

    print("✅ Fichiers PKL générés.")
    print("Stations disponibles :", list(manager.df_Lu_shadow.keys()))

    # Exemple d'accès rapide à un DataFrame
    if manager.df_Lu_shadow:
        tag = list(manager.df_Lu_shadow.keys())[0]
        df = manager.get_df(tag, "distance")
        print(f"DataFrame Distance pour la station {tag} :")
        print(df.head())

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 20 11:25:31 2025

@author: mdlemineahmedou
"""


import os 
import sys 
# 1. Toujours : racine du projet
# Ajouter le dossier racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
from core.calibration_manager import CalibrationManager

def main():


    # 2. Chemins relatifs à la racine projet
    path_data = os.path.join(BASE_DIR, 'data', 'acquisition', 'export_recife_2024.dat')
    path_calib_dir = os.path.join(BASE_DIR, 'data', 'calibration', 'ALL_2023')
    output_dir = os.path.join(BASE_DIR, 'output', 'calibrated')

    # 3. Utilisation des chemins dans ta logique métier
    calibration_manager = CalibrationManager(path_calib_dir=path_calib_dir)
    calibration_manager.run_full_calibration_pipeline(
        path_data=path_data,
        output_dir=output_dir,
        interpolation_mode='UV_Vis' # UV
    )
    print(f"[INFO] Pipeline terminé : spectres calibrés et exportés dans {output_dir}")

if __name__ == "__main__":
    main()



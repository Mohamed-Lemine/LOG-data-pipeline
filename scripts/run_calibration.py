#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 20 11:25:31 2025

@author: mdlemineahmedou
"""

import os
import sys

# === Importer tes classes maison ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.calibration_manager import CalibrationManager

# Toujours commencer par trouver la racine du projet par rapport à ce script
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Fichier de données brutes (.dat)
path_data = os.path.join(project_root, 'data', 'raw', 'export_recife_2024.dat')

# Dossier calibration (Cal_*, Back_*, *.ini pour chaque capteur)
path_calib_dir = os.path.join(project_root, 'data', 'calibration' ,  'ALL_2023')

# Dossier de sortie
output_dir = os.path.join(project_root)

# 1. Initialiser CalibrationManager avec le dossier calibration
calibration_manager = CalibrationManager(path_calib_dir=path_calib_dir)

# 2. Lancer le pipeline complet (plus besoin de data_manager)
calibration_manager.run_full_calibration_pipeline(
    path_data=path_data,
    output_dir=output_dir,
    interpolation_mode='UV_Vis'  # ou 'UV' selon besoin
)

print(f"[INFO] Pipeline terminé : spectres calibrés et exportés dans {output_dir}")

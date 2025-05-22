#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 10:42:46 2025

@author: mdlemineahmedou
"""

import os
import numpy as np
from scipy.interpolate import interp1d
from core.data_manager import DataManager


class CapteurTRIOS:
    """
    Gère toute la calibration et le traitement métier d'UN capteur TRIOS.
    """
    def __init__(self, nom_capteur, integtime, path_calib_dir):
        self.nom_capteur = nom_capteur
        self.integtime = integtime
        self.path_calib_dir = path_calib_dir

        # Attributs calibration à charger depuis les fichiers
        self.coeff_c = None        # dict des coefficients polynomiaux calibration lambda (c0s, c1s, c2s, c3s)
        self.B0 = None             # Array bruit de fond (colonne B0 du BACK)
        self.B1 = None             # Array bruit de fond (colonne B1 du BACK)
        self.B = None              # Array bruit de fond total (sera calculé)
        self.cal = None            # Array fonction de sensibilité (CAL)
        self.dark_pixels = None    # Indices des pixels sombres
        self.cal_lambda = None     # Lambda calibrées (après calcul/interpolation)
        self.cal_data = None       # Données calibrées (après calcul/interpolation)

    def load_calibration_files(self):
        path_ini = os.path.join(self.path_calib_dir, f"{self.nom_capteur}.ini")
        path_back = os.path.join(self.path_calib_dir, f"Back_{self.nom_capteur}.dat")
        path_cal = os.path.join(self.path_calib_dir, f"Cal_{self.nom_capteur}.dat")

        # Utilisation des méthodes statiques de DataManager
        self.coeff_c = DataManager.read_ini_file(path_ini)
        if 'DarkPixelStart' in self.coeff_c and 'DarkPixelStop' in self.coeff_c:
            self.dark_pixels = (self.coeff_c['DarkPixelStart'], self.coeff_c['DarkPixelStop'])
        self.B0, self.B1 = DataManager.read_back_file(path_back, self.integtime)
        self.cal = DataManager.read_cal_file(path_cal)
        self.cal_lambda = None
        self.cal_data = None
        print(f"[INFO] Calibration chargée pour {self.nom_capteur}")


    def calcul_bruit_de_fond(self):
        t0 = 8192.0
        if self.B0 is None or self.B1 is None:
            raise ValueError("B0 et/ou B1 non initialisés.")
        if self.integtime is None:
            raise ValueError("Le temps d'intégration n'est pas défini.")
        self.B = self.B0 + (float(self.integtime) / t0) * self.B1
        print(f"[INFO] Bruit de fond B calculé pour {self.nom_capteur} (taille : {len(self.B)})")

    def calibrate_wavelengths(self, raw_lamda):
        if self.coeff_c is None:
            raise ValueError("Les coefficients de calibration ne sont pas chargés.")
        c0 = self.coeff_c['c0s']
        c1 = self.coeff_c['c1s']
        c2 = self.coeff_c['c2s']
        c3 = self.coeff_c['c3s']
        lam_mod = raw_lamda + 1
        lambda_calib = c0 + c1 * lam_mod + c2 * (lam_mod ** 2) + c3 * (lam_mod ** 3)
        print(f"[INFO] Longueurs d'onde calibrées min/max : {lambda_calib.min()} / {lambda_calib.max()}")
        return lambda_calib

    def calibrate_spectre(self, raw_data, raw_lamda):
        lambda_calib = self.calibrate_wavelengths(raw_lamda)
        self.cal_lambda = lambda_calib
        t0 = 8192.0
        M = raw_data / 65535.0
        if self.B is None:
            raise ValueError("Bruit de fond B non calculé.")
        c = M - self.B
        if self.dark_pixels is None:
            raise ValueError("Indices des pixels sombres non définis.")
        i0 = self.dark_pixels[0] - 1
        i1 = self.dark_pixels[1]
        offset = np.mean(c[i0:i1])
        d = c - offset
        e = d * (t0 / float(self.integtime))
        if self.cal is None:
            raise ValueError("Fonction de sensibilité (cal) non chargée.")
        f = np.empty_like(e)
        np.divide(e, self.cal, out=f, where=(self.cal != 0))
        f[self.cal == 0] = np.nan
        self.cal_data = f
        print(f"[INFO] Calibration terminée pour un spectre du capteur {self.nom_capteur}.")

    def interpolate_spectre(self, mode='UV_Vis'):
        if self.cal_lambda is None or self.cal_data is None:
            raise ValueError("Données calibrées absentes.")
        if mode == 'UV_Vis':
            new_lam = np.arange(310, 951, 1)
        elif mode == 'UV':
            new_lam = np.arange(280, 501, 1)
        else:
            raise ValueError("Mode d'interpolation inconnu.")
        limite_max = new_lam.max()
        mask = (self.cal_lambda <= limite_max) & np.isfinite(self.cal_data)
        lam = self.cal_lambda[mask]
        dat = self.cal_data[mask]
        if lam.size < 2:
            raise ValueError("Pas assez de points valides pour interpoler.")
        interp = interp1d(lam, dat, kind='cubic', bounds_error=False, fill_value=np.nan)
        new_dat = interp(new_lam)
        self.cal_lambda = new_lam
        self.cal_data = new_dat
        print(f"[INFO] Interpolation '{mode}' effectuée ({len(new_lam)} points).")

    # ... et les méthodes utilitaires de lecture read_ini_file, read_back_file, read_cal_file, etc.

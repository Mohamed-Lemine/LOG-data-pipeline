# -*- coding: utf-8 -*-

import os
import numpy as np

class DataManager:
    """
    DataManager pour la gestion de fichiers de mesures brutes (.dat)
    contenant plusieurs spectres (entête + data).
    Permet la lecture structurée du fichier pour calibration.
    """


    @staticmethod
    def parse_dat_file(path_data):
        """
        Parcourt le fichier .dat, lit chaque (entête + bloc data) et retourne
        une liste de spectres (dict {'entete', 'lambda', 'data'}).
        """
        spectres = []
        with open(path_data, 'r') as f:
            while True:
                # Lire l'entête
                entete = {}
                line = f.readline()
                # Aller jusqu'à [DATA] ou [Data]
                while line and line[0:6] not in ['[DATA]', '[Data]']:
                    if line.startswith('IDDevice'):
                        entete['device'] = line.split('=')[1].strip()
                    elif line.startswith('DateTime'):
                        dt = line.split('=')[1].strip().split(' ')
                        entete['date'] = dt[0]
                        entete['heure'] = dt[1]
                    elif line.startswith('Comment '):
                        entete['comment'] = line.split('=')[1].strip()
                    elif line.startswith('IntegrationTime'):
                        entete['integration_time'] = line.split('=')[1].strip()
                    elif line.startswith('InclX'):
                        entete['InclX'] = line.split('=')[1].strip()
                    elif line.startswith('InclY'):
                        entete['InclY'] = line.split('=')[1].strip()
                    elif line.startswith('Pressure'):
                        entete['Pressure'] = line.split('=')[1].strip()
                    line = f.readline()
                # Si on a atteint la fin du fichier
                if not line:
                    break
                # On est sur [DATA], lire 255 lignes de data
                lamda = []
                data = []
                _ = f.readline()  # Souvent une ligne à sauter après [DATA]
                for _ in range(255):
                    dline = f.readline()
                    if not dline:
                        break
                    parts = dline.strip().split()
                    if len(parts) < 2:
                        continue
                    lamda.append(int(parts[0]))
                    data.append(int(parts[1]))
                # Stocker le spectre
                spectres.append({
                    'entete': entete.copy(),
                    'lambda': lamda.copy(),
                    'data': data.copy()
                })
                # Chercher si un autre bloc arrive (ou EOF)
                pos = f.tell()
                next_line = f.readline()
                while next_line and (next_line.strip() == '' or next_line.startswith('[Spectrum]')):
                    pos = f.tell()
                    next_line = f.readline()
                if not next_line:
                    break
                f.seek(pos)
        return spectres



    @staticmethod
    def read_ini_file(path_ini):
        """
        Lit un fichier .ini TRIOS et retourne un dictionnaire :
        {'DarkPixelStart': ..., 'DarkPixelStop': ..., 'c0s': ..., 'c1s': ..., 'c2s': ..., 'c3s': ...}
        """
        coeff_c = {}
        with open(path_ini, 'r') as fic_ini:
            for ligne in fic_ini:
                if ligne.startswith('DarkPixelStart'):
                    coeff_c['DarkPixelStart'] = int(ligne.split('=')[1])
                elif ligne.startswith('DarkPixelStop'):
                    coeff_c['DarkPixelStop'] = int(ligne.split('=')[1])
                elif ligne[:3] in ['c0s', 'c1s', 'c2s', 'c3s']:
                    coeff_c[ligne[:3]] = float(ligne.split('=')[1])
        return coeff_c

    @staticmethod
    def read_back_file(path_back, integtime):
        """
        Lit le fichier BACK_*.dat, extrait les colonnes B0 et B1, retourne B0_arr et B1_arr.
        Le calcul du B effectif sera fait dans la classe métier.
        """
        b0_list = []
        b1_list = []
        with open(path_back, 'r') as fic_b:
            # Va jusqu'à [Data]
            line = ''
            while not line.strip().lower().startswith('[data]'):
                line = fic_b.readline()
                if not line:
                    raise EOFError(f"[Data] section introuvable dans {path_back}")
            fic_b.readline()  # Passe l'en-tête
            for line in fic_b:
                if line.strip().lower().startswith('[end] of [data]'):
                    break
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                _, B0_str, B1_str, *_ = parts
                b0_list.append(float(B0_str))
                b1_list.append(float(B1_str))
        B0_arr = np.array(b0_list, dtype=float)
        B1_arr = np.array(b1_list, dtype=float)
        return B0_arr, B1_arr

    @staticmethod
    def read_cal_file(path_cal):
        """
        Lit le fichier Cal_*.dat (fonction de sensibilité) et retourne un array float.
        """
        cal_list = []
        with open(path_cal, 'r') as fic_cal:
            # Va jusqu'à [Data]
            line = ''
            while not line.strip().lower().startswith('[data]'):
                line = fic_cal.readline()
                if not line:
                    raise EOFError(f"[Data] section introuvable dans {path_cal}")
            fic_cal.readline()  # Passe l'en-tête
            for line in fic_cal:
                if line.strip().lower().startswith('[end] of [data]'):
                    break
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                _, elem_cal_str, *_ = parts
                cal_list.append(elem_cal_str.replace('+NAN', '0'))
        return np.array([float(x) for x in cal_list], dtype=float)



    @staticmethod
    def save_calibrated_spectre_txt(spectre, sensor, base_dir):
        """
        Crée le fichier .txt d'un spectre calibré dans output/calibrated/.

        - spectre : dict avec 'entete' (doit contenir 'device', 'date', 'heure', etc.)
        - sensor  : objet capteur_TRIOS contenant cal_lambda, cal_data, etc.
        - base_dir : dossier racine du projet (le dossier parent contenant /output)
        """

        out_dir = os.path.join(base_dir)
        os.makedirs(out_dir, exist_ok=True)

        # heure au format safe
        h, m, s = spectre['entete']['heure'].split(':')
        heure_safe = f"{int(h):02d}-{int(m):02d}-{int(s):02d}"

        filename = f"{spectre['entete']['device'].upper()}_{spectre['entete']['date']}_{heure_safe}.txt"
        filepath = os.path.join(out_dir, filename)
        print(f" -> Création de {filepath}")

        # Vérification
        if getattr(sensor, 'cal_lambda', None) is None or getattr(sensor, 'cal_data', None) is None:
            raise RuntimeError(f"Pas de données calibrées pour {spectre['entete']['device']}")

        with open(filepath, 'w', encoding='utf-8') as fo:
            fo.write(
                "Nom de l'instrument : %s\n"
                "Fichier_calib_utilise: %s\n"
                "Date : %s\n"
                "Heure : %s\n"
                % (
                    spectre['entete']['device'].upper(),
                    getattr(sensor, 'fichier_Cal', 'NC'),
                    spectre['entete']['date'],
                    spectre['entete']['heure'],
                )
            )

            # Ajout des champs spécifiques si présents dans l'entête
            nom = spectre['entete']['device']
            comment = spectre['entete'].get('comment', '')
            inclx = spectre['entete'].get('InclX', '')
            incly = spectre['entete'].get('InclY', '')
            pressure = spectre['entete'].get('Pressure', '')

            if nom == 'SAM_8172':
                fo.write(
                    f"InclX : {inclx}\nInclY : {incly}\nPressure : {pressure}\nComment : {comment}\n"
                )
            elif nom == 'SAM_80E0':
                fo.write(f"Comment : {comment}\n")
            elif nom.upper() == 'SAM_839E':
                fo.write(
                    f"InclX : {inclx}\nInclY : {incly}\n"
                )

            fo.write("\nl_onde\tdata\n")
            # Écriture du tableau des valeurs calibrées, une ligne par paire (lambda, data)
            for lam, dat in zip(sensor.cal_lambda, sensor.cal_data):
                fo.write(f"{lam}\t{dat}\n")






# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd 
import re 
from openpyxl import load_workbook

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
                    elif line.startswith('Mission  '):
                        entete['mission'] = line.split('=')[1].strip()

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
                    if parts[1].upper() in ["NAN", "-NAN", "+NAN"]:
                        data.append(0)  # ou np.nan
                    else:
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
    
            # Toujours écrire ces lignes, même si vides
            inclx = spectre['entete'].get('InclX', '')
            incly = spectre['entete'].get('InclY', '')
            pressure = spectre['entete'].get('Pressure', '')
            comment = spectre['entete'].get('comment', '')
            mission = spectre['entete'].get('mission', '')
    
            fo.write(
                f"InclX : {inclx}\n"
                f"InclY : {incly}\n"
                f"Pressure : {pressure}\n"
                f"Comment : {comment}\n"
                f"Mission : {mission}\n"
            )
    
            fo.write("\nl_onde\t\tdata\n")
            for lam, dat in zip(sensor.cal_lambda, sensor.cal_data):
                fo.write(f"{lam}\t\t\t{dat}\n")



      # methode pour bilan_radeau 
      
      
      
      
      
    @staticmethod
    def read_calibrated_measure(path: str) -> list:
        """
        Lit un fichier calibré (.txt) et retourne la liste des valeurs mesurées (colonne 'data').
        Ignore les entêtes textuelles.
        """
        values = []
        with open(path, 'r', encoding='utf-8') as f:
            data_section = False
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("l_onde"):
                    data_section = True
                    continue
                if data_section:
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            value = float(parts[-1])
                            values.append(value)
                        except ValueError:
                            continue
        return values

    
    @staticmethod
    def read_station_metadata(path: str) -> pd.DataFrame:
        """
        Lit le fichier Excel des métadonnées de stations à l'emplacement `path`
        et retourne les colonnes : 'Station', 'date', 'heure_locale', 'lat', 'lon'.
        Adapte le format des heures (ex : '9h45' -> '09:45') pour compatibilité avec enrichissement.
        """
        # Lecture brute
        df = pd.read_excel(path)
        df.columns = [col.strip().lower() for col in df.columns]
    
        # Dictionnaire de correspondance possible
        mapping = {
            'Station': ['station', 'tag', 'nom_station'],
            'date': ['date', 'day', 'jour'],
            'heure_locale': ['heure_locale', 'heure_local', 'hour', 'heure'],
            'lat': ['lat', 'latitude'],
            'lon': ['lon', 'long', 'longitude']
        }
            
        # Détection automatique des bonnes colonnes
        selected_cols = {}
        for key, possibles in mapping.items():
            for option in possibles:
                if option in df.columns:
                    selected_cols[key] = option
                    break
            else:
                selected_cols[key] = None  # Colonne absente
    
        # Construction du DataFrame extrait
        df_extrait = pd.DataFrame()
        for key in mapping.keys():
            col = selected_cols[key]
            if col:
                df_extrait[key] = df[col]
            else:
                df_extrait[key] = pd.NA
    
        # Correction du format de l'heure (ex : '9h45' -> '09:45')
        def normalize_hour(val):
            if pd.isna(val):
                return val
            val = str(val)
            match = re.match(r'^(\d{1,2})h(\d{2})$', val)
            if match:
                h, m = match.groups()
                return f"{int(h):02d}:{m}"
            return val
    
        df_extrait['heure_locale'] = df_extrait['heure_locale'].apply(normalize_hour)
        df_extrait = df_extrait.dropna(subset=['Station', 'date', 'heure_locale'])
        print(df_extrait.to_string())
        return df_extrait



    
    @staticmethod
    def write_bilan_radeau_tagged(df: pd.DataFrame, path: str) -> None:
        """
        Écrit le DataFrame fourni (df) dans un fichier Excel à l'emplacement `path`,
        en ajustant automatiquement la largeur des colonnes pour la lisibilité.
        """
        # Écriture initiale du fichier Excel
        df.to_excel(path, index=False)
        
        # Ajustement automatique des largeurs de colonnes
        wb = load_workbook(path)
        ws = wb.active
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column name
            for cell in col:
                try:
                    if cell.value:
                        length = len(str(cell.value))
                        if length > max_length:
                            max_length = length
                except:
                    pass
            adjusted_width = max_length + 2
            ws.column_dimensions[column].width = adjusted_width
        wb.save(path)


    # methode pour l'absorption 
    @staticmethod
    def read_calibrated_header(path: str) -> dict:
        """
        Lit l'entête d'un fichier calibré (.txt) et retourne un dictionnaire avec :
        - 'InclX'
        - 'InclY'
        Si le champ n'existe pas dans l'entête, sa valeur sera -999.
        """
        header = {
            'InclX': -999,
            'InclY': -999,
        }
    
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("l_onde"):
                    break  # Arrêt dès qu'on atteint la table de données
                if line.startswith("InclX"):
                    try:
                        header['InclX'] = float(line.split(':')[1].strip())
                    except Exception:
                        pass
                elif line.startswith("InclY"):
                    try:
                        header['InclY'] = float(line.split(':')[1].strip())
                    except Exception:
                        pass
        return header



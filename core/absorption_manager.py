#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 18:18:14 2025

@author: mdlemineahmedou
"""
import numpy as np
import pandas as pd 
import datetime as dt
import math
import os
import glob

from core.data_manager import DataManager


    
class AbsorptionManager:
    
    def __init__(self, path_bilan_tagge: str, path_absorption: str = None, path_distance: str = None, path_absorption_default: str = None):
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.path_bilan_tagge = path_bilan_tagge
        self.path_absorption = path_absorption
        self.path_distance = path_distance
    
        # Chemin par défaut (tu peux le coder en dur si besoin)
        if path_absorption_default is None:
            self.path_absorption_default = os.path.join(self.project_root, "data", "absorption", "absorption_default.xlsx")
        else:
            self.path_absorption_default = path_absorption_default
    
        # Mission
        bilan_name = os.path.basename(path_bilan_tagge)
        self.mission = bilan_name[len("bilan_tagge_"):-len(".xlsx")]
    
        # Chargement DataFrame du bilan
        self.df_bilan = pd.read_excel(path_bilan_tagge)
    
        # Chargement absorption principale (si fourni)
        if path_absorption and os.path.isfile(path_absorption):
            self.df_absorption = pd.read_excel(path_absorption)
        else:
            self.df_absorption = None
    
        # Chargement absorption par défaut (toujours existant, lève si absent)
        self.df_absorption_default = pd.read_excel(self.path_absorption_default)

        
        
        
        
    def assign_distances_by_station(self):
        """
        Version ultra-rapide : pour chaque mesure, trouve la distance la plus proche avec searchsorted.
        """
    
        distances = self.read_distance_file(self.path_distance)  # {datetime: distance_cm}
        df = self.df_bilan.copy()
        df['datetime'] = df['nom_fichier_Lu'].str[9:-4].apply(
            lambda s: pd.to_datetime(s, format='%Y-%m-%d_%H-%M-%S')
        )
    
        dict_by_station = {}
    
        if not distances:
            print("[INFO] Aucun fichier de distance fourni : fallback à 4.0 cm partout")
            for tag, group in df.groupby('Tag'):
                dict_by_station[tag] = {ts: 4.0 for ts in group['datetime']}
            return dict_by_station
    
        # Préparation numpy trié
        dist_times = np.array(sorted(distances.keys()))
        dist_timestamps = dist_times.astype('datetime64[ns]').astype(np.int64)
        dist_vals = np.array([distances[d] for d in dist_times])
    
        print("[INFO] Matching mesures et distances (ultra-rapide, searchsorted)…")
        for tag, group in df.groupby('Tag'):
            station_dict = {}
            times = np.array(list(group['datetime']))
            times_ns = times.astype('datetime64[ns]').astype(np.int64)
    
            # Pour chaque time, trouve la position d'insertion la plus proche
            idx = np.searchsorted(dist_timestamps, times_ns)
            idx_left = np.clip(idx - 1, 0, len(dist_timestamps) - 1)
            idx_right = np.clip(idx, 0, len(dist_timestamps) - 1)
    
            dist_left = np.abs(times_ns - dist_timestamps[idx_left])
            dist_right = np.abs(times_ns - dist_timestamps[idx_right])
    
            # Prend l'index du plus proche des deux côtés
            best_idx = np.where(dist_left <= dist_right, idx_left, idx_right)
    
            for ts, idx_match in zip(times, best_idx):
                station_dict[ts] = dist_vals[idx_match]
            dict_by_station[tag] = station_dict
    
            # Debug synthèse
            print(f"[DEBUG] {tag}: {len(times)} mesures, exemples :")
            for i in range(min(3, len(times))):
                print(f"    - {times[i]} → {dist_vals[best_idx[i]]:.2f} cm (distance à {dist_times[best_idx[i]]})")
        return dict_by_station

    
    




    
    @staticmethod
    def read_distance_file(path_distance, dist_sol_mm=247.8):
        """
        Lit un fichier ou un dossier de distances et retourne {datetime: distance_cm}.
        Bloque (Exception) si une seule ligne a un format de date/heure non reconnu.
        Affiche les fichiers trouvés et un extrait du DataFrame résultat.
        """
        distances = {}
    
        if path_distance is None:
            print("[INFO] Aucun chemin de distance fourni.")
            return distances
    
        # 1. Récupération des fichiers à traiter
        files = []
        if os.path.isdir(path_distance):
            files = sorted(glob.glob(os.path.join(path_distance, "*.txt")))
            if not files:
                raise FileNotFoundError(f"Aucun fichier .txt trouvé dans {path_distance}")
        elif os.path.isfile(path_distance):
            files = [path_distance]
        else:
            raise FileNotFoundError(f"Chemin distance non trouvé : {path_distance}")
    
        print("[INFO] Fichiers trouvés pour la distance :")
        for f in files:
            print("  -", os.path.basename(f))
    
        # 2. Parsing
        errors = []
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 3:
                        continue
                    date_str, heure_str, dist_str = parts
                    dt_key = None
                    # Teste tous les formats connus
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
                        try:
                            dt_key = dt.datetime.strptime(f"{date_str} {heure_str}", fmt)
                            break
                        except Exception:
                            continue
                    if dt_key is None:
                        errors.append(f"{file} ({line.strip()}) : format date/heure non reconnu")
                        # BLOQUE dès la première erreur de parsing date/heure :
                        raise ValueError(
                            f"[ERREUR PARSING] Format date/heure non reconnu : {file} → '{date_str} {heure_str}'"
                        )
                    try:
                        valeur_mm = float(dist_str.replace(",", "."))
                        valeur_cm = (dist_sol_mm - valeur_mm) / 10
                        distances[dt_key] = valeur_cm
                    except Exception as e:
                        errors.append(f"{file} ({line.strip()}) : erreur conversion distance ({e})")
        if errors:
            print("[WARNING] Problèmes rencontrés :")
            for e in errors:
                print("   ", e)
    
        # Debug : conversion en DataFrame pour aperçu rapide
        if distances:
            df_dist = pd.DataFrame(
                list(distances.items()), columns=["datetime", "Distance_cm"]
            ).set_index("datetime").sort_index()
            print("\n[INFO] Extrait du DataFrame distance :")
            print(df_dist.head())
        else:
            print("[INFO] Aucun point de distance n'a été lu.")
    
        return distances

    
    def _compute_solar_zenith(self, jour: str, heure: str, lat: float, lon: float) -> float:
            """
            Calcule et retourne l’angle zénithal solaire (thetas/asol) pour la date, l’heure et la position.
            (Méthode privée : appelée au besoin dans le pipeline)
            """
            # Conversion date/heure en objets utilisables
            t = dt.datetime.strptime(heure, '%H:%M:%S')
            hh_deci = t.hour + t.minute / 60. + t.second / 3600.
    
            d = dt.datetime.strptime(jour, '%Y-%m-%d')
            dayref = dt.datetime(d.year, 1, 1)
            day_number = (d - dayref).days + 1
    
            # === Calcul solaire (reprend la logique de possol/possol_Trios) ===
            fac = math.pi / 180.
            tsm = hh_deci + lon / 15.
            tet = 2. * math.pi * day_number / 365.
    
            # Equation du temps
            a1 = .000075
            a2 = .001868
            a3 = .032077
            a4 = .014615
            a5 = .040849
            et = a1 + a2 * math.cos(tet) - a3 * math.sin(tet) - a4 * math.cos(2. * tet) - a5 * (math.sin(2. * tet))
            et = et * 12. * 60. / math.pi
    
            # True solar time
            tsv = tsm + et / 60.
            tsv = tsv - 12.
    
            # Angle horaire
            ah = tsv * 15. * fac
    
            # Déclinaison solaire
            b1 = .006918
            b2 = .399912
            b3 = .070257
            b4 = .006758
            b5 = .000907
            b6 = .002697
            b7 = .001480
            delta = (b1 - b2 * math.cos(tet) + b3 * math.sin(tet) -
                     b4 * math.cos(2. * tet) + b5 * math.sin(2. * tet) -
                     b6 * math.cos(3. * tet) + b7 * math.sin(3. * tet))
    
            # Elevation solaire
            xla = lat * fac
            amuzero = math.sin(xla) * math.sin(delta) + math.cos(xla) * math.cos(delta) * math.cos(ah)
            elev = math.asin(amuzero) * 180. / math.pi  # en degrés
    
            asol = 90. - elev  # angle zénithal solaire
            return asol

    def apply_absorption_correction(self, data_Lu: np.ndarray, tag: str, thetas: float) -> np.ndarray:
        """
        Applique la correction d’absorption sur un spectre Lu donné,
        pour la station `tag` et l’angle solaire `thetas` fourni.
        Utilise la ligne du tag dans df_absorption si dispo, sinon fallback sur df_absorption_default (unique ligne).
        Compatible tous types de colonnes (int, str).
        """
        # 1. Sélection du DataFrame
        if self.df_absorption is not None:
            abs_row = self.df_absorption[self.df_absorption['tag'] == tag]
            if not abs_row.empty:
                row = abs_row
            else:
                print(f"[Absorption] Tag '{tag}' absent du fichier principal. Utilisation du fichier d'absorption par défaut.")
                row = self.df_absorption_default
        else:
            print(f"[Absorption] Aucun fichier d’absorption fourni. Utilisation du fichier par défaut pour '{tag}'.")
            row = self.df_absorption_default
    
        # 2. Récupération des colonnes numériques (spectre)
        numeric_cols = [c for c in row.columns if (isinstance(c, int) or (isinstance(c, str) and str(c).isdigit()))]
        numeric_cols_sorted = sorted(numeric_cols, key=lambda x: int(x))
        N = len(data_Lu)
        if len(numeric_cols_sorted) < N:
            raise ValueError(f"Pas assez de colonnes absorption ({len(numeric_cols_sorted)}) pour spectre LU ({N})")
        cols_needed = numeric_cols_sorted[:N]
        abs_tot = row.loc[:, cols_needed].iloc[0].astype(float).values
    
        # 3. Correction d’absorption
        theta0 = np.arcsin(np.sin(np.deg2rad(thetas)) / 1.338)
        k = 2.0 / np.tan(theta0)
        eps = 1.0 - np.exp(-k * abs_tot * 0.024)
        data_shadow = data_Lu / (1.0 - eps)
        return data_shadow




        


    def process_station_spectra(self):
        """
        Pour chaque ligne du bilan taggé :
        - lit les fichiers spectres et métadonnées,
        - calcule thetas,
        - applique la correction d’absorption/shadow,
        - construit et stocke UN DataFrame PAR STATION pour LU (corrigé), Edref, Rrs.
        """
        path_calibrated = os.path.join(self.project_root, "output", "calibrated", self.mission)
        # ... (reste du traitement)
        lam = np.arange(310, 951)
    
        # Initialisation des dictionnaires de listes, un par station
        dict_Lu_shadow = {}
        dict_Edref = {}
        dict_Rrs = {}
    
        for idx, row in self.df_bilan.iterrows():
            tag = row['Tag']
            lat = float(row['Lat'])
            lon = float(row['Lon'])
            nomfic_Lu = row['nom_fichier_Lu']
            nomfic_Edref = row['nom_fichier_Edref']
    
            # Lecture des données LU (spectre + meta)
            data_Lu = DataManager.read_calibrated_measure(os.path.join(path_calibrated, nomfic_Lu))
            meta_Lu = DataManager.read_calibrated_header(os.path.join(path_calibrated, nomfic_Lu))
            InclX = meta_Lu.get("InclX", np.nan)
            InclY = meta_Lu.get("InclY", np.nan)
            data_Edref = DataManager.read_calibrated_measure(os.path.join(path_calibrated, nomfic_Edref))
    
            # Date/heure pour thetas
            date_str = nomfic_Lu[9:-4]
            jour, heure = date_str[:10], date_str[11:].replace('-', ':')
    
            thetas = self._compute_solar_zenith(jour, heure, lat, lon)
            data_shadow = self.apply_absorption_correction(np.array(data_Lu), tag, thetas)
            data_rrs = data_shadow / np.array(data_Edref) * 0.543
    
            yy, mm, dd = map(int, jour.split('-'))
            hh, mn, ss = map(int, heure.split(':'))
            cle_dic = pd.Timestamp(year=yy, month=mm, day=dd, hour=hh, minute=mn, second=ss)
    
            # Ajout dans la bonne station
            for dico, arr in zip(
                [dict_Lu_shadow, dict_Edref, dict_Rrs],
                [data_shadow, data_Edref, data_rrs]
            ):
                if tag not in dico:
                    dico[tag] = []
                dico[tag].append((cle_dic, InclX, InclY, arr))
    
        # Construction des DataFrames finaux PAR STATION
        self.df_Lu_shadow = {}
        self.df_Edref = {}
        self.df_Rrs = {}
        for tag in dict_Lu_shadow:
            # Pour chaque spectre de la station : index temporel, colonnes lambda, + InclX/InclY
            index = []
            inclx = []
            incly = []
            data_lu_shadow = []
            data_edref = []
            data_rrs = []
    
            # On récupère les tuples pour chaque spectre (dans le même ordre)
            for t, x, y, s in dict_Lu_shadow[tag]:
                index.append(t)
                inclx.append(x)
                incly.append(y)
                data_lu_shadow.append(s)
            for _, _, _, s in dict_Edref[tag]:
                data_edref.append(s)
            for _, _, _, s in dict_Rrs[tag]:
                data_rrs.append(s)
    
            df_lu_shadow = pd.DataFrame(data_lu_shadow, index=index, columns=lam)
            df_lu_shadow.insert(0, 'InclX', inclx)
            df_lu_shadow.insert(1, 'InclY', incly)
            self.df_Lu_shadow[tag] = df_lu_shadow
    
            df_edref = pd.DataFrame(data_edref, index=index, columns=lam)
            df_edref.insert(0, 'InclX', inclx)
            df_edref.insert(1, 'InclY', incly)
            self.df_Edref[tag] = df_edref
    
            df_rrs = pd.DataFrame(data_rrs, index=index, columns=lam)
            df_rrs.insert(0, 'InclX', inclx)
            df_rrs.insert(1, 'InclY', incly)
            self.df_Rrs[tag] = df_rrs
    
        # À ce stade, tu as :
        # - self.df_Lu_shadow[tag] : DataFrame LU corrigé pour chaque station
        # - self.df_Edref[tag]     : DataFrame Edref pour chaque station
        # - self.df_Rrs[tag]       : DataFrame Rrs pour chaque station

    



    def save_pkl_files(self):
        """
        Sauvegarde tous les DataFrames générés dans output/pkl_by_station/{mission}/, 
        un fichier par station et par type (Lu_shadow, Edref, Rrs, Distance).
        """
        output_dir = os.path.join("output", "pkl_by_station", self.mission)
        os.makedirs(output_dir, exist_ok=True)
    
        # 1. Sauvegarde Lu_shadow, Edref, Rrs
        for tag, df in self.df_Lu_shadow.items():
            df.to_pickle(os.path.join(output_dir, f"df_Lu_shadow_{tag}.pkl"))
        for tag, df in self.df_Edref.items():
            df.to_pickle(os.path.join(output_dir, f"df_Edref_{tag}.pkl"))
        for tag, df in self.df_Rrs.items():
            df.to_pickle(os.path.join(output_dir, f"df_Rrs_{tag}.pkl"))
    
        # 2. Distances : on calcule et on sauvegarde aussi (si fichier distance fourni ou valeurs par défaut)
        self.df_Distance = {}
        self.distances_by_station = self.assign_distances_by_station()
        for tag, ts_dict in self.distances_by_station.items():
            df_dist = pd.DataFrame.from_dict(ts_dict, orient="index", columns=["Distance_cm"])
            df_dist.index.name = "datetime"
            self.df_Distance[tag] = df_dist
            df_dist.to_pickle(os.path.join(output_dir, f"df_Distance_{tag}.pkl"))
    
        print(f"[INFO] Fichiers PKL sauvegardés dans {output_dir}")



    
    def get_df(self, tag: str, var: str) -> 'pd.DataFrame':
        """
        Accès rapide à un DataFrame (Lu_shadow, Edref, Rrs) pour une station donnée.
        var doit être l'un de : 'Lu_shadow', 'Edref', 'Rrs'
        """
        var = var.lower()
        if var == 'lu_shadow':
            return self.df_Lu_shadow[tag]
        elif var == 'edref':
            return self.df_Edref[tag]
        elif var == 'rrs':
            return self.df_Rrs[tag]
        elif var == 'distance':
            return self.df_Distance[tag]

        else:
            raise ValueError(f"Type de variable inconnu : {var} (choisir 'Lu_shadow', 'Edref', ou 'Rrs')")



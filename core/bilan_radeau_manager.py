import pandas as pd

from core.data_manager import DataManager
import os 
import re
from datetime import timedelta
import numpy as np

class BilanRadeauBuilder:
    
    def __init__(self, path_calibrated: str, path_stations_metadata: str):
        """
        Initialise la classe avec :
        - path_calibrated : chemin du dossier contenant les fichiers calibrés
        - path_stations_metadata : chemin du fichier Excel des métadonnées stations
        Charge directement les métadonnées des stations en interne.
        """
        self.path_calibrated = path_calibrated
        self.path_stations_metadata = path_stations_metadata
        self.df_mesures = None
        self.df_lu_ref = None
        self.df_bilan_brut = None
    
        # Lecture immédiate des métadonnées des stations
        self.df_stations_metadata = DataManager.read_station_metadata(path_stations_metadata)


    def extract_measure_info(self) -> pd.DataFrame:
        """
        Extrait les infos importantes des fichiers calibrés dans path_calibrated :
        - nom_fichier, capteur, timestamp.
        Retourne et sauvegarde en interne df_mesures.
        """
        files = [f for f in os.listdir(self.path_calibrated) if f.endswith('.txt')]
        records = []
    
        for filename in files:
            # Extraction capteur et timestamp à partir du nom de fichier (ex : SAM_85AE_2024-11-04_14-37-00.txt)
            match = re.match(r'(SAM_[A-Z0-9]+)_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.txt', filename)
            if match:
                capteur, timestamp = match.groups()
                records.append({
                    'nom_fichier': filename,
                    'capteur': capteur,
                    'timestamp': timestamp
                })
    
        # Création et sauvegarde interne du DataFrame des mesures
        self.df_mesures = pd.DataFrame(records)
        return self.df_mesures

    def detect_lu_ref(self) -> pd.DataFrame:
        """
        Détecte les couples Lu/Ref à partir de df_mesures, en attribuant les rôles automatiquement :
        - Le capteur avec la moyenne globale la plus élevée est 'Ref'
        - L'autre est 'Lu'
        Attribue ce rôle fixe à chaque capteur pour toute la campagne.
        Ajoute les colonnes :
          - type_capteur (Lu/Ref)
          - timestamp_couple (clé unique par couple)
        Retourne et sauvegarde en interne df_lu_ref.
        """
        if self.df_mesures is None:
            raise ValueError("Le DataFrame df_mesures n'a pas encore été généré. Appelez extract_measure_info() d'abord.")
    
    
        df = self.df_mesures.copy()
        df['timestamp_dt'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d_%H-%M-%S')
        df['used'] = False
        df['type_capteur'] = pd.Series(dtype="str")
        df['timestamp_couple'] = pd.Series(dtype="str")
    
        # 1. Calcul de la moyenne globale pour chaque capteur
        capteurs = df['capteur'].unique()
        capteur_means = {}
        for capteur in capteurs:
            fichiers = df[df['capteur'] == capteur]['nom_fichier']
            valeurs = []
            for fichier in fichiers:
                file_path = os.path.join(self.path_calibrated, fichier)
                try:
                    valeurs.append(np.nanmean(DataManager.read_calibrated_measure(file_path)))
                except Exception:
                    pass  # ignore les erreurs de lecture
            capteur_means[capteur] = np.nanmean(valeurs) if valeurs else np.nan
    
        # Attribution automatique des rôles
        if len(capteur_means) != 2:
            raise ValueError("La détection automatique attend exactement deux capteurs différents pour l'appariement.")
    
        sorted_caps = sorted(capteur_means.items(), key=lambda item: item[1], reverse=True)
        ref_capteur, lu_capteur = sorted_caps[0][0], sorted_caps[1][0]  # Ref = + grande moyenne
        roles_par_capteur = {ref_capteur: 'Ref', lu_capteur: 'Lu'}
    
        # 2. Apparier chaque couple (à ±1 seconde)
        for idx, row in df.iterrows():
            if df.loc[idx, 'used']:
                continue
            current_time = row['timestamp_dt']
            current_capteur = row['capteur']
            # Chercher un fichier d'un autre capteur, non utilisé, à ±1s
            mask = (
                (df['capteur'] != current_capteur) &
                (~df['used']) &
                (df['timestamp_dt'] >= current_time - timedelta(seconds=1)) &
                (df['timestamp_dt'] <= current_time + timedelta(seconds=1))
            )
            candidates = df[mask]
            if not candidates.empty:
                candidates = candidates.copy()
                candidates['delta'] = candidates['timestamp_dt'].apply(lambda t: abs((t - current_time).total_seconds()))
                best_idx = candidates['delta'].idxmin()
                idx1, idx2 = idx, best_idx
    
                # Rôle d'après la table automatique
                df.loc[idx1, 'type_capteur'] = roles_par_capteur[df.loc[idx1, 'capteur']]
                df.loc[idx2, 'type_capteur'] = roles_par_capteur[df.loc[idx2, 'capteur']]
    
                # Timestamp du Lu pour le couple
                if df.loc[idx1, 'type_capteur'] == 'Lu':
                    ts_lu = df.loc[idx1, 'timestamp']
                else:
                    ts_lu = df.loc[idx2, 'timestamp']
    
                df.loc[[idx1, idx2], 'timestamp_couple'] = ts_lu
                df.loc[[idx1, idx2], 'used'] = True
    
        # Nettoyage final
        df = df.drop(columns=['timestamp_dt', 'used'])
        self.df_lu_ref = df
        return df




    def build_bilan_brut(self) -> pd.DataFrame:
        """
        Construit un DataFrame bilan structuré à partir de df_lu_ref.
        Colonnes finales : nom_fichier_Lu, nom_fichier_Edref, timestamp_couple.
        Retourne et sauvegarde en interne df_bilan_brut.
        """
        # Séparation des fichiers Lu et Ref
        df_lu = self.df_lu_ref[self.df_lu_ref['type_capteur'] == 'Lu'][['timestamp_couple', 'nom_fichier']]
        df_ref = self.df_lu_ref[self.df_lu_ref['type_capteur'] == 'Ref'][['timestamp_couple', 'nom_fichier']]
    
        # Fusion sur la clé de couple (timestamp_couple)
        df_bilan = pd.merge(
            df_lu,
            df_ref,
            on='timestamp_couple',
            suffixes=('_Lu', '_Edref')
        )
    
        # Réorganisation des colonnes
        df_bilan = df_bilan[['nom_fichier_Lu', 'nom_fichier_Edref', 'timestamp_couple']]
    
        # Sauvegarde interne
        self.df_bilan_brut = df_bilan
        return self.df_bilan_brut


    def enrich_with_station_metadata(self) -> pd.DataFrame:
        """
        Enrichit df_bilan_brut avec les métadonnées station (df_stations_metadata).
        Attribue à chaque couple la station dont le début précède son timestamp,
        en tenant compte de l'intervalle [start_i, start_{i+1}[.
        Si aucune station n'est trouvée (orphelin), assigne la station la plus proche.
        Colonnes finales : nom_fichier_Lu, nom_fichier_Edref, Tag, Lat, Lon.
        """
        df_bilan = self.df_bilan_brut.copy()
    
        # 1. Convertir le timestamp_couple en datetime
        df_bilan['datetime_mesure'] = pd.to_datetime(
            df_bilan['timestamp_couple'], format='%Y-%m-%d_%H-%M-%S'
        )
    
        # 2. Préparer les stations triées par datetime_debut
        df_stations = self.df_stations_metadata.copy()
        df_stations['datetime_debut'] = pd.to_datetime(
            df_stations['date'].astype(str) + ' ' + df_stations['heure_locale'].astype(str)
        )
        df_stations = df_stations.sort_values('datetime_debut').reset_index(drop=True)
        df_stations['datetime_fin'] = df_stations['datetime_debut'].shift(-1)
        df_stations.at[len(df_stations) - 1, 'datetime_fin'] = pd.Timestamp.max
    
        # 3. Fonction unique qui gère le cas orphelin aussi
        def trouver_station(mesure_time):
            # Essaye de trouver une station correspondant au créneau
            ligne = df_stations[
                (df_stations['datetime_debut'] <= mesure_time) &
                (df_stations['datetime_fin'] > mesure_time)
            ]
            if not ligne.empty:
                return pd.Series([
                    ligne.iloc[0]['Station'],
                    ligne.iloc[0]['lat'],
                    ligne.iloc[0]['lon']
                ])
            else:
                # Cas orphelin : station la plus proche
                distances = abs(df_stations['datetime_debut'] - mesure_time)
                idx_min = distances.idxmin()
                return pd.Series([
                    df_stations.loc[idx_min, 'Station'],
                    df_stations.loc[idx_min, 'lat'],
                    df_stations.loc[idx_min, 'lon']
                ])
    
        # 4. Application directe
        df_bilan[['Tag', 'Lat', 'Lon']] = df_bilan['datetime_mesure'].apply(trouver_station)
    
        # >>> Ajoute ce tri ici, AVANT d’extraire les colonnes finales <<<
        df_bilan = df_bilan.sort_values(by=['Tag', 'datetime_mesure']).reset_index(drop=True)
        
        # 5. Colonnes finales
        df_final = df_bilan[['nom_fichier_Lu', 'nom_fichier_Edref', 'Tag', 'Lat', 'Lon']]
    
        return df_final





    
    def build_bilan(self, path_output: str) -> pd.DataFrame:
        """
        Enchaîne tout le pipeline de traitement pour produire et enregistrer le bilan enrichi final :
        - Extraction des mesures
        - Appariement Lu/Ref
        - Construction du bilan brut
        - Enrichissement avec les métadonnées stations
        - Sauvegarde dans un fichier Excel via DataManager
        """
        self.extract_measure_info()
        self.detect_lu_ref()
        self.build_bilan_brut()
        df_final = self.enrich_with_station_metadata()
    
        # Création du dossier de sortie si besoin
        os.makedirs(path_output, exist_ok=True)
    
        # Génération du nom de mission à partir du dossier calibré
        mission_name = os.path.basename(os.path.normpath(self.path_calibrated))
    
        # Nom du fichier Excel bilan taggé :
        output_file = os.path.join(path_output, f"bilan_tagge_{mission_name}.xlsx")
    
        # Écriture du fichier final
        DataManager.write_bilan_radeau_tagged(df_final, output_file)
        return df_final






    def get_lu_and_ref_capteurs(self) -> dict:
        """
        Retourne un dictionnaire {capteur: type_capteur} (ex: {'SAM_85AE': 'Lu', 'SAM_8467': 'Ref'})
        Si le type n'existe jamais pour un capteur, on retourne NaN.
        """
        if self.df_lu_ref is None:
            raise ValueError("Le DataFrame df_lu_ref n'a pas encore été généré. Appelez detect_lu_ref() d'abord.")
    
        mapping = self.df_lu_ref[['capteur', 'type_capteur']]
        # Pour chaque capteur, on prend la **première valeur non-NaN** (sinon NaN si aucune)
        roles = (
            mapping
            .drop_duplicates()
            .groupby('capteur', sort=False)['type_capteur']
            .apply(lambda x: x.dropna().iloc[0] if not x.dropna().empty else np.nan)
            .to_dict()
        )
        return roles


    








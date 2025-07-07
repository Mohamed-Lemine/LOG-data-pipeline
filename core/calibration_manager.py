import numpy as np
from core.capteur import CapteurTRIOS  # adapte l'import selon ton organisation
from core.data_manager import DataManager
import sys 
import os 

class CalibrationManager:
    """
    Orchestrateur du pipeline de calibration multi-capteurs TRIOS.
    """
    
    def __init__(self, path_calib_dir):
        """
        path_calib_dir : dossier où se trouvent tous les fichiers calibration pour chaque capteur
        """
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        self.path_calib_dir = path_calib_dir
        self.capteurs = {}  # Cache {nom_capteur: CapteurTRIOS}

    def get_or_create_capteur(self, nom_capteur, integtime):
        """
        Récupère un objet CapteurTRIOS déjà chargé, ou le crée et initialise si besoin.
        """
        key = (nom_capteur, integtime)
        if key in self.capteurs:
            return self.capteurs[key]
        capteur = CapteurTRIOS(nom_capteur, integtime, self.path_calib_dir)
        capteur.load_calibration_files()
        capteur.calcul_bruit_de_fond()
        self.capteurs[key] = capteur
        return capteur



    def run_full_calibration_pipeline(self, path_data, output_dir, interpolation_mode='UV_Vis'):
        """
        Pipeline complet : calibration et export pour tous les spectres d'un .dat multi-capteurs.
        Les fichiers calibrés sont stockés dans un sous-dossier du output_dir nommé selon le fichier brut.
        """
        # 1. Charger tous les spectres bruts (.dat)
        spectres = DataManager.parse_dat_file(path_data)
    
        # 2. Déterminer le nom de la mission : priorité à l'entête du premier spectre
        first_entete = spectres[0]['entete']
        mission_name = first_entete.get('mission', '').strip()
        
        if not mission_name or mission_name.lower() == "no mission":
            # Fallback sur le nom du fichier si non renseigné
            filename = os.path.basename(path_data)
            if filename.startswith("export_"):
                mission_name = filename[len("export_"):]
            else:
                mission_name = filename
            mission_name = os.path.splitext(mission_name)[0]

    
        # 3. Créer le sous-dossier s'il n'existe pas
        calib_out_dir = os.path.join(output_dir, mission_name)
        os.makedirs(calib_out_dir, exist_ok=True)
    
        # 4. Calibration et export
        for spectre in spectres:
            entete = spectre['entete']
            nom_capteur = entete['device']
            integtime = int(entete['integration_time'])
    
            capteur = self.get_or_create_capteur(nom_capteur, integtime)
            raw_data = np.array(spectre['data'])
            raw_lamda = np.array(spectre['lambda'])
            capteur.calibrate_spectre(raw_data, raw_lamda)
            capteur.interpolate_spectre(mode=interpolation_mode)
    
            # Exporter dans le sous-dossier mission !
            DataManager.save_calibrated_spectre_txt(
                spectre=spectre,
                sensor=capteur,
                base_dir=calib_out_dir
            )

        
        print(f"[INFO] Pipeline terminé : {len(spectres)} spectres calibrés et exportés dans {output_dir}")
        return len(spectres) 

    # ... tu peux ajouter des méthodes utilitaires/logs si besoin

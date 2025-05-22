import numpy as np
from core.capteur import CapteurTRIOS  # adapte l'import selon ton organisation
from core.data_manager import DataManager

class CalibrationManager:
    """
    Orchestrateur du pipeline de calibration multi-capteurs TRIOS.
    """

    def __init__(self, path_calib_dir):
        """
        path_calib_dir : dossier où se trouvent tous les fichiers calibration pour chaque capteur
        """
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
        - path_data    : chemin du .dat à traiter
        - output_dir   : dossier output/calibrated/
        - interpolation_mode : 'UV_Vis' ou 'UV'
        """
        # 1. Charger tous les spectres bruts (.dat)
        spectres = DataManager.parse_dat_file(path_data)

        for spectre in spectres:
            entete = spectre['entete']
            nom_capteur = entete['device']
            integtime = int(entete['integration_time'])

            # 2. Obtenir ou créer l'objet CapteurTRIOS approprié
            capteur = self.get_or_create_capteur(nom_capteur, integtime)

            # 3. Calibration du spectre
            raw_data = np.array(spectre['data'])
            raw_lamda = np.array(spectre['lambda'])
            capteur.calibrate_spectre(raw_data, raw_lamda)
            capteur.interpolate_spectre(mode=interpolation_mode)

            # 4. Exporter le spectre calibré via DataManager
            DataManager.save_calibrated_spectre_txt(
                spectre=spectre,
                sensor=capteur,
                base_dir=output_dir  # base_dir ou project_root selon ta méthode d'export
            )

        print(f"[INFO] Pipeline terminé : {len(spectres)} spectres calibrés et exportés dans {output_dir}")

    # ... tu peux ajouter des méthodes utilitaires/logs si besoin

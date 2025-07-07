#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 13:33:55 2025

@author: mdlemineahmedou
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# 1. Racine du projet
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
from core.bilan_radeau_manager import BilanRadeauBuilder

def main():

    # 2. Chemins relatifs à la racine projet
    path_calibrated = os.path.join(BASE_DIR, "output" , "calibrated" ,"recife_2024" )
    path_station_metadata = os.path.join(BASE_DIR, "data","stations_metadata"  ,"santa_cruz_metadata.xlsx")
    path_output = os.path.join(BASE_DIR, "output", "bilan_tagge")

    # 3. Instanciation du builder
    builder = BilanRadeauBuilder(path_calibrated, path_station_metadata)

    # 4. Lancement du pipeline complet
    df_final = builder.build_bilan(path_output)

    # 5. Affichage résumé
    print("✅ Bilan final généré et sauvegardé ")
    print(df_final.head())
    print(builder.get_lu_and_ref_capteurs())

if __name__ == "__main__":
    main()


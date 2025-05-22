#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:54:07 2025

@author: mdlemineahmedou
"""

import sys
import os

# Ajouter le dossier racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer la fenêtre principale
from gui.main_window import MainWindow

if __name__ == "__main__":
    # Instancier et démarrer la fenêtre principale
    app = MainWindow()
    app.mainloop()

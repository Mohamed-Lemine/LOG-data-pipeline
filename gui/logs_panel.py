#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:44:53 2025

@author: mdlemineahmedou
"""

import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class LogsPanel(tk.Frame):
    def __init__(self, master):
        """
        Initialise une zone de texte scrollable pour afficher les logs utilisateur.
        - master : fenêtre ou frame parente.
        """
        super().__init__(master)

        self.text_area = ScrolledText(self, width=80, height=15, state='disabled', wrap='word')
        self.text_area.pack(expand=True, fill='both')

    def log(self, message):
        """
        Affiche un message dans la zone de logs.
        - message : texte à afficher
        """
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.config(state='disabled')
        self.text_area.see(tk.END)

    def clear(self):
        """
        Efface tous les logs de la zone de texte.
        """
        self.text_area.config(state='normal')
        self.text_area.delete('1.0', tk.END)
        self.text_area.config(state='disabled')

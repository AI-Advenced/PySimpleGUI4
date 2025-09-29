"""
Application de Comptabilité Avancée
Développée avec PySimpleGUI4 et SQLite
Version complète avec toutes les fonctionnalités
"""

import PySimpleGUI4 as sg
import sqlite3
import datetime
import os
import json
import csv
import math
from decimal import Decimal
import hashlib
import re
from typing import Dict, List, Tuple, Optional
import threading
import time
import subprocess
import sys

# Configuration de l'application
APP_NAME = "Système de Comptabilité Avancée"
APP_VERSION = "2.0.0"
DB_NAME = "comptabilite.db"
CONFIG_FILE = "config.json"

# Thèmes disponibles
THEMES = [
    'DarkBlue3', 'DarkGreen', 'DarkTeal', 'LightGreen', 'BluePurple',
    'Purple', 'BlueMono', 'GreenMono', 'BrownBlue', 'BrightColors',
    'NeutralBlue', 'Kayak', 'SandyBeach', 'TealMono', 'Topanga'
]

class DatabaseManager:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données avec toutes les tables nécessaires"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Table des comptes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comptes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE NOT NULL,
                    nom TEXT NOT NULL,
                    type TEXT NOT NULL,
                    parent_id INTEGER,
                    solde REAL DEFAULT 0,
                    actif BOOLEAN DEFAULT 1,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES comptes (id)
                )
            ''')
            
            # Table des écritures comptables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ecritures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE NOT NULL,
                    date_ecriture DATE NOT NULL,
                    libelle TEXT NOT NULL,
                    montant_total REAL NOT NULL,
                    statut TEXT DEFAULT 'brouillon',
                    piece_jointe TEXT,
                    utilisateur TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des lignes d'écriture
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lignes_ecriture (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ecriture_id INTEGER NOT NULL,
                    compte_id INTEGER NOT NULL,
                    libelle TEXT NOT NULL,
                    debit REAL DEFAULT 0,
                    credit REAL DEFAULT 0,
                    FOREIGN KEY (ecriture_id) REFERENCES ecritures (id) ON DELETE CASCADE,
                    FOREIGN KEY (compte_id) REFERENCES comptes (id)
                )
            ''')
            
            # Table des clients
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    nom TEXT NOT NULL,
                    prenom TEXT,
                    raison_sociale TEXT,
                    adresse TEXT,
                    ville TEXT,
                    code_postal TEXT,
                    pays TEXT DEFAULT 'France',
                    telephone TEXT,
                    email TEXT,
                    siret TEXT,
                    tva TEXT,
                    conditions_paiement INTEGER DEFAULT 30,
                    limite_credit REAL DEFAULT 0,
                    actif BOOLEAN DEFAULT 1,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des fournisseurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fournisseurs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    nom TEXT NOT NULL,
                    raison_sociale TEXT,
                    adresse TEXT,
                    ville TEXT,
                    code_postal TEXT,
                    pays TEXT DEFAULT 'France',
                    telephone TEXT,
                    email TEXT,
                    siret TEXT,
                    tva TEXT,
                    conditions_paiement INTEGER DEFAULT 30,
                    actif BOOLEAN DEFAULT 1,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des factures
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS factures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE NOT NULL,
                    client_id INTEGER NOT NULL,
                    date_facture DATE NOT NULL,
                    date_echeance DATE NOT NULL,
                    montant_ht REAL NOT NULL,
                    montant_tva REAL NOT NULL,
                    montant_ttc REAL NOT NULL,
                    statut TEXT DEFAULT 'en_cours',
                    libelle TEXT,
                    notes TEXT,
                    ecriture_id INTEGER,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (ecriture_id) REFERENCES ecritures (id)
                )
            ''')
            
            # Table des lignes de factures
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lignes_facture (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    facture_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    quantite REAL NOT NULL,
                    prix_unitaire REAL NOT NULL,
                    taux_tva REAL DEFAULT 20.0,
                    montant_ht REAL NOT NULL,
                    montant_tva REAL NOT NULL,
                    FOREIGN KEY (facture_id) REFERENCES factures (id) ON DELETE CASCADE
                )
            ''')
            
            # Table des règlements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reglements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    facture_id INTEGER NOT NULL,
                    montant REAL NOT NULL,
                    date_reglement DATE NOT NULL,
                    mode_reglement TEXT NOT NULL,
                    reference TEXT,
                    notes TEXT,
                    ecriture_id INTEGER,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (facture_id) REFERENCES factures (id),
                    FOREIGN KEY (ecriture_id) REFERENCES ecritures (id)
                )
            ''')
            
            # Table des budgets
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    annee INTEGER NOT NULL,
                    compte_id INTEGER NOT NULL,
                    montant_previsionnel REAL NOT NULL,
                    montant_realise REAL DEFAULT 0,
                    statut TEXT DEFAULT 'actif',
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (compte_id) REFERENCES comptes (id)
                )
            ''')
            
            # Table des rapprochements bancaires
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rapprochements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    compte_id INTEGER NOT NULL,
                    date_rapprochement DATE NOT NULL,
                    solde_comptable REAL NOT NULL,
                    solde_bancaire REAL NOT NULL,
                    ecart REAL NOT NULL,
                    statut TEXT DEFAULT 'en_cours',
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (compte_id) REFERENCES comptes (id)
                )
            ''')
            
            # Table des immobilisations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS immobilisations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    compte_id INTEGER NOT NULL,
                    valeur_acquisition REAL NOT NULL,
                    date_acquisition DATE NOT NULL,
                    duree_amortissement INTEGER NOT NULL,
                    methode_amortissement TEXT DEFAULT 'lineaire',
                    valeur_residuelle REAL DEFAULT 0,
                    amortissement_cumule REAL DEFAULT 0,
                    statut TEXT DEFAULT 'actif',
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (compte_id) REFERENCES comptes (id)
                )
            ''')
            
            # Table des utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_utilisateur TEXT UNIQUE NOT NULL,
                    mot_de_passe TEXT NOT NULL,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'comptable',
                    actif BOOLEAN DEFAULT 1,
                    derniere_connexion TIMESTAMP,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des paramètres
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parametres (
                    cle TEXT PRIMARY KEY,
                    valeur TEXT NOT NULL,
                    description TEXT,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertion des comptes par défaut
            self.insert_default_accounts(cursor)
            
            # Insertion des paramètres par défaut
            self.insert_default_parameters(cursor)
            
            # Insertion d'un utilisateur par défaut
            self.insert_default_user(cursor)
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            sg.popup_error(f"Erreur lors de l'initialisation de la base de données : {e}")
    
    def insert_default_accounts(self, cursor):
        """Insert les comptes par défaut du plan comptable"""
        comptes_defaut = [
            # Classe 1 - Comptes de capitaux
            ('10', 'Capital et réserves', 'Capitaux'),
            ('101', 'Capital', 'Capitaux'),
            ('106', 'Réserves', 'Capitaux'),
            ('12', 'Résultat de l\'exercice', 'Capitaux'),
            ('13', 'Subventions d\'investissement', 'Capitaux'),
            ('16', 'Emprunts et dettes assimilées', 'Dettes'),
            ('164', 'Emprunts auprès des établissements de crédit', 'Dettes'),
            
            # Classe 2 - Comptes d'immobilisations
            ('20', 'Immobilisations incorporelles', 'Immobilisations'),
            ('206', 'Droit au bail', 'Immobilisations'),
            ('207', 'Fonds commercial', 'Immobilisations'),
            ('21', 'Immobilisations corporelles', 'Immobilisations'),
            ('213', 'Constructions', 'Immobilisations'),
            ('215', 'Installations techniques', 'Immobilisations'),
            ('218', 'Autre matériel et outillage', 'Immobilisations'),
            ('27', 'Autres immobilisations financières', 'Immobilisations'),
            ('28', 'Amortissements des immobilisations', 'Immobilisations'),
            ('281', 'Amortissements des immobilisations incorporelles', 'Immobilisations'),
            ('2813', 'Amortissements des constructions', 'Immobilisations'),
            ('2815', 'Amortissements des installations techniques', 'Immobilisations'),
            
            # Classe 3 - Comptes de stocks
            ('31', 'Matières premières', 'Stocks'),
            ('32', 'Autres approvisionnements', 'Stocks'),
            ('33', 'En-cours de production de biens', 'Stocks'),
            ('35', 'Stocks de produits', 'Stocks'),
            ('37', 'Stocks de marchandises', 'Stocks'),
            ('39', 'Dépréciations des stocks', 'Stocks'),
            
            # Classe 4 - Comptes de tiers
            ('40', 'Fournisseurs et comptes rattachés', 'Tiers'),
            ('401', 'Fournisseurs', 'Tiers'),
            ('4011', 'Fournisseurs - Achats de biens ou de prestations de services', 'Tiers'),
            ('403', 'Fournisseurs - Effets à payer', 'Tiers'),
            ('408', 'Fournisseurs - Factures non parvenues', 'Tiers'),
            ('409', 'Fournisseurs débiteurs', 'Tiers'),
            ('41', 'Clients et comptes rattachés', 'Tiers'),
            ('411', 'Clients', 'Tiers'),
            ('4111', 'Clients - Ventes de biens ou de prestations de services', 'Tiers'),
            ('413', 'Clients - Effets à recevoir', 'Tiers'),
            ('416', 'Clients douteux ou litigieux', 'Tiers'),
            ('418', 'Clients - Produits non encore facturés', 'Tiers'),
            ('419', 'Clients créditeurs', 'Tiers'),
            ('42', 'Personnel et comptes rattachés', 'Tiers'),
            ('421', 'Personnel - Rémunérations dues', 'Tiers'),
            ('43', 'Sécurité sociale et autres organismes sociaux', 'Tiers'),
            ('44', 'État et collectivités publiques', 'Tiers'),
            ('445', 'État - Taxes sur le chiffre d\'affaires', 'Tiers'),
            ('4456', 'Taxes sur le chiffre d\'affaires déductibles', 'Tiers'),
            ('4457', 'Taxes sur le chiffre d\'affaires collectées', 'Tiers'),
            ('447', 'Autres impôts, taxes et versements assimilés', 'Tiers'),
            
            # Classe 5 - Comptes financiers
            ('50', 'Valeurs mobilières de placement', 'Financiers'),
            ('51', 'Banques, établissements financiers', 'Financiers'),
            ('512', 'Banques', 'Financiers'),
            ('5121', 'Compte courant Banque A', 'Financiers'),
            ('5122', 'Compte courant Banque B', 'Financiers'),
            ('53', 'Caisse', 'Financiers'),
            ('531', 'Caisse siège social', 'Financiers'),
            
            # Classe 6 - Comptes de charges
            ('60', 'Achats', 'Charges'),
            ('601', 'Achats stockés - Matières premières', 'Charges'),
            ('602', 'Achats stockés - Autres approvisionnements', 'Charges'),
            ('606', 'Achats non stockés de matières et fournitures', 'Charges'),
            ('607', 'Achats de marchandises', 'Charges'),
            ('61', 'Services extérieurs', 'Charges'),
            ('611', 'Sous-traitance générale', 'Charges'),
            ('613', 'Locations', 'Charges'),
            ('6135', 'Locations mobilières', 'Charges'),
            ('614', 'Charges locatives et de copropriété', 'Charges'),
            ('615', 'Entretien et réparations', 'Charges'),
            ('616', 'Primes d\'assurances', 'Charges'),
            ('62', 'Autres services extérieurs', 'Charges'),
            ('621', 'Personnel extérieur à l\'entreprise', 'Charges'),
            ('622', 'Rémunérations d\'intermédiaires et honoraires', 'Charges'),
            ('623', 'Publicité, publications, relations publiques', 'Charges'),
            ('624', 'Transports de biens et transports collectifs du personnel', 'Charges'),
            ('625', 'Déplacements, missions et réceptions', 'Charges'),
            ('626', 'Frais postaux et de télécommunications', 'Charges'),
            ('627', 'Services bancaires et assimilés', 'Charges'),
            ('63', 'Impôts, taxes et versements assimilés', 'Charges'),
            ('64', 'Charges de personnel', 'Charges'),
            ('641', 'Rémunérations du personnel', 'Charges'),
            ('645', 'Charges de sécurité sociale et de prévoyance', 'Charges'),
            ('65', 'Autres charges de gestion courante', 'Charges'),
            ('66', 'Charges financières', 'Charges'),
            ('661', 'Charges d\'intérêts', 'Charges'),
            ('67', 'Charges exceptionnelles', 'Charges'),
            ('68', 'Dotations aux amortissements et aux provisions', 'Charges'),
            ('681', 'Dotations aux amortissements et aux provisions - Charges d\'exploitation', 'Charges'),
            ('69', 'Participation des salariés - Impôts sur les bénéfices', 'Charges'),
            
            # Classe 7 - Comptes de produits
            ('70', 'Ventes de produits fabriqués, prestations de services', 'Produits'),
            ('701', 'Ventes de produits finis', 'Produits'),
            ('706', 'Prestations de services', 'Produits'),
            ('707', 'Ventes de marchandises', 'Produits'),
            ('708', 'Produits des activités annexes', 'Produits'),
            ('71', 'Production stockée', 'Produits'),
            ('72', 'Production immobilisée', 'Produits'),
            ('74', 'Subventions d\'exploitation', 'Produits'),
            ('75', 'Autres produits de gestion courante', 'Produits'),
            ('76', 'Produits financiers', 'Produits'),
            ('77', 'Produits exceptionnels', 'Produits'),
            ('78', 'Reprises sur amortissements et provisions', 'Produits'),
        ]
        
        for numero, nom, type_compte in comptes_defaut:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO comptes (numero, nom, type) 
                    VALUES (?, ?, ?)
                ''', (numero, nom, type_compte))
            except sqlite3.Error:
                pass  # Ignore les doublons
    
    def insert_default_parameters(self, cursor):
        """Insert les paramètres par défaut"""
        parametres = [
            ('entreprise_nom', 'Ma Société', 'Nom de l\'entreprise'),
            ('entreprise_adresse', '123 Rue de la Comptabilité', 'Adresse de l\'entreprise'),
            ('entreprise_ville', '75000 Paris', 'Ville de l\'entreprise'),
            ('entreprise_telephone', '01 23 45 67 89', 'Téléphone de l\'entreprise'),
            ('entreprise_email', 'contact@masociete.fr', 'Email de l\'entreprise'),
            ('entreprise_siret', '12345678901234', 'SIRET de l\'entreprise'),
            ('tva_numero', 'FR12345678901', 'Numéro de TVA'),
            ('exercice_debut', '2024-01-01', 'Date de début d\'exercice'),
            ('exercice_fin', '2024-12-31', 'Date de fin d\'exercice'),
            ('devise', 'EUR', 'Devise principale'),
            ('theme', 'DarkBlue3', 'Thème de l\'interface'),
        ]
        
        for cle, valeur, description in parametres:
            cursor.execute('''
                INSERT OR REPLACE INTO parametres (cle, valeur, description) 
                VALUES (?, ?, ?)
            ''', (cle, valeur, description))
    
    def insert_default_user(self, cursor):
        """Insert un utilisateur administrateur par défaut"""
        # Mot de passe par défaut : "admin" (hashé)
        mot_de_passe_hash = hashlib.sha256("admin".encode()).hexdigest()
        
        cursor.execute('''
            INSERT OR IGNORE INTO utilisateurs 
            (nom_utilisateur, mot_de_passe, nom, prenom, role) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', mot_de_passe_hash, 'Administrateur', 'Système', 'admin'))
    
    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Exécute une requête SELECT et retourne les résultats"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            conn.close()
            return results
            
        except sqlite3.Error as e:
            sg.popup_error(f"Erreur lors de l'exécution de la requête : {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Exécute une requête INSERT/UPDATE/DELETE"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            sg.popup_error(f"Erreur lors de la mise à jour : {e}")
            return False

class ConfigManager:
    """Gestionnaire de configuration"""
    
    @staticmethod
    def load_config() -> dict:
        """Charge la configuration depuis le fichier"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            'theme': 'DarkBlue3',
            'window_size': (1200, 800),
            'last_user': '',
            'auto_backup': True,
            'backup_interval': 24
        }
    
    @staticmethod
    def save_config(config: dict):
        """Sauvegarde la configuration"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            sg.popup_error(f"Erreur lors de la sauvegarde de la configuration : {e}")

class AuthManager:
    """Gestionnaire d'authentification"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        """Hash un mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authentifie un utilisateur"""
        hashed_password = self.hash_password(password)
        
        result = self.db_manager.execute_query('''
            SELECT id, nom_utilisateur, nom, prenom, role, actif 
            FROM utilisateurs 
            WHERE nom_utilisateur = ? AND mot_de_passe = ? AND actif = 1
        ''', (username, hashed_password))
        
        if result:
            user_data = result[0]
            self.current_user = {
                'id': user_data[0],
                'nom_utilisateur': user_data[1],
                'nom': user_data[2],
                'prenom': user_data[3],
                'role': user_data[4]
            }
            
            # Mise à jour de la dernière connexion
            self.db_manager.execute_update('''
                UPDATE utilisateurs 
                SET derniere_connexion = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user_data[0],))
            
            return True
        
        return False
    
    def logout(self):
        """Déconnecte l'utilisateur actuel"""
        self.current_user = None
    
    def create_user(self, username: str, password: str, nom: str, prenom: str, 
                   email: str = '', role: str = 'comptable') -> bool:
        """Crée un nouvel utilisateur"""
        hashed_password = self.hash_password(password)
        
        return self.db_manager.execute_update('''
            INSERT INTO utilisateurs 
            (nom_utilisateur, mot_de_passe, nom, prenom, email, role) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, hashed_password, nom, prenom, email, role))

class ReportManager:
    """Gestionnaire de rapports"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def generate_balance_sheet(self, date_fin: str) -> Dict:
        """Génère un bilan comptable"""
        # Actifs
        actifs = {}
        
        # Immobilisations
        immobilisations = self.db_manager.execute_query('''
            SELECT c.nom, SUM(CASE WHEN le.debit > 0 THEN le.debit ELSE -le.credit END) as solde
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            LEFT JOIN ecritures e ON le.ecriture_id = e.id
            WHERE c.numero LIKE '2%' AND (e.date_ecriture <= ? OR e.date_ecriture IS NULL)
            GROUP BY c.id, c.nom
            HAVING solde != 0
        ''', (date_fin,))
        
        actifs['Immobilisations'] = immobilisations
        
        # Stocks
        stocks = self.db_manager.execute_query('''
            SELECT c.nom, SUM(CASE WHEN le.debit > 0 THEN le.debit ELSE -le.credit END) as solde
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            LEFT JOIN ecritures e ON le.ecriture_id = e.id
            WHERE c.numero LIKE '3%' AND (e.date_ecriture <= ? OR e.date_ecriture IS NULL)
            GROUP BY c.id, c.nom
            HAVING solde != 0
        ''', (date_fin,))
        
        actifs['Stocks'] = stocks
        
        # Créances
        creances = self.db_manager.execute_query('''
            SELECT c.nom, SUM(CASE WHEN le.debit > 0 THEN le.debit ELSE -le.credit END) as solde
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            LEFT JOIN ecritures e ON le.ecriture_id = e.id
            WHERE c.numero LIKE '41%' AND (e.date_ecriture <= ? OR e.date_ecriture IS NULL)
            GROUP BY c.id, c.nom
            HAVING solde > 0
        ''', (date_fin,))
        
        actifs['Créances'] = creances
        
        # Trésorerie
        tresorerie = self.db_manager.execute_query('''
            SELECT c.nom, SUM(CASE WHEN le.debit > 0 THEN le.debit ELSE -le.credit END) as solde
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            LEFT JOIN ecritures e ON le.ecriture_id = e.id
            WHERE (c.numero LIKE '51%' OR c.numero LIKE '53%') 
            AND (e.date_ecriture <= ? OR e.date_ecriture IS NULL)
            GROUP BY c.id, c.nom
            HAVING solde != 0
        ''', (date_fin,))
        
        actifs['Trésorerie'] = tresorerie
        
        # Passifs
        passifs = {}
        
        # Capitaux propres
        capitaux = self.db_manager.execute_query('''
            SELECT c.nom, SUM(CASE WHEN le.credit > 0 THEN le.credit ELSE -le.debit END) as solde
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            LEFT JOIN ecritures e ON le.ecriture_id = e.id
            WHERE c.numero LIKE '1%' AND (e.date_ecriture <= ? OR e.date_ecriture IS NULL)
            GROUP BY c.id, c.nom
            HAVING solde != 0
        ''', (date_fin,))
        
        passifs['Capitaux propres'] = capitaux
        
        # Dettes
        dettes = self.db_manager.execute_query('''
            SELECT c.nom, SUM(CASE WHEN le.credit > 0 THEN le.credit ELSE -le.debit END) as solde
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            LEFT JOIN ecritures e ON le.ecriture_id = e.id
            WHERE (c.numero LIKE '40%' OR c.numero LIKE '42%' OR c.numero LIKE '43%' OR c.numero LIKE '44%') 
            AND (e.date_ecriture <= ? OR e.date_ecriture IS NULL)
            GROUP BY c.id, c.nom
            HAVING solde > 0
        ''', (date_fin,))
        
        passifs['Dettes'] = dettes
        
        return {
            'actifs': actifs,
            'passifs': passifs,
            'date': date_fin
        }
    
    def generate_profit_loss(self, date_debut: str, date_fin: str) -> Dict:
        """Génère un compte de résultat"""
        # Charges
        charges = self.db_manager.execute_query('''
            SELECT c.nom, SUM(le.debit - le.credit) as montant
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            LEFT JOIN ecritures e ON le.ecriture_id = e.id
            WHERE c.numero LIKE '6%' 
            AND e.date_ecriture BETWEEN ? AND ?
            GROUP BY c.id, c.nom
            HAVING montant > 0
            ORDER BY c.numero
        ''', (date_debut, date_fin))
        
        # Produits
        produits = self.db_manager.execute_query('''
            SELECT c.nom, SUM(le.credit - le.debit) as montant
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            LEFT JOIN ecritures e ON le.ecriture_id = e.id
            WHERE c.numero LIKE '7%' 
            AND e.date_ecriture BETWEEN ? AND ?
            GROUP BY c.id, c.nom
            HAVING montant > 0
            ORDER BY c.numero
        ''', (date_debut, date_fin))
        
        total_charges = sum(charge[1] for charge in charges) if charges else 0
        total_produits = sum(produit[1] for produit in produits) if produits else 0
        resultat = total_produits - total_charges
        
        return {
            'charges': charges,
            'produits': produits,
            'total_charges': total_charges,
            'total_produits': total_produits,
            'resultat': resultat,
            'date_debut': date_debut,
            'date_fin': date_fin
        }
    
    def generate_grand_livre(self, compte_id: int, date_debut: str, date_fin: str) -> Dict:
        """Génère le grand livre d'un compte"""
        # Informations du compte
        compte_info = self.db_manager.execute_query('''
            SELECT numero, nom FROM comptes WHERE id = ?
        ''', (compte_id,))
        
        if not compte_info:
            return {}
        
        # Solde initial
        solde_initial = self.db_manager.execute_query('''
            SELECT COALESCE(SUM(le.debit - le.credit), 0) as solde
            FROM lignes_ecriture le
            JOIN ecritures e ON le.ecriture_id = e.id
            WHERE le.compte_id = ? AND e.date_ecriture < ?
        ''', (compte_id, date_debut))
        
        # Mouvements de la période
        mouvements = self.db_manager.execute_query('''
            SELECT e.date_ecriture, e.numero, le.libelle, le.debit, le.credit
            FROM lignes_ecriture le
            JOIN ecritures e ON le.ecriture_id = e.id
            WHERE le.compte_id = ? 
            AND e.date_ecriture BETWEEN ? AND ?
            ORDER BY e.date_ecriture, e.numero
        ''', (compte_id, date_debut, date_fin))
        
        # Calcul du solde progressif
        solde_courant = solde_initial[0][0] if solde_initial else 0
        mouvements_avec_solde = []
        
        for mouvement in mouvements:
            solde_courant += mouvement[3] - mouvement[4]  # debit - credit
            mouvements_avec_solde.append(mouvement + (solde_courant,))
        
        return {
            'compte': compte_info[0],
            'solde_initial': solde_initial[0][0] if solde_initial else 0,
            'mouvements': mouvements_avec_solde,
            'solde_final': solde_courant,
            'date_debut': date_debut,
            'date_fin': date_fin
        }

class PrintManager:
    """Gestionnaire d'impression et d'export"""
    
    @staticmethod
    def export_to_csv(data: List[tuple], headers: List[str], filename: str):
        """Exporte des données vers un fichier CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)
            
            sg.popup(f"Export réussi : {filename}")
            
        except Exception as e:
            sg.popup_error(f"Erreur lors de l'export : {e}")
    
    @staticmethod
    def print_report(title: str, content: str):
        """Imprime un rapport (simulation)"""
        try:
            # Création d'un fichier temporaire pour l'impression
            temp_file = f"temp_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n")
                f.write("=" * len(title) + "\n\n")
                f.write(content)
            
            # Simulation d'impression (ouverture du fichier)
            if sys.platform == "win32":
                os.startfile(temp_file)
            else:
                subprocess.run(["xdg-open", temp_file])
            
        except Exception as e:
            sg.popup_error(f"Erreur lors de l'impression : {e}")

class BackupManager:
    """Gestionnaire de sauvegardes"""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.backup_dir = "backups"
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self) -> str:
        """Crée une sauvegarde de la base de données"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copie de la base de données
            with open(self.db_name, 'rb') as source:
                with open(backup_path, 'wb') as backup:
                    backup.write(source.read())
            
            return backup_path
            
        except Exception as e:
            sg.popup_error(f"Erreur lors de la création de la sauvegarde : {e}")
            return ""
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restaure une sauvegarde"""
        try:
            if not os.path.exists(backup_path):
                sg.popup_error("Le fichier de sauvegarde n'existe pas.")
                return False
            
            # Confirmation
            if sg.popup_yes_no("Êtes-vous sûr de vouloir restaurer cette sauvegarde ?\nToutes les données actuelles seront remplacées.") != 'Yes':
                return False
            
            # Sauvegarde de sécurité
            security_backup = self.create_backup()
            
            # Restauration
            with open(backup_path, 'rb') as backup:
                with open(self.db_name, 'wb') as target:
                    target.write(backup.read())
            
            sg.popup("Restauration effectuée avec succès.")
            return True
            
        except Exception as e:
            sg.popup_error(f"Erreur lors de la restauration : {e}")
            return False
    
    def auto_backup(self):
        """Effectue une sauvegarde automatique en arrière-plan"""
        def backup_thread():
            backup_path = self.create_backup()
            if backup_path:
                # Nettoyage des anciennes sauvegardes (garde les 10 dernières)
                self.cleanup_old_backups(10)
        
        thread = threading.Thread(target=backup_thread)
        thread.daemon = True
        thread.start()
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """Supprime les anciennes sauvegardes"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('backup_') and filename.endswith('.db'):
                    filepath = os.path.join(self.backup_dir, filename)
                    backup_files.append((filepath, os.path.getctime(filepath)))
            
            # Trie par date de création (plus récent en premier)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Supprime les fichiers excédentaires
            for filepath, _ in backup_files[keep_count:]:
                os.remove(filepath)
                
        except Exception as e:
            print(f"Erreur lors du nettoyage des sauvegardes : {e}")

class ValidationManager:
    """Gestionnaire de validation des données"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valide un email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_siret(siret: str) -> bool:
        """Valide un numéro SIRET"""
        if not siret or len(siret) != 14:
            return False
        
        try:
            # Algorithme de validation SIRET
            total = 0
            for i, digit in enumerate(siret):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n = n // 10 + n % 10
                total += n
            
            return total % 10 == 0
            
        except ValueError:
            return False
    
    @staticmethod
    def validate_tva_number(tva: str) -> bool:
        """Valide un numéro de TVA français"""
        pattern = r'^FR[0-9A-Z]{2}[0-9]{9}$'
        return re.match(pattern, tva) is not None
    
    @staticmethod
    def validate_amount(amount_str: str) -> Tuple[bool, float]:
        """Valide et convertit un montant"""
        try:
            # Remplace la virgule par un point
            amount_str = amount_str.replace(',', '.')
            amount = float(amount_str)
            return True, amount
        except ValueError:
            return False, 0.0
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Valide une date au format YYYY-MM-DD"""
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

class ComptabiliteApp:
    """Application principale de comptabilité"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager(self.db_manager)
        self.report_manager = ReportManager(self.db_manager)
        self.backup_manager = BackupManager(DB_NAME)
        
        self.config = ConfigManager.load_config()
        sg.theme(self.config.get('theme', 'DarkBlue3'))
        
        self.current_window = None
        self.running = True
    
    def run(self):
        """Lance l'application"""
        # Sauvegarde automatique au démarrage
        self.backup_manager.auto_backup()
        
        # Fenêtre de connexion
        if self.show_login_window():
            # Fenêtre principale
            self.show_main_window()
    
    def show_login_window(self) -> bool:
        """Affiche la fenêtre de connexion"""
        layout = [
            [sg.Text(APP_NAME, font=('Arial', 16, 'bold'), justification='center')],
            [sg.Text(f"Version {APP_VERSION}", justification='center')],
            [sg.HSeparator()],
            [sg.Text('Nom d\'utilisateur:'), sg.Input(key='username', size=(20, 1), default_text=self.config.get('last_user', ''))],
            [sg.Text('Mot de passe:'), sg.Input(key='password', password_char='*', size=(20, 1))],
            [sg.HSeparator()],
            [sg.Button('Se connecter', bind_return_key=True), sg.Button('Quitter'), sg.Button('Créer un compte')],
            [sg.Text('Utilisateur par défaut: admin / admin', font=('Arial', 8), text_color='gray')]
        ]
        
        window = sg.Window('Connexion - ' + APP_NAME, layout, finalize=True, 
                          icon=None, element_justification='center')
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Quitter'):
                window.close()
                return False
            
            elif event == 'Se connecter':
                username = values['username'].strip()
                password = values['password']
                
                if not username or not password:
                    sg.popup_error('Veuillez saisir un nom d\'utilisateur et un mot de passe.')
                    continue
                
                if self.auth_manager.authenticate(username, password):
                    self.config['last_user'] = username
                    ConfigManager.save_config(self.config)
                    window.close()
                    return True
                else:
                    sg.popup_error('Nom d\'utilisateur ou mot de passe incorrect.')
            
            elif event == 'Créer un compte':
                window.close()
                if self.show_create_user_window():
                    return self.show_login_window()
                else:
                    return False
    
    def show_create_user_window(self) -> bool:
        """Affiche la fenêtre de création d'utilisateur"""
        layout = [
            [sg.Text('Création d\'un nouveau compte', font=('Arial', 14, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Nom d\'utilisateur:'), sg.Input(key='username', size=(30, 1))],
            [sg.Text('Mot de passe:'), sg.Input(key='password', password_char='*', size=(30, 1))],
            [sg.Text('Confirmation:'), sg.Input(key='password_confirm', password_char='*', size=(30, 1))],
            [sg.Text('Nom:'), sg.Input(key='nom', size=(30, 1))],
            [sg.Text('Prénom:'), sg.Input(key='prenom', size=(30, 1))],
            [sg.Text('Email:'), sg.Input(key='email', size=(30, 1))],
            [sg.Text('Rôle:'), sg.Combo(['comptable', 'admin'], default_value='comptable', key='role', size=(28, 1))],
            [sg.HSeparator()],
            [sg.Button('Créer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window('Création de compte', layout, finalize=True)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                window.close()
                return False
            
            elif event == 'Créer':
                # Validation des champs
                if not all([values['username'], values['password'], values['nom'], values['prenom']]):
                    sg.popup_error('Veuillez remplir tous les champs obligatoires.')
                    continue
                
                if values['password'] != values['password_confirm']:
                    sg.popup_error('Les mots de passe ne correspondent pas.')
                    continue
                
                if len(values['password']) < 4:
                    sg.popup_error('Le mot de passe doit contenir au moins 4 caractères.')
                    continue
                
                if values['email'] and not ValidationManager.validate_email(values['email']):
                    sg.popup_error('Format d\'email invalide.')
                    continue
                
                # Création du compte
                if self.auth_manager.create_user(
                    values['username'], values['password'], values['nom'], 
                    values['prenom'], values['email'], values['role']
                ):
                    sg.popup('Compte créé avec succès!')
                    window.close()
                    return True
                else:
                    sg.popup_error('Erreur lors de la création du compte.\nLe nom d\'utilisateur existe peut-être déjà.')
    
    def show_main_window(self):
        """Affiche la fenêtre principale"""
        # Menu principal
        menu_def = [
            ['&Fichier', ['&Nouveau', '&Ouvrir', '&Sauvegarder', 'Sauvegarder &sous...', '---', 
                         'Import/Export', ['Importer CSV', 'Exporter CSV'], '---', 
                         'Sauvegardes', ['Créer sauvegarde', 'Restaurer sauvegarde'], '---', '&Quitter']],
            ['&Comptabilité', ['Plan comptable', 'Écritures', 'Lettrage', 'Rapprochement bancaire']],
            ['&Tiers', ['Clients', 'Fournisseurs']],
            ['&Facturation', ['Factures clients', 'Factures fournisseurs', 'Règlements']],
            ['&Immobilisations', ['Gestion des immobilisations', 'Calcul amortissements']],
            ['&Budgets', ['Budgets prévisionnels', 'Suivi budgétaire']],
            ['&États', ['Bilan', 'Compte de résultat', 'Balance', 'Grand livre', 'Journaux']],
            ['&Outils', ['Calculatrice', 'Convertisseur', 'Clôture exercice']],
            ['&Paramètres', ['Configuration', 'Utilisateurs', 'Thèmes', 'Préférences']],
            ['&Aide', ['Documentation', 'À propos']]
        ]
        
        # Tableau de bord avec statistiques
        dashboard_col = [
            [sg.Frame('Tableau de bord', [
                [sg.Text('Chiffre d\'affaires du mois:', size=(25, 1)), 
                 sg.Text('0,00 €', key='ca_mois', font=('Arial', 10, 'bold'))],
                [sg.Text('Résultat net:', size=(25, 1)), 
                 sg.Text('0,00 €', key='resultat_net', font=('Arial', 10, 'bold'))],
                [sg.Text('Trésorerie:', size=(25, 1)), 
                 sg.Text('0,00 €', key='tresorerie', font=('Arial', 10, 'bold'))],
                [sg.Text('Créances clients:', size=(25, 1)), 
                 sg.Text('0,00 €', key='creances', font=('Arial', 10, 'bold'))],
                [sg.Text('Dettes fournisseurs:', size=(25, 1)), 
                 sg.Text('0,00 €', key='dettes', font=('Arial', 10, 'bold'))],
                [sg.HSeparator()],
                [sg.Button('Actualiser', key='refresh_dashboard')]
            ], size=(400, 200))],
            
            [sg.Frame('Accès rapide', [
                [sg.Button('Nouvelle écriture', size=(15, 1)), sg.Button('Nouvelle facture', size=(15, 1))],
                [sg.Button('Nouveau client', size=(15, 1)), sg.Button('Nouveau fournisseur', size=(15, 1))],
                [sg.Button('Règlement', size=(15, 1)), sg.Button('Rapprochement', size=(15, 1))],
                [sg.Button('Balance', size=(15, 1)), sg.Button('Grand livre', size=(15, 1))]
            ], size=(400, 150))],
            
            [sg.Frame('Notifications', [
                [sg.Listbox(values=['Aucune notification'], size=(50, 6), key='notifications')]
            ], size=(400, 150))]
        ]
        
        # Onglets pour les différentes fonctionnalités
        tab_group = sg.TabGroup([
            [sg.Tab('Plan comptable', self.create_plan_comptable_tab())],
            [sg.Tab('Écritures', self.create_ecritures_tab())],
            [sg.Tab('Tiers', self.create_tiers_tab())],
            [sg.Tab('Facturation', self.create_facturation_tab())],
            [sg.Tab('États', self.create_etats_tab())]
        ], key='main_tabs')
        
        # Layout principal
        layout = [
            [sg.MenuBar(menu_def)],
            [sg.Text(f'Connecté en tant que: {self.auth_manager.current_user["nom"]} {self.auth_manager.current_user["prenom"]} ({self.auth_manager.current_user["role"]})',
                    key='user_info')],
            [sg.HSeparator()],
            [tab_group],
            [sg.HSeparator()],
            [sg.Text('Prêt', key='status_bar', size=(50, 1)), 
             sg.Text(f'Base de données: {DB_NAME}', size=(30, 1)),
             sg.Button('Déconnexion')]
        ]
        
        window = sg.Window(APP_NAME, layout, finalize=True, 
                          size=self.config.get('window_size', (1200, 800)),
                          resizable=True)
        
        # Actualiser le tableau de bord au démarrage
        self.refresh_dashboard(window)
        
        # Boucle principale
        while self.running:
            event, values = window.read(timeout=30000)  # Timeout de 30 secondes
            
            if event in (sg.WIN_CLOSED, 'Quitter'):
                break
            
            elif event == 'Déconnexion':
                if sg.popup_yes_no('Êtes-vous sûr de vouloir vous déconnecter ?') == 'Yes':
                    break
            
            # Gestion des événements du menu
            elif event in ['Plan comptable', 'plan_comptable']:
                self.show_plan_comptable_window()
            
            elif event in ['Écritures', 'ecritures']:
                self.show_ecritures_window()
            
            elif event in ['Clients', 'clients']:
                self.show_clients_window()
            
            elif event in ['Fournisseurs', 'fournisseurs']:
                self.show_fournisseurs_window()
            
            elif event in ['Factures clients', 'factures']:
                self.show_factures_window()
            
            elif event == 'Bilan':
                self.show_bilan_window()
            
            elif event == 'Compte de résultat':
                self.show_compte_resultat_window()
            
            elif event == 'Balance':
                self.show_balance_window()
            
            elif event == 'Grand livre':
                self.show_grand_livre_window()
            
            elif event == 'Configuration':
                self.show_configuration_window()
            
            elif event == 'Utilisateurs':
                self.show_users_window()
            
            elif event == 'Thèmes':
                self.show_themes_window()
            
            elif event == 'Créer sauvegarde':
                backup_path = self.backup_manager.create_backup()
                if backup_path:
                    sg.popup(f'Sauvegarde créée : {backup_path}')
            
            elif event == 'Restaurer sauvegarde':
                backup_file = sg.popup_get_file('Sélectionner le fichier de sauvegarde',
                                               file_types=(('Base de données', '*.db'),))
                if backup_file:
                    self.backup_manager.restore_backup(backup_file)
            
            elif event == 'À propos':
                self.show_about_window()
            
            # Événements du tableau de bord
            elif event in ['refresh_dashboard', 'Actualiser']:
                self.refresh_dashboard(window)
            
            # Événements des accès rapides
            elif event == 'Nouvelle écriture':
                self.show_nouvelle_ecriture_window()
            
            elif event == 'Nouvelle facture':
                self.show_nouvelle_facture_window()
            
            elif event == 'Nouveau client':
                self.show_nouveau_client_window()
            
            elif event == 'Nouveau fournisseur':
                self.show_nouveau_fournisseur_window()
            
            # Gestion des onglets
            elif event == 'main_tabs':
                active_tab = values['main_tabs']
                if active_tab == 'Plan comptable':
                    self.refresh_plan_comptable_tab(window)
                elif active_tab == 'Écritures':
                    self.refresh_ecritures_tab(window)
                elif active_tab == 'Tiers':
                    self.refresh_tiers_tab(window)
            
            # Timeout pour actualisation automatique
            elif event == sg.TIMEOUT_KEY:
                self.refresh_dashboard(window)
        
        window.close()
        self.auth_manager.logout()
    
    def create_plan_comptable_tab(self) -> list:
        """Crée l'onglet du plan comptable"""
        return [
            [sg.Text('Plan Comptable', font=('Arial', 12, 'bold'))],
            [sg.Input(key='search_compte', size=(30, 1)), sg.Button('Rechercher', key='search_comptes')],
            [sg.Table(values=[], headings=['Numéro', 'Nom', 'Type', 'Solde'],
                     key='table_comptes', size=(80, 15),
                     justification='left', auto_size_columns=False,
                     col_widths=[10, 40, 15, 15])],
            [sg.Button('Ajouter compte', key='add_compte'),
             sg.Button('Modifier compte', key='edit_compte'),
             sg.Button('Supprimer compte', key='del_compte'),
             sg.Button('Actualiser', key='refresh_comptes')]
        ]
    
    def create_ecritures_tab(self) -> list:
        """Crée l'onglet des écritures"""
        return [
            [sg.Text('Écritures Comptables', font=('Arial', 12, 'bold'))],
            [sg.Text('Du:'), sg.Input(key='date_debut_ecr', size=(12, 1)),
             sg.Text('Au:'), sg.Input(key='date_fin_ecr', size=(12, 1)),
             sg.Button('Filtrer', key='filter_ecritures')],
            [sg.Table(values=[], headings=['Numéro', 'Date', 'Libellé', 'Montant', 'Statut'],
                     key='table_ecritures', size=(80, 12),
                     justification='left')],
            [sg.Button('Nouvelle écriture', key='new_ecriture'),
             sg.Button('Modifier écriture', key='edit_ecriture'),
             sg.Button('Supprimer écriture', key='del_ecriture'),
             sg.Button('Valider écriture', key='validate_ecriture')]
        ]
    
    def create_tiers_tab(self) -> list:
        """Crée l'onglet des tiers"""
        return [
            [sg.Text('Gestion des Tiers', font=('Arial', 12, 'bold'))],
            [sg.Radio('Clients', 'tiers_type', default=True, key='radio_clients'),
             sg.Radio('Fournisseurs', 'tiers_type', key='radio_fournisseurs')],
            [sg.Input(key='search_tiers', size=(30, 1)), sg.Button('Rechercher', key='search_tiers_btn')],
            [sg.Table(values=[], headings=['Code', 'Nom', 'Ville', 'Téléphone', 'Email'],
                     key='table_tiers', size=(80, 12),
                     justification='left')],
            [sg.Button('Ajouter', key='add_tiers'),
             sg.Button('Modifier', key='edit_tiers'),
             sg.Button('Supprimer', key='del_tiers'),
             sg.Button('Actualiser', key='refresh_tiers')]
        ]
    
    def create_facturation_tab(self) -> list:
        """Crée l'onglet de facturation"""
        return [
            [sg.Text('Facturation', font=('Arial', 12, 'bold'))],
            [sg.Radio('Factures clients', 'fact_type', default=True, key='radio_fact_clients'),
             sg.Radio('Factures fournisseurs', 'fact_type', key='radio_fact_fournisseurs')],
            [sg.Text('Statut:'), sg.Combo(['Tous', 'En cours', 'Payée', 'En retard'], 
                                         default_value='Tous', key='combo_statut_fact')],
            [sg.Table(values=[], headings=['Numéro', 'Client', 'Date', 'Montant TTC', 'Statut'],
                     key='table_factures', size=(80, 12),
                     justification='left')],
            [sg.Button('Nouvelle facture', key='new_facture'),
             sg.Button('Modifier facture', key='edit_facture'),
             sg.Button('Supprimer facture', key='del_facture'),
             sg.Button('Imprimer', key='print_facture'),
             sg.Button('Règlement', key='reglement_facture')]
        ]
    
    def create_etats_tab(self) -> list:
        """Crée l'onglet des états"""
        return [
            [sg.Text('États Comptables', font=('Arial', 12, 'bold'))],
            [sg.Frame('Période', [
                [sg.Text('Du:'), sg.Input(key='date_debut_etat', size=(12, 1)),
                 sg.Text('Au:'), sg.Input(key='date_fin_etat', size=(12, 1))]
            ])],
            [sg.Frame('États disponibles', [
                [sg.Button('Bilan', size=(15, 2)), sg.Button('Compte de résultat', size=(15, 2))],
                [sg.Button('Balance générale', size=(15, 2)), sg.Button('Grand livre', size=(15, 2))],
                [sg.Button('Journaux', size=(15, 2)), sg.Button('Échéancier', size=(15, 2))]
            ])],
            [sg.Output(size=(80, 10), key='output_etats')]
        ]
    
    def refresh_dashboard(self, window):
        """Actualise les données du tableau de bord"""
        try:
            # Calcul du chiffre d'affaires du mois
            current_month = datetime.datetime.now().strftime('%Y-%m')
            ca_mois = self.db_manager.execute_query('''
                SELECT COALESCE(SUM(le.credit - le.debit), 0)
                FROM lignes_ecriture le
                JOIN ecritures e ON le.ecriture_id = e.id
                JOIN comptes c ON le.compte_id = c.id
                WHERE c.numero LIKE '70%' 
                AND strftime('%Y-%m', e.date_ecriture) = ?
            ''', (current_month,))
            
            ca_value = ca_mois[0][0] if ca_mois else 0
            window['ca_mois'].update(f"{ca_value:,.2f} €")
            
            # Calcul de la trésorerie
            tresorerie = self.db_manager.execute_query('''
                SELECT COALESCE(SUM(le.debit - le.credit), 0)
                FROM lignes_ecriture le
                JOIN comptes c ON le.compte_id = c.id
                WHERE c.numero LIKE '51%' OR c.numero LIKE '53%'
            ''')
            
            treso_value = tresorerie[0][0] if tresorerie else 0
            window['tresorerie'].update(f"{treso_value:,.2f} €")
            
            # Calcul des créances clients
            creances = self.db_manager.execute_query('''
                SELECT COALESCE(SUM(le.debit - le.credit), 0)
                FROM lignes_ecriture le
                JOIN comptes c ON le.compte_id = c.id
                WHERE c.numero LIKE '411%'
            ''')
            
            creances_value = creances[0][0] if creances else 0
            window['creances'].update(f"{creances_value:,.2f} €")
            
            # Calcul des dettes fournisseurs
            dettes = self.db_manager.execute_query('''
                SELECT COALESCE(SUM(le.credit - le.debit), 0)
                FROM lignes_ecriture le
                JOIN comptes c ON le.compte_id = c.id
                WHERE c.numero LIKE '401%'
            ''')
            
            dettes_value = dettes[0][0] if dettes else 0
            window['dettes'].update(f"{dettes_value:,.2f} €")
            
            # Calcul du résultat net
            resultat_value = ca_value  # Simplification pour l'exemple
            window['resultat_net'].update(f"{resultat_value:,.2f} €")
            
            # Mise à jour des notifications
            notifications = []
            
            # Vérifier les factures en retard
            factures_retard = self.db_manager.execute_query('''
                SELECT COUNT(*) FROM factures 
                WHERE date_echeance < date('now') AND statut = 'en_cours'
            ''')
            
            if factures_retard and factures_retard[0][0] > 0:
                notifications.append(f"{factures_retard[0][0]} facture(s) en retard de paiement")
            
            # Vérifier la trésorerie faible
            if treso_value < 1000:
                notifications.append("Attention: Trésorerie faible")
            
            if not notifications:
                notifications = ["Aucune notification"]
            
            window['notifications'].update(notifications)
            
        except Exception as e:
            print(f"Erreur lors de l'actualisation du tableau de bord: {e}")
    
    def refresh_plan_comptable_tab(self, window):
        """Actualise l'onglet du plan comptable"""
        try:
            comptes = self.db_manager.execute_query('''
                SELECT c.numero, c.nom, c.type,
                       COALESCE(SUM(le.debit - le.credit), 0) as solde
                FROM comptes c
                LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
                WHERE c.actif = 1
                GROUP BY c.id, c.numero, c.nom, c.type
                ORDER BY c.numero
            ''')
            
            # Format des données pour l'affichage
            table_data = []
            for compte in comptes:
                numero, nom, type_compte, solde = compte
                table_data.append([numero, nom, type_compte, f"{solde:,.2f} €"])
            
            window['table_comptes'].update(table_data)
            
        except Exception as e:
            sg.popup_error(f"Erreur lors du chargement des comptes: {e}")
    
    def refresh_ecritures_tab(self, window):
        """Actualise l'onglet des écritures"""
        try:
            ecritures = self.db_manager.execute_query('''
                SELECT numero, date_ecriture, libelle, montant_total, statut
                FROM ecritures
                ORDER BY date_ecriture DESC, numero DESC
                LIMIT 100
            ''')
            
            table_data = []
            for ecriture in ecritures:
                numero, date_ecr, libelle, montant, statut = ecriture
                table_data.append([numero, date_ecr, libelle, f"{montant:,.2f} €", statut])
            
            window['table_ecritures'].update(table_data)
            
        except Exception as e:
            sg.popup_error(f"Erreur lors du chargement des écritures: {e}")
    
    def refresh_tiers_tab(self, window):
        """Actualise l'onglet des tiers"""
        try:
            # Par défaut, afficher les clients
            clients = self.db_manager.execute_query('''
                SELECT code, nom, ville, telephone, email
                FROM clients
                WHERE actif = 1
                ORDER BY nom
            ''')
            
            table_data = []
            for client in clients:
                table_data.append(list(client))
            
            window['table_tiers'].update(table_data)
            
        except Exception as e:
            sg.popup_error(f"Erreur lors du chargement des tiers: {e}")
    
    def show_plan_comptable_window(self):
        """Affiche la fenêtre de gestion du plan comptable"""
        layout = [
            [sg.Text('Gestion du Plan Comptable', font=('Arial', 14, 'bold'))],
            [sg.HSeparator()],
            [sg.Frame('Recherche', [
                [sg.Text('Rechercher:'), sg.Input(key='search', size=(30, 1)), sg.Button('Rechercher')]
            ])],
            [sg.Table(values=[], headings=['ID', 'Numéro', 'Nom', 'Type', 'Solde', 'Actif'],
                     key='table_comptes', size=(100, 20),
                     justification='left', enable_events=True,
                     col_widths=[5, 10, 40, 15, 15, 8])],
            [sg.Button('Ajouter'), sg.Button('Modifier'), sg.Button('Supprimer'), 
             sg.Button('Actualiser'), sg.Button('Exporter CSV'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Plan Comptable', layout, finalize=True, size=(900, 600))
        
        # Charger les données initiales
        self.refresh_plan_comptable_window(window)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Actualiser':
                self.refresh_plan_comptable_window(window)
            
            elif event == 'Ajouter':
                if self.show_compte_form_window():
                    self.refresh_plan_comptable_window(window)
            
            elif event == 'Modifier':
                selected = values['table_comptes']
                if selected:
                    row_index = selected[0]
                    compte_data = window['table_comptes'].get()[row_index]
                    compte_id = compte_data[0]
                    if self.show_compte_form_window(compte_id):
                        self.refresh_plan_comptable_window(window)
                else:
                    sg.popup('Veuillez sélectionner un compte à modifier.')
            
            elif event == 'Supprimer':
                selected = values['table_comptes']
                if selected:
                    if sg.popup_yes_no('Êtes-vous sûr de vouloir supprimer ce compte ?') == 'Yes':
                        row_index = selected[0]
                        compte_data = window['table_comptes'].get()[row_index]
                        compte_id = compte_data[0]
                        
                        if self.db_manager.execute_update('UPDATE comptes SET actif = 0 WHERE id = ?', (compte_id,)):
                            sg.popup('Compte désactivé avec succès.')
                            self.refresh_plan_comptable_window(window)
                else:
                    sg.popup('Veuillez sélectionner un compte à supprimer.')
            
            elif event == 'Rechercher':
                search_term = values['search']
                if search_term:
                    self.search_comptes(window, search_term)
                else:
                    self.refresh_plan_comptable_window(window)
            
            elif event == 'Exporter CSV':
                data = window['table_comptes'].get()
                headers = ['ID', 'Numéro', 'Nom', 'Type', 'Solde', 'Actif']
                filename = sg.popup_get_file('Nom du fichier', save_as=True, 
                                           default_extension='.csv',
                                           file_types=(('CSV', '*.csv'),))
                if filename:
                    PrintManager.export_to_csv(data, headers, filename)
        
        window.close()
    
    def refresh_plan_comptable_window(self, window):
        """Actualise les données du plan comptable"""
        comptes = self.db_manager.execute_query('''
            SELECT c.id, c.numero, c.nom, c.type,
                   COALESCE(SUM(le.debit - le.credit), 0) as solde,
                   CASE WHEN c.actif = 1 THEN 'Oui' ELSE 'Non' END as actif
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            GROUP BY c.id, c.numero, c.nom, c.type, c.actif
            ORDER BY c.numero
        ''')
        
        table_data = []
        for compte in comptes:
            id_compte, numero, nom, type_compte, solde, actif = compte
            table_data.append([id_compte, numero, nom, type_compte, f"{solde:,.2f}", actif])
        
        window['table_comptes'].update(table_data)
    
    def search_comptes(self, window, search_term: str):
        """Recherche des comptes"""
        comptes = self.db_manager.execute_query('''
            SELECT c.id, c.numero, c.nom, c.type,
                   COALESCE(SUM(le.debit - le.credit), 0) as solde,
                   CASE WHEN c.actif = 1 THEN 'Oui' ELSE 'Non' END as actif
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            WHERE c.numero LIKE ? OR c.nom LIKE ?
            GROUP BY c.id, c.numero, c.nom, c.type, c.actif
            ORDER BY c.numero
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        table_data = []
        for compte in comptes:
            id_compte, numero, nom, type_compte, solde, actif = compte
            table_data.append([id_compte, numero, nom, type_compte, f"{solde:,.2f}", actif])
        
        window['table_comptes'].update(table_data)
    
    def show_compte_form_window(self, compte_id: int = None) -> bool:
        """Affiche le formulaire d'ajout/modification de compte"""
        title = 'Modifier le compte' if compte_id else 'Ajouter un compte'
        
        # Types de comptes
        types_comptes = ['Actifs', 'Passifs', 'Charges', 'Produits', 'Capitaux', 
                        'Dettes', 'Créances', 'Immobilisations', 'Stocks', 'Financiers', 'Tiers']
        
        layout = [
            [sg.Text(title, font=('Arial', 12, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Numéro de compte:'), sg.Input(key='numero', size=(15, 1))],
            [sg.Text('Nom du compte:'), sg.Input(key='nom', size=(50, 1))],
            [sg.Text('Type de compte:'), sg.Combo(types_comptes, key='type', size=(20, 1))],
            [sg.Text('Compte parent:'), sg.Combo([], key='parent', size=(40, 1))],
            [sg.Checkbox('Compte actif', key='actif', default=True)],
            [sg.HSeparator()],
            [sg.Button('Enregistrer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window(title, layout, finalize=True)
        
        # Charger la liste des comptes parents
        comptes_parents = self.db_manager.execute_query('''
            SELECT CONCAT(numero, ' - ', nom) FROM comptes 
            WHERE actif = 1 ORDER BY numero
        ''')
        parent_list = [''] + [compte[0] for compte in comptes_parents]
        window['parent'].update(values=parent_list)
        
        # Si modification, charger les données existantes
        if compte_id:
            compte_data = self.db_manager.execute_query('''
                SELECT numero, nom, type, actif FROM comptes WHERE id = ?
            ''', (compte_id,))
            
            if compte_data:
                numero, nom, type_compte, actif = compte_data[0]
                window['numero'].update(numero)
                window['nom'].update(nom)
                window['type'].update(type_compte)
                window['actif'].update(actif)
        
        result = False
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Enregistrer':
                # Validation
                if not values['numero'] or not values['nom'] or not values['type']:
                    sg.popup_error('Veuillez remplir tous les champs obligatoires.')
                    continue
                
                # Vérifier l'unicité du numéro de compte
                if compte_id:
                    existing = self.db_manager.execute_query('''
                        SELECT id FROM comptes WHERE numero = ? AND id != ?
                    ''', (values['numero'], compte_id))
                else:
                    existing = self.db_manager.execute_query('''
                        SELECT id FROM comptes WHERE numero = ?
                    ''', (values['numero'],))
                
                if existing:
                    sg.popup_error('Ce numéro de compte existe déjà.')
                    continue
                
                # Enregistrement
                if compte_id:
                    # Modification
                    success = self.db_manager.execute_update('''
                        UPDATE comptes 
                        SET numero = ?, nom = ?, type = ?, actif = ?, 
                            date_modification = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (values['numero'], values['nom'], values['type'], 
                          values['actif'], compte_id))
                else:
                    # Ajout
                    success = self.db_manager.execute_update('''
                        INSERT INTO comptes (numero, nom, type, actif) 
                        VALUES (?, ?, ?, ?)
                    ''', (values['numero'], values['nom'], values['type'], values['actif']))
                
                if success:
                    sg.popup('Compte enregistré avec succès.')
                    result = True
                    break
                else:
                    sg.popup_error('Erreur lors de l\'enregistrement.')
        
        window.close()
        return result
    
    def show_ecritures_window(self):
        """Affiche la fenêtre de gestion des écritures"""
        layout = [
            [sg.Text('Gestion des Écritures Comptables', font=('Arial', 14, 'bold'))],
            [sg.HSeparator()],
            [sg.Frame('Filtres', [
                [sg.Text('Du:'), sg.Input(key='date_debut', size=(12, 1)),
                 sg.Text('Au:'), sg.Input(key='date_fin', size=(12, 1)),
                 sg.Text('Statut:'), sg.Combo(['Tous', 'brouillon', 'validé'], 
                                             default_value='Tous', key='statut'),
                 sg.Button('Filtrer')]
            ])],
            [sg.Table(values=[], headings=['ID', 'Numéro', 'Date', 'Libellé', 'Montant', 'Statut'],
                     key='table_ecritures', size=(120, 15),
                     justification='left', enable_events=True)],
            [sg.Frame('Lignes de l\'écriture sélectionnée', [
                [sg.Table(values=[], headings=['Compte', 'Libellé', 'Débit', 'Crédit'],
                         key='table_lignes', size=(120, 8),
                         justification='left')]
            ])],
            [sg.Button('Nouvelle écriture'), sg.Button('Modifier'), sg.Button('Supprimer'), 
             sg.Button('Valider'), sg.Button('Actualiser'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Écritures Comptables', layout, finalize=True, size=(1000, 700))
        
        # Charger les données initiales
        self.refresh_ecritures_window(window)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Actualiser':
                self.refresh_ecritures_window(window)
            
            elif event == 'table_ecritures':
                # Afficher les lignes de l'écriture sélectionnée
                selected = values['table_ecritures']
                if selected:
                    row_index = selected[0]
                    ecriture_data = window['table_ecritures'].get()[row_index]
                    ecriture_id = ecriture_data[0]
                    self.load_lignes_ecriture(window, ecriture_id)
            
            elif event == 'Nouvelle écriture':
                if self.show_ecriture_form_window():
                    self.refresh_ecritures_window(window)
            
            elif event == 'Modifier':
                selected = values['table_ecritures']
                if selected:
                    row_index = selected[0]
                    ecriture_data = window['table_ecritures'].get()[row_index]
                    ecriture_id = ecriture_data[0]
                    if self.show_ecriture_form_window(ecriture_id):
                        self.refresh_ecritures_window(window)
                else:
                    sg.popup('Veuillez sélectionner une écriture à modifier.')
            
            elif event == 'Valider':
                selected = values['table_ecritures']
                if selected:
                    row_index = selected[0]
                    ecriture_data = window['table_ecritures'].get()[row_index]
                    ecriture_id = ecriture_data[0]
                    
                    if sg.popup_yes_no('Êtes-vous sûr de vouloir valider cette écriture ?') == 'Yes':
                        if self.db_manager.execute_update('''
                            UPDATE ecritures SET statut = 'validé' WHERE id = ?
                        ''', (ecriture_id,)):
                            sg.popup('Écriture validée avec succès.')
                            self.refresh_ecritures_window(window)
                else:
                    sg.popup('Veuillez sélectionner une écriture à valider.')
            
            elif event == 'Filtrer':
                self.filter_ecritures(window, values['date_debut'], 
                                     values['date_fin'], values['statut'])
        
        window.close()
    
    def refresh_ecritures_window(self, window):
        """Actualise les données des écritures"""
        ecritures = self.db_manager.execute_query('''
            SELECT id, numero, date_ecriture, libelle, montant_total, statut
            FROM ecritures
            ORDER BY date_ecriture DESC, numero DESC
            LIMIT 200
        ''')
        
        table_data = []
        for ecriture in ecritures:
            id_ecriture, numero, date_ecr, libelle, montant, statut = ecriture
            table_data.append([id_ecriture, numero, date_ecr, libelle, 
                             f"{montant:,.2f} €", statut])
        
        window['table_ecritures'].update(table_data)
    
    def load_lignes_ecriture(self, window, ecriture_id: int):
        """Charge les lignes d'une écriture"""
        lignes = self.db_manager.execute_query('''
            SELECT c.numero || ' - ' || c.nom, le.libelle, le.debit, le.credit
            FROM lignes_ecriture le
            JOIN comptes c ON le.compte_id = c.id
            WHERE le.ecriture_id = ?
            ORDER BY le.id
        ''', (ecriture_id,))
        
        table_data = []
        for ligne in lignes:
            compte, libelle, debit, credit = ligne
            table_data.append([compte, libelle, f"{debit:,.2f}", f"{credit:,.2f}"])
        
        window['table_lignes'].update(table_data)
    
    def filter_ecritures(self, window, date_debut: str, date_fin: str, statut: str):
        """Filtre les écritures selon les critères"""
        query = '''
            SELECT id, numero, date_ecriture, libelle, montant_total, statut
            FROM ecritures
            WHERE 1=1
        '''
        params = []
        
        if date_debut:
            query += ' AND date_ecriture >= ?'
            params.append(date_debut)
        
        if date_fin:
            query += ' AND date_ecriture <= ?'
            params.append(date_fin)
        
        if statut and statut != 'Tous':
            query += ' AND statut = ?'
            params.append(statut)
        
        query += ' ORDER BY date_ecriture DESC, numero DESC LIMIT 200'
        
        ecritures = self.db_manager.execute_query(query, tuple(params))
        
        table_data = []
        for ecriture in ecritures:
            id_ecriture, numero, date_ecr, libelle, montant, statut = ecriture
            table_data.append([id_ecriture, numero, date_ecr, libelle, 
                             f"{montant:,.2f} €", statut])
        
        window['table_ecritures'].update(table_data)
    
    def show_ecriture_form_window(self, ecriture_id: int = None) -> bool:
        """Affiche le formulaire d'écriture"""
        title = 'Modifier l\'écriture' if ecriture_id else 'Nouvelle écriture'
        
        # Génération du numéro automatique
        if not ecriture_id:
            last_numero = self.db_manager.execute_query('''
                SELECT MAX(CAST(numero AS INTEGER)) FROM ecritures 
                WHERE numero REGEXP '^[0-9]+$'
            ''')
            next_numero = (last_numero[0][0] + 1) if last_numero and last_numero[0][0] else 1
        else:
            next_numero = ""
        
        layout = [
            [sg.Text(title, font=('Arial', 12, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Numéro:'), sg.Input(key='numero', size=(15, 1), 
                                         default_text=str(next_numero) if next_numero else "")],
            [sg.Text('Date:'), sg.Input(key='date_ecriture', size=(15, 1), 
                                       default_text=datetime.datetime.now().strftime('%Y-%m-%d'))],
            [sg.Text('Libellé:'), sg.Input(key='libelle', size=(60, 1))],
            [sg.HSeparator()],
            [sg.Text('Lignes d\'écriture:', font=('Arial', 10, 'bold'))],
            [sg.Table(values=[], headings=['Compte', 'Libellé', 'Débit', 'Crédit'],
                     key='table_lignes_form', size=(80, 10),
                     justification='left', enable_events=True)],
            [sg.Button('Ajouter ligne'), sg.Button('Modifier ligne'), sg.Button('Supprimer ligne')],
            [sg.HSeparator()],
            [sg.Text('Totaux:', font=('Arial', 10, 'bold'))],
            [sg.Text('Total Débits:'), sg.Text('0,00 €', key='total_debits'),
             sg.Text('Total Crédits:'), sg.Text('0,00 €', key='total_credits')],
            [sg.Text('Différence:'), sg.Text('0,00 €', key='difference', text_color='red')],
            [sg.HSeparator()],
            [sg.Button('Enregistrer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window(title, layout, finalize=True, size=(800, 600))
        
        # Variables pour stocker les lignes
        lignes_ecriture = []
        
        # Si modification, charger les données existantes
        if ecriture_id:
            ecriture_data = self.db_manager.execute_query('''
                SELECT numero, date_ecriture, libelle FROM ecritures WHERE id = ?
            ''', (ecriture_id,))
            
            if ecriture_data:
                numero, date_ecr, libelle = ecriture_data[0]
                window['numero'].update(numero)
                window['date_ecriture'].update(date_ecr)
                window['libelle'].update(libelle)
            
            # Charger les lignes existantes
            lignes_data = self.db_manager.execute_query('''
                SELECT le.compte_id, c.numero || ' - ' || c.nom, le.libelle, le.debit, le.credit
                FROM lignes_ecriture le
                JOIN comptes c ON le.compte_id = c.id
                WHERE le.ecriture_id = ?
            ''', (ecriture_id,))
            
            for ligne_data in lignes_data:
                compte_id, compte_nom, libelle_ligne, debit, credit = ligne_data
                lignes_ecriture.append({
                    'compte_id': compte_id,
                    'compte_nom': compte_nom,
                    'libelle': libelle_ligne,
                    'debit': debit,
                    'credit': credit
                })
        
        # Actualiser l'affichage des lignes
        self.update_lignes_display(window, lignes_ecriture)
        
        result = False
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Ajouter ligne':
                ligne = self.show_ligne_ecriture_form()
                if ligne:
                    lignes_ecriture.append(ligne)
                    self.update_lignes_display(window, lignes_ecriture)
            
            elif event == 'Modifier ligne':
                selected = values['table_lignes_form']
                if selected:
                    index = selected[0]
                    ligne_modifiee = self.show_ligne_ecriture_form(lignes_ecriture[index])
                    if ligne_modifiee:
                        lignes_ecriture[index] = ligne_modifiee
                        self.update_lignes_display(window, lignes_ecriture)
                else:
                    sg.popup('Veuillez sélectionner une ligne à modifier.')
            
            elif event == 'Supprimer ligne':
                selected = values['table_lignes_form']
                if selected:
                    index = selected[0]
                    if sg.popup_yes_no('Supprimer cette ligne ?') == 'Yes':
                        del lignes_ecriture[index]
                        self.update_lignes_display(window, lignes_ecriture)
                else:
                    sg.popup('Veuillez sélectionner une ligne à supprimer.')
            
            elif event == 'Enregistrer':
                # Validation
                if not values['numero'] or not values['date_ecriture'] or not values['libelle']:
                    sg.popup_error('Veuillez remplir tous les champs obligatoires.')
                    continue
                
                if not lignes_ecriture:
                    sg.popup_error('Veuillez ajouter au moins une ligne d\'écriture.')
                    continue
                
                # Vérifier l'équilibre
                total_debits = sum(ligne['debit'] for ligne in lignes_ecriture)
                total_credits = sum(ligne['credit'] for ligne in lignes_ecriture)
                
                if abs(total_debits - total_credits) > 0.01:
                    sg.popup_error('L\'écriture n\'est pas équilibrée.\nLes débits doivent égaler les crédits.')
                    continue
                
                # Enregistrement
                if self.save_ecriture(ecriture_id, values, lignes_ecriture):
                    sg.popup('Écriture enregistrée avec succès.')
                    result = True
                    break
        
        window.close()
        return result
    
    def update_lignes_display(self, window, lignes_ecriture: list):
        """Met à jour l'affichage des lignes d'écriture"""
        table_data = []
        total_debits = 0
        total_credits = 0
        
        for ligne in lignes_ecriture:
            table_data.append([
                ligne['compte_nom'],
                ligne['libelle'],
                f"{ligne['debit']:,.2f}",
                f"{ligne['credit']:,.2f}"
            ])
            total_debits += ligne['debit']
            total_credits += ligne['credit']
        
        window['table_lignes_form'].update(table_data)
        window['total_debits'].update(f"{total_debits:,.2f} €")
        window['total_credits'].update(f"{total_credits:,.2f} €")
        
        difference = total_debits - total_credits
        color = 'green' if abs(difference) < 0.01 else 'red'
        window['difference'].update(f"{difference:,.2f} €", text_color=color)
    
    def show_ligne_ecriture_form(self, ligne_existante: dict = None) -> dict:
        """Affiche le formulaire d'ajout/modification de ligne d'écriture"""
        title = 'Modifier la ligne' if ligne_existante else 'Ajouter une ligne'
        
        layout = [
            [sg.Text(title, font=('Arial', 10, 'bold'))],
            [sg.Text('Compte:'), sg.Combo([], key='compte', size=(50, 1))],
            [sg.Text('Libellé:'), sg.Input(key='libelle', size=(50, 1))],
            [sg.Text('Débit:'), sg.Input(key='debit', size=(15, 1))],
            [sg.Text('Crédit:'), sg.Input(key='credit', size=(15, 1))],
            [sg.HSeparator()],
            [sg.Button('Enregistrer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window(title, layout, finalize=True)
        
        # Charger la liste des comptes
        comptes = self.db_manager.execute_query('''
            SELECT id, numero || ' - ' || nom FROM comptes 
            WHERE actif = 1 ORDER BY numero
        ''')
        
        compte_list = []
        compte_map = {}
        for compte_id, compte_nom in comptes:
            compte_list.append(compte_nom)
            compte_map[compte_nom] = compte_id
        
        window['compte'].update(values=compte_list)
        
        # Si modification, charger les données existantes
        if ligne_existante:
            window['compte'].update(ligne_existante['compte_nom'])
            window['libelle'].update(ligne_existante['libelle'])
            window['debit'].update(str(ligne_existante['debit']) if ligne_existante['debit'] > 0 else '')
            window['credit'].update(str(ligne_existante['credit']) if ligne_existante['credit'] > 0 else '')
        
        result = None
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Enregistrer':
                if not values['compte'] or not values['libelle']:
                    sg.popup_error('Veuillez sélectionner un compte et saisir un libellé.')
                    continue
                
                # Validation des montants
                debit_valid, debit = ValidationManager.validate_amount(values['debit'] or '0')
                credit_valid, credit = ValidationManager.validate_amount(values['credit'] or '0')
                
                if not debit_valid or not credit_valid:
                    sg.popup_error('Montants invalides.')
                    continue
                
                if debit > 0 and credit > 0:
                    sg.popup_error('Une ligne ne peut pas avoir à la fois un débit et un crédit.')
                    continue
                
                if debit == 0 and credit == 0:
                    sg.popup_error('Veuillez saisir un montant en débit ou en crédit.')
                    continue
                
                compte_nom = values['compte']
                compte_id = compte_map.get(compte_nom)
                
                if not compte_id:
                    sg.popup_error('Compte invalide.')
                    continue
                
                result = {
                    'compte_id': compte_id,
                    'compte_nom': compte_nom,
                    'libelle': values['libelle'],
                    'debit': debit,
                    'credit': credit
                }
                break
        
        window.close()
        return result
    
    def save_ecriture(self, ecriture_id: int, values: dict, lignes_ecriture: list) -> bool:
        """Sauvegarde une écriture avec ses lignes"""
        try:
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            
            montant_total = sum(ligne['debit'] for ligne in lignes_ecriture)
            
            if ecriture_id:
                # Modification
                cursor.execute('''
                    UPDATE ecritures 
                    SET numero = ?, date_ecriture = ?, libelle = ?, montant_total = ?,
                        date_modification = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (values['numero'], values['date_ecriture'], values['libelle'], 
                      montant_total, ecriture_id))
                
                # Supprimer les anciennes lignes
                cursor.execute('DELETE FROM lignes_ecriture WHERE ecriture_id = ?', (ecriture_id,))
                
                current_ecriture_id = ecriture_id
            else:
                # Ajout
                cursor.execute('''
                    INSERT INTO ecritures (numero, date_ecriture, libelle, montant_total, utilisateur)
                    VALUES (?, ?, ?, ?, ?)
                ''', (values['numero'], values['date_ecriture'], values['libelle'], 
                      montant_total, self.auth_manager.current_user['nom_utilisateur']))
                
                current_ecriture_id = cursor.lastrowid
            
            # Insérer les nouvelles lignes
            for ligne in lignes_ecriture:
                cursor.execute('''
                    INSERT INTO lignes_ecriture (ecriture_id, compte_id, libelle, debit, credit)
                    VALUES (?, ?, ?, ?, ?)
                ''', (current_ecriture_id, ligne['compte_id'], ligne['libelle'], 
                      ligne['debit'], ligne['credit']))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            sg.popup_error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def show_clients_window(self):
        """Affiche la fenêtre de gestion des clients"""
        layout = [
            [sg.Text('Gestion des Clients', font=('Arial', 14, 'bold'))],
            [sg.HSeparator()],
            [sg.Frame('Recherche', [
                [sg.Text('Rechercher:'), sg.Input(key='search', size=(30, 1)), sg.Button('Rechercher')]
            ])],
            [sg.Table(values=[], headings=['ID', 'Code', 'Nom', 'Prénom', 'Ville', 'Téléphone', 'Email'],
                     key='table_clients', size=(120, 20),
                     justification='left', enable_events=True)],
            [sg.Button('Ajouter'), sg.Button('Modifier'), sg.Button('Supprimer'), 
             sg.Button('Actualiser'), sg.Button('Exporter CSV'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Clients', layout, finalize=True, size=(1000, 600))
        
        self.refresh_clients_window(window)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Actualiser':
                self.refresh_clients_window(window)
            
            elif event == 'Ajouter':
                if self.show_client_form_window():
                    self.refresh_clients_window(window)
            
            elif event == 'Modifier':
                selected = values['table_clients']
                if selected:
                    row_index = selected[0]
                    client_data = window['table_clients'].get()[row_index]
                    client_id = client_data[0]
                    if self.show_client_form_window(client_id):
                        self.refresh_clients_window(window)
                else:
                    sg.popup('Veuillez sélectionner un client à modifier.')
        
        window.close()
    
    def refresh_clients_window(self, window):
        """Actualise les données des clients"""
        clients = self.db_manager.execute_query('''
            SELECT id, code, nom, prenom, ville, telephone, email
            FROM clients
            WHERE actif = 1
            ORDER BY nom, prenom
        ''')
        
        table_data = []
        for client in clients:
            table_data.append(list(client))
        
        window['table_clients'].update(table_data)
    
    def show_client_form_window(self, client_id: int = None) -> bool:
        """Affiche le formulaire de client"""
        title = 'Modifier le client' if client_id else 'Ajouter un client'
        
        layout = [
            [sg.Text(title, font=('Arial', 12, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Code client:'), sg.Input(key='code', size=(20, 1))],
            [sg.Text('Nom:'), sg.Input(key='nom', size=(40, 1))],
            [sg.Text('Prénom:'), sg.Input(key='prenom', size=(40, 1))],
            [sg.Text('Raison sociale:'), sg.Input(key='raison_sociale', size=(40, 1))],
            [sg.HSeparator()],
            [sg.Text('Adresse:'), sg.Input(key='adresse', size=(60, 1))],
            [sg.Text('Ville:'), sg.Input(key='ville', size=(30, 1))],
            [sg.Text('Code postal:'), sg.Input(key='code_postal', size=(10, 1))],
            [sg.Text('Pays:'), sg.Input(key='pays', size=(30, 1), default_text='France')],
            [sg.HSeparator()],
            [sg.Text('Téléphone:'), sg.Input(key='telephone', size=(20, 1))],
            [sg.Text('Email:'), sg.Input(key='email', size=(40, 1))],
            [sg.HSeparator()],
            [sg.Text('SIRET:'), sg.Input(key='siret', size=(20, 1))],
            [sg.Text('N° TVA:'), sg.Input(key='tva', size=(20, 1))],
            [sg.Text('Conditions de paiement (jours):'), sg.Input(key='conditions_paiement', 
                                                                   size=(10, 1), default_text='30')],
            [sg.Text('Limite de crédit:'), sg.Input(key='limite_credit', size=(15, 1), default_text='0')],
            [sg.Checkbox('Client actif', key='actif', default=True)],
            [sg.HSeparator()],
            [sg.Button('Enregistrer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window(title, layout, finalize=True, size=(600, 500))
        
        # Si modification, charger les données existantes
        if client_id:
            client_data = self.db_manager.execute_query('''
                SELECT code, nom, prenom, raison_sociale, adresse, ville, code_postal, pays,
                       telephone, email, siret, tva, conditions_paiement, limite_credit, actif
                FROM clients WHERE id = ?
            ''', (client_id,))
            
            if client_data:
                (code, nom, prenom, raison_sociale, adresse, ville, code_postal, pays,
                 telephone, email, siret, tva, conditions_paiement, limite_credit, actif) = client_data[0]
                
                window['code'].update(code)
                window['nom'].update(nom or '')
                window['prenom'].update(prenom or '')
                window['raison_sociale'].update(raison_sociale or '')
                window['adresse'].update(adresse or '')
                window['ville'].update(ville or '')
                window['code_postal'].update(code_postal or '')
                window['pays'].update(pays or 'France')
                window['telephone'].update(telephone or '')
                window['email'].update(email or '')
                window['siret'].update(siret or '')
                window['tva'].update(tva or '')
                window['conditions_paiement'].update(str(conditions_paiement or 30))
                window['limite_credit'].update(str(limite_credit or 0))
                window['actif'].update(bool(actif))
        else:
            # Générer un code client automatique
            last_code = self.db_manager.execute_query('''
                SELECT MAX(CAST(SUBSTR(code, 2) AS INTEGER)) 
                FROM clients 
                WHERE code LIKE 'C%' AND LENGTH(code) <= 10
            ''')
            next_number = (last_code[0][0] + 1) if last_code and last_code[0][0] else 1
            window['code'].update(f"C{next_number:06d}")
        
        result = False
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Enregistrer':
                # Validation
                if not values['code'] or not values['nom']:
                    sg.popup_error('Le code et le nom sont obligatoires.')
                    continue
                
                # Validation de l'email
                if values['email'] and not ValidationManager.validate_email(values['email']):
                    sg.popup_error('Format d\'email invalide.')
                    continue
                
                # Validation du SIRET
                if values['siret'] and not ValidationManager.validate_siret(values['siret']):
                    sg.popup_error('Numéro SIRET invalide.')
                    continue
                
                # Validation des montants
                try:
                    limite_credit = float(values['limite_credit'] or 0)
                    conditions_paiement = int(values['conditions_paiement'] or 30)
                except ValueError:
                    sg.popup_error('Valeurs numériques invalides.')
                    continue
                
                # Vérifier l'unicité du code
                if client_id:
                    existing = self.db_manager.execute_query('''
                        SELECT id FROM clients WHERE code = ? AND id != ?
                    ''', (values['code'], client_id))
                else:
                    existing = self.db_manager.execute_query('''
                        SELECT id FROM clients WHERE code = ?
                    ''', (values['code'],))
                
                if existing:
                    sg.popup_error('Ce code client existe déjà.')
                    continue
                
                # Enregistrement
                if client_id:
                    success = self.db_manager.execute_update('''
                        UPDATE clients SET
                        code = ?, nom = ?, prenom = ?, raison_sociale = ?, adresse = ?,
                        ville = ?, code_postal = ?, pays = ?, telephone = ?, email = ?,
                        siret = ?, tva = ?, conditions_paiement = ?, limite_credit = ?, actif = ?
                        WHERE id = ?
                    ''', (values['code'], values['nom'], values['prenom'], values['raison_sociale'],
                          values['adresse'], values['ville'], values['code_postal'], values['pays'],
                          values['telephone'], values['email'], values['siret'], values['tva'],
                          conditions_paiement, limite_credit, values['actif'], client_id))
                else:
                    success = self.db_manager.execute_update('''
                        INSERT INTO clients 
                        (code, nom, prenom, raison_sociale, adresse, ville, code_postal, pays,
                         telephone, email, siret, tva, conditions_paiement, limite_credit, actif)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (values['code'], values['nom'], values['prenom'], values['raison_sociale'],
                          values['adresse'], values['ville'], values['code_postal'], values['pays'],
                          values['telephone'], values['email'], values['siret'], values['tva'],
                          conditions_paiement, limite_credit, values['actif']))
                
                if success:
                    sg.popup('Client enregistré avec succès.')
                    result = True
                    break
        
        window.close()
        return result
    
    def show_fournisseurs_window(self):
        """Affiche la fenêtre de gestion des fournisseurs"""
        # Similaire à show_clients_window mais pour les fournisseurs
        layout = [
            [sg.Text('Gestion des Fournisseurs', font=('Arial', 14, 'bold'))],
            [sg.HSeparator()],
            [sg.Frame('Recherche', [
                [sg.Text('Rechercher:'), sg.Input(key='search', size=(30, 1)), sg.Button('Rechercher')]
            ])],
            [sg.Table(values=[], headings=['ID', 'Code', 'Nom', 'Ville', 'Téléphone', 'Email'],
                     key='table_fournisseurs', size=(120, 20),
                     justification='left', enable_events=True)],
            [sg.Button('Ajouter'), sg.Button('Modifier'), sg.Button('Supprimer'), 
             sg.Button('Actualiser'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Fournisseurs', layout, finalize=True, size=(1000, 600))
        
        self.refresh_fournisseurs_window(window)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Actualiser':
                self.refresh_fournisseurs_window(window)
            
            elif event == 'Ajouter':
                if self.show_fournisseur_form_window():
                    self.refresh_fournisseurs_window(window)
        
        window.close()
    
    def refresh_fournisseurs_window(self, window):
        """Actualise les données des fournisseurs"""
        fournisseurs = self.db_manager.execute_query('''
            SELECT id, code, nom, ville, telephone, email
            FROM fournisseurs
            WHERE actif = 1
            ORDER BY nom
        ''')
        
        table_data = []
        for fournisseur in fournisseurs:
            table_data.append(list(fournisseur))
        
        window['table_fournisseurs'].update(table_data)
    
    def show_fournisseur_form_window(self, fournisseur_id: int = None) -> bool:
        """Affiche le formulaire de fournisseur (similaire au client)"""
        title = 'Modifier le fournisseur' if fournisseur_id else 'Ajouter un fournisseur'
        
        layout = [
            [sg.Text(title, font=('Arial', 12, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Code fournisseur:'), sg.Input(key='code', size=(20, 1))],
            [sg.Text('Nom:'), sg.Input(key='nom', size=(40, 1))],
            [sg.Text('Raison sociale:'), sg.Input(key='raison_sociale', size=(40, 1))],
            [sg.Text('Adresse:'), sg.Input(key='adresse', size=(60, 1))],
            [sg.Text('Ville:'), sg.Input(key='ville', size=(30, 1))],
            [sg.Text('Téléphone:'), sg.Input(key='telephone', size=(20, 1))],
            [sg.Text('Email:'), sg.Input(key='email', size=(40, 1))],
            [sg.Checkbox('Fournisseur actif', key='actif', default=True)],
            [sg.HSeparator()],
            [sg.Button('Enregistrer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window(title, layout, finalize=True)
        
        # Générer un code automatique pour nouveau fournisseur
        if not fournisseur_id:
            last_code = self.db_manager.execute_query('''
                SELECT MAX(CAST(SUBSTR(code, 2) AS INTEGER)) 
                FROM fournisseurs 
                WHERE code LIKE 'F%' AND LENGTH(code) <= 10
            ''')
            next_number = (last_code[0][0] + 1) if last_code and last_code[0][0] else 1
            window['code'].update(f"F{next_number:06d}")
        
        result = False
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Enregistrer':
                if not values['code'] or not values['nom']:
                    sg.popup_error('Le code et le nom sont obligatoires.')
                    continue
                
                # Validation email
                if values['email'] and not ValidationManager.validate_email(values['email']):
                    sg.popup_error('Format d\'email invalide.')
                    continue
                
                # Enregistrement
                success = self.db_manager.execute_update('''
                    INSERT INTO fournisseurs 
                    (code, nom, raison_sociale, adresse, ville, telephone, email, actif)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (values['code'], values['nom'], values['raison_sociale'],
                      values['adresse'], values['ville'], values['telephone'], 
                      values['email'], values['actif']))
                
                if success:
                    sg.popup('Fournisseur enregistré avec succès.')
                    result = True
                    break
        
        window.close()
        return result
    
    def show_factures_window(self):
        """Affiche la fenêtre de gestion des factures"""
        layout = [
            [sg.Text('Gestion des Factures', font=('Arial', 14, 'bold'))],
            [sg.HSeparator()],
            [sg.Frame('Filtres', [
                [sg.Radio('Factures clients', 'type_facture', default=True, key='clients'),
                 sg.Radio('Factures fournisseurs', 'type_facture', key='fournisseurs')],
                [sg.Text('Statut:'), sg.Combo(['Tous', 'en_cours', 'payee', 'en_retard'], 
                                             default_value='Tous', key='statut')]
            ])],
            [sg.Table(values=[], headings=['ID', 'Numéro', 'Client/Fournisseur', 'Date', 'Échéance', 'Montant TTC', 'Statut'],
                     key='table_factures', size=(140, 20),
                     justification='left', enable_events=True)],
            [sg.Button('Nouvelle facture'), sg.Button('Modifier'), sg.Button('Supprimer'), 
             sg.Button('Règlement'), sg.Button('Imprimer'), sg.Button('Actualiser'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Factures', layout, finalize=True, size=(1100, 600))
        
        self.refresh_factures_window(window)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Actualiser':
                self.refresh_factures_window(window)
            
            elif event == 'Nouvelle facture':
                if self.show_facture_form_window():
                    self.refresh_factures_window(window)
        
        window.close()
    
    def refresh_factures_window(self, window):
        """Actualise les données des factures"""
        factures = self.db_manager.execute_query('''
            SELECT f.id, f.numero, c.nom, f.date_facture, f.date_echeance, 
                   f.montant_ttc, f.statut
            FROM factures f
            JOIN clients c ON f.client_id = c.id
            ORDER BY f.date_facture DESC
            LIMIT 200
        ''')
        
        table_data = []
        for facture in factures:
            id_fact, numero, client, date_fact, date_ech, montant, statut = facture
            table_data.append([id_fact, numero, client, date_fact, date_ech, 
                              f"{montant:,.2f} €", statut])
        
        window['table_factures'].update(table_data)
    
    def show_facture_form_window(self, facture_id: int = None) -> bool:
        """Affiche le formulaire de facture"""
        title = 'Modifier la facture' if facture_id else 'Nouvelle facture'
        
        layout = [
            [sg.Text(title, font=('Arial', 12, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Numéro:'), sg.Input(key='numero', size=(20, 1))],
            [sg.Text('Client:'), sg.Combo([], key='client', size=(50, 1))],
            [sg.Text('Date facture:'), sg.Input(key='date_facture', size=(15, 1),
                                               default_text=datetime.datetime.now().strftime('%Y-%m-%d'))],
            [sg.Text('Date échéance:'), sg.Input(key='date_echeance', size=(15, 1))],
            [sg.Text('Libellé:'), sg.Input(key='libelle', size=(60, 1))],
            [sg.HSeparator()],
            [sg.Text('Lignes de facture:', font=('Arial', 10, 'bold'))],
            [sg.Table(values=[], headings=['Description', 'Quantité', 'Prix unit.', 'TVA %', 'Montant HT'],
                     key='table_lignes_fact', size=(80, 8),
                     justification='left')],
            [sg.Button('Ajouter ligne'), sg.Button('Supprimer ligne')],
            [sg.HSeparator()],
            [sg.Text('Total HT:'), sg.Text('0,00 €', key='total_ht'),
             sg.Text('Total TVA:'), sg.Text('0,00 €', key='total_tva'),
             sg.Text('Total TTC:'), sg.Text('0,00 €', key='total_ttc')],
            [sg.HSeparator()],
            [sg.Button('Enregistrer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window(title, layout, finalize=True, size=(800, 600))
        
        # Charger la liste des clients
        clients = self.db_manager.execute_query('''
            SELECT id, code || ' - ' || nom FROM clients WHERE actif = 1 ORDER BY nom
        ''')
        client_list = []
        client_map = {}
        for client_id, client_nom in clients:
            client_list.append(client_nom)
            client_map[client_nom] = client_id
        
        window['client'].update(values=client_list)
        
        # Générer numéro de facture automatique
        if not facture_id:
            last_numero = self.db_manager.execute_query('''
                SELECT MAX(CAST(SUBSTR(numero, 3) AS INTEGER)) 
                FROM factures 
                WHERE numero LIKE 'FA%'
            ''')
            next_numero = (last_numero[0][0] + 1) if last_numero and last_numero[0][0] else 1
            window['numero'].update(f"FA{next_numero:06d}")
        
        # Variables pour les lignes
        lignes_facture = []
        
        result = False
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Ajouter ligne':
                ligne = self.show_ligne_facture_form()
                if ligne:
                    lignes_facture.append(ligne)
                    self.update_facture_totals(window, lignes_facture)
            
            elif event == 'Supprimer ligne':
                selected = values['table_lignes_fact']
                if selected and lignes_facture:
                    index = selected[0]
                    del lignes_facture[index]
                    self.update_facture_totals(window, lignes_facture)
            
            elif event == 'Enregistrer':
                if not values['numero'] or not values['client']:
                    sg.popup_error('Numéro et client obligatoires.')
                    continue
                
                if not lignes_facture:
                    sg.popup_error('Veuillez ajouter au moins une ligne.')
                    continue
                
                # Calcul des échéances
                if not values['date_echeance']:
                    client_id = client_map[values['client']]
                    conditions = self.db_manager.execute_query('''
                        SELECT conditions_paiement FROM clients WHERE id = ?
                    ''', (client_id,))
                    
                    jours = conditions[0][0] if conditions else 30
                    date_facture = datetime.datetime.strptime(values['date_facture'], '%Y-%m-%d')
                    date_echeance = date_facture + datetime.timedelta(days=jours)
                    window['date_echeance'].update(date_echeance.strftime('%Y-%m-%d'))
                    continue
                
                if self.save_facture(facture_id, values, lignes_facture, client_map):
                    sg.popup('Facture enregistrée avec succès.')
                    result = True
                    break
        
        window.close()
        return result
    
    def show_ligne_facture_form(self) -> dict:
        """Formulaire de ligne de facture"""
        layout = [
            [sg.Text('Ajouter une ligne de facture')],
            [sg.Text('Description:'), sg.Input(key='description', size=(50, 1))],
            [sg.Text('Quantité:'), sg.Input(key='quantite', size=(10, 1))],
            [sg.Text('Prix unitaire:'), sg.Input(key='prix_unitaire', size=(15, 1))],
            [sg.Text('Taux TVA (%):'), sg.Input(key='taux_tva', size=(10, 1), default_text='20.0')],
            [sg.Button('Ajouter'), sg.Button('Annuler')]
        ]
        
        window = sg.Window('Ligne de facture', layout, finalize=True)
        
        result = None
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Ajouter':
                if not all([values['description'], values['quantite'], values['prix_unitaire']]):
                    sg.popup_error('Tous les champs sont obligatoires.')
                    continue
                
                try:
                    quantite = float(values['quantite'])
                    prix_unitaire = float(values['prix_unitaire'])
                    taux_tva = float(values['taux_tva'])
                    
                    montant_ht = quantite * prix_unitaire
                    montant_tva = montant_ht * (taux_tva / 100)
                    
                    result = {
                        'description': values['description'],
                        'quantite': quantite,
                        'prix_unitaire': prix_unitaire,
                        'taux_tva': taux_tva,
                        'montant_ht': montant_ht,
                        'montant_tva': montant_tva
                    }
                    break
                    
                except ValueError:
                    sg.popup_error('Valeurs numériques invalides.')
        
        window.close()
        return result
    
    def update_facture_totals(self, window, lignes_facture: list):
        """Met à jour les totaux de la facture"""
        table_data = []
        total_ht = 0
        total_tva = 0
        
        for ligne in lignes_facture:
            table_data.append([
                ligne['description'],
                f"{ligne['quantite']:.2f}",
                f"{ligne['prix_unitaire']:.2f}",
                f"{ligne['taux_tva']:.1f}%",
                f"{ligne['montant_ht']:.2f}"
            ])
            total_ht += ligne['montant_ht']
            total_tva += ligne['montant_tva']
        
        total_ttc = total_ht + total_tva
        
        window['table_lignes_fact'].update(table_data)
        window['total_ht'].update(f"{total_ht:.2f} €")
        window['total_tva'].update(f"{total_tva:.2f} €")
        window['total_ttc'].update(f"{total_ttc:.2f} €")
    
    def save_facture(self, facture_id: int, values: dict, lignes_facture: list, client_map: dict) -> bool:
        """Sauvegarde la facture"""
        try:
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            
            client_id = client_map[values['client']]
            
            # Calculs des totaux
            total_ht = sum(ligne['montant_ht'] for ligne in lignes_facture)
            total_tva = sum(ligne['montant_tva'] for ligne in lignes_facture)
            total_ttc = total_ht + total_tva
            
            if facture_id:
                # Modification
                cursor.execute('''
                    UPDATE factures SET
                    numero = ?, client_id = ?, date_facture = ?, date_echeance = ?,
                    montant_ht = ?, montant_tva = ?, montant_ttc = ?, libelle = ?
                    WHERE id = ?
                ''', (values['numero'], client_id, values['date_facture'], values['date_echeance'],
                      total_ht, total_tva, total_ttc, values['libelle'], facture_id))
                
                cursor.execute('DELETE FROM lignes_facture WHERE facture_id = ?', (facture_id,))
                current_facture_id = facture_id
            else:
                # Création
                cursor.execute('''
                    INSERT INTO factures 
                    (numero, client_id, date_facture, date_echeance, montant_ht, montant_tva, montant_ttc, libelle)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (values['numero'], client_id, values['date_facture'], values['date_echeance'],
                      total_ht, total_tva, total_ttc, values['libelle']))
                
                current_facture_id = cursor.lastrowid
            
            # Lignes de facture
            for ligne in lignes_facture:
                cursor.execute('''
                    INSERT INTO lignes_facture 
                    (facture_id, description, quantite, prix_unitaire, taux_tva, montant_ht, montant_tva)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (current_facture_id, ligne['description'], ligne['quantite'], 
                      ligne['prix_unitaire'], ligne['taux_tva'], ligne['montant_ht'], ligne['montant_tva']))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            sg.popup_error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def show_bilan_window(self):
        """Affiche le bilan comptable"""
        layout = [
            [sg.Text('Bilan Comptable', font=('Arial', 14, 'bold'))],
            [sg.Text('Date du bilan:'), sg.Input(key='date_bilan', size=(15, 1),
                                               default_text=datetime.datetime.now().strftime('%Y-%m-%d')),
             sg.Button('Générer')],
            [sg.HSeparator()],
            [sg.Column([
                [sg.Text('ACTIF', font=('Arial', 12, 'bold'))],
                [sg.Table(values=[], headings=['Poste', 'Montant'],
                         key='table_actif', size=(50, 15))]
            ]), sg.VSeparator(), sg.Column([
                [sg.Text('PASSIF', font=('Arial', 12, 'bold'))],
                [sg.Table(values=[], headings=['Poste', 'Montant'],
                         key='table_passif', size=(50, 15))]
            ])],
            [sg.HSeparator()],
            [sg.Button('Imprimer'), sg.Button('Exporter PDF'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Bilan', layout, finalize=True, size=(900, 600))
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Générer':
                date_bilan = values['date_bilan']
                if not ValidationManager.validate_date(date_bilan):
                    sg.popup_error('Date invalide.')
                    continue
                
                bilan = self.report_manager.generate_balance_sheet(date_bilan)
                self.display_bilan(window, bilan)
            
            elif event == 'Imprimer':
                self.print_bilan(values['date_bilan'])
            
            elif event == 'Exporter PDF':
                sg.popup('Fonctionnalité à implémenter')
        
        window.close()
    
    def display_bilan(self, window, bilan: dict):
        """Affiche les données du bilan"""
        # Actif
        actif_data = []
        for categorie, comptes in bilan['actifs'].items():
            if comptes:
                actif_data.append([f"--- {categorie} ---", ""])
                for compte in comptes:
                    nom, solde = compte
                    actif_data.append([nom, f"{solde:,.2f} €"])
        
        # Passif
        passif_data = []
        for categorie, comptes in bilan['passifs'].items():
            if comptes:
                passif_data.append([f"--- {categorie} ---", ""])
                for compte in comptes:
                    nom, solde = compte
                    passif_data.append([nom, f"{solde:,.2f} €"])
        
        window['table_actif'].update(actif_data)
        window['table_passif'].update(passif_data)
    
    def show_compte_resultat_window(self):
        """Affiche le compte de résultat"""
        layout = [
            [sg.Text('Compte de Résultat', font=('Arial', 14, 'bold'))],
            [sg.Text('Période du:'), sg.Input(key='date_debut', size=(12, 1)),
             sg.Text('au:'), sg.Input(key='date_fin', size=(12, 1)),
             sg.Button('Générer')],
            [sg.HSeparator()],
            [sg.Column([
                [sg.Text('CHARGES', font=('Arial', 12, 'bold'))],
                [sg.Table(values=[], headings=['Compte', 'Montant'],
                         key='table_charges', size=(50, 15))]
            ]), sg.VSeparator(), sg.Column([
                [sg.Text('PRODUITS', font=('Arial', 12, 'bold'))],
                [sg.Table(values=[], headings=['Compte', 'Montant'],
                         key='table_produits', size=(50, 15))]
            ])],
            [sg.HSeparator()],
            [sg.Text('Résultat:'), sg.Text('0,00 €', key='resultat', font=('Arial', 12, 'bold'))],
            [sg.Button('Imprimer'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Compte de Résultat', layout, finalize=True, size=(900, 600))
        
        # Dates par défaut (année en cours)
        current_year = datetime.datetime.now().year
        window['date_debut'].update(f"{current_year}-01-01")
        window['date_fin'].update(f"{current_year}-12-31")
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Générer':
                if not values['date_debut'] or not values['date_fin']:
                    sg.popup_error('Veuillez saisir les dates.')
                    continue
                
                resultat = self.report_manager.generate_profit_loss(
                    values['date_debut'], values['date_fin'])
                self.display_compte_resultat(window, resultat)
        
        window.close()
    
    def display_compte_resultat(self, window, resultat: dict):
        """Affiche le compte de résultat"""
        # Charges
        charges_data = []
        for nom, montant in resultat['charges']:
            charges_data.append([nom, f"{montant:,.2f} €"])
        
        if charges_data:
            charges_data.append(["--- TOTAL CHARGES ---", f"{resultat['total_charges']:,.2f} €"])
        
        # Produits
        produits_data = []
        for nom, montant in resultat['produits']:
            produits_data.append([nom, f"{montant:,.2f} €"])
        
        if produits_data:
            produits_data.append(["--- TOTAL PRODUITS ---", f"{resultat['total_produits']:,.2f} €"])
        
        window['table_charges'].update(charges_data)
        window['table_produits'].update(produits_data)
        
        # Résultat
        resultat_net = resultat['resultat']
        couleur = 'green' if resultat_net >= 0 else 'red'
        type_resultat = 'BÉNÉFICE' if resultat_net >= 0 else 'PERTE'
        
        window['resultat'].update(f"{type_resultat}: {abs(resultat_net):,.2f} €", text_color=couleur)
    
    def show_balance_window(self):
        """Affiche la balance générale"""
        layout = [
            [sg.Text('Balance Générale', font=('Arial', 14, 'bold'))],
            [sg.Text('Date:'), sg.Input(key='date_balance', size=(15, 1),
                                       default_text=datetime.datetime.now().strftime('%Y-%m-%d')),
             sg.Button('Générer'), sg.Button('Exporter CSV')],
            [sg.HSeparator()],
            [sg.Table(values=[], headings=['N° Compte', 'Intitulé', 'Débit', 'Crédit', 'Solde débiteur', 'Solde créditeur'],
                     key='table_balance', size=(120, 25),
                     justification='left')],
            [sg.HSeparator()],
            [sg.Text('Totaux:')],
            [sg.Text('Total débits:'), sg.Text('0,00 €', key='total_debits_balance'),
             sg.Text('Total crédits:'), sg.Text('0,00 €', key='total_credits_balance')],
            [sg.Button('Fermer')]
        ]
        
        window = sg.Window('Balance', layout, finalize=True, size=(1200, 700))
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Générer':
                self.generate_balance(window, values['date_balance'])
            
            elif event == 'Exporter CSV':
                data = window['table_balance'].get()
                if data:
                    headers = ['N° Compte', 'Intitulé', 'Débit', 'Crédit', 'Solde débiteur', 'Solde créditeur']
                    filename = sg.popup_get_file('Nom du fichier', save_as=True, 
                                               default_extension='.csv',
                                               file_types=(('CSV', '*.csv'),))
                    if filename:
                        PrintManager.export_to_csv(data, headers, filename)
        
        window.close()
    
    def generate_balance(self, window, date_balance: str):
        """Génère la balance générale"""
        balance_data = self.db_manager.execute_query('''
            SELECT c.numero, c.nom,
                   COALESCE(SUM(le.debit), 0) as total_debit,
                   COALESCE(SUM(le.credit), 0) as total_credit
            FROM comptes c
            LEFT JOIN lignes_ecriture le ON c.id = le.compte_id
            LEFT JOIN ecritures e ON le.ecriture_id = e.id
            WHERE (e.date_ecriture <= ? OR e.date_ecriture IS NULL)
            AND c.actif = 1
            GROUP BY c.id, c.numero, c.nom
            HAVING total_debit != 0 OR total_credit != 0
            ORDER BY c.numero
        ''', (date_balance,))
        
        table_data = []
        total_debits = 0
        total_credits = 0
        
        for compte in balance_data:
            numero, nom, debit, credit = compte
            solde = debit - credit
            
            solde_debiteur = solde if solde > 0 else 0
            solde_crediteur = abs(solde) if solde < 0 else 0
            
            table_data.append([
                numero, nom,
                f"{debit:,.2f}",
                f"{credit:,.2f}",
                f"{solde_debiteur:,.2f}" if solde_debiteur > 0 else "",
                f"{solde_crediteur:,.2f}" if solde_crediteur > 0 else ""
            ])
            
            total_debits += debit
            total_credits += credit
        
        window['table_balance'].update(table_data)
        window['total_debits_balance'].update(f"{total_debits:,.2f} €")
        window['total_credits_balance'].update(f"{total_credits:,.2f} €")
    
    def show_grand_livre_window(self):
        """Affiche le grand livre"""
        layout = [
            [sg.Text('Grand Livre', font=('Arial', 14, 'bold'))],
            [sg.Text('Compte:'), sg.Combo([], key='compte_grand_livre', size=(50, 1))],
            [sg.Text('Du:'), sg.Input(key='date_debut_gl', size=(12, 1)),
             sg.Text('Au:'), sg.Input(key='date_fin_gl', size=(12, 1)),
             sg.Button('Afficher')],
            [sg.HSeparator()],
            [sg.Text('', key='info_compte', font=('Arial', 12, 'bold'))],
            [sg.Text('Solde initial:'), sg.Text('0,00 €', key='solde_initial')],
            [sg.Table(values=[], headings=['Date', 'N° Écriture', 'Libellé', 'Débit', 'Crédit', 'Solde'],
                     key='table_grand_livre', size=(120, 20),
                     justification='left')],
            [sg.Text('Solde final:'), sg.Text('0,00 €', key='solde_final')],
            [sg.Button('Imprimer'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Grand Livre', layout, finalize=True, size=(1000, 600))
        
        # Charger la liste des comptes
        comptes = self.db_manager.execute_query('''
            SELECT id, numero || ' - ' || nom FROM comptes 
            WHERE actif = 1 ORDER BY numero
        ''')
        
        compte_list = []
        compte_map = {}
        for compte_id, compte_nom in comptes:
            compte_list.append(compte_nom)
            compte_map[compte_nom] = compte_id
        
        window['compte_grand_livre'].update(values=compte_list)
        
        # Dates par défaut
        current_year = datetime.datetime.now().year
        window['date_debut_gl'].update(f"{current_year}-01-01")
        window['date_fin_gl'].update(f"{current_year}-12-31")
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Afficher':
                if not values['compte_grand_livre']:
                    sg.popup_error('Veuillez sélectionner un compte.')
                    continue
                
                compte_id = compte_map[values['compte_grand_livre']]
                grand_livre = self.report_manager.generate_grand_livre(
                    compte_id, values['date_debut_gl'], values['date_fin_gl'])
                
                if grand_livre:
                    self.display_grand_livre(window, grand_livre)
        
        window.close()
    
    def display_grand_livre(self, window, grand_livre: dict):
        """Affiche les données du grand livre"""
        window['info_compte'].update(f"Compte: {grand_livre['compte'][0]} - {grand_livre['compte'][1]}")
        window['solde_initial'].update(f"{grand_livre['solde_initial']:,.2f} €")
        
        table_data = []
        for mouvement in grand_livre['mouvements']:
            date_ecr, numero, libelle, debit, credit, solde = mouvement
            table_data.append([
                date_ecr, numero, libelle,
                f"{debit:,.2f}" if debit > 0 else "",
                f"{credit:,.2f}" if credit > 0 else "",
                f"{solde:,.2f}"
            ])
        
        window['table_grand_livre'].update(table_data)
        window['solde_final'].update(f"{grand_livre['solde_final']:,.2f} €")
    
    def show_configuration_window(self):
        """Affiche la fenêtre de configuration"""
        layout = [
            [sg.Text('Configuration', font=('Arial', 14, 'bold'))],
            [sg.HSeparator()],
            [sg.Frame('Informations entreprise', [
                [sg.Text('Nom:'), sg.Input(key='entreprise_nom', size=(40, 1))],
                [sg.Text('Adresse:'), sg.Input(key='entreprise_adresse', size=(50, 1))],
                [sg.Text('Ville:'), sg.Input(key='entreprise_ville', size=(30, 1))],
                [sg.Text('Téléphone:'), sg.Input(key='entreprise_telephone', size=(20, 1))],
                [sg.Text('Email:'), sg.Input(key='entreprise_email', size=(30, 1))],
                [sg.Text('SIRET:'), sg.Input(key='entreprise_siret', size=(20, 1))],
                [sg.Text('N° TVA:'), sg.Input(key='tva_numero', size=(20, 1))]
            ])],
            [sg.Frame('Paramètres comptables', [
                [sg.Text('Début d\'exercice:'), sg.Input(key='exercice_debut', size=(15, 1))],
                [sg.Text('Fin d\'exercice:'), sg.Input(key='exercice_fin', size=(15, 1))],
                [sg.Text('Devise:'), sg.Input(key='devise', size=(10, 1))]
            ])],
            [sg.HSeparator()],
            [sg.Button('Enregistrer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window('Configuration', layout, finalize=True)
        
        # Charger les paramètres existants
        self.load_configuration(window)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Enregistrer':
                if self.save_configuration(values):
                    sg.popup('Configuration sauvegardée.')
                    break
        
        window.close()
    
    def load_configuration(self, window):
        """Charge la configuration existante"""
        parametres = self.db_manager.execute_query('SELECT cle, valeur FROM parametres')
        
        param_dict = {}
        for cle, valeur in parametres:
            param_dict[cle] = valeur
        
        # Mise à jour des champs
        for cle, valeur in param_dict.items():
            if cle in window.AllKeysDict:
                window[cle].update(valeur)
    
    def save_configuration(self, values: dict) -> bool:
        """Sauvegarde la configuration"""
        try:
            for cle, valeur in values.items():
                if valeur:  # Ne pas sauvegarder les valeurs vides
                    self.db_manager.execute_update('''
                        INSERT OR REPLACE INTO parametres (cle, valeur) VALUES (?, ?)
                    ''', (cle, valeur))
            return True
        except Exception as e:
            sg.popup_error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def show_users_window(self):
        """Affiche la fenêtre de gestion des utilisateurs"""
        if self.auth_manager.current_user['role'] != 'admin':
            sg.popup_error('Accès réservé aux administrateurs.')
            return
        
        layout = [
            [sg.Text('Gestion des Utilisateurs', font=('Arial', 14, 'bold'))],
            [sg.HSeparator()],
            [sg.Table(values=[], headings=['ID', 'Nom d\'utilisateur', 'Nom', 'Prénom', 'Rôle', 'Actif', 'Dernière connexion'],
                     key='table_users', size=(120, 15),
                     justification='left', enable_events=True)],
            [sg.Button('Ajouter'), sg.Button('Modifier'), sg.Button('Désactiver'), 
             sg.Button('Actualiser'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Utilisateurs', layout, finalize=True, size=(1000, 500))
        
        self.refresh_users_window(window)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Actualiser':
                self.refresh_users_window(window)
            
            elif event == 'Ajouter':
                if self.show_create_user_window():
                    self.refresh_users_window(window)
        
        window.close()
    
    def refresh_users_window(self, window):
        """Actualise la liste des utilisateurs"""
        users = self.db_manager.execute_query('''
            SELECT id, nom_utilisateur, nom, prenom, role, 
                   CASE WHEN actif = 1 THEN 'Oui' ELSE 'Non' END,
                   COALESCE(derniere_connexion, 'Jamais')
            FROM utilisateurs
            ORDER BY nom, prenom
        ''')
        
        window['table_users'].update(users or [])
    
    def show_themes_window(self):
        """Affiche la fenêtre de sélection des thèmes"""
        layout = [
            [sg.Text('Sélection du thème', font=('Arial', 12, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Thème actuel:'), sg.Text(sg.theme(), key='current_theme')],
            [sg.Text('Nouveau thème:'), sg.Combo(THEMES, key='new_theme', size=(20, 1))],
            [sg.Button('Aperçu'), sg.Button('Appliquer'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Thèmes', layout, finalize=True)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Aperçu':
                if values['new_theme']:
                    sg.theme(values['new_theme'])
                    sg.popup(f'Aperçu du thème: {values["new_theme"]}', title='Aperçu')
            
            elif event == 'Appliquer':
                if values['new_theme']:
                    sg.theme(values['new_theme'])
                    self.config['theme'] = values['new_theme']
                    ConfigManager.save_config(self.config)
                    
                    # Sauvegarder aussi en base
                    self.db_manager.execute_update('''
                        INSERT OR REPLACE INTO parametres (cle, valeur) VALUES ('theme', ?)
                    ''', (values['new_theme'],))
                    
                    sg.popup('Thème appliqué. Redémarrez l\'application pour une prise en compte complète.')
                    break
        
        window.close()
    
    def show_about_window(self):
        """Affiche la fenêtre À propos"""
        layout = [
            [sg.Text(APP_NAME, font=('Arial', 16, 'bold'), justification='center')],
            [sg.Text(f'Version {APP_VERSION}', justification='center')],
            [sg.HSeparator()],
            [sg.Text('Système de comptabilité avancée développé avec PySimpleGUI4')],
            [sg.Text('Fonctionnalités:', font=('Arial', 10, 'bold'))],
            [sg.Text('• Plan comptable complet')],
            [sg.Text('• Écritures comptables')],
            [sg.Text('• Gestion des tiers (clients/fournisseurs)')],
            [sg.Text('• Facturation')],
            [sg.Text('• États comptables (bilan, compte de résultat, balance, grand livre)')],
            [sg.Text('• Rapprochement bancaire')],
            [sg.Text('• Gestion des immobilisations')],
            [sg.Text('• Budgets prévisionnels')],
            [sg.Text('• Sauvegardes automatiques')],
            [sg.Text('• Multi-utilisateurs avec authentification')],
            [sg.Text('• Interface personnalisable (thèmes)')],
            [sg.HSeparator()],
            [sg.Text('© 2024 - Système de Comptabilité Avancée')],
            [sg.Button('Fermer')]
        ]
        
        window = sg.Window('À propos', layout, finalize=True, element_justification='center')
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
        
        window.close()
    
    def show_nouvelle_ecriture_window(self):
        """Raccourci pour nouvelle écriture"""
        if self.show_ecriture_form_window():
            sg.popup('Écriture créée avec succès.')
    
    def show_nouvelle_facture_window(self):
        """Raccourci pour nouvelle facture"""
        if self.show_facture_form_window():
            sg.popup('Facture créée avec succès.')
    
    def show_nouveau_client_window(self):
        """Raccourci pour nouveau client"""
        if self.show_client_form_window():
            sg.popup('Client créé avec succès.')
    
    def show_nouveau_fournisseur_window(self):
        """Raccourci pour nouveau fournisseur"""
        if self.show_fournisseur_form_window():
            sg.popup('Fournisseur créé avec succès.')
    
    def print_bilan(self, date_bilan: str):
        """Imprime le bilan"""
        bilan = self.report_manager.generate_balance_sheet(date_bilan)
        
        content = f"BILAN COMPTABLE au {date_bilan}\n\n"
        content += "ACTIF\n"
        content += "=" * 50 + "\n"
        
        for categorie, comptes in bilan['actifs'].items():
            if comptes:
                content += f"\n{categorie}:\n"
                for nom, solde in comptes:
                    content += f"  {nom:<40} {solde:>12,.2f} €\n"
        
        content += "\n\nPASSIF\n"
        content += "=" * 50 + "\n"
        
        for categorie, comptes in bilan['passifs'].items():
            if comptes:
                content += f"\n{categorie}:\n"
                for nom, solde in comptes:
                    content += f"  {nom:<40} {solde:>12,.2f} €\n"
        
        PrintManager.print_report(f"Bilan au {date_bilan}", content)

class CalculatorWindow:
    """Calculatrice intégrée"""
    
    @staticmethod
    def show():
        layout = [
            [sg.Text('Calculatrice', font=('Arial', 12, 'bold'))],
            [sg.Input('0', key='display', size=(20, 1), justification='right', 
                     font=('Arial', 14), readonly=True)],
            [sg.Button('C', size=(4, 2)), sg.Button('CE', size=(4, 2)), 
             sg.Button('±', size=(4, 2)), sg.Button('/', size=(4, 2))],
            [sg.Button('7', size=(4, 2)), sg.Button('8', size=(4, 2)), 
             sg.Button('9', size=(4, 2)), sg.Button('*', size=(4, 2))],
            [sg.Button('4', size=(4, 2)), sg.Button('5', size=(4, 2)), 
             sg.Button('6', size=(4, 2)), sg.Button('-', size=(4, 2))],
            [sg.Button('1', size=(4, 2)), sg.Button('2', size=(4, 2)), 
             sg.Button('3', size=(4, 2)), sg.Button('+', size=(4, 2))],
            [sg.Button('0', size=(8, 2)), sg.Button('.', size=(4, 2)), 
             sg.Button('=', size=(4, 2))],
            [sg.Button('Fermer')]
        ]
        
        window = sg.Window('Calculatrice', layout, finalize=True)
        
        current_number = "0"
        previous_number = ""
        operation = ""
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event in '0123456789':
                if current_number == "0":
                    current_number = event
                else:
                    current_number += event
                window['display'].update(current_number)
            
            elif event == '.':
                if '.' not in current_number:
                    current_number += '.'
                    window['display'].update(current_number)
            
            elif event in '+-*/':
                previous_number = current_number
                current_number = "0"
                operation = event
                window['display'].update(f"{previous_number} {operation}")
            
            elif event == '=':
                if previous_number and operation:
                    try:
                        if operation == '+':
                            result = float(previous_number) + float(current_number)
                        elif operation == '-':
                            result = float(previous_number) - float(current_number)
                        elif operation == '*':
                            result = float(previous_number) * float(current_number)
                        elif operation == '/':
                            if float(current_number) != 0:
                                result = float(previous_number) / float(current_number)
                            else:
                                result = "Erreur"
                        
                        if isinstance(result, float):
                            current_number = str(result)
                        else:
                            current_number = str(result)
                        
                        window['display'].update(current_number)
                        previous_number = ""
                        operation = ""
                        
                    except Exception:
                        window['display'].update("Erreur")
                        current_number = "0"
            
            elif event == 'C':
                current_number = "0"
                previous_number = ""
                operation = ""
                window['display'].update(current_number)
            
            elif event == 'CE':
                current_number = "0"
                window['display'].update(current_number)
            
            elif event == '±':
                if current_number != "0":
                    if current_number.startswith('-'):
                        current_number = current_number[1:]
                    else:
                        current_number = '-' + current_number
                    window['display'].update(current_number)
        
        window.close()

class CurrencyConverter:
    """Convertisseur de devises (simplifié)"""
    
    # Taux de change fictifs pour la démonstration
    EXCHANGE_RATES = {
        'EUR': 1.0,
        'USD': 1.1,
        'GBP': 0.85,
        'CHF': 1.05,
        'JPY': 130.0,
        'CAD': 1.35
    }
    
    @staticmethod
    def show():
        currencies = list(CurrencyConverter.EXCHANGE_RATES.keys())
        
        layout = [
            [sg.Text('Convertisseur de Devises', font=('Arial', 12, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Montant:'), sg.Input(key='amount', size=(15, 1))],
            [sg.Text('De:'), sg.Combo(currencies, key='from_currency', default_value='EUR', size=(10, 1))],
            [sg.Text('Vers:'), sg.Combo(currencies, key='to_currency', default_value='USD', size=(10, 1))],
            [sg.Button('Convertir')],
            [sg.HSeparator()],
            [sg.Text('Résultat:'), sg.Text('', key='result', font=('Arial', 12, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Note: Taux de change fictifs pour démonstration', font=('Arial', 8))],
            [sg.Button('Fermer')]
        ]
        
        window = sg.Window('Convertisseur', layout, finalize=True)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Convertir':
                try:
                    amount = float(values['amount'])
                    from_curr = values['from_currency']
                    to_curr = values['to_currency']
                    
                    # Conversion via EUR comme référence
                    eur_amount = amount / CurrencyConverter.EXCHANGE_RATES[from_curr]
                    result = eur_amount * CurrencyConverter.EXCHANGE_RATES[to_curr]
                    
                    window['result'].update(f"{result:.2f} {to_curr}")
                    
                except ValueError:
                    sg.popup_error('Montant invalide')
                except Exception as e:
                    sg.popup_error(f'Erreur: {e}')
        
        window.close()

# Extensions de fonctionnalités supplémentaires

class ImmobilisationManager:
    """Gestionnaire des immobilisations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def show_immobilisations_window(self):
        """Affiche la fenêtre de gestion des immobilisations"""
        layout = [
            [sg.Text('Gestion des Immobilisations', font=('Arial', 14, 'bold'))],
            [sg.HSeparator()],
            [sg.Table(values=[], headings=['ID', 'Nom', 'Valeur acquisition', 'Date acquisition', 
                                         'Durée amort.', 'Amort. cumulé', 'VNC', 'Statut'],
                     key='table_immobilisations', size=(120, 15),
                     justification='left', enable_events=True)],
            [sg.Button('Ajouter'), sg.Button('Modifier'), sg.Button('Calculer amortissements'), 
             sg.Button('Céder'), sg.Button('Actualiser'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Immobilisations', layout, finalize=True, size=(1000, 600))
        
        self.refresh_immobilisations_window(window)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Actualiser':
                self.refresh_immobilisations_window(window)
            
            elif event == 'Ajouter':
                if self.show_immobilisation_form():
                    self.refresh_immobilisations_window(window)
            
            elif event == 'Calculer amortissements':
                self.calculer_amortissements()
                self.refresh_immobilisations_window(window)
        
        window.close()
    
    def refresh_immobilisations_window(self, window):
        """Actualise la liste des immobilisations"""
        immobilisations = self.db_manager.execute_query('''
            SELECT i.id, i.nom, i.valeur_acquisition, i.date_acquisition,
                   i.duree_amortissement, i.amortissement_cumule,
                   (i.valeur_acquisition - i.amortissement_cumule) as vnc,
                   i.statut
            FROM immobilisations i
            ORDER BY i.date_acquisition DESC
        ''')
        
        table_data = []
        for immo in immobilisations:
            id_immo, nom, valeur, date_acq, duree, amort_cumule, vnc, statut = immo
            table_data.append([
                id_immo, nom, f"{valeur:,.2f} €", date_acq,
                f"{duree} ans", f"{amort_cumule:,.2f} €", 
                f"{vnc:,.2f} €", statut
            ])
        
        window['table_immobilisations'].update(table_data)
    
    def show_immobilisation_form(self, immo_id: int = None) -> bool:
        """Formulaire d'immobilisation"""
        title = 'Modifier l\'immobilisation' if immo_id else 'Nouvelle immobilisation'
        
        layout = [
            [sg.Text(title, font=('Arial', 12, 'bold'))],
            [sg.Text('Nom:'), sg.Input(key='nom', size=(40, 1))],
            [sg.Text('Compte:'), sg.Combo([], key='compte', size=(40, 1))],
            [sg.Text('Valeur d\'acquisition:'), sg.Input(key='valeur_acquisition', size=(15, 1))],
            [sg.Text('Date d\'acquisition:'), sg.Input(key='date_acquisition', size=(15, 1),
                                                     default_text=datetime.datetime.now().strftime('%Y-%m-%d'))],
            [sg.Text('Durée d\'amortissement (années):'), sg.Input(key='duree_amortissement', size=(10, 1))],
            [sg.Text('Méthode:'), sg.Combo(['lineaire', 'degressive'], 
                                          default_value='lineaire', key='methode_amortissement')],
            [sg.Text('Valeur résiduelle:'), sg.Input(key='valeur_residuelle', size=(15, 1), default_text='0')],
            [sg.Button('Enregistrer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window(title, layout, finalize=True)
        
        # Charger les comptes d'immobilisation
        comptes = self.db_manager.execute_query('''
            SELECT id, numero || ' - ' || nom FROM comptes 
            WHERE numero LIKE '2%' AND actif = 1 ORDER BY numero
        ''')
        
        compte_list = []
        compte_map = {}
        for compte_id, compte_nom in comptes:
            compte_list.append(compte_nom)
            compte_map[compte_nom] = compte_id
        
        window['compte'].update(values=compte_list)
        
        result = False
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Enregistrer':
                if not all([values['nom'], values['compte'], values['valeur_acquisition'], 
                           values['duree_amortissement']]):
                    sg.popup_error('Veuillez remplir tous les champs obligatoires.')
                    continue
                
                try:
                    valeur_acquisition = float(values['valeur_acquisition'])
                    duree_amortissement = int(values['duree_amortissement'])
                    valeur_residuelle = float(values['valeur_residuelle'] or 0)
                    
                    compte_id = compte_map[values['compte']]
                    
                    success = self.db_manager.execute_update('''
                        INSERT INTO immobilisations 
                        (nom, compte_id, valeur_acquisition, date_acquisition, 
                         duree_amortissement, methode_amortissement, valeur_residuelle)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (values['nom'], compte_id, valeur_acquisition, values['date_acquisition'],
                          duree_amortissement, values['methode_amortissement'], valeur_residuelle))
                    
                    if success:
                        sg.popup('Immobilisation enregistrée avec succès.')
                        result = True
                        break
                    
                except ValueError:
                    sg.popup_error('Valeurs numériques invalides.')
        
        window.close()
        return result
    
    def calculer_amortissements(self):
        """Calcule les amortissements automatiquement"""
        immobilisations = self.db_manager.execute_query('''
            SELECT id, valeur_acquisition, date_acquisition, duree_amortissement, 
                   methode_amortissement, valeur_residuelle, amortissement_cumule
            FROM immobilisations
            WHERE statut = 'actif'
        ''')
        
        date_actuelle = datetime.datetime.now().date()
        annee_actuelle = date_actuelle.year
        
        for immo in immobilisations:
            (id_immo, valeur_acq, date_acq_str, duree, methode, 
             valeur_res, amort_cumule) = immo
            
            date_acq = datetime.datetime.strptime(date_acq_str, '%Y-%m-%d').date()
            
            # Calcul de l'âge en années
            age_annees = (date_actuelle - date_acq).days / 365.25
            
            if age_annees < duree:
                # Calcul de l'amortissement selon la méthode
                if methode == 'lineaire':
                    amort_annuel = (valeur_acq - valeur_res) / duree
                    nouvel_amort_cumule = min(amort_annuel * age_annees, valeur_acq - valeur_res)
                else:  # degressive
                    # Simplification pour la méthode dégressive
                    taux = 2 / duree  # Taux dégressif
                    nouvel_amort_cumule = valeur_acq * (1 - (1 - taux) ** age_annees)
                    nouvel_amort_cumule = min(nouvel_amort_cumule, valeur_acq - valeur_res)
                
                # Mise à jour si nécessaire
                if abs(nouvel_amort_cumule - amort_cumule) > 0.01:
                    self.db_manager.execute_update('''
                        UPDATE immobilisations 
                        SET amortissement_cumule = ? 
                        WHERE id = ?
                    ''', (nouvel_amort_cumule, id_immo))
        
        sg.popup('Amortissements calculés et mis à jour.')

class BudgetManager:
    """Gestionnaire des budgets"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def show_budgets_window(self):
        """Affiche la fenêtre de gestion des budgets"""
        layout = [
            [sg.Text('Gestion des Budgets', font=('Arial', 14, 'bold'))],
            [sg.Text('Année:'), sg.Combo(list(range(2020, 2030)), 
                                        default_value=datetime.datetime.now().year, 
                                        key='annee_budget'),
             sg.Button('Filtrer')],
            [sg.HSeparator()],
            [sg.Table(values=[], headings=['ID', 'Nom', 'Compte', 'Prévisionnel', 'Réalisé', 'Écart', '%'],
                     key='table_budgets', size=(120, 15),
                     justification='left')],
            [sg.Button('Nouveau budget'), sg.Button('Modifier'), sg.Button('Actualiser réalisé'), 
             sg.Button('Rapport'), sg.Button('Fermer')]
        ]
        
        window = sg.Window('Budgets', layout, finalize=True, size=(1000, 600))
        
        self.refresh_budgets_window(window, datetime.datetime.now().year)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Fermer'):
                break
            
            elif event == 'Filtrer':
                self.refresh_budgets_window(window, values['annee_budget'])
            
            elif event == 'Nouveau budget':
                if self.show_budget_form(values['annee_budget']):
                    self.refresh_budgets_window(window, values['annee_budget'])
            
            elif event == 'Actualiser réalisé':
                self.actualiser_budgets_realises(values['annee_budget'])
                self.refresh_budgets_window(window, values['annee_budget'])
        
        window.close()
    
    def refresh_budgets_window(self, window, annee: int):
        """Actualise les données des budgets"""
        budgets = self.db_manager.execute_query('''
            SELECT b.id, b.nom, c.numero || ' - ' || c.nom,
                   b.montant_previsionnel, b.montant_realise,
                   (b.montant_realise - b.montant_previsionnel) as ecart,
                   CASE WHEN b.montant_previsionnel != 0 
                        THEN (b.montant_realise * 100.0 / b.montant_previsionnel)
                        ELSE 0 END as pourcentage
            FROM budgets b
            JOIN comptes c ON b.compte_id = c.id
            WHERE b.annee = ?
            ORDER BY b.nom
        ''', (annee,))
        
        table_data = []
        for budget in budgets:
            (id_budget, nom, compte, previsionnel, realise, 
             ecart, pourcentage) = budget
            
            table_data.append([
                id_budget, nom, compte,
                f"{previsionnel:,.2f} €",
                f"{realise:,.2f} €",
                f"{ecart:,.2f} €",
                f"{pourcentage:.1f}%"
            ])
        
        window['table_budgets'].update(table_data)
    
    def show_budget_form(self, annee: int, budget_id: int = None) -> bool:
        """Formulaire de budget"""
        title = 'Modifier le budget' if budget_id else 'Nouveau budget'
        
        layout = [
            [sg.Text(title, font=('Arial', 12, 'bold'))],
            [sg.Text('Nom du budget:'), sg.Input(key='nom', size=(40, 1))],
            [sg.Text('Année:'), sg.Input(key='annee', size=(10, 1), default_text=str(annee))],
            [sg.Text('Compte:'), sg.Combo([], key='compte', size=(50, 1))],
            [sg.Text('Montant prévisionnel:'), sg.Input(key='montant_previsionnel', size=(15, 1))],
            [sg.Text('Notes:'), sg.Multiline(key='notes', size=(50, 5))],
            [sg.Button('Enregistrer'), sg.Button('Annuler')]
        ]
        
        window = sg.Window(title, layout, finalize=True)
        
        # Charger les comptes
        comptes = self.db_manager.execute_query('''
            SELECT id, numero || ' - ' || nom FROM comptes 
            WHERE actif = 1 ORDER BY numero
        ''')
        
        compte_list = []
        compte_map = {}
        for compte_id, compte_nom in comptes:
            compte_list.append(compte_nom)
            compte_map[compte_nom] = compte_id
        
        window['compte'].update(values=compte_list)
        
        result = False
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, 'Annuler'):
                break
            
            elif event == 'Enregistrer':
                if not all([values['nom'], values['compte'], values['montant_previsionnel']]):
                    sg.popup_error('Veuillez remplir tous les champs obligatoires.')
                    continue
                
                try:
                    montant = float(values['montant_previsionnel'])
                    compte_id = compte_map[values['compte']]
                    
                    success = self.db_manager.execute_update('''
                        INSERT INTO budgets (nom, annee, compte_id, montant_previsionnel, notes)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (values['nom'], int(values['annee']), compte_id, montant, values['notes']))
                    
                    if success:
                        sg.popup('Budget enregistré avec succès.')
                        result = True
                        break
                    
                except ValueError:
                    sg.popup_error('Montant invalide.')
        
        window.close()
        return result
    
    def actualiser_budgets_realises(self, annee: int):
        """Met à jour les montants réalisés des budgets"""
        budgets = self.db_manager.execute_query('''
            SELECT id, compte_id FROM budgets WHERE annee = ?
        ''', (annee,))
        
        for budget_id, compte_id in budgets:
            # Calculer le réalisé pour ce compte sur l'année
            realise = self.db_manager.execute_query('''
                SELECT COALESCE(SUM(
                    CASE WHEN c.numero LIKE '6%' THEN le.debit - le.credit
                         WHEN c.numero LIKE '7%' THEN le.credit - le.debit
                         ELSE le.debit - le.credit END
                ), 0)
                FROM lignes_ecriture le
                JOIN ecritures e ON le.ecriture_id = e.id
                JOIN comptes c ON le.compte_id = c.id
                WHERE le.compte_id = ? 
                AND strftime('%Y', e.date_ecriture) = ?
            ''', (compte_id, str(annee)))
            
            montant_realise = realise[0][0] if realise else 0
            
            self.db_manager.execute_update('''
                UPDATE budgets SET montant_realise = ? WHERE id = ?
            ''', (montant_realise, budget_id))
        
        sg.popup('Montants réalisés mis à jour.')

# Point d'entrée principal
def main():
    """Fonction principale"""
    try:
        # Initialisation de l'application
        app = ComptabiliteApp()
        
        # Lancement de l'application
        app.run()
        
    except Exception as e:
        sg.popup_error(f"Erreur fatale: {e}")
        sg.popup_error("L'application va se fermer.")

if __name__ == '__main__':
    main()
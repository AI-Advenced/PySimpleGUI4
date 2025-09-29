#!/usr/bin/env python3
"""
Exemple 05: Gestionnaire de base de données SQLite avec CRUD
Fonctionnalités: Interface CRUD complète, requêtes SQL, import/export, relations
"""

import PySimpleGUI4 as sg
import sqlite3
import os
import csv
import json
import datetime
from pathlib import Path
import pandas as pd

sg.theme('DarkGreen7')

class DatabaseManager:
    def __init__(self):
        self.db_path = None
        self.connection = None
        self.current_table = None
        
    def create_connection(self, db_path):
        """Crée une connexion à la base de données SQLite"""
        try:
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
            self.db_path = db_path
            return True
        except Exception as e:
            sg.popup_error(f'Erreur de connexion: {str(e)}')
            return False
    
    def close_connection(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.db_path = None
    
    def execute_query(self, query, parameters=None, fetch=True):
        """Exécute une requête SQL"""
        try:
            cursor = self.connection.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            if fetch:
                results = cursor.fetchall()
                return results
            else:
                self.connection.commit()
                return cursor.rowcount
        except Exception as e:
            raise Exception(f'Erreur SQL: {str(e)}')
    
    def get_tables(self):
        """Récupère la liste des tables"""
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            results = self.execute_query(query)
            return [row[0] for row in results if not row[0].startswith('sqlite_')]
        except Exception as e:
            print(f"Erreur lors de la récupération des tables: {e}")
            return []
    
    def get_table_info(self, table_name):
        """Récupère les informations sur une table"""
        try:
            query = f"PRAGMA table_info({table_name})"
            results = self.execute_query(query)
            columns = []
            for row in results:
                columns.append({
                    'name': row[1],
                    'type': row[2],
                    'not_null': bool(row[3]),
                    'default': row[4],
                    'primary_key': bool(row[5])
                })
            return columns
        except Exception as e:
            print(f"Erreur lors de la récupération des infos de table: {e}")
            return []
    
    def get_table_data(self, table_name, limit=100, offset=0):
        """Récupère les données d'une table avec pagination"""
        try:
            # Compter le nombre total de lignes
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            total_rows = self.execute_query(count_query)[0][0]
            
            # Récupérer les données avec limite
            query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
            results = self.execute_query(query)
            
            return results, total_rows
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {e}")
            return [], 0
    
    def insert_record(self, table_name, data):
        """Insert un nouvel enregistrement"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_query(query, list(data.values()), fetch=False)
    
    def update_record(self, table_name, data, where_clause, where_params):
        """Met à jour un enregistrement"""
        set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        params = list(data.values()) + where_params
        return self.execute_query(query, params, fetch=False)
    
    def delete_record(self, table_name, where_clause, where_params):
        """Supprime un enregistrement"""
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        return self.execute_query(query, where_params, fetch=False)
    
    def create_table_from_schema(self, table_name, schema):
        """Crée une nouvelle table"""
        column_definitions = []
        for col in schema:
            definition = f"{col['name']} {col['type']}"
            if col.get('primary_key'):
                definition += " PRIMARY KEY"
            if col.get('not_null'):
                definition += " NOT NULL"
            if col.get('default'):
                definition += f" DEFAULT {col['default']}"
            column_definitions.append(definition)
        
        query = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
        return self.execute_query(query, fetch=False)


class DatabaseGUI:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.current_page = 0
        self.page_size = 50
        
    def create_connection_layout(self):
        """Layout pour la connexion à la base de données"""
        layout = [
            [sg.Text('🗃️ Gestionnaire de Base de Données SQLite', font=('Arial', 16, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Base de données:')],
            [sg.Input(key='DB_PATH', size=(50, 1)), 
             sg.FileBrowse('Parcourir', file_types=(('SQLite DB', '*.db'), ('Tous', '*.*'))),
             sg.Button('Nouvelle DB', key='NEW_DB')],
            [sg.Button('Se connecter', key='CONNECT'), 
             sg.Button('Créer Exemple', key='CREATE_SAMPLE')],
            [sg.HSeparator()],
            [sg.Text('Bases de données récentes:')],
            [sg.Listbox([], key='RECENT_DBS', size=(60, 8), enable_events=True)]
        ]
        return layout
    
    def create_main_layout(self):
        """Layout principal de gestion de la base de données"""
        # Panneau des tables
        table_panel = [
            [sg.Text('📋 Tables', font=('Arial', 12, 'bold'))],
            [sg.Listbox([], key='TABLE_LIST', size=(25, 15), enable_events=True)],
            [sg.Button('➕ Nouvelle Table', key='NEW_TABLE'),
             sg.Button('🗑️ Supprimer Table', key='DROP_TABLE')],
            [sg.HSeparator()],
            [sg.Text('🔍 Requête SQL:')],
            [sg.Multiline('', key='SQL_QUERY', size=(25, 8))],
            [sg.Button('▶️ Exécuter', key='EXECUTE_SQL')]
        ]
        
        # Panneau des données
        data_panel = [
            [sg.Text('📊 Données de la table:', font=('Arial', 12, 'bold')),
             sg.Text('', key='CURRENT_TABLE', font=('Arial', 12, 'bold'), text_color='yellow')],
            [sg.Table([], headings=[], key='DATA_TABLE', size=(80, 20),
                     enable_events=True, select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                     alternating_row_color='#2d2d30')],
            [sg.Text('Page:'), sg.Text('1', key='PAGE_INFO'),
             sg.Button('⬅️ Précédent', key='PREV_PAGE'),
             sg.Button('➡️ Suivant', key='NEXT_PAGE'),
             sg.Text('Lignes par page:'), 
             sg.Combo([25, 50, 100, 200], default_value=50, key='PAGE_SIZE', enable_events=True)],
            [sg.Button('➕ Ajouter', key='ADD_RECORD'),
             sg.Button('✏️ Modifier', key='EDIT_RECORD'),
             sg.Button('🗑️ Supprimer', key='DELETE_RECORD'),
             sg.Button('🔄 Actualiser', key='REFRESH_DATA')]
        ]
        
        # Panneau d'informations sur la table
        info_panel = [
            [sg.Text('ℹ️ Structure de la table', font=('Arial', 12, 'bold'))],
            [sg.Table([], headings=['Colonne', 'Type', 'Null', 'Défaut', 'Clé'],
                     key='STRUCTURE_TABLE', size=(40, 10))],
            [sg.HSeparator()],
            [sg.Text('📈 Statistiques')],
            [sg.Text('Nombre de lignes:'), sg.Text('0', key='ROW_COUNT')],
            [sg.Text('Taille de la table:'), sg.Text('0 KB', key='TABLE_SIZE')],
            [sg.HSeparator()],
            [sg.Button('📤 Exporter CSV', key='EXPORT_CSV'),
             sg.Button('📥 Importer CSV', key='IMPORT_CSV')],
            [sg.Button('💾 Sauvegarder', key='SAVE_DB'),
             sg.Button('📋 Copier Structure', key='COPY_STRUCTURE')]
        ]
        
        layout = [
            [sg.Text(f'Base de données: {self.db_manager.db_path}', key='DB_INFO')],
            [sg.HSeparator()],
            [sg.Column(table_panel), sg.VSeparator(),
             sg.Column(data_panel), sg.VSeparator(),
             sg.Column(info_panel)],
            [sg.HSeparator()],
            [sg.Button('🔌 Déconnecter', key='DISCONNECT'),
             sg.Button('🔄 Actualiser Tables', key='REFRESH_TABLES'),
             sg.StatusBar('Connecté', key='STATUS')]
        ]
        
        return layout
    
    def create_record_form(self, columns, record_data=None, mode='add'):
        """Crée un formulaire pour ajouter/modifier un enregistrement"""
        layout = [
            [sg.Text(f'{"✏️ Modifier" if mode == "edit" else "➕ Ajouter"} un enregistrement', 
                    font=('Arial', 14, 'bold'))]
        ]
        
        for col in columns:
            default_value = ''
            if record_data and col['name'] in record_data:
                default_value = str(record_data[col['name']]) if record_data[col['name']] is not None else ''
            
            # Déterminer le type d'input selon le type de colonne
            if col['type'].upper() in ['TEXT', 'VARCHAR', 'CHAR']:
                input_element = sg.Input(default_value, key=f"COL_{col['name']}", size=(40, 1))
            elif col['type'].upper() in ['INTEGER', 'INT']:
                input_element = sg.Input(default_value, key=f"COL_{col['name']}", size=(20, 1))
            elif col['type'].upper() in ['REAL', 'FLOAT', 'DOUBLE']:
                input_element = sg.Input(default_value, key=f"COL_{col['name']}", size=(20, 1))
            elif col['type'].upper() == 'BOOLEAN':
                input_element = sg.Checkbox('True', default=default_value.lower() == 'true' if default_value else False,
                                          key=f"COL_{col['name']}")
            elif col['type'].upper() in ['DATE', 'DATETIME', 'TIMESTAMP']:
                input_element = sg.Input(default_value or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                       key=f"COL_{col['name']}", size=(30, 1))
            else:
                input_element = sg.Multiline(default_value, key=f"COL_{col['name']}", size=(40, 3))
            
            # Marquer les champs obligatoires
            required = " *" if col['not_null'] else ""
            layout.append([
                sg.Text(f"{col['name']} ({col['type']}){required}:", size=(20, 1)),
                input_element
            ])
        
        layout.extend([
            [sg.HSeparator()],
            [sg.Button('💾 Sauvegarder', key='SAVE_RECORD'),
             sg.Button('❌ Annuler', key='CANCEL_FORM')]
        ])
        
        return layout
    
    def create_table_designer(self):
        """Interface de création de table"""
        layout = [
            [sg.Text('🛠️ Créateur de Table', font=('Arial', 16, 'bold'))],
            [sg.Text('Nom de la table:'), sg.Input(key='NEW_TABLE_NAME', size=(30, 1))],
            [sg.HSeparator()],
            [sg.Text('Colonnes:')],
            [sg.Table([], headings=['Nom', 'Type', 'Clé primaire', 'Non null', 'Défaut'],
                     key='COLUMN_TABLE', size=(80, 15))],
            [sg.Text('Nom colonne:'), sg.Input(key='COL_NAME', size=(15, 1)),
             sg.Text('Type:'), sg.Combo(['TEXT', 'INTEGER', 'REAL', 'BOOLEAN', 'DATE', 'BLOB'], 
                                       key='COL_TYPE', size=(10, 1)),
             sg.Checkbox('Clé primaire', key='COL_PK'),
             sg.Checkbox('Non null', key='COL_NN'),
             sg.Text('Défaut:'), sg.Input(key='COL_DEFAULT', size=(10, 1)),
             sg.Button('➕ Ajouter Colonne', key='ADD_COLUMN')],
            [sg.Button('🗑️ Supprimer Colonne', key='REMOVE_COLUMN'),
             sg.Button('⬆️ Monter', key='MOVE_UP'),
             sg.Button('⬇️ Descendre', key='MOVE_DOWN')],
            [sg.HSeparator()],
            [sg.Button('✅ Créer Table', key='CREATE_TABLE'),
             sg.Button('❌ Annuler', key='CANCEL_TABLE')]
        ]
        
        return layout
    
    def load_table_data(self, window, table_name):
        """Charge les données d'une table"""
        try:
            # Récupérer les informations de structure
            columns = self.db_manager.get_table_info(table_name)
            if not columns:
                return
            
            # Récupérer les données avec pagination
            data, total_rows = self.db_manager.get_table_data(
                table_name, self.page_size, self.current_page * self.page_size
            )
            
            # Préparer les en-têtes et données pour le tableau
            headings = [col['name'] for col in columns]
            table_data = []
            
            for row in data:
                table_data.append([str(row[col]) if row[col] is not None else '' for col in headings])
            
            # Mettre à jour l'interface
            window['DATA_TABLE'].update(values=table_data, num_rows=len(table_data))
            window['DATA_TABLE'].Widget.config(show='headings')  # Afficher les en-têtes
            
            # Configurer les en-têtes
            for i, heading in enumerate(headings):
                window['DATA_TABLE'].Widget.heading(f'#{i+1}', text=heading)
            
            # Mettre à jour les informations
            window['CURRENT_TABLE'].update(table_name)
            window['ROW_COUNT'].update(str(total_rows))
            
            # Structure de la table
            structure_data = []
            for col in columns:
                structure_data.append([
                    col['name'],
                    col['type'],
                    'Non' if col['not_null'] else 'Oui',
                    str(col['default']) if col['default'] else '',
                    'Oui' if col['primary_key'] else 'Non'
                ])
            window['STRUCTURE_TABLE'].update(values=structure_data)
            
            # Informations de pagination
            total_pages = (total_rows + self.page_size - 1) // self.page_size
            current_page_display = self.current_page + 1
            window['PAGE_INFO'].update(f'{current_page_display} / {max(1, total_pages)}')
            
            self.db_manager.current_table = table_name
            
        except Exception as e:
            sg.popup_error(f'Erreur lors du chargement des données: {str(e)}')
    
    def create_sample_database(self):
        """Crée une base de données d'exemple"""
        db_path = sg.popup_get_file('Créer une nouvelle base de données', save_as=True,
                                   file_types=(('SQLite DB', '*.db'),))
        if not db_path:
            return False
        
        # Supprimer le fichier s'il existe
        if os.path.exists(db_path):
            os.remove(db_path)
        
        try:
            # Se connecter à la nouvelle base
            if not self.db_manager.create_connection(db_path):
                return False
            
            # Créer des tables d'exemple
            # Table utilisateurs
            users_query = """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
            """
            self.db_manager.execute_query(users_query, fetch=False)
            
            # Table produits
            products_query = """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT,
                description TEXT,
                stock INTEGER DEFAULT 0
            )
            """
            self.db_manager.execute_query(products_query, fetch=False)
            
            # Table commandes
            orders_query = """
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_price REAL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            """
            self.db_manager.execute_query(orders_query, fetch=False)
            
            # Insérer des données d'exemple
            sample_users = [
                ('alice', 'alice@example.com'),
                ('bob', 'bob@example.com'),
                ('charlie', 'charlie@example.com')
            ]
            
            for username, email in sample_users:
                self.db_manager.execute_query(
                    "INSERT INTO users (username, email) VALUES (?, ?)",
                    (username, email), fetch=False
                )
            
            sample_products = [
                ('Ordinateur portable', 999.99, 'Électronique', 'PC portable haute performance', 10),
                ('Souris sans fil', 29.99, 'Accessoires', 'Souris ergonomique', 50),
                ('Clavier mécanique', 149.99, 'Accessoires', 'Clavier gaming RGB', 25)
            ]
            
            for name, price, category, description, stock in sample_products:
                self.db_manager.execute_query(
                    "INSERT INTO products (name, price, category, description, stock) VALUES (?, ?, ?, ?, ?)",
                    (name, price, category, description, stock), fetch=False
                )
            
            sg.popup('Base de données d\'exemple créée avec succès!')
            return True
            
        except Exception as e:
            sg.popup_error(f'Erreur lors de la création: {str(e)}')
            return False
    
    def export_to_csv(self, table_name):
        """Exporte une table vers CSV"""
        if not table_name:
            sg.popup_error('Aucune table sélectionnée')
            return
        
        filename = sg.popup_get_file('Exporter vers CSV', save_as=True,
                                   file_types=(('CSV', '*.csv'),))
        if not filename:
            return
        
        try:
            # Récupérer toutes les données
            query = f"SELECT * FROM {table_name}"
            data = self.db_manager.execute_query(query)
            
            if not data:
                sg.popup('Aucune donnée à exporter')
                return
            
            # Récupérer les noms de colonnes
            columns = self.db_manager.get_table_info(table_name)
            column_names = [col['name'] for col in columns]
            
            # Écrire le CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(column_names)
                
                for row in data:
                    writer.writerow([row[col] for col in column_names])
            
            sg.popup(f'Données exportées vers {filename}')
            
        except Exception as e:
            sg.popup_error(f'Erreur lors de l\'export: {str(e)}')
    
    def run(self):
        # Fenêtre de connexion
        connection_window = sg.Window('Connexion Base de Données', 
                                    self.create_connection_layout(), finalize=True)
        
        while True:
            event, values = connection_window.read()
            
            if event == sg.WIN_CLOSED:
                connection_window.close()
                return
            
            elif event == 'CONNECT':
                db_path = values['DB_PATH']
                if db_path and os.path.exists(db_path):
                    if self.db_manager.create_connection(db_path):
                        connection_window.close()
                        self.run_main_interface()
                        return
                else:
                    sg.popup_error('Fichier de base de données non trouvé')
            
            elif event == 'NEW_DB':
                connection_window.close()
                if self.create_sample_database():
                    self.run_main_interface()
                return
            
            elif event == 'CREATE_SAMPLE':
                connection_window.close()
                if self.create_sample_database():
                    self.run_main_interface()
                return
        
        connection_window.close()
    
    def run_main_interface(self):
        """Interface principale de gestion"""
        window = sg.Window('Gestionnaire de Base de Données', self.create_main_layout(),
                          finalize=True, resizable=True, size=(1400, 800))
        
        # Charger la liste des tables
        tables = self.db_manager.get_tables()
        window['TABLE_LIST'].update(tables)
        window['DB_INFO'].update(f'Base de données: {self.db_manager.db_path}')
        
        while True:
            event, values = window.read()
            
            if event == sg.WIN_CLOSED or event == 'DISCONNECT':
                self.db_manager.close_connection()
                break
            
            elif event == 'TABLE_LIST':
                if values['TABLE_LIST']:
                    selected_table = values['TABLE_LIST'][0]
                    self.current_page = 0
                    self.load_table_data(window, selected_table)
            
            elif event == 'PAGE_SIZE':
                self.page_size = values['PAGE_SIZE']
                if self.db_manager.current_table:
                    self.current_page = 0
                    self.load_table_data(window, self.db_manager.current_table)
            
            elif event == 'NEXT_PAGE':
                if self.db_manager.current_table:
                    self.current_page += 1
                    self.load_table_data(window, self.db_manager.current_table)
            
            elif event == 'PREV_PAGE':
                if self.db_manager.current_table and self.current_page > 0:
                    self.current_page -= 1
                    self.load_table_data(window, self.db_manager.current_table)
            
            elif event == 'REFRESH_DATA':
                if self.db_manager.current_table:
                    self.load_table_data(window, self.db_manager.current_table)
            
            elif event == 'REFRESH_TABLES':
                tables = self.db_manager.get_tables()
                window['TABLE_LIST'].update(tables)
            
            elif event == 'ADD_RECORD':
                if self.db_manager.current_table:
                    columns = self.db_manager.get_table_info(self.db_manager.current_table)
                    self.show_record_form(columns, mode='add')
                    self.load_table_data(window, self.db_manager.current_table)
            
            elif event == 'EXPORT_CSV':
                if self.db_manager.current_table:
                    self.export_to_csv(self.db_manager.current_table)
            
            elif event == 'EXECUTE_SQL':
                sql_query = values['SQL_QUERY'].strip()
                if sql_query:
                    try:
                        if sql_query.upper().startswith('SELECT'):
                            results = self.db_manager.execute_query(sql_query)
                            # Afficher les résultats dans une nouvelle fenêtre
                            self.show_query_results(results)
                        else:
                            affected_rows = self.db_manager.execute_query(sql_query, fetch=False)
                            sg.popup(f'Requête exécutée. {affected_rows} ligne(s) affectée(s).')
                            # Actualiser les tables
                            tables = self.db_manager.get_tables()
                            window['TABLE_LIST'].update(tables)
                    except Exception as e:
                        sg.popup_error(f'Erreur SQL: {str(e)}')
        
        window.close()
    
    def show_record_form(self, columns, record_data=None, mode='add'):
        """Affiche le formulaire d'ajout/modification d'enregistrement"""
        form_layout = self.create_record_form(columns, record_data, mode)
        form_window = sg.Window(f'{"Modifier" if mode == "edit" else "Ajouter"} Enregistrement',
                               form_layout, modal=True)
        
        while True:
            event, values = form_window.read()
            
            if event == sg.WIN_CLOSED or event == 'CANCEL_FORM':
                break
            
            elif event == 'SAVE_RECORD':
                try:
                    # Préparer les données
                    data = {}
                    for col in columns:
                        key = f"COL_{col['name']}"
                        if key in values:
                            value = values[key]
                            if col['type'].upper() == 'BOOLEAN':
                                value = 1 if value else 0
                            elif value == '':
                                value = None
                            data[col['name']] = value
                    
                    if mode == 'add':
                        self.db_manager.insert_record(self.db_manager.current_table, data)
                        sg.popup('Enregistrement ajouté avec succès!')
                    else:
                        # Pour la modification, il faudrait implémenter la logique de WHERE
                        sg.popup('Fonctionnalité de modification en cours de développement')
                    
                    break
                
                except Exception as e:
                    sg.popup_error(f'Erreur lors de la sauvegarde: {str(e)}')
        
        form_window.close()
    
    def show_query_results(self, results):
        """Affiche les résultats d'une requête SELECT"""
        if not results:
            sg.popup('Aucun résultat')
            return
        
        # Préparer les données pour l'affichage
        headings = list(results[0].keys())
        data = []
        for row in results:
            data.append([str(row[col]) if row[col] is not None else '' for col in headings])
        
        layout = [
            [sg.Text('Résultats de la requête', font=('Arial', 14, 'bold'))],
            [sg.Table(data, headings=headings, size=(100, 20), alternating_row_color='#2d2d30')],
            [sg.Text(f'Nombre de résultats: {len(results)}')],
            [sg.Button('Fermer')]
        ]
        
        results_window = sg.Window('Résultats de la Requête', layout, modal=True, resizable=True)
        
        while True:
            event, values = results_window.read()
            if event == sg.WIN_CLOSED or event == 'Fermer':
                break
        
        results_window.close()

if __name__ == '__main__':
    app = DatabaseGUI()
    app.run()
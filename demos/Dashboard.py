#!/usr/bin/env python3
"""
Exemple 04: Dashboard de monitoring système avec graphiques
Fonctionnalités: Monitoring temps réel, graphiques, alertes, historique
"""

import PySimpleGUI4 as sg
import psutil
import threading
import time
import datetime
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
import base64
from PIL import Image
import json
import os

sg.theme('DarkBlue')

class SystemMonitor:
    def __init__(self):
        self.monitoring = False
        self.data_history = {
            'cpu': deque(maxlen=100),
            'memory': deque(maxlen=100),
            'disk': deque(maxlen=100),
            'network_sent': deque(maxlen=100),
            'network_recv': deque(maxlen=100),
            'timestamps': deque(maxlen=100)
        }
        self.alerts = []
        self.alert_thresholds = {
            'cpu': 80.0,
            'memory': 85.0,
            'disk': 90.0
        }
        
        # Configuration matplotlib
        plt.style.use('dark_background')
        
    def get_system_info(self):
        """Récupère les informations système détaillées"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Mémoire
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disque
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Réseau
            network = psutil.net_io_counters()
            
            # Processus
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Trier par utilisation CPU
            processes = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else 0
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': processes,
                'timestamp': datetime.datetime.now()
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des données système: {e}")
            return None
    
    def format_bytes(self, bytes_value):
        """Formate les octets en unités lisibles"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def check_alerts(self, system_data):
        """Vérifie les seuils d'alerte"""
        alerts = []
        timestamp = system_data['timestamp']
        
        # Alerte CPU
        if system_data['cpu']['percent'] > self.alert_thresholds['cpu']:
            alerts.append({
                'type': 'cpu',
                'message': f"Utilisation CPU élevée: {system_data['cpu']['percent']:.1f}%",
                'timestamp': timestamp,
                'severity': 'warning' if system_data['cpu']['percent'] < 95 else 'critical'
            })
        
        # Alerte mémoire
        if system_data['memory']['percent'] > self.alert_thresholds['memory']:
            alerts.append({
                'type': 'memory',
                'message': f"Utilisation mémoire élevée: {system_data['memory']['percent']:.1f}%",
                'timestamp': timestamp,
                'severity': 'warning' if system_data['memory']['percent'] < 95 else 'critical'
            })
        
        # Alerte disque
        if system_data['disk']['percent'] > self.alert_thresholds['disk']:
            alerts.append({
                'type': 'disk',
                'message': f"Espace disque faible: {system_data['disk']['percent']:.1f}%",
                'timestamp': timestamp,
                'severity': 'warning' if system_data['disk']['percent'] < 98 else 'critical'
            })
        
        return alerts
    
    def create_graph(self, data_type, title):
        """Crée un graphique pour les données spécifiées"""
        fig, ax = plt.subplots(figsize=(6, 3))
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#3b3b3b')
        
        if len(self.data_history['timestamps']) > 1:
            timestamps = list(self.data_history['timestamps'])
            values = list(self.data_history[data_type])
            
            ax.plot(timestamps, values, color='#00ff41', linewidth=2)
            ax.fill_between(timestamps, values, alpha=0.3, color='#00ff41')
            
            # Formatage des axes
            ax.set_title(title, color='white', fontsize=12, fontweight='bold')
            ax.set_xlabel('Temps', color='white')
            ax.set_ylabel('Pourcentage (%)', color='white')
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.3)
            
            # Format des dates sur l'axe X
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            fig.autofmt_xdate()
        
        # Conversion en image base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='PNG', facecolor='#2b2b2b', bbox_inches='tight')
        buffer.seek(0)
        
        image = Image.open(buffer)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        bio.seek(0)
        
        plt.close(fig)
        return base64.b64encode(bio.getvalue())
    
    def create_layout(self):
        # Panneau des informations système en temps réel
        info_column = [
            [sg.Text('📊 Monitoring Système en Temps Réel', font=('Arial', 16, 'bold'))],
            [sg.HSeparator()],
            
            # CPU
            [sg.Text('🖥️ Processeur', font=('Arial', 12, 'bold'))],
            [sg.Text('Utilisation:'), sg.Text('0%', key='CPU_PERCENT', text_color='green'),
             sg.Text('Fréquence:'), sg.Text('0 MHz', key='CPU_FREQ')],
            [sg.ProgressBar(100, key='CPU_PROGRESS', size=(30, 15), bar_color=('green', 'grey'))],
            
            # Mémoire
            [sg.Text('💾 Mémoire', font=('Arial', 12, 'bold'))],
            [sg.Text('Utilisée:'), sg.Text('0 MB', key='MEM_USED'),
             sg.Text('Disponible:'), sg.Text('0 MB', key='MEM_AVAILABLE')],
            [sg.Text('Pourcentage:'), sg.Text('0%', key='MEM_PERCENT', text_color='green')],
            [sg.ProgressBar(100, key='MEM_PROGRESS', size=(30, 15), bar_color=('blue', 'grey'))],
            
            # Disque
            [sg.Text('💿 Disque', font=('Arial', 12, 'bold'))],
            [sg.Text('Utilisé:'), sg.Text('0 GB', key='DISK_USED'),
             sg.Text('Libre:'), sg.Text('0 GB', key='DISK_FREE')],
            [sg.Text('Pourcentage:'), sg.Text('0%', key='DISK_PERCENT', text_color='green')],
            [sg.ProgressBar(100, key='DISK_PROGRESS', size=(30, 15), bar_color=('orange', 'grey'))],
            
            # Réseau
            [sg.Text('🌐 Réseau', font=('Arial', 12, 'bold'))],
            [sg.Text('Envoyé:'), sg.Text('0 MB', key='NET_SENT'),
             sg.Text('Reçu:'), sg.Text('0 MB', key='NET_RECV')],
            
            [sg.HSeparator()],
            [sg.Button('▶️ Démarrer', key='START_MONITORING'),
             sg.Button('⏹️ Arrêter', key='STOP_MONITORING', disabled=True),
             sg.Button('📋 Exporter', key='EXPORT_DATA')]
        ]
        
        # Panneau des graphiques
        graph_column = [
            [sg.Text('📈 Graphiques en Temps Réel', font=('Arial', 16, 'bold'))],
            [sg.HSeparator()],
            [sg.Image(key='CPU_GRAPH', size=(600, 300))],
            [sg.Image(key='MEMORY_GRAPH', size=(600, 300))],
            [sg.HSeparator()],
            [sg.Text('⚙️ Configuration des Alertes')],
            [sg.Text('Seuil CPU (%):'), sg.Input('80', key='CPU_THRESHOLD', size=(10, 1)),
             sg.Text('Mémoire (%):'), sg.Input('85', key='MEM_THRESHOLD', size=(10, 1)),
             sg.Text('Disque (%):'), sg.Input('90', key='DISK_THRESHOLD', size=(10, 1)),
             sg.Button('Appliquer', key='UPDATE_THRESHOLDS')]
        ]
        
        # Panneau des processus
        process_column = [
            [sg.Text('🔄 Processus les Plus Gourmands', font=('Arial', 14, 'bold'))],
            [sg.Table([], headings=['PID', 'Nom', 'CPU%', 'Mémoire%'], 
                     key='PROCESS_TABLE', size=(50, 15), auto_size_columns=False,
                     col_widths=[8, 20, 8, 10])],
            [sg.Button('🔄 Rafraîchir', key='REFRESH_PROCESSES'),
             sg.Button('🛑 Tuer Processus', key='KILL_PROCESS')]
        ]
        
        # Panneau des alertes
        alert_column = [
            [sg.Text('🚨 Alertes Système', font=('Arial', 14, 'bold'))],
            [sg.Multiline('', key='ALERT_LOG', size=(50, 10), disabled=True, autoscroll=True)],
            [sg.Button('🗑️ Effacer Alertes', key='CLEAR_ALERTS'),
             sg.Button('💾 Sauvegarder Log', key='SAVE_ALERTS')]
        ]
        
        # Onglets principaux
        tab_layout = [
            [sg.TabGroup([
                [sg.Tab('Monitoring', [
                    [sg.Column(info_column, vertical_alignment='top'), 
                     sg.VSeparator(),
                     sg.Column(graph_column, vertical_alignment='top')]
                ])],
                [sg.Tab('Processus', process_column)],
                [sg.Tab('Alertes', alert_column)],
                [sg.Tab('Historique', [
                    [sg.Text('📊 Historique des Données')],
                    [sg.Multiline('', key='HISTORY_DISPLAY', size=(100, 25), disabled=True)],
                    [sg.Button('📈 Graphique Détaillé', key='DETAILED_GRAPH'),
                     sg.Button('💾 Exporter Historique', key='EXPORT_HISTORY')]
                ])]
            ], key='TAB_GROUP')]
        ]
        
        layout = [
            tab_layout,
            [sg.StatusBar('Prêt', key='STATUS_BAR')]
        ]
        
        return layout
    
    def update_display(self, window, system_data):
        """Met à jour l'affichage avec les nouvelles données"""
        if not system_data:
            return
        
        # Mise à jour des informations CPU
        cpu_percent = system_data['cpu']['percent']
        window['CPU_PERCENT'].update(f"{cpu_percent:.1f}%")
        window['CPU_FREQ'].update(f"{system_data['cpu']['frequency']:.0f} MHz")
        window['CPU_PROGRESS'].update(cpu_percent)
        
        # Couleur selon l'utilisation CPU
        if cpu_percent > 80:
            color = 'red'
        elif cpu_percent > 60:
            color = 'orange'
        else:
            color = 'green'
        window['CPU_PERCENT'].update(text_color=color)
        
        # Mise à jour des informations mémoire
        mem_percent = system_data['memory']['percent']
        mem_used = self.format_bytes(system_data['memory']['used'])
        mem_available = self.format_bytes(system_data['memory']['available'])
        
        window['MEM_USED'].update(mem_used)
        window['MEM_AVAILABLE'].update(mem_available)
        window['MEM_PERCENT'].update(f"{mem_percent:.1f}%")
        window['MEM_PROGRESS'].update(mem_percent)
        
        # Couleur selon l'utilisation mémoire
        if mem_percent > 85:
            color = 'red'
        elif mem_percent > 70:
            color = 'orange'
        else:
            color = 'green'
        window['MEM_PERCENT'].update(text_color=color)
        
        # Mise à jour des informations disque
        disk_percent = system_data['disk']['percent']
        disk_used = self.format_bytes(system_data['disk']['used'])
        disk_free = self.format_bytes(system_data['disk']['free'])
        
        window['DISK_USED'].update(disk_used)
        window['DISK_FREE'].update(disk_free)
        window['DISK_PERCENT'].update(f"{disk_percent:.1f}%")
        window['DISK_PROGRESS'].update(disk_percent)
        
        # Couleur selon l'utilisation disque
        if disk_percent > 90:
            color = 'red'
        elif disk_percent > 80:
            color = 'orange'
        else:
            color = 'green'
        window['DISK_PERCENT'].update(text_color=color)
        
        # Mise à jour des informations réseau
        net_sent = self.format_bytes(system_data['network']['bytes_sent'])
        net_recv = self.format_bytes(system_data['network']['bytes_recv'])
        window['NET_SENT'].update(net_sent)
        window['NET_RECV'].update(net_recv)
        
        # Mise à jour du tableau des processus
        process_data = []
        for proc in system_data['processes'][:10]:
            process_data.append([
                proc['pid'],
                proc['name'][:20] if proc['name'] else 'N/A',
                f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] else '0.0',
                f"{proc['memory_percent']:.1f}" if proc['memory_percent'] else '0.0'
            ])
        window['PROCESS_TABLE'].update(process_data)
        
        # Vérification des alertes
        alerts = self.check_alerts(system_data)
        for alert in alerts:
            timestamp = alert['timestamp'].strftime('%H:%M:%S')
            severity_icon = '🚨' if alert['severity'] == 'critical' else '⚠️'
            alert_message = f"[{timestamp}] {severity_icon} {alert['message']}\n"
            window['ALERT_LOG'].print(alert_message, end='')
        
        # Mise à jour de la barre de statut
        status = f"Dernière mise à jour: {system_data['timestamp'].strftime('%H:%M:%S')}"
        window['STATUS_BAR'].update(status)
    
    def monitoring_thread(self, window):
        """Thread de monitoring en arrière-plan"""
        while self.monitoring:
            try:
                system_data = self.get_system_info()
                if system_data:
                    # Ajouter aux données historiques
                    self.data_history['cpu'].append(system_data['cpu']['percent'])
                    self.data_history['memory'].append(system_data['memory']['percent'])
                    self.data_history['disk'].append(system_data['disk']['percent'])
                    self.data_history['timestamps'].append(system_data['timestamp'])
                    
                    # Mise à jour de l'interface
                    window.write_event_value('UPDATE_DISPLAY', system_data)
                    
                    # Génération des graphiques
                    if len(self.data_history['timestamps']) > 2:
                        cpu_graph = self.create_graph('cpu', 'Utilisation CPU (%)')
                        memory_graph = self.create_graph('memory', 'Utilisation Mémoire (%)')
                        
                        window.write_event_value('UPDATE_GRAPHS', {
                            'cpu': cpu_graph,
                            'memory': memory_graph
                        })
                
                time.sleep(2)  # Mise à jour toutes les 2 secondes
            except Exception as e:
                print(f"Erreur dans le thread de monitoring: {e}")
                break
    
    def export_data(self):
        """Exporte les données historiques"""
        if not self.data_history['timestamps']:
            sg.popup('Aucune donnée à exporter')
            return
        
        filename = sg.popup_get_file('Sauvegarder les données', save_as=True,
                                   file_types=(('JSON', '*.json'),))
        if filename:
            try:
                export_data = {
                    'timestamps': [ts.isoformat() for ts in self.data_history['timestamps']],
                    'cpu': list(self.data_history['cpu']),
                    'memory': list(self.data_history['memory']),
                    'disk': list(self.data_history['disk'])
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                sg.popup(f'Données exportées vers {filename}')
            except Exception as e:
                sg.popup_error(f'Erreur lors de l\'export: {str(e)}')
    
    def run(self):
        window = sg.Window('Dashboard de Monitoring Système', self.create_layout(), 
                          finalize=True, resizable=True, size=(1200, 800))
        
        monitoring_thread = None
        
        while True:
            event, values = window.read(timeout=100)
            
            if event == sg.WIN_CLOSED:
                self.monitoring = False
                if monitoring_thread:
                    monitoring_thread.join(timeout=1)
                break
            
            elif event == 'START_MONITORING':
                self.monitoring = True
                monitoring_thread = threading.Thread(target=self.monitoring_thread, 
                                                   args=(window,), daemon=True)
                monitoring_thread.start()
                
                window['START_MONITORING'].update(disabled=True)
                window['STOP_MONITORING'].update(disabled=False)
                window['STATUS_BAR'].update('Monitoring actif...')
            
            elif event == 'STOP_MONITORING':
                self.monitoring = False
                window['START_MONITORING'].update(disabled=False)
                window['STOP_MONITORING'].update(disabled=True)
                window['STATUS_BAR'].update('Monitoring arrêté')
            
            elif event == 'UPDATE_DISPLAY':
                self.update_display(window, values['UPDATE_DISPLAY'])
            
            elif event == 'UPDATE_GRAPHS':
                graphs = values['UPDATE_GRAPHS']
                window['CPU_GRAPH'].update(data=graphs['cpu'])
                window['MEMORY_GRAPH'].update(data=graphs['memory'])
            
            elif event == 'UPDATE_THRESHOLDS':
                try:
                    self.alert_thresholds['cpu'] = float(values['CPU_THRESHOLD'])
                    self.alert_thresholds['memory'] = float(values['MEM_THRESHOLD'])
                    self.alert_thresholds['disk'] = float(values['DISK_THRESHOLD'])
                    sg.popup('Seuils d\'alerte mis à jour')
                except ValueError:
                    sg.popup_error('Valeurs de seuil invalides')
            
            elif event == 'EXPORT_DATA':
                self.export_data()
            
            elif event == 'CLEAR_ALERTS':
                window['ALERT_LOG'].update('')
            
            elif event == 'REFRESH_PROCESSES':
                system_data = self.get_system_info()
                if system_data:
                    self.update_display(window, system_data)
            
            elif event == 'KILL_PROCESS':
                selected_rows = values['PROCESS_TABLE']
                if selected_rows:
                    # Implementation du kill process nécessiterait des permissions administrateur
                    sg.popup('Fonctionnalité disponible avec les permissions administrateur')
        
        window.close()

if __name__ == '__main__':
    monitor = SystemMonitor()
    monitor.run()
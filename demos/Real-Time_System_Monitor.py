import PySimpleGUI4 as sg
import psutil
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class SystemMonitor:
    def __init__(self):
        self.cpu_data = []
        self.memory_data = []
        self.network_data = []
        self.monitoring = False
        self.max_points = 60
        
    def draw_figure(self, canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg
    
    def create_plots(self):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))
        fig.patch.set_facecolor('#2b2b2b')
        
        # CPU Usage Plot
        ax1.set_title('CPU Usage (%)', color='white')
        ax1.set_facecolor('#2b2b2b')
        ax1.tick_params(colors='white')
        ax1.grid(True, alpha=0.3)
        
        # Memory Usage Plot  
        ax2.set_title('Memory Usage (%)', color='white')
        ax2.set_facecolor('#2b2b2b')
        ax2.tick_params(colors='white')
        ax2.grid(True, alpha=0.3)
        
        # Network Usage Plot
        ax3.set_title('Network I/O (MB/s)', color='white')
        ax3.set_facecolor('#2b2b2b')
        ax3.tick_params(colors='white')
        ax3.grid(True, alpha=0.3)
        
        return fig, (ax1, ax2, ax3)
    
    def monitor_system(self, window):
        while self.monitoring:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            net_io = psutil.net_io_counters()
            if hasattr(self, 'prev_net_io'):
                bytes_sent = (net_io.bytes_sent - self.prev_net_io.bytes_sent) / 1024 / 1024
                bytes_recv = (net_io.bytes_recv - self.prev_net_io.bytes_recv) / 1024 / 1024
                network_usage = bytes_sent + bytes_recv
            else:
                network_usage = 0
            
            self.prev_net_io = net_io
            
            # Update data
            self.cpu_data.append(cpu_percent)
            self.memory_data.append(memory_percent)
            self.network_data.append(network_usage)
            
            # Keep only last N points
            if len(self.cpu_data) > self.max_points:
                self.cpu_data.pop(0)
                self.memory_data.pop(0) 
                self.network_data.pop(0)
            
            # Update GUI
            try:
                window.write_event_value('-UPDATE-', {
                    'cpu': cpu_percent,
                    'memory': memory_percent,
                    'network': network_usage
                })
            except:
                break
    
    def create_layout(self):
        sg.theme('DarkBlack')
        
        info_frame = [
            [sg.Text('System Information', font=('Arial', 14, 'bold'))],
            [sg.Text('CPU:', size=(15, 1)), sg.Text('', key='-CPU-INFO-', size=(20, 1))],
            [sg.Text('Memory:', size=(15, 1)), sg.Text('', key='-MEM-INFO-', size=(20, 1))],
            [sg.Text('Disk:', size=(15, 1)), sg.Text('', key='-DISK-INFO-', size=(20, 1))],
            [sg.Text('Network:', size=(15, 1)), sg.Text('', key='-NET-INFO-', size=(20, 1))],
            [sg.HSeparator()],
            [sg.Text('Processes:', font=('Arial', 12, 'bold'))],
            [sg.Listbox([], size=(40, 10), key='-PROCESSES-')]
        ]
        
        control_frame = [
            [sg.Button('Start Monitoring', key='-START-', button_color=('white', 'green'))],
            [sg.Button('Stop Monitoring', key='-STOP-', button_color=('white', 'red'), disabled=True)],
            [sg.Button('Refresh Processes', key='-REFRESH-PROC-')],
            [sg.Button('Kill Selected Process', key='-KILL-PROC-', button_color=('white', 'red'))],
            [sg.HSeparator()],
            [sg.Text('Alerts:', font=('Arial', 12, 'bold'))],
            [sg.Checkbox('CPU > 80%', key='-ALERT-CPU-')],
            [sg.Checkbox('Memory > 80%', key='-ALERT-MEM-')],
            [sg.Multiline('', size=(40, 5), key='-ALERTS-', disabled=True)]
        ]
        
        layout = [
            [sg.Column(info_frame, vertical_alignment='top'),
             sg.VSeparator(),
             sg.Column(control_frame, vertical_alignment='top'),
             sg.VSeparator(),
             sg.Canvas(key='-CANVAS-', size=(600, 600))]
        ]
        
        return layout
    
    def run(self):
        window = sg.Window('System Monitor', 
                          self.create_layout(),
                          finalize=True,
                          resizable=True,
                          size=(1200, 700))
        
        # Create plots
        fig, axes = self.create_plots()
        canvas = self.draw_figure(window['-CANVAS-'].TKCanvas, fig)
        
        # Get initial system info
        cpu_info = f"{psutil.cpu_count()} cores @ {psutil.cpu_freq().current:.0f}MHz"
        memory_info = f"{psutil.virtual_memory().total / (1024**3):.1f} GB"
        disk_info = f"{psutil.disk_usage('/').total / (1024**3):.1f} GB"
        
        window['-CPU-INFO-'].update(cpu_info)
        window['-MEM-INFO-'].update(memory_info)
        window['-DISK-INFO-'].update(disk_info)
        
        monitor_thread = None
        
        while True:
            event, values = window.read(timeout=100)
            
            if event == sg.WIN_CLOSED:
                self.monitoring = False
                if monitor_thread:
                    monitor_thread.join()
                break
                
            elif event == '-START-':
                self.monitoring = True
                monitor_thread = threading.Thread(target=self.monitor_system, args=(window,))
                monitor_thread.daemon = True
                monitor_thread.start()
                window['-START-'].update(disabled=True)
                window['-STOP-'].update(disabled=False)
                
            elif event == '-STOP-':
                self.monitoring = False
                window['-START-'].update(disabled=False)
                window['-STOP-'].update(disabled=True)
                
            elif event == '-UPDATE-':
                data = values['-UPDATE-']
                
                # Update plots
                if len(self.cpu_data) > 1:
                    axes[0].clear()
                    axes[0].plot(self.cpu_data, color='cyan', linewidth=2)
                    axes[0].set_title('CPU Usage (%)', color='white')
                    axes[0].set_ylim(0, 100)
                    axes[0].set_facecolor('#2b2b2b')
                    axes[0].tick_params(colors='white')
                    axes[0].grid(True, alpha=0.3)
                    
                    axes[1].clear()
                    axes[1].plot(self.memory_data, color='orange', linewidth=2)
                    axes[1].set_title('Memory Usage (%)', color='white')
                    axes[1].set_ylim(0, 100)
                    axes[1].set_facecolor('#2b2b2b')
                    axes[1].tick_params(colors='white')
                    axes[1].grid(True, alpha=0.3)
                    
                    axes[2].clear()
                    axes[2].plot(self.network_data, color='lime', linewidth=2)
                    axes[2].set_title('Network I/O (MB/s)', color='white')
                    axes[2].set_facecolor('#2b2b2b')
                    axes[2].tick_params(colors='white')
                    axes[2].grid(True, alpha=0.3)
                    
                    canvas.draw()
                
                # Check alerts
                alerts = []
                if values['-ALERT-CPU-'] and data['cpu'] > 80:
                    alerts.append(f"HIGH CPU: {data['cpu']:.1f}%")
                if values['-ALERT-MEM-'] and data['memory'] > 80:
                    alerts.append(f"HIGH MEMORY: {data['memory']:.1f}%")
                
                if alerts:
                    current_alerts = window['-ALERTS-'].get()
                    new_alert = f"{time.strftime('%H:%M:%S')} - {', '.join(alerts)}\n"
                    window['-ALERTS-'].update(current_alerts + new_alert)
        
        window.close()

if __name__ == '__main__':
    monitor = SystemMonitor()
    monitor.run()


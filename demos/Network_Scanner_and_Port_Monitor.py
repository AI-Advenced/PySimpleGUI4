import PySimpleGUI4 as sg
import socket
import threading
import subprocess
import ipaddress
import time
from concurrent.futures import ThreadPoolExecutor
import json
import nmap

class NetworkScanner:
    def __init__(self):
        self.scan_results = []
        self.port_scan_results = []
        self.scanning = False
        self.common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 1723, 3389, 5900, 8080]
        
    def get_local_network(self):
        """Get the local network range"""
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Assume /24 network
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            return str(network)
        except Exception:
            return "192.168.1.0/24"
    
    def ping_host(self, host):
        """Ping a single host"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', host], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            else:  # Linux/Mac
                result = subprocess.run(['ping', '-c', '1', '-W', '1', host], 
                                      capture_output=True, text=True)
                return result.returncode == 0
        except Exception:
            return False
    
    def get_hostname(self, ip):
        """Get hostname for IP address"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return "Unknown"
    
    def scan_port(self, host, port, timeout=1):
        """Scan a single port"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    def get_service_name(self, port):
        """Get service name for port"""
        try:
            return socket.getservbyport(port)
        except OSError:
            return "unknown"
    
    def network_scan(self, network_range, window):
        """Perform network scan"""
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
            active_hosts = []
            
            window.write_event_value('-SCAN_STATUS-', f'Scanning {network_range}...')
            
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = {}
                
                for ip in network.hosts():
                    if not self.scanning:
                        break
                    future = executor.submit(self.ping_host, str(ip))
                    futures[future] = str(ip)
                
                completed = 0
                total = len(futures)
                
                for future in futures:
                    if not self.scanning:
                        break
                        
                    ip = futures[future]
                    completed += 1
                    
                    try:
                        if future.result(timeout=2):
                            hostname = self.get_hostname(ip)
                            active_hosts.append({
                                'ip': ip,
                                'hostname': hostname,
                                'status': 'Active'
                            })
                            
                            window.write_event_value('-HOST_FOUND-', {
                                'ip': ip,
                                'hostname': hostname
                            })
                    
                    except Exception:
                        pass
                    
                    progress = int((completed / total) * 100)
                    window.write_event_value('-SCAN_PROGRESS-', progress)
            
            self.scan_results = active_hosts
            window.write_event_value('-SCAN_COMPLETE-', len(active_hosts))
            
        except Exception as e:
            window.write_event_value('-SCAN_ERROR-', str(e))
    
    def port_scan(self, host, port_range, window):
        """Perform port scan on host"""
        try:
            if '-' in port_range:
                start_port, end_port = map(int, port_range.split('-'))
                ports = range(start_port, end_port + 1)
            elif ',' in port_range:
                ports = [int(p.strip()) for p in port_range.split(',')]
            else:
                ports = [int(port_range)]
            
            open_ports = []
            window.write_event_value('-PORT_SCAN_STATUS-', f'Scanning ports on {host}...')
            
            with ThreadPoolExecutor(max_workers=100) as executor:
                futures = {}
                
                for port in ports:
                    if not self.scanning:
                        break
                    future = executor.submit(self.scan_port, host, port)
                    futures[future] = port
                
                completed = 0
                total = len(futures)
                
                for future in futures:
                    if not self.scanning:
                        break
                        
                    port = futures[future]
                    completed += 1
                    
                    try:
                        if future.result(timeout=1):
                            service = self.get_service_name(port)
                            open_ports.append({
                                'port': port,
                                'service': service,
                                'status': 'Open'
                            })
                            
                            window.write_event_value('-PORT_FOUND-', {
                                'host': host,
                                'port': port,
                                'service': service
                            })
                    
                    except Exception:
                        pass
                    
                    progress = int((completed / total) * 100)
                    window.write_event_value('-PORT_SCAN_PROGRESS-', progress)
            
            self.port_scan_results = open_ports
            window.write_event_value('-PORT_SCAN_COMPLETE-', {
                'host': host,
                'count': len(open_ports)
            })
            
        except Exception as e:
            window.write_event_value('-PORT_SCAN_ERROR-', str(e))
    
    def create_layout(self):
        # Network scan tab
        network_scan_layout = [
            [sg.Text('Network Range:'), 
             sg.Input(self.get_local_network(), key='-NETWORK_RANGE-', size=(20, 1)),
             sg.Button('Scan Network', key='-SCAN_NETWORK-'),
             sg.Button('Stop Scan', key='-STOP_NETWORK_SCAN-', disabled=True)],
            [sg.ProgressBar(100, orientation='h', size=(50, 20), key='-NETWORK_PROGRESS-')],
            [sg.Text('', key='-NETWORK_STATUS-', size=(60, 1))],
            [sg.Table(values=[],
                     headings=['IP Address', 'Hostname', 'Status'],
                     key='-NETWORK_RESULTS-',
                     col_widths=[15, 25, 10],
                     justification='left',
                     alternating_row_color='lightgray',
                     selected_row_colors='blue on yellow',
                     enable_events=True,
                     expand_x=True,
                     expand_y=True,
                     num_rows=15,
                     right_click_menu=['', ['Port Scan', 'Ping', 'Traceroute', 'Export']])],
            [sg.Button('Export Results', key='-EXPORT_NETWORK-'),
             sg.Button('Clear Results', key='-CLEAR_NETWORK-')]
        ]
        
        # Port scan tab
        port_scan_layout = [
            [sg.Text('Target Host:'), 
             sg.Input('', key='-TARGET_HOST-', size=(20, 1)),
             sg.Text('Ports:'),
             sg.Input('1-1000', key='-PORT_RANGE-', size=(15, 1))],
            [sg.Button('Common Ports', key='-COMMON_PORTS-'),
             sg.Button('Scan Ports', key='-SCAN_PORTS-'),
             sg.Button('Stop Scan', key='-STOP_PORT_SCAN-', disabled=True)],
            [sg.ProgressBar(100, orientation='h', size=(50, 20), key='-PORT_PROGRESS-')],
            [sg.Text('', key='-PORT_STATUS-', size=(60, 1))],
            [sg.Table(values=[],
                     headings=['Port', 'Service', 'Status'],
                     key='-PORT_RESULTS-',
                     col_widths=[8, 20, 10],
                     justification='left',
                     alternating_row_color='lightgray',
                     expand_x=True,
                     expand_y=True,
                     num_rows=15)],
            [sg.Button('Export Port Results', key='-EXPORT_PORTS-'),
             sg.Button('Clear Port Results', key='-CLEAR_PORTS-')]
        ]
        
        # Tools tab
        tools_layout = [
            [sg.Text('Network Tools', font=('Arial', 14, 'bold'))],
            [sg.Frame('Ping Tool', [
                [sg.Text('Host:'), sg.Input(key='-PING_HOST-', size=(20, 1)),
                 sg.Button('Ping', key='-PING-')],
                [sg.Multiline('', key='-PING_RESULT-', size=(60, 8), disabled=True)]
            ])],
            [sg.Frame('Traceroute Tool', [
                [sg.Text('Host:'), sg.Input(key='-TRACE_HOST-', size=(20, 1)),
                 sg.Button('Traceroute', key='-TRACEROUTE-')],
                [sg.Multiline('', key='-TRACE_RESULT-', size=(60, 8), disabled=True)]
            ])],
            [sg.Frame('DNS Lookup', [
                [sg.Text('Host:'), sg.Input(key='-DNS_HOST-', size=(20, 1)),
                 sg.Button('Lookup', key='-DNS_LOOKUP-')],
                [sg.Multiline('', key='-DNS_RESULT-', size=(60, 8), disabled=True)]
            ])]
        ]
        
        # Main layout
        layout = [
            [sg.TabGroup([
                [sg.Tab('Network Scan', network_scan_layout, key='-TAB_NETWORK-')],
                [sg.Tab('Port Scan', port_scan_layout, key='-TAB_PORTS-')],
                [sg.Tab('Tools', tools_layout, key='-TAB_TOOLS-')]
            ], expand_x=True, expand_y=True)],
            [sg.StatusBar('Ready', key='-STATUS-', size=(80, 1))]
        ]
        
        return layout
    
    def run(self):
        sg.theme('DarkBlue3')
        
        window = sg.Window('Network Scanner & Port Monitor',
                          self.create_layout(),
                          finalize=True,
                          resizable=True,
                          size=(800, 700))
        
        while True:
            event, values = window.read()
            
            if event == sg.WIN_CLOSED:
                self.scanning = False
                break
            
            elif event == '-SCAN_NETWORK-':
                network_range = values['-NETWORK_RANGE-']
                if network_range:
                    self.scanning = True
                    window['-SCAN_NETWORK-'].update(disabled=True)
                    window['-STOP_NETWORK_SCAN-'].update(disabled=False)
                    window['-NETWORK_RESULTS-'].update(values=[])
                    window['-NETWORK_PROGRESS-'].update(0)
                    
                    # Start scan in thread
                    threading.Thread(
                        target=self.network_scan,
                        args=(network_range, window),
                        daemon=True
                    ).start()
            
            elif event == '-STOP_NETWORK_SCAN-':
                self.scanning = False
                window['-SCAN_NETWORK-'].update(disabled=False)
                window['-STOP_NETWORK_SCAN-'].update(disabled=True)
                window['-NETWORK_STATUS-'].update('Scan stopped by user')
            
            elif event == '-HOST_FOUND-':
                data = values['-HOST_FOUND-']
                current_results = window['-NETWORK_RESULTS-'].get()
                current_results.append([data['ip'], data['hostname'], 'Active'])
                window['-NETWORK_RESULTS-'].update(values=current_results)
            
            elif event == '-SCAN_PROGRESS-':
                progress = values['-SCAN_PROGRESS-']
                window['-NETWORK_PROGRESS-'].update(progress)
            
            elif event == '-SCAN_COMPLETE-':
                count = values['-SCAN_COMPLETE-']
                self.scanning = False
                window['-SCAN_NETWORK-'].update(disabled=False)
                window['-STOP_NETWORK_SCAN-'].update(disabled=True)
                window['-NETWORK_STATUS-'].update(f'Scan complete. Found {count} active hosts.')
            
            elif event == '-SCAN_PORTS-':
                host = values['-TARGET_HOST-']
                port_range = values['-PORT_RANGE-']
                
                if host and port_range:
                    self.scanning = True
                    window['-SCAN_PORTS-'].update(disabled=True)
                    window['-STOP_PORT_SCAN-'].update(disabled=False)
                    window['-PORT_RESULTS-'].update(values=[])
                    window['-PORT_PROGRESS-'].update(0)
                    
                    # Start port scan in thread
                    threading.Thread(
                        target=self.port_scan,
                        args=(host, port_range, window),
                        daemon=True
                    ).start()
            
            elif event == '-COMMON_PORTS-':
                window['-PORT_RANGE-'].update(','.join(map(str, self.common_ports)))
            
            elif event == '-PORT_FOUND-':
                data = values['-PORT_FOUND-']
                current_results = window['-PORT_RESULTS-'].get()
                current_results.append([data['port'], data['service'], 'Open'])
                window['-PORT_RESULTS-'].update(values=current_results)
            
            elif event == '-PORT_SCAN_PROGRESS-':
                progress = values['-PORT_SCAN_PROGRESS-']
                window['-PORT_PROGRESS-'].update(progress)
            
            elif event == '-PORT_SCAN_COMPLETE-':
                data = values['-PORT_SCAN_COMPLETE-']
                self.scanning = False
                window['-SCAN_PORTS-'].update(disabled=False)
                window['-STOP_PORT_SCAN-'].update(disabled=False)
                window['-PORT_STATUS-'].update(f'Port scan complete on {data["host"]}. Found {data["count"]} open ports.')
            
            elif event == '-PING-':
                host = values['-PING_HOST-']
                if host:
                    # Run ping in thread
                    def run_ping():
                        try:
                            if os.name == 'nt':
                                result = subprocess.run(['ping', '-n', '4', host], 
                                                      capture_output=True, text=True)
                            else:
                                result = subprocess.run(['ping', '-c', '4', host], 
                                                      capture_output=True, text=True)
                            
                            window.write_event_value('-PING_COMPLETE-', result.stdout)
                        except Exception as e:
                            window.write_event_value('-PING_ERROR-', str(e))
                    
                    threading.Thread(target=run_ping, daemon=True).start()
                    window['-PING_RESULT-'].update('Pinging...')
            
            elif event == '-PING_COMPLETE-':
                window['-PING_RESULT-'].update(values['-PING_COMPLETE-'])
            
            elif event == '-PING_ERROR-':
                window['-PING_RESULT-'].update(f'Error: {values["-PING_ERROR-"]}')
        
        window.close()

if __name__ == '__main__':
    scanner = NetworkScanner()
    scanner.run()
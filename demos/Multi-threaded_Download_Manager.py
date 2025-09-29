import PySimpleGUI4 as sg
import requests
import threading
import time
from urllib.parse import urlparse
import os
from queue import Queue
import json

class DownloadManager:
    def __init__(self):
        self.downloads = {}
        self.download_queue = Queue()
        self.active_downloads = 0
        self.max_concurrent = 3
        self.download_history = []
        self.load_history()
        
    def load_history(self):
        """Load download history from file"""
        try:
            with open('download_history.json', 'r') as f:
                self.download_history = json.load(f)
        except FileNotFoundError:
            pass
    
    def save_history(self):
        """Save download history to file"""
        with open('download_history.json', 'w') as f:
            json.dump(self.download_history, f, indent=2)
    
    def get_filename_from_url(self, url):
        """Extract filename from URL"""
        parsed = urlparse(url)
        if parsed.path:
            return os.path.basename(parsed.path)
        return f"download_{int(time.time())}"
    
    def download_file(self, url, filename, download_id, window):
        """Download file with progress tracking"""
        try:
            self.downloads[download_id]['status'] = 'Downloading'
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.downloads[download_id]['status'] == 'Cancelled':
                        return
                        
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        speed = downloaded / (time.time() - self.downloads[download_id]['start_time'])
                        
                        window.write_event_value('-UPDATE_PROGRESS-', {
                            'id': download_id,
                            'progress': progress,
                            'downloaded': downloaded,
                            'total': total_size,
                            'speed': speed
                        })
            
            self.downloads[download_id]['status'] = 'Completed'
            self.downloads[download_id]['end_time'] = time.time()
            
            # Add to history
            self.download_history.append({
                'url': url,
                'filename': filename,
                'size': total_size,
                'completed': time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Completed'
            })
            self.save_history()
            
            window.write_event_value('-DOWNLOAD_COMPLETE-', download_id)
            
        except Exception as e:
            self.downloads[download_id]['status'] = f'Error: {str(e)}'
            window.write_event_value('-DOWNLOAD_ERROR-', {
                'id': download_id,
                'error': str(e)
            })
        finally:
            self.active_downloads -= 1
    
    def start_download(self, url, save_path, window):
        """Start a new download"""
        if self.active_downloads >= self.max_concurrent:
            sg.popup('Maximum concurrent downloads reached. Please wait.')
            return
        
        filename = self.get_filename_from_url(url)
        full_path = os.path.join(save_path, filename)
        
        download_id = f"dl_{int(time.time())}"
        
        self.downloads[download_id] = {
            'url': url,
            'filename': full_path,
            'status': 'Starting',
            'progress': 0,
            'speed': 0,
            'start_time': time.time()
        }
        
        self.active_downloads += 1
        
        thread = threading.Thread(
            target=self.download_file,
            args=(url, full_path, download_id, window),
            daemon=True
        )
        thread.start()
        
        return download_id
    
    def format_size(self, size):
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def format_speed(self, speed):
        """Format speed in human readable format"""
        return f"{self.format_size(speed)}/s"
    
    def create_layout(self):
        # Download input section
        input_layout = [
            [sg.Text('Download URL:', size=(12, 1)), 
             sg.Input(key='-URL-', expand_x=True),
             sg.Button('Add', key='-ADD_DOWNLOAD-')],
            [sg.Text('Save to:', size=(12, 1)),
             sg.Input(key='-SAVE_PATH-', default_text=os.path.expanduser('~/Downloads'), expand_x=True),
             sg.FolderBrowse(target='-SAVE_PATH-')]
        ]
        
        # Download list
        downloads_layout = [
            [sg.Text('Active Downloads:', font=('Arial', 12, 'bold'))],
            [sg.Table(values=[],
                     headings=['File', 'Status', 'Progress', 'Speed', 'Size'],
                     key='-DOWNLOADS_TABLE-',
                     col_widths=[25, 15, 10, 12, 12],
                     justification='left',
                     alternating_row_color='lightgray',
                     selected_row_colors='blue on yellow',
                     enable_events=True,
                     expand_x=True,
                     num_rows=10,
                     right_click_menu=['', ['Pause', 'Resume', 'Cancel', 'Remove']])],
            [sg.Button('Pause All', key='-PAUSE_ALL-'),
             sg.Button('Resume All', key='-RESUME_ALL-'),
             sg.Button('Cancel All', key='-CANCEL_ALL-'),
             sg.Button('Clear Completed', key='-CLEAR_COMPLETED-')]
        ]
        
        # Settings and stats
        settings_layout = [
            [sg.Text('Settings', font=('Arial', 12, 'bold'))],
            [sg.Text('Max Concurrent:'), 
             sg.Spin([1, 2, 3, 4, 5], initial_value=self.max_concurrent, key='-MAX_CONCURRENT-', size=(5, 1))],
            [sg.Checkbox('Auto-start downloads', key='-AUTO_START-', default=True)],
            [sg.Checkbox('Shutdown when complete', key='-SHUTDOWN-')],
            [sg.HSeparator()],
            [sg.Text('Statistics', font=('Arial', 12, 'bold'))],
            [sg.Text('Active:', size=(12, 1)), sg.Text('0', key='-STAT_ACTIVE-')],
            [sg.Text('Completed:', size=(12, 1)), sg.Text('0', key='-STAT_COMPLETED-')],
            [sg.Text('Total Size:', size=(12, 1)), sg.Text('0 B', key='-STAT_SIZE-')],
            [sg.HSeparator()],
            [sg.Button('View History', key='-VIEW_HISTORY-')],
            [sg.Button('Import URLs', key='-IMPORT_URLS-')],
            [sg.Button('Export List', key='-EXPORT_LIST-')]
        ]
        
        # History tab
        history_layout = [
            [sg.Text('Download History', font=('Arial', 12, 'bold'))],
            [sg.Table(values=[],
                     headings=['Filename', 'Size', 'Completed', 'Status'],
                     key='-HISTORY_TABLE-',
                     col_widths=[30, 12, 20, 15],
                     justification='left',
                     alternating_row_color='lightgray',
                     expand_x=True,
                     expand_y=True,
                     num_rows=15)],
            [sg.Button('Clear History', key='-CLEAR_HISTORY-'),
             sg.Button('Export History', key='-EXPORT_HISTORY-')]
        ]
        
        # Main layout with tabs
        layout = [
            [sg.Frame('Add Download', input_layout, expand_x=True)],
            [sg.TabGroup([
                [sg.Tab('Downloads', downloads_layout, key='-TAB_DOWNLOADS-')],
                [sg.Tab('History', history_layout, key='-TAB_HISTORY-')]
            ], expand_x=True, expand_y=True),
             sg.Column(settings_layout, vertical_alignment='top', size=(250, 400))],
            [sg.StatusBar('Ready', key='-STATUS-', size=(80, 1))]
        ]
        
        return layout
    
    def update_downloads_table(self, window):
        """Update the downloads table display"""
        table_data = []
        for dl_id, dl_info in self.downloads.items():
            filename = os.path.basename(dl_info['filename'])
            status = dl_info['status']
            progress = f"{dl_info.get('progress', 0)}%"
            speed = self.format_speed(dl_info.get('speed', 0))
            
            # Get file size info
            if 'total_size' in dl_info:
                size = self.format_size(dl_info['total_size'])
            else:
                size = 'Unknown'
            
            table_data.append([filename, status, progress, speed, size])
        
        window['-DOWNLOADS_TABLE-'].update(values=table_data)
        
        # Update statistics
        active_count = sum(1 for dl in self.downloads.values() if dl['status'] in ['Starting', 'Downloading'])
        completed_count = sum(1 for dl in self.downloads.values() if dl['status'] == 'Completed')
        
        window['-STAT_ACTIVE-'].update(str(active_count))
        window['-STAT_COMPLETED-'].update(str(completed_count))
    
    def update_history_table(self, window):
        """Update the history table display"""
        table_data = []
        for item in self.download_history:
            filename = os.path.basename(item['filename'])
            size = self.format_size(item.get('size', 0))
            completed = item.get('completed', 'Unknown')
            status = item.get('status', 'Unknown')
            
            table_data.append([filename, size, completed, status])
        
        window['-HISTORY_TABLE-'].update(values=table_data)
    
    def run(self):
        sg.theme('DefaultNoMoreNagging')
        
        window = sg.Window('Advanced Download Manager',
                          self.create_layout(),
                          finalize=True,
                          resizable=True,
                          size=(900, 700))
        
        # Load history
        self.update_history_table(window)
        
        while True:
            event, values = window.read(timeout=1000)
            
            if event == sg.WIN_CLOSED:
                break
            
            elif event == '-ADD_DOWNLOAD-':
                url = values['-URL-'].strip()
                save_path = values['-SAVE_PATH-'].strip()
                
                if url and save_path:
                    if os.path.exists(save_path):
                        download_id = self.start_download(url, save_path, window)
                        window['-URL-'].update('')
                        window['-STATUS-'].update(f'Started download: {download_id}')
                    else:
                        sg.popup_error('Save path does not exist!')
                else:
                    sg.popup_error('Please enter URL and save path!')
            
            elif event == '-UPDATE_PROGRESS-':
                data = values['-UPDATE_PROGRESS-']
                dl_id = data['id']
                if dl_id in self.downloads:
                    self.downloads[dl_id].update({
                        'progress': data['progress'],
                        'speed': data['speed'],
                        'total_size': data['total']
                    })
            
            elif event == '-DOWNLOAD_COMPLETE-':
                window['-STATUS-'].update(f'Download completed: {values["-DOWNLOAD_COMPLETE-"]}')
            
            elif event == '-DOWNLOAD_ERROR-':
                data = values['-DOWNLOAD_ERROR-']
                sg.popup_error(f'Download failed: {data["error"]}')
            
            elif event == '-MAX_CONCURRENT-':
                self.max_concurrent = values['-MAX_CONCURRENT-']
            
            elif event == '-CLEAR_COMPLETED-':
                self.downloads = {k: v for k, v in self.downloads.items() 
                                if v['status'] not in ['Completed', 'Error']}
            
            elif event == '-VIEW_HISTORY-':
                self.update_history_table(window)
            
            elif event == '-CLEAR_HISTORY-':
                if sg.popup_yes_no('Clear all download history?') == 'Yes':
                    self.download_history = []
                    self.save_history()
                    self.update_history_table(window)
            
            # Regular table update
            if event == sg.TIMEOUT_EVENT or event.startswith('-UPDATE'):
                self.update_downloads_table(window)
        
        window.close()

if __name__ == '__main__':
    dm = DownloadManager()
    dm.run()


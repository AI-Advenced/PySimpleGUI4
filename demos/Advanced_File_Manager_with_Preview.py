import PySimpleGUI4 as sg
import os
import shutil
from pathlib import Path
import mimetypes
from PIL import Image, ImageTk
import threading

class FileManager:
    def __init__(self):
        self.current_path = Path.home()
        self.clipboard = []
        self.clipboard_operation = None  # 'copy' or 'cut'
        
    def get_file_icon(self, path):
        """Get appropriate icon based on file type"""
        if path.is_dir():
            return '📁'
        elif path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return '🖼️'
        elif path.suffix.lower() in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            return '📄'
        elif path.suffix.lower() in ['.mp4', '.avi', '.mkv', '.mov']:
            return '🎬'
        elif path.suffix.lower() in ['.mp3', '.wav', '.flac']:
            return '🎵'
        elif path.suffix.lower() in ['.zip', '.rar', '.7z', '.tar']:
            return '📦'
        else:
            return '📋'
    
    def get_directory_contents(self, path):
        """Get contents of directory with file information"""
        try:
            contents = []
            for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                try:
                    icon = self.get_file_icon(item)
                    size = self.format_size(item.stat().st_size) if item.is_file() else '<DIR>'
                    modified = item.stat().st_mtime
                    modified_str = Path(item).stat().st_mtime
                    
                    contents.append([
                        icon,
                        item.name,
                        size,
                        modified_str,
                        str(item)  # Full path
                    ])
                except PermissionError:
                    continue
            return contents
        except PermissionError:
            sg.popup_error('Permission denied accessing this directory')
            return []
    
    def format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def preview_file(self, file_path, window):
        """Preview file content based on type"""
        try:
            path = Path(file_path)
            
            if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                self.preview_image(path, window)
            elif path.suffix.lower() in ['.txt', '.py', '.js', '.html', '.css', '.md']:
                self.preview_text(path, window)
            else:
                window['-PREVIEW-'].update('Preview not available for this file type')
                
        except Exception as e:
            window['-PREVIEW-'].update(f'Error previewing file: {str(e)}')
    
    def preview_image(self, path, window):
        """Preview image file"""
        try:
            img = Image.open(path)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            window['-PREVIEW-IMAGE-'].update(data=None)
            window['-PREVIEW-IMAGE-'].update(filename=str(path))
            
            # Update info
            info = f"Image: {img.size[0]}x{img.size[1]} pixels"
            window['-PREVIEW-'].update(info)
            
        except Exception as e:
            window['-PREVIEW-'].update(f'Error loading image: {str(e)}')
    
    def preview_text(self, path, window):
        """Preview text file"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # Read first 1000 characters
                if len(content) == 1000:
                    content += "\n... (truncated)"
                window['-PREVIEW-'].update(content)
        except Exception as e:
            window['-PREVIEW-'].update(f'Error reading file: {str(e)}')
    
    def create_layout(self):
        # Navigation bar
        nav_layout = [
            [sg.Button('🏠', key='-HOME-', tooltip='Home'),
             sg.Button('⬅️', key='-BACK-', tooltip='Back'),
             sg.Button('⬆️', key='-UP-', tooltip='Up'),
             sg.Input(str(self.current_path), key='-PATH-', expand_x=True),
             sg.Button('Go', key='-GOTO-')]
        ]
        
        # File list
        file_list_layout = [
            [sg.Table(values=[], 
                     headings=['', 'Name', 'Size', 'Modified', 'Path'],
                     key='-FILES-',
                     col_widths=[3, 20, 10, 15, 0],
                     justification='left',
                     alternating_row_color='lightgray',
                     selected_row_colors='blue on yellow',
                     enable_events=True,
                     expand_x=True,
                     expand_y=True,
                     num_rows=20,
                     right_click_menu=['', ['Copy', 'Cut', 'Paste', 'Delete', 'Rename', 'Properties']])]
        ]
        
        # Toolbar
        toolbar_layout = [
            [sg.Button('New Folder', key='-NEWFOLDER-'),
             sg.Button('Copy', key='-COPY-'),
             sg.Button('Cut', key='-CUT-'),
             sg.Button('Paste', key='-PASTE-'),
             sg.Button('Delete', key='-DELETE-'),
             sg.Button('Rename', key='-RENAME-'),
             sg.Button('Properties', key='-PROPERTIES-')]
        ]
        
        # Preview panel
        preview_layout = [
            [sg.Text('File Preview', font=('Arial', 12, 'bold'))],
            [sg.Image(key='-PREVIEW-IMAGE-', size=(300, 300))],
            [sg.Multiline('Select a file to preview', 
                         key='-PREVIEW-',
                         size=(40, 15),
                         disabled=True)]
        ]
        
        # Status bar
        status_layout = [
            [sg.StatusBar('Ready', key='-STATUS-', size=(100, 1))]
        ]
        
        # Main layout
        layout = [
            nav_layout,
            [sg.HSeparator()],
            toolbar_layout,
            [sg.HSeparator()],
            [sg.Column(file_list_layout, expand_x=True, expand_y=True),
             sg.VSeparator(),
             sg.Column(preview_layout, vertical_alignment='top')],
            [sg.HSeparator()],
            status_layout
        ]
        
        return layout
    
    def refresh_file_list(self, window):
        """Refresh the file list display"""
        contents = self.get_directory_contents(self.current_path)
        window['-FILES-'].update(values=contents)
        window['-PATH-'].update(str(self.current_path))
        
        # Update status
        dirs = sum(1 for item in contents if '<DIR>' in item[2])
        files = len(contents) - dirs
        window['-STATUS-'].update(f'{dirs} folders, {files} files')
    
    def run(self):
        sg.theme('LightBlue3')
        
        window = sg.Window('Advanced File Manager',
                          self.create_layout(),
                          finalize=True,
                          resizable=True,
                          size=(1000, 700))
        
        # Initial file list
        self.refresh_file_list(window)
        
        while True:
            event, values = window.read()
            
            if event == sg.WIN_CLOSED:
                break
            
            elif event == '-HOME-':
                self.current_path = Path.home()
                self.refresh_file_list(window)
                
            elif event == '-UP-':
                if self.current_path.parent != self.current_path:
                    self.current_path = self.current_path.parent
                    self.refresh_file_list(window)
                    
            elif event == '-GOTO-':
                try:
                    new_path = Path(values['-PATH-'])
                    if new_path.exists() and new_path.is_dir():
                        self.current_path = new_path
                        self.refresh_file_list(window)
                    else:
                        sg.popup_error('Invalid path')
                except Exception:
                    sg.popup_error('Invalid path')
                    
            elif event == '-FILES-':
                if values['-FILES-']:
                    row = values['-FILES-'][0]
                    contents = self.get_directory_contents(self.current_path)
                    if row < len(contents):
                        selected_item = contents[row]
                        file_path = selected_item[4]  # Full path
                        
                        # If double-click on directory, enter it
                        if Path(file_path).is_dir():
                            self.current_path = Path(file_path)
                            self.refresh_file_list(window)
                        else:
                            # Preview file
                            threading.Thread(
                                target=self.preview_file,
                                args=(file_path, window),
                                daemon=True
                            ).start()
            
            elif event == '-NEWFOLDER-':
                folder_name = sg.popup_get_text('Enter folder name:', 'New Folder')
                if folder_name:
                    try:
                        new_folder = self.current_path / folder_name
                        new_folder.mkdir()
                        self.refresh_file_list(window)
                    except Exception as e:
                        sg.popup_error(f'Error creating folder: {str(e)}')
            
            elif event in ['-COPY-', 'Copy']:
                if values['-FILES-']:
                    row = values['-FILES-'][0]
                    contents = self.get_directory_contents(self.current_path)
                    if row < len(contents):
                        self.clipboard = [contents[row][4]]
                        self.clipboard_operation = 'copy'
                        window['-STATUS-'].update(f'Copied: {Path(self.clipboard[0]).name}')
            
            elif event in ['-PASTE-', 'Paste']:
                if self.clipboard and self.clipboard_operation:
                    try:
                        for item in self.clipboard:
                            source = Path(item)
                            dest = self.current_path / source.name
                            
                            if self.clipboard_operation == 'copy':
                                if source.is_dir():
                                    shutil.copytree(source, dest)
                                else:
                                    shutil.copy2(source, dest)
                            elif self.clipboard_operation == 'cut':
                                shutil.move(source, dest)
                        
                        self.refresh_file_list(window)
                        window['-STATUS-'].update('Paste completed')
                        
                        if self.clipboard_operation == 'cut':
                            self.clipboard = []
                            self.clipboard_operation = None
                            
                    except Exception as e:
                        sg.popup_error(f'Error pasting: {str(e)}')
        
        window.close()

if __name__ == '__main__':
    fm = FileManager()
    fm.run()


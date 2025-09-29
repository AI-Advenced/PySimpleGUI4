import PySimpleGUI4 as sg
import sqlite3
import threading
from datetime import datetime

class DatabaseApp:
    def __init__(self):
        self.db_file = 'advanced_app.db'
        self.init_database()
        
    def init_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_layout(self):
        # Tab 1: Data Entry
        tab1_layout = [
            [sg.Text('Name:'), sg.Input(key='-NAME-', size=(30, 1))],
            [sg.Text('Email:'), sg.Input(key='-EMAIL-', size=(30, 1))],
            [sg.Button('Add User', key='-ADD-'), sg.Button('Clear', key='-CLEAR-')],
            [sg.Text('', size=(50, 1), key='-STATUS-')]
        ]
        
        # Tab 2: Data View
        tab2_layout = [
            [sg.Table(values=[], headings=['ID', 'Name', 'Email', 'Created'],
                     key='-TABLE-', justification='left',
                     alternating_row_color='lightgray',
                     selected_row_colors='red on yellow',
                     enable_events=True,
                     expand_x=True, expand_y=True,
                     num_rows=20)],
            [sg.Button('Refresh', key='-REFRESH-'),
             sg.Button('Delete Selected', key='-DELETE-'),
             sg.Button('Export CSV', key='-EXPORT-')]
        ]
        
        # Tab 3: Analytics
        tab3_layout = [
            [sg.Text('User Statistics', font=('Arial', 16))],
            [sg.Text('Total Users:', size=(20, 1)), sg.Text('', key='-TOTAL-', size=(10, 1))],
            [sg.Text('Users Today:', size=(20, 1)), sg.Text('', key='-TODAY-', size=(10, 1))],
            [sg.Canvas(key='-CANVAS-', size=(400, 300))],
            [sg.Button('Generate Report', key='-REPORT-')]
        ]
        
        layout = [
            [sg.TabGroup([
                [sg.Tab('Data Entry', tab1_layout, key='-TAB1-')],
                [sg.Tab('View Data', tab2_layout, key='-TAB2-')],
                [sg.Tab('Analytics', tab3_layout, key='-TAB3-')]
            ], key='-TABGROUP-', expand_x=True, expand_y=True)],
            [sg.StatusBar('Ready', key='-STATUSBAR-', size=(80, 1))]
        ]
        
        return layout
    
    def add_user(self, name, email):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)",
            (name, email, datetime.now())
        )
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        conn.close()
        return users
    
    def delete_user(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def run(self):
        sg.theme('DarkBlue3')
        window = sg.Window('Advanced Database Application', 
                          self.create_layout(), 
                          finalize=True,
                          resizable=True,
                          size=(800, 600))
        
        while True:
            event, values = window.read()
            
            if event == sg.WIN_CLOSED:
                break
                
            elif event == '-ADD-':
                if values['-NAME-'] and values['-EMAIL-']:
                    self.add_user(values['-NAME-'], values['-EMAIL-'])
                    window['-STATUS-'].update('User added successfully!', text_color='green')
                    window['-NAME-'].update('')
                    window['-EMAIL-'].update('')
                else:
                    window['-STATUS-'].update('Please fill all fields!', text_color='red')
                    
            elif event == '-CLEAR-':
                window['-NAME-'].update('')
                window['-EMAIL-'].update('')
                window['-STATUS-'].update('')
                
            elif event == '-REFRESH-':
                users = self.get_all_users()
                window['-TABLE-'].update(values=users)
                window['-STATUSBAR-'].update(f'Loaded {len(users)} users')
                
            elif event == '-DELETE-':
                selected_rows = values['-TABLE-']
                if selected_rows:
                    users = self.get_all_users()
                    user_id = users[selected_rows[0]][0]
                    self.delete_user(user_id)
                    window['-TABLE-'].update(values=self.get_all_users())
        
        window.close()

if __name__ == '__main__':
    app = DatabaseApp()
    app.run()


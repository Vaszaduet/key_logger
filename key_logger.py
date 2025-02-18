import tkinter.messagebox
import pynput
import sqlite3
import tkinter as tk
import tkinter
import pystray
import threading
import sys
import socket
from pathlib import Path
from PIL import Image
from time import sleep
from win32com.client import Dispatch


# pyinstaller --onefile --windowed --icon=key_logger.ico --name=KeyLogger --add-data "key_logger.ico;." --hidden-import win32com.client --hidden-import pystray --hidden-import PIL --hidden-import sqlite3 --hidden-import pynput.keyboard --hidden-import tkinter key_logger.py

class Key_logger:
    '''The keys return in list "ten_keys" and upload to data base\n
    Use method "start"'''

    def __init__(self, window: tk.Tk, lbl_last, lbl_monitoring, btn_startup, btn_speed_db, icon_path):
        self.window = window
        self.btn_startup = btn_startup
        self.btn_speed_db = btn_speed_db
        self.labels_last = lbl_last
        self.label_monitoring = lbl_monitoring
        self.ten_keys = ['' for n in range(10)]
        self.listener = pynput.keyboard.Listener(on_release=self.released)
        self.path = Path().home() /'key_logger.db'
        self.icon = Image.open(icon_path)
        self.window.iconbitmap(icon_path)
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.tray = self.create_tray_icon()
        self.dct_speed_db = {'slow': 3000, 'normal': 1000, 'fast': 100}
        self.dct_startup = {'activated': True, 'deactivated': False}
        self.count_keys = {}
        for key in 'qwertyuiopasdfghjklzxcvbnm'.upper():
            self.count_keys[key] = 0

    def __str__(self):
        return 'You are gay'
    def released(self, key):
        try:
            vk = key.vk
            if 65 <= vk <= 90:
                checked_key = chr(vk)
                self.count_keys[checked_key] += 1
                self.ten_keys.append(checked_key)
                self.ten_keys.pop(0)
                idx = 9
                for key in reversed(self.ten_keys):
                    self.labels_last[idx]['text'] = key
                    idx -= 1
                    sleep(0.003)
        except:
            return

    def start(self):
        self.listener.start()
        if not self.path.exists():
            self.connection = sqlite3.connect(self.path)
            self.cursor = self.connection.cursor()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Counter_keys(
            Key TEXT,
            Count INT
            )''')
            for key in tuple(self.count_keys.items()):
                self.cursor.execute('INSERT INTO Counter_keys VALUES(?,?)', key)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Configure(
            Setting TEXT,
            Value TEXT
            )''')
            self.cursor.execute('INSERT INTO Configure VALUES(?,?)', ('Startup', 'deactivated'))
            self.cursor.execute('INSERT INTO Configure VALUES(?,?)', ('Speed_db', 'normal'))
        else:
            self.connection = sqlite3.connect(self.path)
            self.cursor = self.connection.cursor()
        self.cursor.execute('SELECT * FROM Configure')
        self.settings = dict(self.cursor.fetchall())
        self.btn_startup['text'] = f'Startup: {self.settings["Startup"]}'
        self.btn_speed_db['text'] = f'Refresh DB: {self.settings["Speed_db"]}'
        if len(sys.argv) > 1 and sys.argv[1] == '--startup':
            self.close_window()

        self.check_db()
    def stop(self):
        self.listener.stop()
        self.connection.commit()
        self.connection.close()
    
    def update_db(self):
        self.cursor.execute('SELECT * FROM Counter_keys')
        db = dict(self.cursor.fetchall())
        for key in db:
            self.cursor.execute('UPDATE Counter_keys SET Count=? WHERE Key=?', (db[key]+self.count_keys[key], key))
            self.count_keys[key] = 0
        self.connection.commit()

    def check_db(self):
        self.update_db()
        self.cursor.execute('SELECT * FROM Counter_keys')
        db = self.cursor.fetchall()
        db = sorted(db, key=lambda x: x[1], reverse=True)
        one_percent = sum(x[1] for x in db) / 100
        keys_monitoring = ''
        try:
            for key in db:
                keys_monitoring += f'{key[0]} - {key[1]} ({key[1]/one_percent:.2f}%)\n'
        except ZeroDivisionError:
            pass
        self.label_monitoring['text'] = keys_monitoring
        window.after(self.dct_speed_db[self.settings['Speed_db']], self.check_db)

    def close_window(self):
        self.window.withdraw()

    def create_tray_icon(self):
        def show_window():
            self.window.deiconify()
        def quit_app():
            icon.stop()
            window.destroy()
            logger.stop()
        menu = (
            pystray.MenuItem("Open", show_window, default=True),
            pystray.MenuItem("Quit", quit_app),
        )
        icon = pystray.Icon("Key Logger", self.icon, "Key Logger", menu)
        threading.Thread(target=icon.run, daemon=True).start()
        return icon

    def clear_db(self):
        answer_del = tkinter.messagebox.askquestion('Clear data base', 'Are you sure you want to clear up the data base?', icon='warning')
        if answer_del == 'yes':
            self.cursor.execute('UPDATE Counter_keys SET Count=0')
            self.connection.commit()
        else:
            return

    def startup(self):
        if sys.platform == 'win32':
            startup_path = Path().home() / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
        elif sys.platform == 'darwin':  # macOS
            startup_path = Path().home() / 'Library' / 'LaunchAgents'
        elif sys.platform == 'linux':  # Linux
            startup_path = Path().home() / '.config' / 'autostart'
        app_name = 'keylogger'
        if getattr(sys, 'frozen', False):
            current_file = Path(sys.executable)
        else:
            current_file = Path(__file__).absolute()
        if self.settings['Startup'] == 'activated':
            if sys.platform == 'win32':
                (startup_path / f'{app_name}.lnk').unlink(missing_ok=True)
            elif sys.platform == 'darwin':
                (startup_path / f'com.{app_name}.plist').unlink(missing_ok=True)
            elif sys.platform == 'linux':
                (startup_path / f'{app_name}.desktop').unlink(missing_ok=True)
            self.settings['Startup'] = 'deactivated'
        else:
            startup_path.mkdir(parents=True, exist_ok=True)
            if sys.platform == 'win32':
                shortcut = Dispatch('WScript.Shell').CreateShortCut(str(startup_path / f'{app_name}.lnk'))
                shortcut.Targetpath = str(current_file)
                shortcut.Arguments = '--startup'
                shortcut.WorkingDirectory = str(current_file.parent)
                shortcut.save()
            elif sys.platform == 'darwin':
                plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
                <plist version="1.0">
                <dict>
                    <key>Label</key>
                    <string>com.{app_name}</string>
                    <key>ProgramArguments</key>
                    <array>
                        <string>python3</string>
                        <string>{current_file}</string>
                    </array>
                    <key>RunAtLoad</key>
                    <true/>
                </dict>
                </plist>'''
                (startup_path / f'com.{app_name}.plist').write_text(plist_content)
            elif sys.platform == 'linux':
                desktop_entry = f'''[Desktop Entry]
                Type=Application
                Name={app_name}
                Exec=python3 {current_file}
                Terminal=false
                X-GNOME-Autostart-enabled=true'''
                (startup_path / f'{app_name}.desktop').write_text(desktop_entry)
            self.settings['Startup'] = 'activated'
        self.btn_startup['text'] = f'Startup: {self.settings["Startup"]}'
        self.cursor.execute('UPDATE Configure SET Value=? WHERE Setting=?', (self.settings['Startup'], 'Startup'))
        self.connection.commit()

    def speed_db(self):
        if self.settings['Speed_db'] == 'slow':
            self.settings['Speed_db'] = 'normal'
            self.btn_speed_db['text'] = f'Refresh DB: {self.settings['Speed_db']}'
            self.cursor.execute('UPDATE Configure SET Value=? WHERE Setting=?', ('normal', 'Speed_db'))
            self.connection.commit()
        elif self.settings['Speed_db'] == 'normal':
            self.settings['Speed_db'] = 'fast'
            self.btn_speed_db['text'] = f'Refresh DB: {self.settings['Speed_db']}'
            self.cursor.execute('UPDATE Configure SET Value=? WHERE Setting=?', ('fast', 'Speed_db'))
            self.connection.commit()
        else:
            self.settings['Speed_db'] = 'slow'
            self.btn_speed_db['text'] = f'Refresh DB: {self.settings['Speed_db']}'
            self.cursor.execute('UPDATE Configure SET Value=? WHERE Setting=?', ('slow', 'Speed_db'))
            self.connection.commit()
        

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 18945))
except socket.error:
    sys.exit(0)

window = tk.Tk()
window.title('Key logger')
window.resizable(False, False)
window.configure(background='#160c66')
frm_last = tk.Frame(master=window, background='#160c66')
frm_monitoring = tk.Frame(master=window, background='#231874', relief='raised', borderwidth=5)
frm_last.grid(column=0, row=1, sticky='nsew', padx=10, pady=10)
frm_monitoring.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)
lbl_monitoring = tk.Label(master=frm_monitoring, font=('Arial', 18), width=30, height=10, anchor='n', background='#231874', foreground='white')
lbl_monitoring.grid(columnspan=3, row=0, sticky='nsew')

labels_last = {}
for lbl in range(10):
    labels_last[lbl] = tk.Label(master=frm_last, font=('Arial', 20), background='#1a0f66', foreground='#0f0846',
                                highlightbackground='#190e66', highlightthickness=3)
    labels_last[lbl].pack(side=tk.BOTTOM)

btn_clear_db = tk.Button(master=frm_monitoring, text='Clear DB', font=('Arial', 11), background='#1a0f66', foreground='white', command=lambda: logger.clear_db(), relief='raised')
btn_startup = tk.Button(master=frm_monitoring, text='Startup:', font=('Arial', 11), background='#1a0f66', foreground='white', command=lambda: logger.startup(), relief='raised')
btn_speed_db = tk.Button(master=frm_monitoring, text='Refresh DB:', font=('Arial', 11), background='#1a0f66', foreground='white', command=lambda: logger.speed_db(), relief='raised')
btn_clear_db.grid(columnspan=3, row=1, pady=3)
btn_startup.grid(column=0, row=1, sticky='w', padx=5)
btn_speed_db.grid(column=2, row=1, sticky='e', padx=5)

logger = Key_logger(window, labels_last, lbl_monitoring, btn_startup, btn_speed_db, icon_path='key_logger.ico')
logger.start()
window.mainloop()
logger.stop()

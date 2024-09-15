import platform
import os
from tkinter import messagebox, filedialog
from tkinter import *
from pygame import mixer
import translations as key
try:
    import winreg
except:
    import plistlib

import requests
import zipfile

icon_path = os.path.join('resources', 'bepinstaller.ico')

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        # Create a temporary label to calculate text width
        temp_label = Label(self.widget, text=self.text, background="#353738", fg="#edf2f4", font=("Calibri", 10))
        temp_label.pack()
        text_width = temp_label.winfo_reqwidth()
        temp_label.destroy()

        # Get widget position and calculate center
        x, y, _, _ = self.widget.bbox(key.WIDGETS_INSERT)
        x += self.widget.winfo_rootx()
        y += self.widget.winfo_rooty() + 25

        # Center the tooltip horizontally
        x_centered = x + (self.widget.winfo_width() - text_width) // 2

        # Create tooltip window
        self.tooltip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x_centered}+{y}")
        label = Label(tw, text=self.text, background="#353738", fg="#edf2f4", relief="solid", borderwidth=1, font=("Calibri", 10))
        label.pack()


    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class InterfaceMenu:
    def __init__(self):
        self.root = Tk()
        mixer.init()
        self.root.configure(background="#353738")
        self.root.geometry("400x335")
        self.root.resizable(0, 0)
        self.root.title(key.ROOT_TITLE)
        self.root.iconbitmap(icon_path)

        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.steam_frame = Frame(self.main_frame, background="#353738")
        self.nonsteam_frame = Frame(self.main_frame, background="#353738")

        # Steam installation page
        self.create_steam_page(self.steam_frame)
        # Non-Steam installation page
        self.create_nonsteam_page(self.nonsteam_frame)

        # Show steam frame by default
        self.current_frame = self.steam_frame
        self.show_frame(self.current_frame)

        # Create toggle button
        nav_frame = Frame(self.root, background="#353738")
        nav_frame.pack()
        self.toggle_button = Button(nav_frame, text=key.NON_STEAM, bg="#353738", fg="#edf2f4",
                                    command=self.toggle_installation_mode)
        self.toggle_button.grid(row=0, column=0, padx=10, pady=(10, 10))

        self.root.mainloop()

    def show_frame(self, frame_to_show):
        """Show only the selected frame and hide the others."""
        self.steam_frame.pack_forget()  # Hide Steam frame
        self.nonsteam_frame.pack_forget()  # Hide Non-Steam frame
        frame_to_show.pack(fill="both", expand=True)  # Show the selected frame

    def toggle_installation_mode(self):
        """Toggle between Steam and Non-Steam installation pages."""
        if self.current_frame == self.steam_frame:
            self.current_frame = self.nonsteam_frame
            self.toggle_button.config(text=key.STEAM_INSTALL)
        else:
            self.current_frame = self.steam_frame
            self.toggle_button.config(text=key.NON_STEAM_INSTALL)
        self.show_frame(self.current_frame)

    def create_steam_page(self, parent):
        frame = Frame(parent, background="#353738")
        frame.pack(fill="both", expand=True)

        heading = Label(frame, text=key.ROOT_SHORT_TITLE, font=("Calibri", 18), background="#353738", fg="#edf2f4")
        heading.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
        
        Label(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12), text="Game Name Folder").grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        self.game_folder_entry = Entry(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12))
        self.game_folder_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")
        Tooltip(self.game_folder_entry, key.STEAM_COMMON_DIR_PROMPT)

        def auto_find_steam_directory():
            foldername = self.game_folder_entry.get()
            steampath = self.steam_dir_entry.get()
            if not os.path.isdir(os.path.join(steampath, foldername)):
                # Try to find the correct Steam directory
                steam_path = find_steam_directory(foldername)
                if not steam_path:
                    messagebox.showerror(key.ERRORS_GAMENOTFOUND_TITLE,
                                        key.ERRORS_GAMENOTFOUND_DESC + f" \"{os.path.join(steam_path, foldername)}\"",
                                        parent=self)
                    return False
                
                self.steam_dir_entry.delete(0, "end")
                self.steam_dir_entry.insert(0, steam_path)
            elif steampath==find_steam_directory(foldername):
                messagebox.showinfo("Steam Directory Already Set", "The correct Steam directory has already been set.")
            else:
                messagebox.showwarning("Something went wrong :(", f"Directory {os.path.join(steampath, foldername)} does not exist.")
            frame.focus()

        Label(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12), text="Steam Directory").grid(row=3, column=0, padx=10, pady=(5, 5), sticky="e")
        Button(frame, text="Auto Find Steam Directory", bg="#353738", fg="#edf2f4", command=auto_find_steam_directory).grid(row=3, column=0, padx=10, pady=(5, 5), sticky="w")
        self.steam_dir_entry = Entry(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12))
        self.steam_dir_entry.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")
        Tooltip(self.steam_dir_entry, "Enter the Steam installation directory. Auto-detection available.")

        def install_bepinex():
            foldername = self.game_folder_entry.get()
            steam_dir = self.steam_dir_entry.get()

            if not foldername.strip():
                messagebox.showerror("Error", "Game Name Folder cannot be empty.")
                return
            if not steam_dir.strip():
                messagebox.showerror("Error", "Steam Directory cannot be empty.")
                return

            if steam_dir and os.path.isdir(os.path.join(steam_dir, foldername)):
                architecture = get_system_architecture()
                download_url = get_bepinex_download_url(architecture)
                dest = os.path.join(os.getcwd(), "resources/BepInEx.zip")
                if not os.path.isdir(os.path.join(steam_dir, foldername, "BepInEx")):
                    download_file(download_url, dest)
                    extract_zip(dest, os.path.join(steam_dir, foldername))
                    os.remove(dest)
                    doorstop_dest = os.path.join(steam_dir, foldername, ".doorstop_version")
                    if os.path.exists(doorstop_dest):
                        os.remove(doorstop_dest)
                    messagebox.showinfo("BepInEx Installed", "BepInEx has been installed. Please run the game once, then exit.")
                else:
                    messagebox.showinfo("BepInEx Already Installed", f"BepInEx is already installed in {os.path.join(steam_dir, foldername)}")
            else:
                messagebox.showerror("Error", "Invalid directory: The game folder does not exist.")
                
        

        Button(frame, text="Install BepInEX", bg="#353738", fg="#edf2f4", command=install_bepinex).grid(row=5, column=0, columnspan=2, padx=10, pady=(10, 20))

        # Configure grid columns to ensure centering
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_rowconfigure(4, weight=1)
        frame.grid_rowconfigure(5, weight=1)


    def create_nonsteam_page(self, parent):
        frame = Frame(parent, background="#353738")
        frame.pack(fill="both", expand=True)

        heading = Label(frame, text="Non-Steam Installer", font=("Calibri", 18), background="#353738", fg="#edf2f4")
        heading.grid(row=0, column=0, columnspan=2, pady=15, sticky="ew")

        Label(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12), text="Game Directory").grid(row=1, column=0, columnspan=2, padx=10, sticky="ews")
        self.game_dir_entry = Entry(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12))
        self.game_dir_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ewn")

        Tooltip(self.game_dir_entry, "Enter the full directory path for the game installation.")

        def install_bepinex_nonsteam():
            foldername = self.game_dir_entry.get()

            if not foldername.strip():
                messagebox.showerror("Error", "Game Directory cannot be empty.")
                return

            if os.path.isdir(foldername):
                architecture = get_system_architecture()
                download_url = get_bepinex_download_url(architecture)
                dest = os.path.join(os.getcwd(), "resources/BepInEx.zip")
                if not os.path.isdir(os.path.join(foldername, "BepInEx")):
                    download_file(download_url, dest)
                    extract_zip(dest, foldername)
                    os.remove(dest)
                    doorstop_dest = os.path.join(foldername, ".doorstop_version")
                    if os.path.exists(doorstop_dest):
                        os.remove(doorstop_dest)
                    messagebox.showinfo("BepInEx Installed", "BepInEx has been installed. Please run the game once, then exit.")
                else:
                    messagebox.showinfo("BepInEx Already Installed", f"BepInEx is already installed in {foldername}")
            else:
                messagebox.showerror("Error", "Invalid directory: The specified directory does not exist.")

        def open_folder():
            dest = game_dir_prompt()  
            if dest:
                self.game_dir_entry.delete(0, "end")
                self.game_dir_entry.insert(0, dest)

        def game_dir_prompt():
            root = Tk()
            root.withdraw()
            steam_path = filedialog.askdirectory(title="Select Non-Steam Game Directory")
            if steam_path and os.path.exists(os.path.join(steam_path, "steamapps", "common")):
                return steam_path
            else:
                messagebox.showerror("Error", "Path " + os.path.join(steam_path, "steamapps", "common") + " doesn't exist")
            return None

        # Create a label to explain the "Open Folder" button
        # open_folder_label = Label(frame, text="Click 'Open Folder' to select your game directory", background="#353738", fg="#edf2f4", font=("Calibri", 10))
        # open_folder_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")

        # Place the "Open Folder" button directly below the explanatory label
        open_folder_btn = Button(frame, text="Open Folder", bg="#353738", fg="#edf2f4", command=open_folder)
        open_folder_btn.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="ewn")
        Tooltip(open_folder_btn, "Click 'Open Folder' to select your game directory or type it in yourself")

        # Add an empty row for spacing
        frame.grid_rowconfigure(5, minsize=20)

        # Place the "Install BepInEX" button below the spacing row
        Button(frame, text="Install BepInEX", bg="#353738", fg="#edf2f4", command=install_bepinex_nonsteam).grid(row=6, column=0, columnspan=2, padx=10, pady=(5, 10))

        # Configure grid columns to ensure centering
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_rowconfigure(4, weight=1)
        frame.grid_rowconfigure(6, weight=1)

def find_steam_directory(folder_name):
    steam_path = get_steam_directory()
    if steam_path and os.path.exists(os.path.join(steam_path, "steamapps", "common", folder_name)):
        return os.path.join(steam_path, "steamapps", "common")

    # Check common custom drive locations
    common_drives = ["C:", "D:", "E:", "F:", "Z:"]
    for drive in common_drives:
        possible_path = os.path.join(drive, "SteamLibrary", "steamapps", "common")
        if os.path.exists(os.path.join(possible_path, folder_name)):
            return possible_path
        
        program_files_path = os.path.join(drive, "Program Files", "Steam", "steamapps", "common", folder_name)
        if os.path.exists(program_files_path):
            return os.path.join(drive, "Program Files", "Steam", "steamapps", "common")
        
        program_files_x86_path = os.path.join(drive, "Program Files (x86)", "Steam", "steamapps", "common", folder_name)
        if os.path.exists(program_files_x86_path):
            return os.path.join(drive, "Program Files (x86)", "Steam", "steamapps", "common")
    return None

def get_steam_directory():
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
        steam_path = winreg.QueryValueEx(reg_key, "InstallPath")[0]
        winreg.CloseKey(reg_key)
        return steam_path
    except FileNotFoundError:
        return None

def get_system_architecture():
    architecture = platform.architecture()[0]
    return 'x64' if '64' in architecture else 'x86'

def get_bepinex_download_url(architecture):
    base_url = "https://github.com/BepInEx/BepInEx/releases/download/v5.4.23.2/BepInEx"
    os_system = platform.system()
    if os_system == "Windows":
        return f"{base_url}_win_{architecture}_5.4.23.2.zip"
    elif os_system == "Linux":
        return f"{base_url}_linux_{architecture}_5.4.23.2.zip"
    elif os_system == "Darwin":
        return f"{base_url}_macos_x64_5.4.23.2.zip"
    else:
        messagebox.showerror("Error", "Unsupported OS detected.")
        return None

def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def extract_zip(file_path, extract_to):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


if __name__ == "__main__":
    InterfaceMenu()

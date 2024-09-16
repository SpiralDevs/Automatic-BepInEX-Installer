import platform
import os
from tkinter import messagebox, filedialog, ttk, StringVar
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
        self.root.geometry("435x425")
        self.root.resizable(0, 0)
        self.root.title(key.ROOT_TITLE)
        self.root.iconbitmap(icon_path)

        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.steam_frame = Frame(self.main_frame, background="#353738")
        self.nonsteam_frame = Frame(self.main_frame, background="#353738")
        
        self.bepinex_versions = self.get_bepinex_versions()
        self.selected_version = StringVar(self.root)
        self.selected_version.set(self.get_default_stable_version()) # Default to most recent stable version
        
        self.scripting_backend = "Mono"

        # Steam installation page
        self.create_steam_page(self.steam_frame)
        
        # Non-Steam installation page
        self.create_nonsteam_page(self.nonsteam_frame)

        # Show steam frame by  default
        self.current_frame = self.steam_frame
        self.show_frame(self.current_frame)

        # Create togglle button
        nav_frame = Frame(self.root, background="#353738")
        nav_frame.pack()
        self.toggle_button = Button(nav_frame, text=key.NON_STEAM_INSTALL, bg="#353738", fg="#edf2f4",
                                    command=self.toggle_installation_mode)
        self.toggle_button.grid(row=0, column=0, padx=10, pady=(10, 10))
        
        self.root.mainloop()
    
    def get_bepinex_versions(self):
        releases = []
        url = "https://api.github.com/repos/BepInEx/BepInEx/releases"
        
        while url:
            response = requests.get(url)
            if response.status_code == 200:
                releases_data = response.json()
                releases.extend([release['tag_name'] for release in releases_data])
                
                # Check if there is a "next" page
                if 'next' in response.links:
                    url = response.links['next']['url']
                else:
                    url = None
            else:
                # print(f"Error fetching versions: {response.status_code}")
                return ["5.4.21", "6.0.0-pre.1", "6.0.0-pre.2"]  # Default falback

        return releases
    
    def get_default_stable_version(self):
        stable_versions = [version for version in self.bepinex_versions if 'pre' not in version and 'RC' not in version] # Filters out any pre or RC(release canidate) versions
        
        if stable_versions:
            return stable_versions[0]  # Return the latest stable version
        else:
            return self.bepinex_versions[0]  # Fallback 

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

        heading = Label(frame, text=key.ROOT_STEAM, font=("Calibri", 18), background="#353738", fg="#edf2f4")
        heading.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
        
        Label(frame, text=key.SELECTBEPINEX, background="#353738", fg="#edf2f4", font=("Calibri", 12)).grid(row=5, column=0, columnspan=2, padx=10, pady=(5, 5), sticky="ew")
        version_dropdown = OptionMenu(frame, self.selected_version, *self.bepinex_versions)
        version_dropdown.config(background="#353738", fg="#edf2f4", font=("Calibri", 12))
        version_dropdown.grid(row=6, column=0, columnspan=2, padx=10, pady=(5, 20), sticky="")

        Label(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12), text=key.STEAM_GAMENAMEFOLDER).grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        self.game_folder_entry = Entry(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12))
        self.game_folder_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")
        Tooltip(self.game_folder_entry, key.TOOLTIP_GAMENAMEFOLDER)

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
                messagebox.showinfo(key.INFO_STEAMALREADYSET_TITLE, key.INFO_STEAMALREADYSET_TITLE)
            else:
                messagebox.showerror(key.ERRORS_GAMENOTFOUND_TITLE, key.ERRORS_GAMENOTFOUND_DESC + f" \"{os.path.join(steam_path, foldername)}\"")
            frame.focus()

        Label(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12), text=key.STEAM_STEAMDIR).grid(row=3, column=0, padx=10, pady=(5, 5), sticky="e")
        
        Button(frame, text=key.STEAM_AUTOFINDDIR, bg="#353738", fg="#edf2f4", command=auto_find_steam_directory).grid(row=3, column=0, padx=10, pady=(5, 5), sticky="w")
        
        self.steam_dir_entry = Entry(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12))
        self.steam_dir_entry.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")
        Tooltip(self.steam_dir_entry, key.TOOLTIP_ENTERSTEAMDIR)

        def install_bepinex():
            foldername = self.game_folder_entry.get()
            steam_dir = self.steam_dir_entry.get()
            version = self.selected_version.get()
            scripting_backend = detect_scripting_backend(os.path.join(steam_dir, foldername))

            if not foldername.strip():
                messagebox.showerror(key.ERRORS_EMPTYGAMEFOLDER_TITLE, key.ERRORS_EMPTYGAMEFOLDER_DESC)
                return
            if not steam_dir.strip():
                messagebox.showerror(key.ERRORS_EMPTYSTEAMDIR_TITLE, key.ERRORS_EMPTYSTEAMDIR_DESC)
                return

            if steam_dir and os.path.isdir(os.path.join(steam_dir, foldername)):
                architecture = get_system_architecture()
                download_url = get_bepinex_download_url(architecture, version, scripting_backend)
                dest = os.path.join(os.getcwd(), "resources/BepInEx.zip")
                if not os.path.isdir(os.path.join(steam_dir, foldername, "BepInEx")):
                    download_file(download_url, dest)
                    extract_zip(dest, os.path.join(steam_dir, foldername))
                    os.remove(dest)
                    doorstop_dest = os.path.join(steam_dir, foldername, ".doorstop_version")
                    if os.path.exists(doorstop_dest):
                        os.remove(doorstop_dest)
                    messagebox.showinfo(key.INFO_BEPINEXINSTALLED_TITLE, key.INFO_BEPINEXINSTALLED_DESC)
                else:
                    messagebox.showinfo(key.INFO_BEPINEXALREADYADDED_TITLE, key.INFO_BEPINEXALREADYADDED_DESC + foldername)
            else:
                messagebox.showerror(key.ERRORS_INVALIDDIR_TITLE, key.ERRORS_INVALIDDIR_DESC)
                
        
        Button(frame, text=key.INSTALL_BEPINEX, bg="#353738", fg="#edf2f4", command=install_bepinex).grid(row=7, column=0, columnspan=2, padx=10, pady=(10, 20))

        # Configure grid columns to ensure centering
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_rowconfigure(4, weight=1)
        frame.grid_rowconfigure(5, weight=1)
        frame.grid_rowconfigure(6, weight=1)
        frame.grid_rowconfigure(7, weight=1)


    def create_nonsteam_page(self, parent):
        frame = Frame(parent, background="#353738")
        frame.pack(fill="both", expand=True)

        heading = Label(frame, text=key.NON_STEAM_INSTALL, font=("Calibri", 18), background="#353738", fg="#edf2f4")
        heading.grid(row=0, column=0, columnspan=2, pady=15, sticky="ews")

        Label(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12), text=key.NONSTEAM_GAMEDIR).grid(row=1, column=0, columnspan=2, padx=10, sticky="ews")
        self.game_dir_entry = Entry(frame, background="#353738", fg="#edf2f4", font=("Calibri", 12))
        self.game_dir_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=0, sticky="ewn")

        Tooltip(self.game_dir_entry, key.TOOLTIP_ENTERDIR)

        def install_bepinex_nonsteam():
            foldername = self.game_dir_entry.get()
            version = self.selected_version.get()
            scripting_backend = detect_scripting_backend(foldername)
            
            if not foldername.strip():
                messagebox.showerror(key.ERRORS_EMPTYGAMEDIR_TITLE, key.ERRORS_EMPTYGAMEDIR_DESC)
                return

            if os.path.isdir(foldername):
                architecture = get_system_architecture()
                download_url = get_bepinex_download_url(architecture, version,scripting_backend)
                dest = os.path.join(os.getcwd(), "resources/BepInEx.zip")
                if not os.path.isdir(os.path.join(foldername, "BepInEx")):
                    download_file(download_url, dest)
                    extract_zip(dest, foldername)
                    os.remove(dest)
                    doorstop_dest = os.path.join(foldername, ".doorstop_version")
                    if os.path.exists(doorstop_dest):
                        os.remove(doorstop_dest)
                    messagebox.showinfo(key.INFO_BEPINEXINSTALLED_TITLE, key.INFO_BEPINEXINSTALLED_DESC)
                else:
                    messagebox.showinfo(key.INFO_BEPINEXALREADYADDED_TITLE, key.INFO_BEPINEXALREADYADDED_DESC + foldername)
            else:
                messagebox.showerror(key.ERRORS_INVALIDDIR_TITLE, key.ERRORS_INVALIDDIR_DESC)

        def open_folder():
            dest = game_dir_prompt()  
            if dest:
                self.game_dir_entry.delete(0, "end")
                self.game_dir_entry.insert(0, dest)

        def game_dir_prompt():
            root = Tk()
            root.withdraw()
            steam_path = filedialog.askdirectory(title=key.NONSTEAM_ASKDIR)
            if steam_path and os.path.exists(os.path.join(steam_path, "steamapps", "common")):
                return steam_path
            else:
                messagebox.showerror(key.ERRORS_INVALIDPATH_TITLE, key.ERRORS_INVALIDPATH_DESC + os.path.join(steam_path, "steamapps", "common"))
            return None

        # Place the "Open Folder" button directly below the explanatory label
        open_folder_btn = Button(frame, text=key.NONSTEAM_OPENFOLDER, bg="#353738", fg="#edf2f4", command=open_folder)
        open_folder_btn.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        Tooltip(open_folder_btn, key.TOOLTIP_OPENDIR)
        
        Label(frame, text=key.SELECTBEPINEX, background="#353738", fg="#edf2f4", font=("Calibri", 12)).grid(row=4, column=0, columnspan=2, padx=10, pady=(5, 5), sticky="ew")
        version_dropdown = OptionMenu(frame, self.selected_version, *self.bepinex_versions)
        version_dropdown.config(background="#353738", fg="#edf2f4", font=("Calibri", 12))
        version_dropdown.grid(row=6, column=0, columnspan=2, padx=10, pady=(5, 70), sticky="")

        # Add an empty row for spacing
        frame.grid_rowconfigure(9, minsize=20)

        # Place the "Install BepInEX" button below the spacing row
        Button(frame, text=key.INSTALL_BEPINEX, bg="#353738", fg="#edf2f4", command=install_bepinex_nonsteam).grid(row=9, column=0, columnspan=2, padx=10, pady=(5, 50))

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

def generate_urls(base_url, architecture, version, os_system, scripting_backend):
    nov = version.replace("v", "")
    nop = scripting_backend.replace(".", "")
    suffixes = [
        f"{base_url}_{os_system.lower()}_{architecture}_{nov}.zip",
        f"{base_url}_{os_system.lower()}_{architecture}_{nov}.0.zip",
        f"{base_url}_{os_system.lower()}_{architecture}_{nov}.0.0.zip",
        f"{base_url}_{architecture}_{nov}.zip",
        f"{base_url}_{architecture}_{nov}.0.zip",
        f"{base_url}_{architecture}_{nov}.0.0.zip",
        f"{base_url}-{scripting_backend}-{os_system.lower()}-{architecture}-{nov}.zip",
        f"{base_url}-{scripting_backend}-{os_system.lower()}-{architecture}-{nov}.0.zip",
        f"{base_url}-{scripting_backend}-{os_system.lower()}-{architecture}-{nov}.0.0.zip",
        f"{base_url}_{nop}_{architecture}_{nov}.zip",
        f"{base_url}_{nop}_{architecture}_{nov}.0.zip",
        f"{base_url}_{nop}_{architecture}_{nov}.0.0.zip",
        f"{base_url}_{version}.zip"
    ]
    return suffixes

def get_bepinex_download_url(architecture, version, scripting_backend):
    base_url = f"https://github.com/BepInEx/BepInEx/releases/download/{version}/BepInEx"
    os_system = platform.system()

    if os_system not in ["Windows", "Linux", "Darwin"]:
        messagebox.showerror(key.ERRORS_UNSUPPORTEDOS_TITLE, key.ERRORS_UNSUPPORTEDOS_DESC)
        return None

    os_system = "win" if os_system == "Windows" else "linux" if os_system == "Linux" else "macos_x64"
    urls = generate_urls(base_url, architecture, version, os_system, scripting_backend)

    for url in urls:
        try:
            response = requests.head(url, allow_redirects=True)
            if response.status_code == 200:
                return url
        except requests.RequestException as e:
            print(f"Failed to retrieve URL: {url}, Error: {e}")

    messagebox.showerror(key.ERRORS_NOVALIDURL_TITLE, key.ERRORS_NOVALIDURL_DESC)
    return None

def detect_scripting_backend(game_directory): # REQUIRED FOR VERSIONS 6.0.0 PRE 1 AND HIGHER
    # List of known IL2CPP files
    il2cpp_files = [
        "GameAssembly.dll",
        "global-metadata.dat",
        "libil2cpp.so",
        "GameAssembly.dll",
        # Add other common IL2CPP files here
    ]
    
    # List of known Mono files
    mono_files = [
        "Assembly-CSharp.dll",
        "mono.dll",
        "libmono.so",
        # Add other common Mono files here
    ]
    data_folder = None
    for folder in os.listdir(game_directory):
        if folder.endswith('_Data') and os.path.isdir(os.path.join(game_directory, folder)):
            data_folder = os.path.join(game_directory, folder)
            break

    if not data_folder:
        return "No _Data folder found in the game directory"
    
    # Check for Mono files
    for file in mono_files:
        if os.path.isfile(os.path.join(data_folder, 'Managed', file)):
            return "Unity.Mono"
        elif os.path.isfile(os.path.join(game_directory, file)):
            return "Unity.Mono"
    
    # Check for IL2CPP files
    for file in il2cpp_files:
        if os.path.isfile(os.path.join(data_folder, file)):
            return "Unity.IL2CPP"
        elif os.path.isfile(os.path.join(game_directory, file)):
            return "Unity.IL2CPP"
    
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

import os
import sys
import shutil
import subprocess

def build():
    print("Installing PyInstaller...")
    # Ensure PyInstaller is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    import customtkinter
    customtkinter_path = os.path.dirname(customtkinter.__file__)
    print(f"CustomTkinter path found: {customtkinter_path}")
    
    # Run PyInstaller
    # --onefile packages everything into a single .exe
    # --windowed removes the command prompt pop-up when starting the application
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--add-data={customtkinter_path};customtkinter/",
        "--name=SunK Macro",
        "main.py"
    ]
    
    print("Running PyInstaller to compile code into a standalone binary...")
    subprocess.run(cmd, check=True)
    
    # Destination file
    exe_name = "SunK Macro.exe"
    dist_path = os.path.join("dist", exe_name)
    
    if os.path.exists(dist_path):
        # Locate user desktop folder
        desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
        desktop_dest = os.path.join(desktop_path, exe_name)
        
        # Clean up old AntigravityMacro.exe if it exists on the desktop
        old_exe_path = os.path.join(desktop_path, "AntigravityMacro.exe")
        if os.path.exists(old_exe_path):
            try:
                os.remove(old_exe_path)
                print(f"Removed old version: {old_exe_path}")
            except Exception as e:
                print(f"Warning: Could not remove old executable: {e}")
                
        print(f"Copying built executable to user desktop: {desktop_dest}")
        shutil.copy2(dist_path, desktop_dest)
        print("Success! stand-alone desktop executable successfully built.")
    else:
        print("Error: Could not locate built binary in dist/ directory.")

if __name__ == "__main__":
    build()

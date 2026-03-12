import os
import subprocess
import sys
import shutil

# --- Configuration for Code Signing (Optional) ---
SIGN_TOOL_PATH = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe" # Updated automatically
PFX_FILE = "MyCert.pfx"
PFX_PASSWORD = "Aleian123" # Update this password!
TIMESTAMP_URL = "http://timestamp.digicert.com"

def run_command(command):
    print(f"Running: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error:\n{stderr}")
        return False
    print(stdout)
    return True

def sign_file(file_path):
    if not os.path.exists(file_path):
        return False
    
    if not os.path.exists(PFX_FILE):
        print(f"Warning: Certificate file '{PFX_FILE}' not found. Skipping signing.")
        return False

    # Try to find signtool in PATH if specific path is invalid
    signtool = SIGN_TOOL_PATH
    if not os.path.exists(signtool):
        signtool = shutil.which("signtool")
    
    if not signtool:
         print("Warning: SignTool.exe not found. Skipping signing.")
         return False

    print(f"--- Signing {os.path.basename(file_path)} ---")
    cmd = f'"{signtool}" sign /f "{PFX_FILE}" /p "{PFX_PASSWORD}" /tr "{TIMESTAMP_URL}" /td sha256 /fd sha256 "{file_path}"'
    
    if run_command(cmd):
        print("File signed successfully!")
        return True
    else:
        print("Failed to sign file.")
        return False

def build_exe():
    print("--- Building Portable Executable (FileSMPy.exe) ---")
    # Clean previous build if necessary (optional)
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)
    
    # PyInstaller command
    # Using --onefile for portable version
    cmd = (
        'pyinstaller --noconfirm --onefile --windowed --name "FileSMPy" '
        '--icon "FolderSizeManagerPy 2 logo.ico" '
        '--add-data ".venv/Lib/site-packages/customtkinter;customtkinter" '
        '--hidden-import "packaging" --hidden-import "customtkinter" '
        '--hidden-import "darkdetect" --hidden-import "PIL" --hidden-import "PIL.Image" '
        '"main_modern.py"'
    )
    
    # Check if venv exists to use correct path for customtkinter
    if not os.path.exists(".venv"):
        # Try to find customtkinter in current python environment
        import customtkinter
        ctk_path = os.path.dirname(customtkinter.__file__)
        cmd = cmd.replace(".venv/Lib/site-packages/customtkinter", ctk_path)

    if run_command(cmd):
        print("Portable Executable built successfully in 'dist/FileSMPy.exe'")
        # Sign the portable executable
        sign_file("dist/FileSMPy.exe")
        return True
    else:
        print("Failed to build Portable Executable.")
        return False

def build_installer():
    print("\n--- Building Professional Installer (Install_FSMPy.exe) ---")
    # Check for Inno Setup Compiler
    iscc_path = shutil.which("iscc")
    
    # Common paths for Inno Setup if not in PATH
    if not iscc_path:
        possible_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                iscc_path = p
                break
    
    if iscc_path:
        print(f"Found Inno Setup Compiler at: {iscc_path}")
        cmd = f'"{iscc_path}" "setup_script.iss"'
        if run_command(cmd):
            print("Installer built successfully in 'dist/Install_FSMPy.exe'")
            # Sign the installer
            sign_file("dist/Install_FSMPy.exe")
            return True
        else:
            print("Failed to build Installer.")
            return False
    else:
        print("Inno Setup Compiler (ISCC) not found.")
        print("Please install Inno Setup 6 from https://jrsoftware.org/isdl.php")
        print("After installing, run this script again or right-click 'setup_script.iss' and select 'Compile'.")
        return False

def create_release_package():
    print("\n--- Creating Release Package ---")
    release_dir = "Release_Package"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)

    # Copy files
    files_to_copy = [
        ("dist/FileSMPy.exe", "FileSMPy_Portable.exe"),
        ("dist/Install_FSMPy.exe", "FileSMPy_Installer.exe"),
        ("MyCert.cer", "Certificate.cer")
    ]

    for src, dst_name in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(release_dir, dst_name))
            print(f"Copied {src} to {release_dir}/{dst_name}")
        else:
            print(f"Warning: {src} not found!")

    # Create README_INSTALL.txt
    readme_content = """FileSMPy - Folder Size Manager
==============================

Thank you for downloading FileSMPy!

CONTENTS
--------
1. FileSMPy_Portable.exe  : Standalone version (no installation required).
2. FileSMPy_Installer.exe : Professional Installer (adds shortcuts, context menu).
3. Certificate.cer        : Security certificate for trust.

INSTALLATION INSTRUCTIONS (IMPORTANT)
-------------------------------------
Since this application is signed with a Self-Signed Certificate, you need to install the certificate ONCE to avoid "Unknown Publisher" warnings.

1. Double-click "Certificate.cer".
2. Click "Install Certificate...".
3. Select "Local Machine" and click Next.
4. Select "Place all certificates in the following store".
5. Click Browse, select "Trusted Root Certification Authorities", and click OK.
6. Click Next, then Finish.

After this, you can run the Installer or Portable version without security warnings.

Developed by Aleian & Trae AI.
"""
    with open(os.path.join(release_dir, "README_INSTALL.txt"), "w") as f:
        f.write(readme_content)
    print("Created README_INSTALL.txt")

    # Zip the package
    shutil.make_archive("FileSMPy_Release", 'zip', release_dir)
    print(f"Release package created: FileSMPy_Release.zip")

if __name__ == "__main__":
    exe_built = build_exe()
    installer_built = build_installer()
    
    if exe_built or installer_built:
        create_release_package()

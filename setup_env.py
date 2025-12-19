import sys
import subprocess
import os
import platform

def install_dependencies():
    print("------------------------------------------------")
    print("🚀 SIGNFLOW ENTERPRISE - ENVIRONMENT SETUP")
    print("------------------------------------------------")

    major = sys.version_info.major
    minor = sys.version_info.minor
    
    print(f"ℹ️  Detected Python: {major}.{minor}")

    if major != 3 or (minor != 10 and minor != 11):
        print("\n❌ CRITICAL ERROR: Wrong Python Version.")
        print(f"   You are using Python {major}.{minor}, but MediaPipe requires 3.10 or 3.11.")
        print("   Please install Python 3.10 from python.org and try again.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    in_venv = (sys.prefix != sys.base_prefix)
    
    if not in_venv:
        print("⚠️  WARNING: Not running in a Virtual Environment.")
        print("   It is highly recommended to run the 'START_APP.bat' file instead of this script.")
        print("   Continuing anyway (this might mess up your global pip)...")
        time.sleep(2)

    print("\n📦 Installing Dependencies (This may take a few minutes)...")
    req_file = os.path.join(os.path.dirname(_file_), "requirements.txt")
    
    if not os.path.exists(req_file):
        print("❌ Error: requirements.txt not found!")
        sys.exit(1)

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("\n✅ Dependencies Installed Successfully.")
    except subprocess.CalledProcessError:
        print("\n❌ Error installing dependencies.")
        print("   Tip: Try running as Administrator.")
        sys.exit(1)

    print("\n🚀 Launching SignFlow...")
    app_path = os.path.join(os.path.dirname(_file_), "Modular", "main_gui.py")
    
    if os.path.exists(app_path):
        subprocess.call([sys.executable, app_path])
    else:
        print(f"❌ Error: Could not find application at {app_path}")

if _name_ == "_main_":
    import time
    install_dependencies()
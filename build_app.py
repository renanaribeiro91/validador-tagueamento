# build_app.py
import os
import shutil
import subprocess
import platform

def clean_build_directories():
    """Clean build and dist directories"""
    print("🧹 Cleaning build directories...")
    
    for directory in ['dist', 'build']:
        if os.path.exists(directory):
            print(f"  - Removing '{directory}' directory...")
            shutil.rmtree(directory)
    
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            print(f"  - Removing '{file}'...")
            os.remove(file)
    
    print("✅ Cleanup complete!")

def build_executable():
    """Build the TagValidator executable"""
    print("🚀 Building Tag Validator...")
    
    # Clean directories
    clean_build_directories()
    
    # Define main script and resources
    main_script = 'main.py'
    
    # List all files needed for the application
    resources = [
        'template_dashboard.html',
        'template_dashboard.css',
        'dashboard.js',
        'dashboard-utils.js',
        'readme.md'
    ]
    
    # Python modules (excluding main.py and build_app.py)
    modules = [
        'ai_analyzer.py',
        'devices.py',
        'dialog_utils.py',
        'file_utils.py',
        'log_processor.py',
        'tag_validator.py',
        'ui_theme.py'
    ]
    
    # Create a special wrapper script for macOS
    with open('macos_wrapper.py', 'w') as f:
        f.write('''
import os
import sys

# Fix for macOS bundle resources
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Fix working directory
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as compiled app
    if sys.platform == 'darwin':
        os.chdir(sys._MEIPASS)
        print(f"Changed working directory to: {os.getcwd()}")

# Import the main module
import main
main.main()  # Call the main function
''')

    # Build command with data files
    data_files = []
    for resource in resources:
        if os.path.exists(resource):
            data_files.append(f'--add-data={resource}:.')
    
    for module in modules:
        if os.path.exists(module):
            data_files.append(f'--add-data={module}:.')
    
    # Ensure main.py is included
    data_files.append(f'--add-data={main_script}:.')
    
    # Base command
    cmd = [
        'pyinstaller',
        '--name=TagValidator',
        '--clean',
        '--onedir',  # Create a directory with multiple files (more reliable)
        '--windowed',  # No console window
        '--noconfirm',  # Overwrite without asking
    ]
    
    # Add all data files
    cmd.extend(data_files)
    
    # Add hidden imports
    cmd.extend([
        '--hidden-import=tkinter',
        '--hidden-import=pandas', 
        '--hidden-import=matplotlib',
        '--hidden-import=numpy',
    ])
    
    # Finally add the wrapper script
    cmd.append('macos_wrapper.py')
    
    # Execute PyInstaller
    print("🔨 Running PyInstaller with these options:")
    for arg in cmd:
        if arg.startswith('--add-data='):
            print(f"  - Adding: {arg.split('=')[1].split(':')[0]}")
        else:
            print(f"  - {arg}")
    
    result = subprocess.run(cmd)
    
    # Clean up wrapper script
    if os.path.exists('macos_wrapper.py'):
        os.remove('macos_wrapper.py')
    
    if result.returncode == 0:
        print("✅ Build completed successfully!")
        
        # Set permissions for macOS
        app_path = os.path.abspath('dist/TagValidator.app')
        subprocess.run(['chmod', '-R', '755', app_path])
        subprocess.run(['xattr', '-rd', 'com.apple.quarantine', app_path])
        print(f"\n📦 App built at: {app_path}")
        
        print("\n🔍 To troubleshoot any issues:")
        print("1. Run the app from Terminal with:")
        print(f"   ./dist/TagValidator.app/Contents/MacOS/TagValidator")
        print("2. If it works in Terminal but not when double-clicked, it's likely a path issue.")
    else:
        print("❌ Build failed")
    
    return result.returncode == 0

if __name__ == "__main__":
    build_executable()
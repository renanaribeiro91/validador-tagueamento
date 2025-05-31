import os
import shutil
import subprocess
import platform

def find_platform_tools():
    """Find platform-specific tools needed for device detection"""
    tools = {}
    
    # Encontrar ADB
    adb_cmd = "adb"
    if platform.system() == "Windows":
        adb_cmd += ".exe"
    
    adb_path = shutil.which(adb_cmd)
    if adb_path:
        tools["adb"] = adb_path
    
    # Encontrar ferramentas iOS
    if platform.system() in ["Darwin", "Linux"]:
        for tool in ["idevice_id", "ideviceinfo", "idevicesyslog"]:
            path = shutil.which(tool)
            if path:
                tools[tool] = path
    
    return tools

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
    
    # Create directory for platform tools
    tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
    os.makedirs(tools_dir, exist_ok=True)
    
    # Find and copy platform tools
    tools = find_platform_tools()
    platform_binaries = []
    
    if tools:
        print("🔍 Found platform tools:")
        for tool_name, tool_path in tools.items():
            print(f"  - {tool_name}: {tool_path}")
            
            # Determine separator based on OS
            separator = ";" if platform.system() == "Windows" else ":"
            platform_binaries.append(f"--add-binary={tool_path}{separator}.")
    else:
        print("⚠️ No platform tools (adb, idevice_id) found in PATH!")
        print("   Device detection might not work in the packaged application.")

    # Build command with data files
    data_files = []
    for resource in resources:
        if os.path.exists(resource):
            data_files.append(f'--add-data={resource}:.')
    
    # Add module files as data
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
    
    # Add platform-specific binaries
    cmd.extend(platform_binaries)
    
    # Add hidden imports for all modules
    hidden_imports = [
        '--hidden-import=tkinter',
        '--hidden-import=pandas', 
        '--hidden-import=matplotlib',
        '--hidden-import=numpy',
    ]
    
    # Add all Python modules as hidden imports
    for module in modules:
        module_name = module.replace('.py', '')
        hidden_imports.append(f'--hidden-import={module_name}')
    
    cmd.extend(hidden_imports)
    
    # Finally add the wrapper script
    cmd.append('macos_wrapper.py')
    
    # Execute PyInstaller
    print("🔨 Running PyInstaller with these options:")
    for arg in cmd:
        if arg.startswith('--add-data='):
            print(f"  - Adding data: {arg.split('=')[1].split(':')[0]}")
        elif arg.startswith('--add-binary='):
            print(f"  - Adding binary: {arg.split('=')[1].split(':')[0]}")
        elif arg.startswith('--hidden-import='):
            print(f"  - Hidden import: {arg.split('=')[1]}")
        else:
            print(f"  - {arg}")
    
    result = subprocess.run(cmd)
    
    # Clean up wrapper script
    if os.path.exists('macos_wrapper.py'):
        os.remove('macos_wrapper.py')
    
    if result.returncode == 0:
        print("✅ Build completed successfully!")
        
        if platform.system() == "Darwin":  # macOS specific
            app_path = os.path.abspath('dist/TagValidator.app')
            subprocess.run(['chmod', '-R', '755', app_path])
            subprocess.run(['xattr', '-rd', 'com.apple.quarantine', app_path])
            print(f"\n📦 App built at: {app_path}")
            
            print("\n🔍 To troubleshoot any issues:")
            print("1. Run the app from Terminal with:")
            print(f"   ./dist/TagValidator.app/Contents/MacOS/TagValidator")
            print("2. If it works in Terminal but not when double-clicked, it's likely a path issue.")
        else:
            print(f"\n📦 App built at: {os.path.abspath('dist')}")
    else:
        print("❌ Build failed")
    
    return result.returncode == 0

if __name__ == "__main__":
    build_executable()
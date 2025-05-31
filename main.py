# Ponto de entrada principal
import logging
import os
import sys
import platform

from tag_validator import TagValidator
from ui_theme import ValidationApp

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Ensure bundled tools are in PATH
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as compiled app
    bundle_dir = sys._MEIPASS
    logging.info(f"Running as bundled app from: {bundle_dir}")
    
    # Add bundle directory to PATH for tools access
    if platform.system() == "Windows":
        os.environ["PATH"] = f"{bundle_dir};{os.environ.get('PATH', '')}"
    else:
        os.environ["PATH"] = f"{bundle_dir}:{os.environ.get('PATH', '')}"
    
    logging.info(f"Updated PATH: {os.environ['PATH']}")
else:
    logging.info("Running in development mode")



def main():
    # Inicializa e executa a aplicação
    validator = TagValidator()

    app = ValidationApp(validator)
    app.run()

if __name__ == "__main__":
    main()
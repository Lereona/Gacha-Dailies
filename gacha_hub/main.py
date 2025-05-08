import sys
from pathlib import Path
from dotenv import load_dotenv
from gacha_hub.ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize Qt Application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
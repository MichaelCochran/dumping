import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from database import EncryptionManager, DatabaseManager
from utils import PromptManager, ClaudeAPIManager
from config import Settings
from ui import AuthDialog, MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Personal Journal")
    
    settings = Settings()
    
    is_first_time = not settings.salt_path.exists()
    
    auth_dialog = AuthDialog(is_first_time=is_first_time)
    
    if auth_dialog.exec_() != AuthDialog.Accepted:
        return 0
    
    password = auth_dialog.get_password()
    
    try:
        if is_first_time:
            encryption = EncryptionManager(password)
            settings.save_salt(encryption.get_salt())
        else:
            salt = settings.get_salt()
            encryption = EncryptionManager(password, salt)
        
        db_manager = DatabaseManager(str(settings.db_path), encryption)
        
        if not is_first_time:
            try:
                db_manager.get_all_entries()
            except Exception:
                QMessageBox.critical(
                    None, 
                    "Authentication Failed",
                    "Incorrect password or corrupted database."
                )
                return 1
        
        prompt_manager = PromptManager(str(settings.prompts_path))
        claude_api = ClaudeAPIManager(settings.claude_api_key)
        
        main_window = MainWindow(db_manager, prompt_manager, claude_api, settings)
        main_window.show()
        
        return app.exec_()
    
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to start application: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QListWidget, QListWidgetItem,
                             QDateEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime
from .detail_window import DetailWindow


class SearchWindow(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.entries = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Browse Entries")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        date_layout = QHBoxLayout()
        date_label = QLabel("Search by Date:")
        date_layout.addWidget(date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_edit)
        
        date_search_btn = QPushButton("Search")
        date_search_btn.clicked.connect(self.search_by_date)
        date_layout.addWidget(date_search_btn)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        text_layout = QHBoxLayout()
        text_label = QLabel("Search by Text:")
        text_layout.addWidget(text_label)
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter search terms...")
        self.text_input.returnPressed.connect(self.search_by_text)
        text_layout.addWidget(self.text_input)
        
        text_search_btn = QPushButton("Search")
        text_search_btn.clicked.connect(self.search_by_text)
        text_layout.addWidget(text_search_btn)
        
        layout.addLayout(text_layout)
        
        layout.addSpacing(10)
        
        results_label = QLabel("Results:")
        results_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(results_label)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.open_entry)
        layout.addWidget(self.results_list)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        view_btn = QPushButton("View Selected")
        view_btn.clicked.connect(self.open_selected_entry)
        button_layout.addWidget(view_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.load_all_entries()
    
    def load_all_entries(self):
        self.entries = self.db_manager.get_all_entries()
        self.display_entries(self.entries)
    
    def search_by_date(self):
        selected_date = self.date_edit.date().toPyDate()
        search_datetime = datetime.combine(selected_date, datetime.min.time())
        
        self.entries = self.db_manager.search_by_date(search_datetime)
        self.display_entries(self.entries)
        
        if not self.entries:
            QMessageBox.information(self, "No Results", "No entries found for this date.")
    
    def search_by_text(self):
        search_term = self.text_input.text().strip()
        
        if not search_term:
            QMessageBox.warning(self, "Error", "Please enter a search term.")
            return
        
        self.entries = self.db_manager.search_by_text(search_term)
        self.display_entries(self.entries)
        
        if not self.entries:
            QMessageBox.information(self, "No Results", "No entries found matching your search.")
    
    def display_entries(self, entries):
        self.results_list.clear()
        
        for entry in entries:
            date_str = entry['date'].strftime("%Y-%m-%d %I:%M %p")
            prompt_preview = entry['prompt'][:50] + "..." if len(entry['prompt']) > 50 else entry['prompt']
            
            item_text = f"{date_str} - Prompt: {prompt_preview}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, entry)
            
            self.results_list.addItem(item)
    
    def open_selected_entry(self):
        current_item = self.results_list.currentItem()
        if current_item:
            self.open_entry(current_item)
        else:
            QMessageBox.warning(self, "Error", "Please select an entry to view.")
    
    def open_entry(self, item):
        entry = item.data(Qt.UserRole)
        detail_window = DetailWindow(entry, self.db_manager, self)
        detail_window.entry_updated.connect(self.refresh_entries)
        detail_window.entry_deleted.connect(self.refresh_entries)
        detail_window.exec_()
    
    def refresh_entries(self):
        self.load_all_entries()

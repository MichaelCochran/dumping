import sys
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from PyQt6 import QtWidgets, QtCore, QtGui

# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_GROUPS = {
    "group_1": {"name": "My Tasks", "color": "#4A90E2", "order": 0}
}

COLUMNS = [
    {"name": "Planning", "color": "#95A5A6"},
    {"name": "In Work", "color": "#F39C12"},
    {"name": "Review", "color": "#3498DB"},
    {"name": "Done", "color": "#27AE60"},
    {"name": "Hand-off", "color": "#9B59B6"}
]

PRIORITY_COLORS = {
    "high": "#E74C3C",
    "medium": "#F39C12",
    "low": "#2ECC71"
}

CARD_WIDTH = 250
COLUMN_PADDING = 5

# ============================================================================
# TASK CARD
# ============================================================================

class TaskCard(QtWidgets.QFrame):
    """Visual representation of a task card."""
    
    def __init__(self, task_data: Dict, group: str, column: str, board_ref, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.group = group
        self.column = column
        self.board_ref = board_ref
        self.is_selected = False
        
        priority = task_data.get("priority", "medium").lower()
        self.priority_color = PRIORITY_COLORS.get(priority, PRIORITY_COLORS["medium"])
        
        self.setFixedWidth(CARD_WIDTH)
        self.setObjectName("taskCard")
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_Hover, True)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self._update_style()
        
        # Add shadow effect
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)
        
        self._create_ui()
    
    def _create_ui(self):
        """Creates the card UI."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Priority bar
        priority_bar = QtWidgets.QFrame()
        priority_bar.setStyleSheet(f"background-color: {self.priority_color}; border-radius: 4px 4px 0px 0px;")
        priority_bar.setFixedHeight(4)
        priority_bar.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(priority_bar)
        
        # Content area
        content = QtWidgets.QWidget()
        content.setStyleSheet("background-color: transparent; border: none;")
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(6, 6, 6, 6)
        content_layout.setSpacing(4)
        
        # Title
        title = self.task_data.get("task_title", "Untitled")
        if len(title) > 50:
            title = title[:47] + "..."
        
        title_label = QtWidgets.QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-weight: bold; font-size: 9pt; color: #2C3E50;")
        title_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content_layout.addWidget(title_label)
        
        # Category badge
        category = self.task_data.get("category", "Task")
        category_label = QtWidgets.QLabel(f"📌 {category}")
        category_label.setStyleSheet("""
            background-color: #ECF0F1; 
            color: #34495E; 
            padding: 2px 4px; 
            border-radius: 3px;
            font-size: 7pt;
        """)
        category_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content_layout.addWidget(category_label)
        
        # Sender
        sender = self.task_data.get("email_sender", "Unknown")
        if len(sender) > 30:
            sender = sender[:27] + "..."
        sender_label = QtWidgets.QLabel(f"From: {sender}")
        sender_label.setStyleSheet("font-size: 7pt; color: #7F8C8D;")
        sender_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content_layout.addWidget(sender_label)
        
        # Time estimate
        time_label = QtWidgets.QLabel(f"⏱ {self.task_data.get('estimated_time', 'N/A')}")
        time_label.setStyleSheet("font-size: 7pt; color: #7F8C8D;")
        time_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content_layout.addWidget(time_label)
        
        # Move button
        move_btn = QtWidgets.QPushButton("Move →")
        move_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 7pt;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        move_btn.clicked.connect(self._show_move_menu)
        move_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        content_layout.addWidget(move_btn)
        
        layout.addWidget(content)
    
    def _update_style(self):
        """Update card styling based on selection state."""
        if self.is_selected:
            self.setStyleSheet(f"""
                QFrame#taskCard {{
                    background-color: #E8F4F8;
                    border: 3px solid #3498DB;
                    border-radius: 6px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame#taskCard {{
                    background-color: white;
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                }}
                QFrame#taskCard:hover {{
                    border: 2px solid {self.priority_color};
                }}
            """)
    
    def mousePressEvent(self, event):
        """Toggle selection on click."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_selected = not self.is_selected
            self._update_style()
            self.board_ref.update_selection_count()
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Show details on double-click."""
        self.board_ref.show_task_details(self.task_data)
    
    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        menu = QtWidgets.QMenu(self)
        
        edit_action = menu.addAction("✏️ Edit Task")
        details_action = menu.addAction("📋 View Details")
        menu.addSeparator()
        move_action = menu.addAction("➡️ Move Task")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Delete Task")
        
        action = menu.exec(event.globalPos())
        
        if action == edit_action:
            self.board_ref.edit_task_properties(self)
        elif action == details_action:
            self.board_ref.show_task_details(self.task_data)
        elif action == move_action:
            self._show_move_menu()
        elif action == delete_action:
            self.is_selected = True
            self.board_ref.delete_selected_tasks()
    
    def _show_move_menu(self):
        """Show context menu to move card."""
        menu = QtWidgets.QMenu(self)
        
        for col in COLUMNS:
            col_name = col["name"]
            if col_name == self.column:
                continue
            action = menu.addAction(col_name)
            action.triggered.connect(
                lambda checked, c=col_name: self.board_ref.move_task(self, self.group, c)
            )
        
        menu.exec(QtGui.QCursor.pos())

# ============================================================================
# KANBAN BOARD
# ============================================================================

class KanbanBoard(QtWidgets.QMainWindow):
    """Main Kanban board application."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Email Task Kanban Board")
        
        # Data
        self.tasks_file = "generated_tasks.json"
        self.board_state_file = "kanban_board_state.json"
        self.tasks = []
        self.board_state = {}
        self.groups = {}  # Dynamic groups
        self.filters = {}  # Email filters {group_id: [filter_rules]}
        self.task_cards = {}
        self.column_widgets = {}  # {group: {column: widget}}
        
        # Load data
        self.load_tasks()
        self.load_board_state()
        self.load_groups()
        self.load_filters()
        
        # Calculate window size
        num_columns = len(COLUMNS)
        num_groups = len(self.groups)
        SCROLLBAR_WIDTH = 20
        column_width = CARD_WIDTH + (COLUMN_PADDING * 2) + SCROLLBAR_WIDTH
        column_spacing = 3
        total_width = (num_columns * column_width) + ((num_columns - 1) * column_spacing) + 20
        CARD_HEIGHT_ESTIMATE = 115
        group_height = (CARD_HEIGHT_ESTIMATE * 2) + 70
        total_height = (num_groups * group_height) + 80
        self.resize(total_width, total_height)
        
        # Create UI
        self._create_menu()
        self._create_board_ui()
        
        # Populate
        self.refresh_board()
    
    def _create_menu(self):
        """Creates menu bar."""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Refresh Tasks", self.refresh_board)
        file_menu.addAction("Load New Emails", self.load_new_emails)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        edit_menu = menubar.addMenu("Edit")
        delete_action = edit_menu.addAction("Delete Selected Tasks", self.delete_selected_tasks)
        delete_action.setShortcut("Delete")
        edit_menu.addAction("Select All", self.select_all_tasks)
        edit_menu.addAction("Deselect All", self.deselect_all_tasks)
        
        groups_menu = menubar.addMenu("Groups")
        groups_menu.addAction("Add New Group", self.add_group_dialog)
        groups_menu.addAction("Manage Groups", self.manage_groups_dialog)
        groups_menu.addSeparator()
        groups_menu.addAction("Manage Filters", self.manage_filters_dialog)
        
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", lambda: QtWidgets.QMessageBox.information(
            self, "About", "Email Task Kanban Board\nVersion 2.0\n\nDynamic Group Management"
        ))
    
    def _create_board_ui(self):
        """Creates the board layout."""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)
        
        # Scroll area for entire board
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        board_widget = QtWidgets.QWidget()
        board_layout = QtWidgets.QVBoxLayout(board_widget)
        board_layout.setSpacing(3)
        board_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create groups (sorted by order)
        sorted_groups = sorted(self.groups.items(), key=lambda x: x[1].get('order', 0))
        for group_key, group_info in sorted_groups:
            group_frame = self._create_group(group_key, group_info)
            board_layout.addWidget(group_frame)
        
        # Don't add stretch - let groups determine size
        scroll.setWidget(board_widget)
        main_layout.addWidget(scroll)
    
    def _create_group(self, group_key: str, group_info: Dict):
        """Creates a group with columns."""
        # Group frame
        group_frame = QtWidgets.QGroupBox(group_info["name"])
        group_frame.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 11pt;
                border: 2px solid {group_info["color"]};
                border-radius: 5px;
                margin-top: 10px;
                background-color: #ECF0F1;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: {group_info["color"]};
                color: white;
                border-radius: 3px;
            }}
        """)
        
        group_layout = QtWidgets.QHBoxLayout(group_frame)
        group_layout.setSpacing(3)  # Tighter spacing between columns
        group_layout.setContentsMargins(3, 20, 3, 3)  # Minimal side margins
        
        self.column_widgets[group_key] = {}
        
        # Create columns
        for col_config in COLUMNS:
            col_name = col_config["name"]
            col_container, inner_widget = self._create_column(col_name, col_config["color"])
            group_layout.addWidget(col_container)
            self.column_widgets[group_key][col_name] = inner_widget
        
        return group_frame
    
    def _create_column(self, col_name: str, col_color: str):
        """Creates a column widget. Returns (container, inner_widget) tuple."""
        # Add extra width for scrollbar (typically 15-20px)
        SCROLLBAR_WIDTH = 20
        col_widget = QtWidgets.QWidget()
        col_widget.setFixedWidth(CARD_WIDTH + (COLUMN_PADDING * 2) + SCROLLBAR_WIDTH)
        
        col_layout = QtWidgets.QVBoxLayout(col_widget)
        col_layout.setContentsMargins(COLUMN_PADDING, 0, COLUMN_PADDING, 0)
        col_layout.setSpacing(3)  # Tighter spacing
        
        # Header
        header = QtWidgets.QLabel(col_name)
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"""
            background-color: {col_color};
            color: white;
            font-weight: bold;
            font-size: 10pt;
            padding: 5px;
            border-radius: 3px;
        """)
        col_layout.addWidget(header)
        
        # Scroll area for cards (sized for 2 cards)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea { 
                background-color: white; 
                border: 1px solid #BDC3C7;
            }
            QScrollArea > QWidget > QWidget {
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #BDC3C7;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95A5A6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Set minimum height to display 2 cards (estimate: 115px per card + spacing)
        CARD_HEIGHT_ESTIMATE = 115
        MIN_HEIGHT_FOR_TWO_CARDS = (CARD_HEIGHT_ESTIMATE * 2) + 20  # 2 cards + minimal spacing
        scroll.setMinimumHeight(MIN_HEIGHT_FOR_TWO_CARDS)
        
        inner = QtWidgets.QWidget()
        inner_layout = QtWidgets.QVBoxLayout(inner)
        inner_layout.setContentsMargins(10, 10, 20, 10)  # Extra right margin to keep cards away from scrollbar
        inner_layout.setSpacing(10)
        inner_layout.addStretch()
        
        scroll.setWidget(inner)
        col_layout.addWidget(scroll)
        
        return col_widget, inner
    
    def load_tasks(self):
        """Load tasks from JSON."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    self.tasks = json.load(f)
                print(f"✓ Loaded {len(self.tasks)} tasks")
            except Exception as e:
                print(f"✗ Error loading tasks: {e}")
                self.tasks = []
        else:
            self.tasks = []
    
    def load_board_state(self):
        """Load board state from JSON."""
        if os.path.exists(self.board_state_file):
            try:
                with open(self.board_state_file, 'r') as f:
                    data = json.load(f)
                    self.board_state = data.get('tasks', {})
            except:
                self.board_state = {}
        else:
            self.board_state = {}
    
    def load_groups(self):
        """Load groups configuration from board state."""
        if os.path.exists(self.board_state_file):
            try:
                with open(self.board_state_file, 'r') as f:
                    data = json.load(f)
                    self.groups = data.get('groups', DEFAULT_GROUPS.copy())
            except:
                self.groups = DEFAULT_GROUPS.copy()
        else:
            self.groups = DEFAULT_GROUPS.copy()
        
        if not self.groups:
            self.groups = DEFAULT_GROUPS.copy()
    
    def load_filters(self):
        """Load email filters from board state."""
        if os.path.exists(self.board_state_file):
            try:
                with open(self.board_state_file, 'r') as f:
                    data = json.load(f)
                    self.filters = data.get('filters', {})
            except:
                self.filters = {}
        else:
            self.filters = {}
    
    def save_board_state(self):
        """Save board state to JSON."""
        try:
            data = {
                'groups': self.groups,
                'filters': self.filters,
                'tasks': self.board_state
            }
            with open(self.board_state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"✗ Error saving board state: {e}")
    
    def get_task_id(self, task: Dict) -> str:
        """Generate unique task ID."""
        return f"{task.get('email_subject', '')}_{task.get('email_sender', '')}_{task.get('generated_at', '')}"
    
    def assign_default_group(self, task: Dict) -> str:
        """Assign task to group based on filters or default."""
        # Try to match filters
        for group_id, filter_rules in self.filters.items():
            if group_id not in self.groups:
                continue
            
            for rule in filter_rules:
                if self._matches_filter(task, rule):
                    return group_id
        
        # No filter match, use first group
        if self.groups:
            sorted_groups = sorted(self.groups.items(), key=lambda x: x[1].get('order', 0))
            return sorted_groups[0][0]
        return "group_1"
    
    def _matches_filter(self, task: Dict, rule: Dict) -> bool:
        """Check if task matches a filter rule."""
        filter_type = rule.get('type')
        pattern = rule.get('pattern', '').lower()
        match_type = rule.get('match_type', 'contains')
        
        if not pattern:
            return False
        
        # Get the field to check
        if filter_type == 'sender':
            field_value = task.get('email_sender', '').lower()
        elif filter_type == 'subject':
            field_value = task.get('email_subject', '').lower()
        elif filter_type == 'body':
            field_value = task.get('task_description', '').lower()
        else:
            return False
        
        # Apply match type
        if match_type == 'contains':
            return pattern in field_value
        elif match_type == 'equals':
            return pattern == field_value
        elif match_type == 'startswith':
            return field_value.startswith(pattern)
        elif match_type == 'endswith':
            return field_value.endswith(pattern)
        
        return False
    
    def refresh_board(self):
        """Clear and rebuild all cards."""
        # Clear existing cards
        self.task_cards.clear()
        for group_widgets in self.column_widgets.values():
            for inner_widget in group_widgets.values():
                layout = inner_widget.layout()
                # Remove all widgets except the stretch
                while layout.count() > 1:
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
        
        # Add cards
        for task in self.tasks:
            task_id = self.get_task_id(task)
            
            if task_id in self.board_state:
                group = self.board_state[task_id]["group"]
                column = self.board_state[task_id]["column"]
            else:
                group = self.assign_default_group(task)
                column = COLUMNS[0]["name"]
                self.board_state[task_id] = {"group": group, "column": column}
            
            self._add_task_card(task, group, column)
        
        self.save_board_state()
    
    def _add_task_card(self, task: Dict, group: str, column: str):
        """Add a card to the board."""
        task_id = self.get_task_id(task)
        
        if group in self.column_widgets and column in self.column_widgets[group]:
            inner_widget = self.column_widgets[group][column]
            layout = inner_widget.layout()
            
            card = TaskCard(task, group, column, self)
            # Insert before the stretch (last item)
            layout.insertWidget(layout.count() - 1, card)
            
            self.task_cards[task_id] = card
    
    def move_task(self, card: TaskCard, new_group: str, new_column: str):
        """Move a task to new location."""
        task_id = self.get_task_id(card.task_data)
        
        self.board_state[task_id] = {"group": new_group, "column": new_column}
        card.group = new_group
        card.column = new_column
        
        self.save_board_state()
        self.refresh_board()
        
        print(f"✓ Moved task to {new_group} / {new_column}")
    
    def show_task_details(self, task: Dict):
        """Show task details dialog."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Task Details")
        dialog.resize(600, 500)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Priority header
        priority = task.get("priority", "medium")
        priority_color = PRIORITY_COLORS.get(priority, PRIORITY_COLORS["medium"])
        
        header = QtWidgets.QLabel(task.get("task_title", "Task Details"))
        header.setStyleSheet(f"""
            background-color: {priority_color};
            color: white;
            font-weight: bold;
            font-size: 12pt;
            padding: 10px;
        """)
        layout.addWidget(header)
        
        # Details text
        details = QtWidgets.QTextEdit()
        details.setReadOnly(True)
        details_text = f"""
📋 TASK INFORMATION
{'=' * 60}

Title: {task.get('task_title', 'N/A')}

Description: {task.get('task_description', 'N/A')}

Category: {task.get('category', 'N/A')}
Priority: {task.get('priority', 'N/A').upper()}
Estimated Time: {task.get('estimated_time', 'N/A')}

{'=' * 60}
📧 EMAIL DETAILS
{'=' * 60}

Subject: {task.get('email_subject', 'N/A')}

From: {task.get('email_sender', 'N/A')}

Received: {task.get('email_received', 'N/A')}

Generated: {task.get('generated_at', 'N/A')}
Method: {task.get('method', 'N/A')}

{'=' * 60}
"""
        details.setPlainText(details_text)
        layout.addWidget(details)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def edit_task_properties(self, card: TaskCard):
        """Edit task priority and category."""
        task = card.task_data
        task_id = self.get_task_id(task)
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Edit Task Properties")
        dialog.resize(400, 300)
        
        layout = QtWidgets.QFormLayout(dialog)
        layout.setSpacing(15)
        
        # Title editing
        title_edit = QtWidgets.QLineEdit()
        title_edit.setText(task.get("task_title", ""))
        title_edit.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 10pt;
            }
        """)
        layout.addRow("Title:", title_edit)
        
        # Priority selection
        priority_combo = QtWidgets.QComboBox()
        priority_combo.addItems(["high", "medium", "low"])
        current_priority = task.get("priority", "medium").lower()
        priority_combo.setCurrentText(current_priority)
        priority_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-size: 10pt;
            }
        """)
        layout.addRow("Priority:", priority_combo)
        
        # Category selection/edit
        category_combo = QtWidgets.QComboBox()
        category_combo.setEditable(True)
        common_categories = ["FYI", "Review", "Action Required", "Meeting", "Follow-up", "Question", "Task"]
        category_combo.addItems(common_categories)
        current_category = task.get("category", "Task")
        category_combo.setCurrentText(current_category)
        category_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-size: 10pt;
            }
        """)
        layout.addRow("Category:", category_combo)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addRow("", button_layout)
        
        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        
        def save_changes():
            new_title = title_edit.text().strip()
            new_priority = priority_combo.currentText()
            new_category = category_combo.currentText()
            
            if not new_title:
                QtWidgets.QMessageBox.warning(
                    self, "Invalid Input", "Title cannot be empty!"
                )
                return
            
            # Update task in the tasks list
            for i, t in enumerate(self.tasks):
                if self.get_task_id(t) == task_id:
                    self.tasks[i]["task_title"] = new_title
                    self.tasks[i]["priority"] = new_priority
                    self.tasks[i]["category"] = new_category
                    break
            
            # Save to file
            try:
                with open(self.tasks_file, 'w', encoding='utf-8') as f:
                    json.dump(self.tasks, f, indent=2)
                
                dialog.accept()
                self.refresh_board()
                
                QtWidgets.QMessageBox.information(
                    self, "Success", "Task properties updated successfully!"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Failed to save changes:\n{str(e)}"
                )
        
        save_btn.clicked.connect(save_changes)
        
        dialog.exec()
    
    def load_new_emails(self):
        """Load new emails from email processor."""
        try:
            import subprocess
            result = subprocess.run(
                ["python", "email_task_generator.py", "process", "--limit", "10"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if result.returncode == 0:
                QtWidgets.QMessageBox.information(
                    self, "Success", "New emails processed! Refreshing board..."
                )
                self.load_tasks()
                self.refresh_board()
            else:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Failed to process emails:\n{result.stderr}"
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to run email processor:\n{str(e)}"
            )
    
    def update_selection_count(self):
        """Update window title with selection count."""
        selected_count = sum(1 for card in self.task_cards.values() if card.is_selected)
        if selected_count > 0:
            self.setWindowTitle(f"Email Task Kanban Board - {selected_count} task(s) selected")
        else:
            self.setWindowTitle("Email Task Kanban Board")
    
    def get_selected_cards(self) -> List[TaskCard]:
        """Get all currently selected cards."""
        return [card for card in self.task_cards.values() if card.is_selected]
    
    def select_all_tasks(self):
        """Select all visible task cards."""
        for card in self.task_cards.values():
            card.is_selected = True
            card._update_style()
        self.update_selection_count()
    
    def deselect_all_tasks(self):
        """Deselect all task cards."""
        for card in self.task_cards.values():
            card.is_selected = False
            card._update_style()
        self.update_selection_count()
    
    def delete_selected_tasks(self):
        """Delete all selected tasks."""
        selected_cards = self.get_selected_cards()
        
        if not selected_cards:
            QtWidgets.QMessageBox.information(
                self, "No Selection", "No tasks selected. Click tasks to select them, then delete."
            )
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {len(selected_cards)} selected task(s)?\n\nThis will remove them from the board and the task file.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Remove from tasks list and board state
            for card in selected_cards:
                task_id = self.get_task_id(card.task_data)
                
                # Remove from tasks list
                self.tasks = [t for t in self.tasks if self.get_task_id(t) != task_id]
                
                # Remove from board state
                if task_id in self.board_state:
                    del self.board_state[task_id]
            
            # Save updated tasks to file
            try:
                with open(self.tasks_file, 'w', encoding='utf-8') as f:
                    json.dump(self.tasks, f, indent=2)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Failed to save tasks file:\n{str(e)}"
                )
                return
            
            # Save board state
            self.save_board_state()
            
            # Refresh board
            self.refresh_board()
            
            QtWidgets.QMessageBox.information(
                self, "Success", f"Deleted {len(selected_cards)} task(s) successfully!"
            )
    
    def add_group_dialog(self):
        """Dialog to add a new group."""
        name, ok = QtWidgets.QInputDialog.getText(
            self, "Add Group", "Enter group name:"
        )
        
        if ok and name:
            color = QtWidgets.QColorDialog.getColor(
                QtGui.QColor("#4A90E2"),
                self,
                "Select Group Color"
            )
            
            if color.isValid():
                group_id = f"group_{len(self.groups) + 1}"
                max_order = max([g.get('order', 0) for g in self.groups.values()], default=-1)
                
                self.groups[group_id] = {
                    "name": name,
                    "color": color.name(),
                    "order": max_order + 1
                }
                
                self.save_board_state()
                self.rebuild_board()
                
                QtWidgets.QMessageBox.information(
                    self, "Success", f"Group '{name}' added successfully!"
                )
    
    def manage_groups_dialog(self):
        """Dialog to manage existing groups."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Manage Groups")
        dialog.resize(500, 400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        label = QtWidgets.QLabel("Current Groups:")
        label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        layout.addWidget(label)
        
        list_widget = QtWidgets.QListWidget()
        sorted_groups = sorted(self.groups.items(), key=lambda x: x[1].get('order', 0))
        
        for group_id, group_info in sorted_groups:
            item = QtWidgets.QListWidgetItem(f"{group_info['name']} ({group_info['color']})")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, group_id)
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        btn_layout = QtWidgets.QHBoxLayout()
        
        rename_btn = QtWidgets.QPushButton("Rename")
        rename_btn.clicked.connect(lambda: self._rename_selected_group(list_widget))
        btn_layout.addWidget(rename_btn)
        
        color_btn = QtWidgets.QPushButton("Change Color")
        color_btn.clicked.connect(lambda: self._change_group_color(list_widget))
        btn_layout.addWidget(color_btn)
        
        delete_btn = QtWidgets.QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self._delete_selected_group(list_widget, dialog))
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _rename_selected_group(self, list_widget):
        """Rename the selected group."""
        current_item = list_widget.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a group to rename.")
            return
        
        group_id = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        old_name = self.groups[group_id]['name']
        
        new_name, ok = QtWidgets.QInputDialog.getText(
            self, "Rename Group", "Enter new name:", text=old_name
        )
        
        if ok and new_name:
            self.groups[group_id]['name'] = new_name
            self.save_board_state()
            self.rebuild_board()
            QtWidgets.QMessageBox.information(self, "Success", "Group renamed successfully!")
    
    def _change_group_color(self, list_widget):
        """Change the color of the selected group."""
        current_item = list_widget.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a group to change color.")
            return
        
        group_id = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        current_color = self.groups[group_id]['color']
        
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor(current_color),
            self,
            "Select Group Color"
        )
        
        if color.isValid():
            self.groups[group_id]['color'] = color.name()
            self.save_board_state()
            self.rebuild_board()
            QtWidgets.QMessageBox.information(self, "Success", "Group color changed successfully!")
    
    def _delete_selected_group(self, list_widget, dialog):
        """Delete the selected group."""
        current_item = list_widget.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a group to delete.")
            return
        
        if len(self.groups) <= 1:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Cannot delete the last group. At least one group must exist."
            )
            return
        
        group_id = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        group_name = self.groups[group_id]['name']
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete group '{group_name}'?\n\nTasks in this group will be moved to the first group.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            sorted_groups = sorted(self.groups.items(), key=lambda x: x[1].get('order', 0))
            target_group = sorted_groups[0][0] if sorted_groups[0][0] != group_id else sorted_groups[1][0]
            
            for task_id, task_state in self.board_state.items():
                if task_state.get('group') == group_id:
                    task_state['group'] = target_group
            
            del self.groups[group_id]
            self.save_board_state()
            self.rebuild_board()
            dialog.accept()
            QtWidgets.QMessageBox.information(self, "Success", "Group deleted successfully!")
    
    def rebuild_board(self):
        """Rebuild the entire board UI."""
        self.setCentralWidget(QtWidgets.QWidget())
        self.column_widgets.clear()
        self.task_cards.clear()
        self._create_board_ui()
        self.refresh_board()
    
    def manage_filters_dialog(self):
        """Dialog to manage email filters."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Manage Email Filters")
        dialog.resize(700, 500)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Instructions
        info = QtWidgets.QLabel(
            "📧 Automatically sort emails into groups\n\n"
            "Add filters to route emails based on who sent them, the subject line, or keywords in the email."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            "color: #2C3E50; font-size: 10pt; padding: 10px; "
            "background-color: #ECF0F1; border-radius: 5px; border: 1px solid #BDC3C7;"
        )
        layout.addWidget(info)
        
        # Group selection
        group_layout = QtWidgets.QHBoxLayout()
        group_layout.addWidget(QtWidgets.QLabel("Group:"))
        
        group_combo = QtWidgets.QComboBox()
        sorted_groups = sorted(self.groups.items(), key=lambda x: x[1].get('order', 0))
        for group_id, group_info in sorted_groups:
            group_combo.addItem(group_info['name'], group_id)
        group_layout.addWidget(group_combo)
        group_layout.addStretch()
        
        layout.addLayout(group_layout)
        
        # Filter list
        list_label = QtWidgets.QLabel("📋 Filters for selected group:")
        list_label.setStyleSheet("font-weight: bold; margin-top: 10px; font-size: 10pt;")
        layout.addWidget(list_label)
        
        filter_list = QtWidgets.QListWidget()
        filter_list.setStyleSheet("""
            QListWidget {
                font-size: 10pt;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ECF0F1;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
                color: white;
            }
        """)
        layout.addWidget(filter_list)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        add_btn = QtWidgets.QPushButton("Add Filter")
        add_btn.clicked.connect(lambda: self._add_filter_dialog(group_combo, filter_list))
        btn_layout.addWidget(add_btn)
        
        edit_btn = QtWidgets.QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self._edit_filter_dialog(group_combo, filter_list))
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QtWidgets.QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self._delete_filter(group_combo, filter_list))
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        layout.addWidget(close_btn)
        
        # Update filter list when group changes
        def update_filter_list():
            filter_list.clear()
            group_id = group_combo.currentData()
            if group_id in self.filters:
                for rule in self.filters[group_id]:
                    filter_type = rule.get('type', 'sender')
                    pattern = rule.get('pattern', '')
                    
                    # Friendly display
                    if filter_type == 'sender':
                        icon = "👤"
                        display = f"From emails containing: {pattern}"
                    elif filter_type == 'subject':
                        icon = "📧"
                        display = f"Subject contains: {pattern}"
                    elif filter_type == 'body':
                        icon = "📝"
                        display = f"Email mentions: {pattern}"
                    else:
                        icon = "🔍"
                        display = pattern
                    
                    filter_list.addItem(f"{icon} {display}")
        
        group_combo.currentIndexChanged.connect(update_filter_list)
        update_filter_list()
        
        dialog.exec()
    
    def _add_filter_dialog(self, group_combo, filter_list):
        """Dialog to add a new filter."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add Filter")
        dialog.resize(550, 350)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # Title
        title = QtWidgets.QLabel("✨ Create a New Filter")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)
        
        # Filter type selection with descriptions
        type_group = QtWidgets.QGroupBox("What should trigger this filter?")
        type_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; }")
        type_layout = QtWidgets.QVBoxLayout()
        
        type_radio_sender = QtWidgets.QRadioButton("👤 From a specific person or email address")
        type_radio_sender.setChecked(True)
        type_layout.addWidget(type_radio_sender)
        
        type_radio_subject = QtWidgets.QRadioButton("📧 Subject line contains certain words")
        type_layout.addWidget(type_radio_subject)
        
        type_radio_body = QtWidgets.QRadioButton("📝 Email mentions specific keywords")
        type_layout.addWidget(type_radio_body)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Pattern input with dynamic example
        pattern_label = QtWidgets.QLabel("Enter the text to look for:")
        pattern_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        layout.addWidget(pattern_label)
        
        pattern_input = QtWidgets.QLineEdit()
        pattern_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 10pt;
                border: 2px solid #BDC3C7;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)
        layout.addWidget(pattern_input)
        
        # Dynamic example label
        example_label = QtWidgets.QLabel()
        example_label.setStyleSheet("color: #7F8C8D; font-size: 9pt; padding-left: 5px;")
        example_label.setWordWrap(True)
        layout.addWidget(example_label)
        
        # Update example text based on selection
        def update_example():
            if type_radio_sender.isChecked():
                pattern_input.setPlaceholderText("e.g., john@company.com or @team.com")
                example_label.setText(
                    "💡 Tip: You can enter a full email (john@company.com) or just part of it (@company.com)"
                )
            elif type_radio_subject.isChecked():
                pattern_input.setPlaceholderText("e.g., urgent, invoice, meeting")
                example_label.setText(
                    "💡 Tip: Enter any word or phrase that appears in the subject line"
                )
            elif type_radio_body.isChecked():
                pattern_input.setPlaceholderText("e.g., budget, deadline, approval")
                example_label.setText(
                    "💡 Tip: Enter keywords that might appear in the email content"
                )
        
        type_radio_sender.toggled.connect(update_example)
        type_radio_subject.toggled.connect(update_example)
        type_radio_body.toggled.connect(update_example)
        update_example()
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("✓ Add Filter")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        def save_filter():
            pattern = pattern_input.text().strip()
            if not pattern:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Missing Information", 
                    "Please enter the text you want to filter by."
                )
                return
            
            # Determine filter type
            if type_radio_sender.isChecked():
                filter_type = 'sender'
            elif type_radio_subject.isChecked():
                filter_type = 'subject'
            else:
                filter_type = 'body'
            
            group_id = group_combo.currentData()
            if group_id not in self.filters:
                self.filters[group_id] = []
            
            filter_rule = {
                'type': filter_type,
                'match_type': 'contains',
                'pattern': pattern
            }
            
            self.filters[group_id].append(filter_rule)
            self.save_board_state()
            
            # Update list with friendly display
            filter_list.clear()
            for rule in self.filters[group_id]:
                filter_type = rule.get('type', 'sender')
                pattern = rule.get('pattern', '')
                
                if filter_type == 'sender':
                    icon = "👤"
                    display = f"From emails containing: {pattern}"
                elif filter_type == 'subject':
                    icon = "📧"
                    display = f"Subject contains: {pattern}"
                elif filter_type == 'body':
                    icon = "📝"
                    display = f"Email mentions: {pattern}"
                else:
                    icon = "🔍"
                    display = pattern
                
                filter_list.addItem(f"{icon} {display}")
            
            dialog.accept()
            QtWidgets.QMessageBox.information(
                self, 
                "Filter Added! ✓", 
                f"New emails matching this filter will automatically go to '{self.groups[group_id]['name']}'."
            )
        
        save_btn.clicked.connect(save_filter)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def _edit_filter_dialog(self, group_combo, filter_list):
        """Dialog to edit an existing filter."""
        current_row = filter_list.currentRow()
        if current_row < 0:
            QtWidgets.QMessageBox.information(
                self, 
                "Select a Filter", 
                "Please click on a filter from the list to edit it."
            )
            return
        
        group_id = group_combo.currentData()
        if group_id not in self.filters or current_row >= len(self.filters[group_id]):
            return
        
        current_rule = self.filters[group_id][current_row]
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Edit Filter")
        dialog.resize(550, 350)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # Title
        title = QtWidgets.QLabel("✏️ Edit Filter")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)
        
        # Filter type selection
        type_group = QtWidgets.QGroupBox("What should trigger this filter?")
        type_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; }")
        type_layout = QtWidgets.QVBoxLayout()
        
        type_radio_sender = QtWidgets.QRadioButton("👤 From a specific person or email address")
        type_layout.addWidget(type_radio_sender)
        
        type_radio_subject = QtWidgets.QRadioButton("📧 Subject line contains certain words")
        type_layout.addWidget(type_radio_subject)
        
        type_radio_body = QtWidgets.QRadioButton("📝 Email mentions specific keywords")
        type_layout.addWidget(type_radio_body)
        
        # Set current selection
        current_type = current_rule.get('type', 'sender')
        if current_type == 'sender':
            type_radio_sender.setChecked(True)
        elif current_type == 'subject':
            type_radio_subject.setChecked(True)
        else:
            type_radio_body.setChecked(True)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Pattern input
        pattern_label = QtWidgets.QLabel("Enter the text to look for:")
        pattern_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        layout.addWidget(pattern_label)
        
        pattern_input = QtWidgets.QLineEdit()
        pattern_input.setText(current_rule.get('pattern', ''))
        pattern_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 10pt;
                border: 2px solid #BDC3C7;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)
        layout.addWidget(pattern_input)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("✓ Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        def save_changes():
            pattern = pattern_input.text().strip()
            if not pattern:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Missing Information", 
                    "Please enter the text you want to filter by."
                )
                return
            
            # Determine filter type
            if type_radio_sender.isChecked():
                filter_type = 'sender'
            elif type_radio_subject.isChecked():
                filter_type = 'subject'
            else:
                filter_type = 'body'
            
            self.filters[group_id][current_row] = {
                'type': filter_type,
                'match_type': 'contains',
                'pattern': pattern
            }
            
            self.save_board_state()
            
            # Update list with friendly display
            filter_list.clear()
            for rule in self.filters[group_id]:
                filter_type = rule.get('type', 'sender')
                pattern = rule.get('pattern', '')
                
                if filter_type == 'sender':
                    icon = "👤"
                    display = f"From emails containing: {pattern}"
                elif filter_type == 'subject':
                    icon = "📧"
                    display = f"Subject contains: {pattern}"
                elif filter_type == 'body':
                    icon = "📝"
                    display = f"Email mentions: {pattern}"
                else:
                    icon = "🔍"
                    display = pattern
                
                filter_list.addItem(f"{icon} {display}")
            
            dialog.accept()
            QtWidgets.QMessageBox.information(
                self, 
                "Filter Updated! ✓", 
                "Your filter has been updated successfully."
            )
        
        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def _delete_filter(self, group_combo, filter_list):
        """Delete the selected filter."""
        current_row = filter_list.currentRow()
        if current_row < 0:
            QtWidgets.QMessageBox.information(
                self, 
                "Select a Filter", 
                "Please click on a filter from the list to delete it."
            )
            return
        
        group_id = group_combo.currentData()
        if group_id not in self.filters or current_row >= len(self.filters[group_id]):
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Filter?",
            "Are you sure you want to delete this filter?\n\nEmails matching this filter will no longer be automatically sorted.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            del self.filters[group_id][current_row]
            
            if not self.filters[group_id]:
                del self.filters[group_id]
            
            self.save_board_state()
            
            # Update list
            filter_list.takeItem(current_row)

# ============================================================================
# MAIN
# ============================================================================

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = KanbanBoard()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

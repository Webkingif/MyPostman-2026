import sys
import os
import json
import re
import requests
import base64
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QComboBox, QLineEdit, QPushButton, 
                             QTextEdit, QLabel, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QSplitter, 
                             QListWidget, QInputDialog, QMessageBox, QDialog)

# ==========================================
# WIDGET: A Single Request Tab
# ==========================================
class RequestTab(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app # Reference to the main window for environment variables
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # --- Top Bar (Method, URL, Send) ---
        top_layout = QHBoxLayout()
        self.method_box = QComboBox()
        self.method_box.addItems(["GET", "POST", "PUT", "DELETE", "PATCH"])
        
        self.url_input = QLineEdit("{{base_url}}/posts")
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("font-weight: bold; padding: 5px 15px; background-color: #007bff; color: white;")
        self.send_btn.clicked.connect(self.make_request)

        top_layout.addWidget(self.method_box)
        top_layout.addWidget(self.url_input)
        top_layout.addWidget(self.send_btn)
        layout.addLayout(top_layout)

        # --- Configuration Tabs ---
        self.req_tabs = QTabWidget()
        self.req_tabs.setMaximumHeight(200)
        
        self.params_tab, self.params_table = self.create_kv_table()
        self.req_tabs.addTab(self.params_tab, "Query Params")
        
        self.headers_tab, self.headers_table = self.create_kv_table()
        self.req_tabs.addTab(self.headers_tab, "Headers")
        
        self.req_body = QTextEdit()
        self.req_tabs.addTab(self.req_body, "JSON Body")
        
        layout.addWidget(self.req_tabs)

        # --- Response Area ---
        layout.addWidget(QLabel("<b>Response:</b>"))
        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        self.response_area.setStyleSheet("font-family: Consolas, monospace; background-color: #f8f9fa;") 
        layout.addWidget(self.response_area)

    def create_kv_table(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        table = QTableWidget(1, 2)
        table.setHorizontalHeaderLabels(["Key", "Value"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        btn = QPushButton("+ Add Row")
        btn.clicked.connect(lambda: table.insertRow(table.rowCount()))
        
        layout.addWidget(table)
        layout.addWidget(btn)
        return widget, table

    def get_table_data(self, table):
        data = {}
        for row in range(table.rowCount()):
            k_item, v_item = table.item(row, 0), table.item(row, 1)
            if k_item and k_item.text().strip():
                data[k_item.text().strip()] = v_item.text().strip() if v_item else ""
        return data

    def populate_table_data(self, table, data_dict):
        table.setRowCount(0)
        for key, val in data_dict.items():
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(key)))
            table.setItem(row, 1, QTableWidgetItem(str(val)))
        table.insertRow(table.rowCount())

    def get_state(self):
        return {
            "method": self.method_box.currentText(),
            "url": self.url_input.text().strip(),
            "headers": self.get_table_data(self.headers_table),
            "params": self.get_table_data(self.params_table),
            "body": self.req_body.toPlainText().strip()
        }

    def set_state(self, req_data):
        self.method_box.setCurrentText(req_data.get("method", "GET"))
        self.url_input.setText(req_data.get("url", ""))
        self.req_body.setText(req_data.get("body", ""))
        self.populate_table_data(self.headers_table, req_data.get("headers", {}))
        self.populate_table_data(self.params_table, req_data.get("params", {}))

    # --- HTTP ENGINE WITH ENVIRONMENT INJECTION ---
    def resolve_vars(self, text):
        """Finds {{variable}} and replaces it with the active environment's value."""
        if not text: return text
        env_vars = self.main_app.get_active_env_vars()
        for key, val in env_vars.items():
            text = text.replace(f"{{{{{key}}}}}", str(val))
        return text

    def make_request(self):
        method = self.method_box.currentText()
        # Resolve variables in URL and Body
        raw_url = self.url_input.text().strip()
        url = self.resolve_vars(raw_url)
        payload = self.resolve_vars(self.req_body.toPlainText().strip())

        # Resolve variables in Headers and Params
        req_headers = {self.resolve_vars(k): self.resolve_vars(v) for k, v in self.get_table_data(self.headers_table).items()}
        req_params = {self.resolve_vars(k): self.resolve_vars(v) for k, v in self.get_table_data(self.params_table).items()}

        self.response_area.setText(f"Sending request to:\n{url}\n...")
        QApplication.processEvents() 

        try:
            kwargs = {"headers": req_headers, "params": req_params}
            if payload and method in ["POST", "PUT", "PATCH"]:
                kwargs["data"] = payload.encode('utf-8')
                if "Content-Type" not in [k.title() for k in req_headers.keys()]:
                    kwargs["headers"]["Content-Type"] = "application/json"

            res = requests.request(method, url, **kwargs)

            output = f"Status: {res.status_code} {res.reason}\n"
            output += "-" * 50 + "\n"
            try:
                output += json.dumps(res.json(), indent=4)
            except ValueError:
                output += res.text

            self.response_area.setText(output)
        except Exception as e:
            self.response_area.setText(f"Connection Error:\n{str(e)}\n\n(Did you select the right Environment?)")

# ==========================================
# WIDGET: Simple JWT Decoder Tab
# ==========================================
class JwtDecoderTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("<b>Paste your JWT Token here:</b>"))
        self.token_input = QTextEdit()
        self.token_input.setPlaceholderText("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        self.token_input.setMaximumHeight(100)
        self.token_input.textChanged.connect(self.decode_jwt)
        layout.addWidget(self.token_input)
        
        # Splitter to show Header and Payload side-by-side or stacked
        result_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Header Box
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.addWidget(QLabel("<b>Header (Algorithm & Type)</b>"))
        self.header_output = QTextEdit()
        self.header_output.setReadOnly(True)
        self.header_output.setStyleSheet("font-family: Consolas, monospace; background-color: #f8f9fa;")
        header_layout.addWidget(self.header_output)
        result_splitter.addWidget(header_widget)
        
        # Payload Box
        payload_widget = QWidget()
        payload_layout = QVBoxLayout(payload_widget)
        payload_layout.addWidget(QLabel("<b>Payload (Data/Claims)</b>"))
        self.payload_output = QTextEdit()
        self.payload_output.setReadOnly(True)
        self.payload_output.setStyleSheet("font-family: Consolas, monospace; background-color: #f8f9fa;")
        payload_layout.addWidget(self.payload_output)
        result_splitter.addWidget(payload_widget)
        
        layout.addWidget(result_splitter)

    def decode_jwt(self):
        token = self.token_input.toPlainText().strip()
        if not token:
            self.header_output.clear()
            self.payload_output.clear()
            return
            
        parts = token.split('.')
        if len(parts) < 2:
            self.header_output.setText("Invalid JWT: Missing segments.")
            self.payload_output.setText("A valid JWT must have at least a Header and Payload separated by a dot.")
            return
            
        def decode_part(segment):
            try:
                # Add padding back if missing (Base64 strings must be multiples of 4)
                rem = len(segment) % 4
                if rem > 0:
                    segment += '=' * (4 - rem)
                decoded_bytes = base64.urlsafe_b64decode(segment)
                decoded_json = json.loads(decoded_bytes.decode('utf-8'))
                return json.dumps(decoded_json, indent=4)
            except Exception as e:
                return f"Error decoding segment: {str(e)}"

        self.header_output.setText(decode_part(parts[0]))
        self.payload_output.setText(decode_part(parts[1]))

# ==========================================
# MAIN WINDOW: Workspace Manager
# ==========================================
class MiniPostman(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lightweight API Tester - Pro Edition")
        self.resize(1100, 750)

        # File paths for saving data
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.collections_file = os.path.join(base_dir, "postman_collections.json")
        self.envs_file = os.path.join(base_dir, "postman_envs.json")
        
        self.collections = {}
        self.environments = {"Global": {"base_url": "https://jsonplaceholder.typicode.com"}}

        # --- Layout ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        # 1. Left Sidebar
        self.setup_sidebar()

        # 2. Right Main Area
        main_content = QWidget()
        self.main_layout = QVBoxLayout(main_content)
        
        # Environment Toolbar
        env_layout = QHBoxLayout()
        env_layout.addWidget(QLabel("Environment:"))
        self.env_dropdown = QComboBox()
        self.env_dropdown.currentIndexChanged.connect(self.update_env_dropdown_style)
        
        self.env_edit_btn = QPushButton("⚙ Manage Environments")
        self.env_edit_btn.clicked.connect(self.manage_environments)
        
        env_layout.addWidget(self.env_dropdown)
        env_layout.addWidget(self.env_edit_btn)
        env_layout.addStretch()
        self.main_layout.addLayout(env_layout)

        # Main Tabbed Interface
        self.workspace_tabs = QTabWidget()
        self.workspace_tabs.setTabsClosable(True)
        self.workspace_tabs.tabCloseRequested.connect(self.close_tab)
        self.main_layout.addWidget(self.workspace_tabs)
        
        # Add JWT Decoder Tab (Make it the first tab and non-closable)
        self.jwt_tab = JwtDecoderTab()
        jwt_index = self.workspace_tabs.addTab(self.jwt_tab, "🔒 JWT Decoder")
        # Remove the close button for the JWT tab to prevent accidental closure
        self.workspace_tabs.tabBar().setTabButton(jwt_index, self.workspace_tabs.tabBar().ButtonPosition.RightSide, None)

        self.splitter.addWidget(main_content)
        self.splitter.setSizes([250, 850])

        # Load data and setup initial state
        self.load_disk_data()
        self.add_new_tab("New Request")
        
        # Default view to the "New Request" tab instead of the JWT decoder
        self.workspace_tabs.setCurrentIndex(1)

    # --- Workspace & Tab Logic ---
    def add_new_tab(self, title="New Request", data=None):
        new_tab = RequestTab(self)
        if data:
            new_tab.set_state(data)
        
        index = self.workspace_tabs.addTab(new_tab, title)
        self.workspace_tabs.setCurrentIndex(index)

    def close_tab(self, index):
        # Prevent closing if it's the JWT tab (failsafe) or if it's the last Request tab
        if self.workspace_tabs.widget(index) == self.jwt_tab:
            return
        # Allow close if there is at least one other tab remaining besides the JWT tab
        if self.workspace_tabs.count() > 2:
            self.workspace_tabs.removeTab(index)

    # --- Sidebar & Collections ---
    def setup_sidebar(self):
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.addWidget(QLabel("<b>Saved Requests</b>"))
        
        self.saved_list = QListWidget()
        self.saved_list.itemClicked.connect(self.load_request)
        sidebar_layout.addWidget(self.saved_list)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Current Tab")
        save_btn.clicked.connect(self.save_request)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.delete_request)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(del_btn)
        sidebar_layout.addLayout(btn_layout)
        self.splitter.addWidget(sidebar_widget)

    def load_disk_data(self):
        if os.path.exists(self.collections_file):
            try:
                with open(self.collections_file, "r") as f:
                    self.collections = json.load(f)
                self.saved_list.addItems(self.collections.keys())
            except: pass
            
        if os.path.exists(self.envs_file):
            try:
                with open(self.envs_file, "r") as f:
                    self.environments = json.load(f)
            except: pass
            
        self.refresh_env_dropdown()

    def save_request(self):
        current_tab = self.workspace_tabs.currentWidget()
        if not current_tab or isinstance(current_tab, JwtDecoderTab): 
            return # Don't save if they are on the JWT tab

        name, ok = QInputDialog.getText(self, "Save Request", "Name for this request:")
        if ok and name.strip():
            name = name.strip()
            self.collections[name] = current_tab.get_state()
            
            with open(self.collections_file, "w") as f:
                json.dump(self.collections, f, indent=4)
                
            if not self.saved_list.findItems(name, Qt.MatchFlag.MatchExactly):
                self.saved_list.addItem(name)
            self.workspace_tabs.setTabText(self.workspace_tabs.currentIndex(), name)

    def load_request(self, item):
        name = item.text()
        req_data = self.collections.get(name)
        if req_data:
            # Open it in a new tab to avoid overwriting current work
            self.add_new_tab(name, req_data)

    def delete_request(self):
        current = self.saved_list.currentItem()
        if current:
            name = current.text()
            if name in self.collections:
                del self.collections[name]
                with open(self.collections_file, "w") as f:
                    json.dump(self.collections, f, indent=4)
            self.saved_list.takeItem(self.saved_list.row(current))

    # --- Environment Logic ---
    def get_active_env_vars(self):
        env_name = self.env_dropdown.currentText()
        return self.environments.get(env_name, {})

    def refresh_env_dropdown(self):
        self.env_dropdown.clear()
        self.env_dropdown.addItems(self.environments.keys())

    def update_env_dropdown_style(self):
        # Visually highlight that an environment is active
        if self.env_dropdown.currentText() != "Global":
            self.env_dropdown.setStyleSheet("background-color: #e6f2ff; font-weight: bold;")
        else:
            self.env_dropdown.setStyleSheet("")

    def manage_environments(self):
        # A simple dialog to edit the raw JSON of the environments
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Environments (JSON Edit)")
        dialog.resize(500, 400)
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Define your environments and variables here in JSON format:"))
        
        text_edit = QTextEdit()
        text_edit.setStyleSheet("font-family: Consolas, monospace;")
        text_edit.setText(json.dumps(self.environments, indent=4))
        layout.addWidget(text_edit)
        
        save_btn = QPushButton("Save Environments")
        layout.addWidget(save_btn)
        
        def save_and_close():
            try:
                new_envs = json.loads(text_edit.toPlainText())
                self.environments = new_envs
                with open(self.envs_file, "w") as f:
                    json.dump(self.environments, f, indent=4)
                self.refresh_env_dropdown()
                dialog.accept()
            except ValueError as e:
                QMessageBox.critical(dialog, "Invalid JSON", f"Please fix your JSON formatting:\n{e}")
                
        save_btn.clicked.connect(save_and_close)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiniPostman()
    window.show()
    sys.exit(app.exec())

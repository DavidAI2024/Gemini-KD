import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, \
    QTextEdit, QScrollArea, QHBoxLayout, QLabel, QCheckBox, QDialog, QLineEdit, QMessageBox
from PyQt5.QtGui import QFont, QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QEvent
import requests
import google.generativeai as genai

class EnterSignalEmitter(QObject):
    enter_pressed = pyqtSignal()

class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super(ApiKeyDialog, self).__init__(parent)
        self.setWindowTitle("Enter API Key")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout(self)

        # Set the window icon from URL
        icon_url = "https://i.ibb.co/bLH16qm/man.png"
        icon_image = QImage()
        icon_image.loadFromData(requests.get(icon_url).content)
        self.setWindowIcon(QIcon(QPixmap.fromImage(icon_image)))

        self.api_key_edit = QLineEdit(self)
        self.api_key_edit.setPlaceholderText("Enter your API Key")
        self.set_recursive_font(self.api_key_edit)
        layout.addWidget(self.api_key_edit)

        confirm_button = QPushButton("Confirm", self)
        confirm_button.clicked.connect(self.confirm_button_clicked)
        layout.addWidget(confirm_button)

    def set_recursive_font(self, widget):
        # Replace 'path/to/Recursive.ttf' with the actual path to your Recursive font file
        font = QFont("Recursive", 12)
        widget.setFont(font)

    def confirm_button_clicked(self):
        api_key = self.api_key_edit.text()
        if not api_key or len(api_key) < 10:
            QMessageBox.warning(self, "Warning", "Please enter a valid API KEY.")
        else:
            self.accept()

class StyledCheckbox(QCheckBox):
    def __init__(self, text, color, parent=None):
        super(StyledCheckbox, self).__init__(text, parent)
        self.setStyleSheet(f"""
            QCheckBox {{
                color: #000000;
                background-color: {color};
                padding: 5px;
                border: 2px solid #2980B9;
                border-radius: 5px;
                spacing: 5px;
                font-family: 'Recursive';
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
            }}
        """)

class GeminiApp(QMainWindow):
    def __init__(self, api_key):
        super(GeminiApp, self).__init__()

        if not api_key:
            QMessageBox.warning(self, "Warning", "API Key not provided. Exiting...")
            sys.exit()

        # Configure genai with the API key
        genai.configure(api_key=api_key)

        # Use the gemini-pro model
        self.model = genai.GenerativeModel('gemini-pro')

        # Create main window
        self.setWindowTitle("KDGemini-pro")
        self.setGeometry(100, 100, 900, 800)

        # Set the window icon from URL
        icon_url = "https://i.ibb.co/gyNMj14/Google-Bard-logo-svg.png"
        icon_image = QImage()
        icon_image.loadFromData(requests.get(icon_url).content)
        self.setWindowIcon(QIcon(QPixmap.fromImage(icon_image)))

        # Create central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create QLabel for the icon above "Ask a question" box
        icon_label = QLabel(self)
        icon_url = "https://i.ibb.co/RjmQbW9/KDTools-4.png"  # Replace with the actual URL
        icon_image = QImage()
        icon_image.loadFromData(requests.get(icon_url).content)
        icon_label.setPixmap(QPixmap.fromImage(icon_image).scaledToWidth(250))  # Adjust the width as needed
        icon_label.setAlignment(Qt.AlignHCenter)  # Align the icon to the center
        layout.addWidget(icon_label)

        # Create QTextEdit for user input with Recursive font
        self.input_text_edit = QTextEdit(self)
        self.input_text_edit.setPlaceholderText("Ask a question...")
        self.set_recursive_font(self.input_text_edit)
        self.input_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #F0F8FF;
                padding: 10px;
                border: 2px solid #B0C4DE;
                border-radius: 10px;
                box-shadow: 3px 3px 5px #D3D3D3;
            }
        """)
        layout.addWidget(self.input_text_edit)

        # Create QHBoxLayout for button and icon label
        button_layout = QHBoxLayout()

        # Create QPushButton with HTML and CSS styling
        submit_button = QPushButton("Submit", self)
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #6495ED;
                color: white;
                padding: 10px 20px;
                border: none;
                font-family: "Recursive";
                border-radius: 10px;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #4169E1;
            }
            QPushButton:pressed {
                background-color: #191970;
            }
        """)
        submit_button.clicked.connect(self.display_gemini_response)

        # Add submit button to the layout
        button_layout.addWidget(submit_button)

        # Set the button layout to the main layout
        layout.addLayout(button_layout)

        # Create QScrollArea with QTextEdit for displaying Gemini response with Recursive font
        self.response_text_edit = QTextEdit(self)
        self.response_text_edit.setReadOnly(True)
        self.set_recursive_font(self.response_text_edit)
        self.response_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #F5F5DC;
                padding: 10px;
                border: 2px solid #DAA520;
                border-radius: 10px;
                box-shadow: 3px 3px 5px #D3D3D3;
            }
        """)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.response_text_edit)
        layout.addWidget(scroll_area)

        # Create checkbox to enable/disable conversation state
        self.conversation_state_checkbox = StyledCheckbox("Keep conversation active", "#ff686b", self)
        self.set_recursive_font(self.conversation_state_checkbox)
        layout.addWidget(self.conversation_state_checkbox)

        # Create checkboxes for selecting temperature
        self.temperature_checkboxes = {
            '0.3': StyledCheckbox("Unleash Imagination (0.3) - Diverse and whimsical responses, but less focused.", "#E74C3C", self),
            '0.5': StyledCheckbox("Creative Balance (0.5) - Strikes a balance between originality and coherence for general use.", "#2ECC71", self),
            '1.0': StyledCheckbox("Standard Precision (1.0) - Well-balanced responses suitable for most situations.", "#F39C12", self),
            '1.2': StyledCheckbox("Intense Focus (1.2) - Sharper responses but potentially less imaginative.", "#71B1D9", self)
        }

        # Add temperature checkboxes to layout
        for checkbox in self.temperature_checkboxes.values():
            layout.addWidget(checkbox)

        # Set central widget
        self.setCentralWidget(central_widget)

        # Initialize conversation state
        self.conversation_state = {'context': ''}

        # Connect Enter key press signal to display_gemini_response
        self.enter_signal_emitter = EnterSignalEmitter()
        self.enter_signal_emitter.enter_pressed.connect(self.display_gemini_response)
        self.input_text_edit.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.input_text_edit and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            self.enter_signal_emitter.enter_pressed.emit()
            return True
        return super().eventFilter(obj, event)

    def set_recursive_font(self, text_edit):
        # Replace 'path/to/Recursive.ttf' with the actual path to your Recursive font file
        font = QFont("Recursive", 10)
        text_edit.setFont(font)

    def remove_special_symbols(self, text):
        # Remove "*" and "**" from the text
        return text.replace("*", "").replace("**", "")

    def display_gemini_response(self):
        try:
            # Get user input from QTextEdit
            user_input = self.input_text_edit.toPlainText()

            # Include the context from the previous conversation if checkbox is checked
            if self.conversation_state_checkbox.isChecked():
                user_input_with_context = f"{self.conversation_state['context']} {user_input}".strip()
            else:
                user_input_with_context = user_input

            # Determine selected temperature from checkboxes
            selected_temperature = None
            for temperature, checkbox in self.temperature_checkboxes.items():
                if checkbox.isChecked():
                    selected_temperature = float(temperature)
                    break

            if selected_temperature is None:
                # If no temperature is selected, use the default value
                selected_temperature = 1.0

            # Generate text from user input with selected temperature
            response = self.model.generate_content(
                user_input_with_context,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    
                    temperature=selected_temperature)
            )

            # Remove special symbols from the response
            cleaned_response = self.remove_special_symbols(response.text)

            # Update conversation context if checkbox is checked
            if self.conversation_state_checkbox.isChecked():
                self.conversation_state['context'] = cleaned_response

            # Display Gemini response in QTextEdit
            self.response_text_edit.clear()  # Clear previous content
            self.response_text_edit.append(f"<strong>🐰Question:</strong> {user_input}")
            self.response_text_edit.append(f"<strong>🐘Answer:</strong> {cleaned_response}")
            self.response_text_edit.append("\n")
        except ValueError as e:
            # Handle the specific ValueError
            error_message = "You have entered prohibited words"
            QMessageBox.warning(self, "Error", error_message)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Open the dialog window for entering the API key
    api_key_dialog = ApiKeyDialog()
    result = api_key_dialog.exec_()

    # If the user confirms, proceed with opening the main GUI
    if result == QDialog.Accepted:
        api_key = api_key_dialog.api_key_edit.text()
        window = GeminiApp(api_key)
        window.show()
        sys.exit(app.exec_())

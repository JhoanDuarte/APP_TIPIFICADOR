from PyQt5.QtGui import QIntValidator
from PyQt5 import QtCore, QtGui, QtWidgets
import subprocess, sys, os
from db_connection import conectar_sql_server
import dashboard

# Conexión a BD
conn = conectar_sql_server('DB_DATABASE')
if conn is None:
    raise RuntimeError("No se pudo conectar a la base de datos.")

def authenticate_user_by_doc(num_doc: str, password: str):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ID, FIRST_NAME, LAST_NAME, PASSWORD, STATUS_ID FROM USERS WHERE NUM_DOC = ?",
        (num_doc,),
    )
    row = cursor.fetchone()
    cursor.close()
    if not row:
        return None
    user_id, first_name, last_name, stored_password, status_id = row
    return (user_id, first_name, last_name, status_id) if stored_password == password else None

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Tipificador Médica")
        self.resize(700, 800)
        self.center_on_screen()

        # Layout principal
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addStretch()

        # Fondo
        bg_path = os.path.join(os.path.dirname(__file__), "Fondo.png")
        if os.path.exists(bg_path):
            palette = QtGui.QPalette()
            pix = QtGui.QPixmap(bg_path).scaled(self.size(), QtCore.Qt.IgnoreAspectRatio)
            palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(pix))
            self.setPalette(palette)

        # Panel central semitransparente
        self.panel = QtWidgets.QFrame()
        self.panel.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 150);
                border-radius: 20px;
            }
        """)

        vbox = QtWidgets.QVBoxLayout(self.panel)
        vbox.setContentsMargins(40, 30, 40, 30)
        vbox.setSpacing(30)

        # Logo (o texto si no existe)
        logo_path = os.path.join(os.path.dirname(__file__), "LogoImg.png")
        if os.path.exists(logo_path):
            lbl_logo = QtWidgets.QLabel(self.panel)
            lbl_logo.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            pixmap = QtGui.QPixmap(logo_path).scaled(140, 140,
                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            lbl_logo.setPixmap(pixmap)
            lbl_logo.setAlignment(QtCore.Qt.AlignCenter)
            vbox.addWidget(lbl_logo)
        else:
            lbl_logo = QtWidgets.QLabel(self.panel)
            lbl_logo.setText("")  # imagen vacía
            lbl_logo.setAlignment(QtCore.Qt.AlignCenter)
            vbox.addWidget(lbl_logo)

        # Texto debajo del logo
        lbl_text = QtWidgets.QLabel("Iniciar sesión", alignment=QtCore.Qt.AlignCenter)
        lbl_text.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            background: transparent;
        """)
        vbox.addWidget(lbl_text)

        # Documento
        hdoc = QtWidgets.QHBoxLayout()
        lbl_doc = QtWidgets.QLabel("📄")
        lbl_doc.setFixedWidth(28)
        lbl_doc.setStyleSheet("font-size: 22px; background: transparent;")
        hdoc.addWidget(lbl_doc)

        lbl_doctxt = QtWidgets.QLabel("Documento:")
        lbl_doctxt.setStyleSheet("color: white; background: transparent;")
        hdoc.addWidget(lbl_doctxt)

        self.edit_doc = QtWidgets.QLineEdit()
        self.edit_doc.setPlaceholderText("12345678")
        self.edit_doc.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0,0,0,200);
                color: white;
                border-radius: 15px;
                padding: 8px 12px;
                font-size: 14px;
            }
        """)
        # Solo permitir dígitos, hasta 12 caracteres
        hdoc.addWidget(self.edit_doc, stretch=1)
        vbox.addLayout(hdoc)

        # Contraseña
        hpwd = QtWidgets.QHBoxLayout()
        lbl_pwd = QtWidgets.QLabel("🔒")
        lbl_pwd.setFixedWidth(28)
        lbl_pwd.setStyleSheet("font-size: 22px; background: transparent;")
        hpwd.addWidget(lbl_pwd)

        lbl_pwdtxt = QtWidgets.QLabel("Contraseña:")
        lbl_pwdtxt.setStyleSheet("color: white; background: transparent;")
        hpwd.addWidget(lbl_pwdtxt)

        self.edit_pwd = QtWidgets.QLineEdit()
        self.edit_pwd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.edit_pwd.setPlaceholderText("••••••••")
        self.edit_pwd.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0,0,0,200);
                color: white;
                border-radius: 15px;
                padding: 8px 12px;
                font-size: 14px;
            }
        """)
        hpwd.addWidget(self.edit_pwd, stretch=1)
        vbox.addLayout(hpwd)

        # Botón redondeado y azul
        btn = QtWidgets.QPushButton("Iniciar sesión")
        btn.setFixedSize(200, 50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 25px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #339CFF;
            }
        """)
        btn.clicked.connect(self.on_login)
        vbox.addWidget(btn, alignment=QtCore.Qt.AlignCenter)

        # Centrar el panel en la ventana
        h_container = QtWidgets.QHBoxLayout()
        h_container.addStretch()
        h_container.addWidget(self.panel)
        h_container.addStretch()
        main_layout.addLayout(h_container)
        main_layout.addStretch()

    def center_on_screen(self):
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def on_login(self):
        num_doc = self.edit_doc.text().strip()
        pwd     = self.edit_pwd.text().strip()

        if not num_doc or not pwd:
            QtWidgets.QMessageBox.warning(self, "Datos faltantes", "Debe ingresar documento y contraseña.")
            return

        auth = authenticate_user_by_doc(num_doc, pwd)
        if auth is None:
            QtWidgets.QMessageBox.critical(self, "Error", "Documento o contraseña incorrectos.")
            return

        user_id, first_name, last_name, status_id = auth
        if status_id != 5:
            QtWidgets.QMessageBox.warning(self, "Usuario inactivo", "Tu cuenta no está activa. Contacta al administrador.")
            return

        # Ruta absoluta a dashboard.py
        script = os.path.join(os.path.dirname(__file__), "dashboard.py")

        # Lanza dashboard.py en un proceso separado
        subprocess.Popen([
            sys.executable,
            script,
            str(user_id),
            first_name,
            last_name
        ], cwd=os.path.dirname(__file__))

        # Cierra la ventana de login
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = LoginWindow()
    w.show()
    sys.exit(app.exec_())

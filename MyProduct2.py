import sqlite3
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MyProductWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("자전거용품 관리")
        self.resize(720, 520)

        self.database_path = Path(__file__).with_name("MyProduct2.db")
        self.connection = sqlite3.connect(self.database_path)
        self.create_table()
        self.setup_ui()
        self.load_products()

    def create_table(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS MyProduct (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL
            )
            """
        )
        self.connection.commit()

    def setup_ui(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #071a35, stop: 0.55 #123b63, stop: 1 #1a6b78
                );
            }
            QLabel#titleLabel {
                color: #f6fbff;
                font-size: 27px;
                font-weight: 800;
                padding: 4px 0;
            }
            QLabel#subtitleLabel {
                color: #a9d8e8;
                font-size: 13px;
                padding-bottom: 8px;
            }
            QGroupBox {
                color: #eafaff;
                font-size: 15px;
                font-weight: 700;
                border: 1px solid #4faec4;
                border-radius: 12px;
                margin-top: 10px;
                padding: 18px 14px 12px 14px;
                background: rgba(5, 24, 49, 205);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: #73e6e9;
            }
            QLineEdit {
                color: #eefbff;
                background: #0d2a4b;
                border: 1px solid #4e83a7;
                border-radius: 7px;
                padding: 8px 10px;
                selection-background-color: #19b7bc;
            }
            QLineEdit:focus {
                border: 2px solid #73e6e9;
                background: #12385d;
            }
            QPushButton {
                color: #ffffff;
                background: #167c9b;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #20b7b5;
            }
            QPushButton:pressed {
                background: #0e657f;
                padding-top: 11px;
                padding-left: 17px;
            }
            QTableWidget {
                color: #eafaff;
                background: rgba(6, 27, 51, 235);
                alternate-background-color: #103758;
                border: 1px solid #4faec4;
                border-radius: 10px;
                gridline-color: #285675;
                selection-background-color: #d66b45;
                selection-color: #ffffff;
                padding: 5px;
            }
            QHeaderView::section {
                color: #ffffff;
                background: #d05c3d;
                border: none;
                padding: 9px;
                font-weight: 800;
            }
            QScrollBar:vertical {
                background: #0b2746;
                width: 12px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #45b8bd;
                border-radius: 5px;
                min-height: 30px;
            }
            """
        )

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("검색 또는 수정할 ID")

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("예: 자전거 헬멧")

        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("숫자만 입력")

        form_layout = QFormLayout()
        form_layout.addRow("상품 ID", self.id_edit)
        form_layout.addRow("상품명", self.name_edit)
        form_layout.addRow("가격", self.price_edit)

        input_group = QGroupBox("자전거용품 정보")
        input_group.setLayout(form_layout)

        insert_button = QPushButton("입력")
        update_button = QPushButton("수정")
        delete_button = QPushButton("삭제")
        search_button = QPushButton("검색")
        clear_button = QPushButton("전체보기")
        clear_button.setObjectName("clearButton")

        insert_button.clicked.connect(self.insert_product)
        update_button.clicked.connect(self.update_product)
        delete_button.clicked.connect(self.delete_product)
        search_button.clicked.connect(self.search_products)
        clear_button.clicked.connect(self.show_all_products)

        button_layout = QHBoxLayout()
        for button in (
            insert_button,
            update_button,
            delete_button,
            search_button,
            clear_button,
        ):
            button_layout.addWidget(button)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "상품명", "가격"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellDoubleClicked.connect(self.fill_form_from_row)

        title_label = QLabel("BIKE GEAR  /  PRODUCT DESK")
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("자전거용품을 빠르게 입력하고, 검색하고, 관리하세요.")
        subtitle_label.setObjectName("subtitleLabel")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 18, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(input_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.table, 1)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def get_id(self):
        value = self.id_edit.text().strip()
        if not value.isdigit() or int(value) <= 0:
            raise ValueError("ID는 양의 정수로 입력하세요.")
        return int(value)

    def get_name_and_price(self):
        name = self.name_edit.text().strip()
        price_text = self.price_edit.text().strip()
        if not name:
            raise ValueError("상품명을 입력하세요.")
        if not price_text.isdigit() or int(price_text) < 0:
            raise ValueError("가격은 0 이상의 정수로 입력하세요.")
        return name, int(price_text)

    def insert_product(self):
        try:
            name, price = self.get_name_and_price()
            self.connection.execute(
                "INSERT INTO MyProduct (name, price) VALUES (?, ?)",
                (name, price),
            )
            self.connection.commit()
            self.clear_form()
            self.load_products()
        except ValueError as error:
            self.show_error(str(error))

    def update_product(self):
        try:
            product_id = self.get_id()
            name, price = self.get_name_and_price()
            cursor = self.connection.execute(
                "UPDATE MyProduct SET name = ?, price = ? WHERE id = ?",
                (name, price, product_id),
            )
            self.connection.commit()
            if cursor.rowcount == 0:
                self.show_error("수정할 상품 ID가 없습니다.")
                return
            self.clear_form()
            self.load_products()
        except ValueError as error:
            self.show_error(str(error))

    def delete_product(self):
        try:
            product_id = self.get_id()
            cursor = self.connection.execute(
                "DELETE FROM MyProduct WHERE id = ?", (product_id,)
            )
            self.connection.commit()
            if cursor.rowcount == 0:
                self.show_error("삭제할 상품 ID가 없습니다.")
                return
            self.clear_form()
            self.load_products()
        except ValueError as error:
            self.show_error(str(error))

    def search_products(self):
        keyword = self.id_edit.text().strip() or self.name_edit.text().strip()
        if not keyword:
            self.show_error("ID 또는 상품명을 입력하세요.")
            return

        if keyword.isdigit():
            rows = self.connection.execute(
                "SELECT id, name, price FROM MyProduct WHERE id = ? ORDER BY id",
                (int(keyword),),
            ).fetchall()
        else:
            rows = self.connection.execute(
                """
                SELECT id, name, price FROM MyProduct
                WHERE name LIKE ? ORDER BY id
                """,
                (f"%{keyword}%",),
            ).fetchall()
        self.populate_table(rows)

    def show_all_products(self):
        self.clear_form()
        self.load_products()

    def load_products(self):
        rows = self.connection.execute(
            "SELECT id, name, price FROM MyProduct ORDER BY id"
        ).fetchall()
        self.populate_table(rows)

    def populate_table(self, rows):
        self.table.setRowCount(len(rows))
        for row_index, (product_id, name, price) in enumerate(rows):
            id_item = QTableWidgetItem(str(product_id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item = QTableWidgetItem(f"{price:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_index, 0, id_item)
            self.table.setItem(row_index, 1, QTableWidgetItem(name))
            self.table.setItem(row_index, 2, price_item)
        self.table.resizeColumnsToContents()

    def fill_form_from_row(self, row, _column):
        self.id_edit.setText(self.table.item(row, 0).text())
        self.name_edit.setText(self.table.item(row, 1).text())
        self.price_edit.setText(self.table.item(row, 2).text().replace(",", ""))

    def clear_form(self):
        self.id_edit.clear()
        self.name_edit.clear()
        self.price_edit.clear()

    def show_error(self, message):
        QMessageBox.warning(self, "입력 확인", message)

    def closeEvent(self, event):
        self.connection.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyProductWindow()
    window.show()
    sys.exit(app.exec())
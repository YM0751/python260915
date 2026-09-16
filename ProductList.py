import sqlite3


class ProductList:
    def __init__(self, database_name="MyProduct.db"):
        self.connection = sqlite3.connect(database_name)
        self.create_table()

    def create_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL
            )
        """
        self.connection.execute(query)
        self.connection.commit()

    def insert_product(self, product_id, product_name, product_price):
        query = """
            INSERT INTO Products (productID, productName, productPrice)
            VALUES (?, ?, ?)
        """
        self.connection.execute(
            query,
            (product_id, product_name, product_price),
        )
        self.connection.commit()

    def update_product(self, product_id, product_name, product_price):
        query = """
            UPDATE Products
            SET productName = ?, productPrice = ?
            WHERE productID = ?
        """
        cursor = self.connection.execute(
            query,
            (product_name, product_price, product_id),
        )
        self.connection.commit()
        return cursor.rowcount

    def delete_product(self, product_id):
        query = "DELETE FROM Products WHERE productID = ?"
        cursor = self.connection.execute(query, (product_id,))
        self.connection.commit()
        return cursor.rowcount

    def select_products(self, product_id=None):
        if product_id is None:
            query = """
                SELECT productID, productName, productPrice
                FROM Products
                ORDER BY productID
            """
            cursor = self.connection.execute(query)
        else:
            query = """
                SELECT productID, productName, productPrice
                FROM Products
                WHERE productID = ?
                ORDER BY productID
            """
            cursor = self.connection.execute(query, (product_id,))
        return cursor.fetchall()

    def insert_sample_data(self, count=1000):
        products = [
            (product_id, f"전자제품{product_id:04d}", 10000 + product_id * 100)
            for product_id in range(1, count + 1)
        ]
        query = """
            INSERT OR IGNORE INTO Products (productID, productName, productPrice)
            VALUES (?, ?, ?)
        """
        self.connection.executemany(query, products)
        self.connection.commit()

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


if __name__ == "__main__":
    with ProductList() as product_list:
        product_list.insert_sample_data(1000)
        products = product_list.select_products()
        print(f"Products 테이블에 저장된 제품 수: {len(products)}개")
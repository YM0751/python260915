from pathlib import Path

from openpyxl import Workbook


def create_product_file():
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "전자제품 목록"

    worksheet.append(["제품ID", "제품명", "가격", "수량"])

    for product_id in range(1, 101):
        worksheet.append(
            [
                product_id,
                f"전자제품{product_id:03d}",
                10000 + product_id * 1000,
                10 + product_id % 50,
            ]
        )

    worksheet.freeze_panes = "A2"
    worksheet.column_dimensions["A"].width = 12
    worksheet.column_dimensions["B"].width = 20
    worksheet.column_dimensions["C"].width = 14
    worksheet.column_dimensions["D"].width = 12

    output_path = Path(__file__).with_name("ProductList.xlsx")
    workbook.save(output_path)
    print(f"{output_path}에 제품 데이터 100개를 저장했습니다.")


if __name__ == "__main__":
    create_product_file()
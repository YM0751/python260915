from pathlib import Path
import shutil


DOWNLOADS = Path(r"C:\Users\student\Downloads")
FILE_CATEGORIES = {
    "images": {".jpg", ".jpeg"},
    "data": {".csv", ".xlsx"},
    "docs": {".txt", ".doc", ".pdf"},
    "archive": {".zip"},
}


def get_available_path(destination: Path) -> Path:
    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


def organize_downloads() -> None:
    for folder_name in FILE_CATEGORIES:
        (DOWNLOADS / folder_name).mkdir(parents=True, exist_ok=True)

    for file_path in DOWNLOADS.iterdir():
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()
        for folder_name, extensions in FILE_CATEGORIES.items():
            if extension in extensions:
                destination = get_available_path(DOWNLOADS / folder_name / file_path.name)
                shutil.move(str(file_path), str(destination))
                print(f"이동 완료: {file_path.name} -> {folder_name}\\")
                break


if __name__ == "__main__":
    organize_downloads()
    print("파일 분류가 완료되었습니다.")

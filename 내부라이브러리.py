import os
import os.path
import glob

print(f"운영체제이름:{os.name}")
print(f"환경변수:{os.environ}")

fName = r"c:\python313\python.exe"

if os.path.exists(fName):
    print(f"{fName}파일의 크기: {os.path.getsize(fName)} 바이트")
else:
    print(f"{fName}파일이 존재하지 않습니다.")

print(glob.glob(r'c:\work\*.py'))



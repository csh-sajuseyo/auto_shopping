import os
import subprocess
import sys

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(base_dir, "main", "사주세요.py")

    try:
        subprocess.Popen([sys.executable, target])
        print("✅ 사주세요.py 실행 시작됨")
    except Exception as e:
        print("❌ 실행 중 오류 발생:", e)

if __name__ == "__main__":
    main()
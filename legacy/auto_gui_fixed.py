
import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def run_coupang():
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 스크립트 폴더로 이동
        script = "main_auto_by_site_localized.py"
        site = "쿠팡"
        cmd = f'cmd /k py {script} {site}'  # 콘솔 유지

        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        messagebox.showerror("실행 실패", str(e))

# GUI 생성
root = tk.Tk()
root.title("쿠팡 자동구매 실행기")
root.geometry("300x150")
root.resizable(False, False)

label = tk.Label(root, text="📦 쿠팡 자동구매", font=("맑은 고딕", 14))
label.pack(pady=15)

run_btn = tk.Button(root, text="▶ 자동구매 실행", font=("맑은 고딕", 12), command=run_coupang)
run_btn.pack(pady=10)

root.mainloop()


import tempfile
import atexit
import sys

is_capturing = False
capture_process = None

def ensure_single_instance():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CUSTOM_TEMP_DIR = os.path.join(BASE_DIR, "..", "temp")
    os.makedirs(CUSTOM_TEMP_DIR, exist_ok=True)
    lock_file = os.path.join(CUSTOM_TEMP_DIR, "sajuseyo.lock")
    print(f"🔍 현재 락파일 경로: {lock_file}")
    print(f"🔎 락파일 존재 여부: {os.path.exists(lock_file)}")
    if os.path.exists(lock_file):
        print("🚫 이미 실행 중입니다.")
        sys.exit()
    with open(lock_file, "w", encoding="utf-8") as f:
        f.write("🔐 락파일 생성 테스트 완료")
    def remove_lock():
        if os.path.exists(lock_file):
            os.remove(lock_file)
    atexit.register(remove_lock)



import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import glob
import shutil
import subprocess
import time

uploaded_files = []
last_uploaded_path = None
capture_start_time = 0
WATCH_FOLDER = os.path.join(os.path.expanduser("~"), "Documents", "사주세요_스크린샷")
os.makedirs(WATCH_FOLDER, exist_ok=True)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def update_uploaded_list():
    for widget in uploaded_list_frame.winfo_children():
        widget.destroy()
    for path in uploaded_files:
        name = os.path.basename(path)
        label = tk.Label(uploaded_list_frame, text=name, anchor="w", bg="white", font=("맑은 고딕", 10))
        label.pack(fill="x", padx=5, pady=2)

def find_latest_capture():
    files = glob.glob(os.path.join(WATCH_FOLDER, "screenshot_crop_*.png"))
    if not files:
        return None
    latest = max(files, key=os.path.getctime)
    return latest


def start_drag_capture():
    global capture_process
    global capture_start_time, is_capturing
    if is_capturing:
        print("⚠️ 캡처 실행 중입니다.")
        return
    is_capturing = True
    capture_start_time = time.time()
    py_path = r"C:\Program Files\Python312\python.exe"
    script_path = r"C:\\Users\\user\\Desktop\\auto_shopping_refactored_완전체_with_capture\\modules\\drag_capture_tool_single_capture.py"
    if os.path.exists(script_path):
        capture_process = subprocess.Popen([py_path, script_path])
    poll_for_new_capture_loop()


def poll_for_new_capture_loop():
    global last_uploaded_path, is_capturing, capture_process
    latest = find_latest_capture()

    if latest:
        if latest != last_uploaded_path and os.path.getctime(latest) > capture_start_time:
            uploaded_files.append(latest)
            last_uploaded_path = latest
            update_uploaded_list()
            is_capturing = False
            capture_process = None

    if capture_process is not None:
        try:
            if capture_process.poll() is not None:
                return_code = capture_process.returncode
                print("📋 종료 코드:", return_code)  # 종료 코드 출력
                if return_code == 99:
                    print("⛔ ESC로 캡처 취소됨 → 상태 복원")
                else:
                    print("❗ 드래그툴 종료됨 (파일 없음)")
                is_capturing = False
                capture_process = None
        except Exception as e:
            print("❗ 종료 상태 확인 중 오류:", e)
            is_capturing = False
            capture_process = None

    root.after(1000, poll_for_new_capture_loop)

def select_files():
    paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg")])
    for p in paths:
        dest = os.path.join(WATCH_FOLDER, os.path.basename(p))
        shutil.copy(p, dest)
        uploaded_files.append(dest)
    update_uploaded_list()

def go_to_main_form():
    start_frame.pack_forget()
    root.geometry("520x800")
    center_window(root, 520, 740)
    form_frame.pack(pady=10)

ensure_single_instance()
root = tk.Tk()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
root.title("사주세요 v1.0 | 구매요청서")
center_window(root, 360, 240)
root.configure(bg="#f0f2f5")

# 시작 화면 (쇼핑몰 선택)
start_frame = tk.Frame(root, bg="#f0f2f5")
start_frame.pack(expand=True)

intro_label = tk.Label(start_frame, text="구매를 원하는 사이트를 선택해주세요", font=("맑은 고딕", 12), bg="#f0f2f5")
intro_label.pack(pady=(40, 20))

logo_frame = tk.Frame(start_frame, bg="#f0f2f5")
logo_frame.pack()

logo_path = os.path.join(BASE_DIR, "..", "assets", "coupang.png")
if os.path.exists(logo_path):
    logo_img = Image.open(logo_path)
    logo_img = logo_img.resize((140, 45))
    logo_tk = ImageTk.PhotoImage(logo_img)
    logo_btn = tk.Label(logo_frame, image=logo_tk, bg="#f0f2f5", cursor="hand2")
    logo_btn.image = logo_tk
    logo_btn.pack(side="left", padx=10)
    logo_btn.bind("<Button-1>", lambda e: go_to_main_form())
else:
    logo_btn = tk.Button(logo_frame, text="쿠팡 시작하기", command=go_to_main_form)
    logo_btn.pack(side="left", padx=10)


def show_image_popup(path):
    if not os.path.exists(path):
        return
    popup = tk.Toplevel()
    popup.title("첨부 이미지 보기")
    img = Image.open(path)
    img = img.resize((min(img.width, 800), min(img.height, 600)))
    tk_img = ImageTk.PhotoImage(img)
    label = tk.Label(popup, image=tk_img)
    label.image = tk_img
    label.pack()

def remove_uploaded_file(path):
    if path in uploaded_files:
        uploaded_files.remove(path)
    if os.path.exists(path):
        os.remove(path)
        update_uploaded_list()

def update_uploaded_list():
    for widget in uploaded_list_frame.winfo_children():
        widget.destroy()
    for path in uploaded_files:
        file_frame = tk.Frame(uploaded_list_frame, bg="white")
        file_frame.pack(fill="x", padx=5, pady=2)
        label = tk.Label(file_frame, text=os.path.basename(path), fg="blue", cursor="hand2", bg="white", font=("맑은 고딕", 10))
        label.pack(side="left", anchor="w")
        label.bind("<Button-1>", lambda e, p=path: show_image_popup(p))
        x_btn = tk.Button(file_frame, text="❌", bg="white", fg="red", bd=0, font=("맑은 고딕", 10), command=lambda p=path: remove_uploaded_file(p))
        x_btn.pack(side="right")


def check_and_submit():
    missing_fields = []
    for field, entry in entries.items():
        if not entry.get().strip():
            missing_fields.append(field)
    if not uploaded_files:
        missing_fields.append("스크린샷")

    if missing_fields:
        msg = "\n".join([f"⛔ {f} 항목이 비어있습니다." for f in missing_fields])
        tk.messagebox.showwarning("입력 누락", msg)
        return

    # 추후 구글 업로드 연동 자리
    tk.messagebox.showinfo("완료", "✅ 구매 요청이 접수되었습니다.")

# 구매 요청서 화면
form_frame = tk.Frame(root, bg="#f0f2f5")

title_frame = tk.Frame(form_frame, bg="#f0f2f5")
title_frame.pack(pady=10)
title_label = tk.Label(title_frame, text="쇼핑몰", font=("맑은 고딕", 18, "bold"), bg="#f0f2f5")
title_label.pack(side="left", padx=10)

if os.path.exists(logo_path):
    logo_img2 = Image.open(logo_path)
    logo_img2 = logo_img2.resize((90, 30))
    logo_tk2 = ImageTk.PhotoImage(logo_img2)
    logo_label = tk.Label(title_frame, image=logo_tk2, bg="#f0f2f5")
    logo_label.image = logo_tk2
    logo_label.pack(side="left")

fields = ["품의 제목", "품의 금액", "총 구매 금액", "요청자(성함)"]
entries = {}
for field in fields:
    lbl = tk.Label(form_frame, text=field, bg="#f0f2f5", anchor="w", font=("맑은 고딕", 11, "bold"))
    lbl.pack(fill="x", padx=30)
    ent = tk.Entry(form_frame, font=("맑은 고딕", 11))
    ent.pack(fill="x", padx=30, pady=(0, 10))
    entries[field] = ent

attach_label = tk.Label(form_frame, text="📎 구매 품목(스크린샷) 첨부 방법: 드래그 캡처 또는 저장파일 선택", bg="#f0f2f5", font=("맑은 고딕", 10))
attach_label.pack(anchor="w", padx=30, pady=(10, 5))

btn1 = tk.Button(form_frame, text="📸 드래그 캡처", command=start_drag_capture, font=("맑은 고딕", 11), width=24, height=2)
btn1.pack(pady=5)

btn2 = tk.Button(form_frame, text="📁 저장 파일에서 선택", command=select_files, font=("맑은 고딕", 11), width=24, height=2)
btn2.pack(pady=5)

list_label = tk.Label(form_frame, text="구매 품목(스크린샷)", bg="#f0f2f5", font=("맑은 고딕", 11, "bold"))
list_label.pack(pady=(20, 5))

list_frame = tk.Frame(form_frame, bg="white", bd=1, relief="solid")
list_frame.pack(padx=30, pady=5, fill="both", expand=False)

canvas = tk.Canvas(list_frame, bg="white", height=120)
scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
uploaded_list_frame = tk.Frame(canvas, bg="white")
uploaded_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
canvas.create_window((0, 0), window=uploaded_list_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

submit_btn = tk.Button(form_frame, text="📝 구매 요청 완료", font=("맑은 고딕",   12, "bold"),
                       bg="#0078ff", fg="white", width=42, height=4, command=check_and_submit)
submit_btn.pack(pady=(20, 15))


root.mainloop()

import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import subprocess
import os
import glob
import time

uploaded_files = []

request_root = None

# --- 개인정보 보호 팝업 ---
def show_privacy_popup():
    messagebox.showinfo("⚠️ 주의사항 안내",
        "구매 진행 시, 학교 비상연락망에 등록된 성함과 전화번호를 바탕으로 배송지 등록이 자동으로 이루어집니다.
"
        "해당 비상연락망은 학교 내부 구글 시트에 안전하게 보관되어 있으며,
"
        "외부에서는 접근할 수 없도록 철저히 제한되어 있습니다.
"
        "본 정보는 오직 배송지 등록 기능에만 사용되며,
"
        "다른 용도로 저장되거나 외부로 유출되지 않습니다.

"
        "📦 안전하고 정확한 물품 배송을 위한 협조에 감사드립니다."
    )

# --- 캡처 도구 실행 ---
def start_drag_capture():
    global request_root
    try:
        request_root.iconify()
        time.sleep(1)

        python_path = r"C:\Program Files\Python312\python.exe"
        capture_script_path = os.path.join(
            os.getcwd(),
            "utils",
            "drag_capture_tool_single_capture.py"
        )

        # 현재 시점의 최신 캡처 시간 기록
        before_files = glob.glob(os.path.join(os.path.join(os.path.expanduser("~"), "Documents", "사주세요_스크린샷"), "screenshot_crop_*.png"))
        before_latest = max([os.path.getctime(f) for f in before_files], default=0)

        if not os.path.exists("스크린샷보관함"):
            os.makedirs("스크린샷보관함")

        # 캡처 스크립트 실행
        subprocess.Popen([python_path, capture_script_path])

        # 새 파일 생길 때까지 대기 (최대 10초)
        for _ in range(100):
            time.sleep(0.1)
            after_files = glob.glob(os.path.join(os.path.join(os.path.expanduser("~"), "Documents", "사주세요_스크린샷"), "screenshot_crop_*.png"))
            new_files = [f for f in after_files if os.path.getctime(f) > before_latest]
            if new_files:
                latest_file = max(new_files, key=os.path.getctime)
                break
        else:
            raise Exception("새 스크린샷 파일을 찾지 못했습니다.")

        request_root.deiconify()

        uploaded_files.append(latest_file)
        update_uploaded_list()

    except Exception as e:
        request_root.deiconify()
        messagebox.showerror("캡처 실패", str(e))


def attach_from_file():
    filepaths = filedialog.askopenfilenames(filetypes=[("이미지 파일", "*.png;*.jpg;*.jpeg")])
    if filepaths:
        uploaded_files.extend(filepaths)
        update_uploaded_list()

# --- 첨부 실행 분기 ---
def attach_screenshot():
    mode = capture_mode.get()
    if mode == "drag":
        start_drag_capture()
    else:
        attach_from_file()

def show_image_popup(image_path):
    if not os.path.exists(image_path):
        messagebox.showerror("파일 오류", f"이미지를 열 수 없습니다.
파일 경로:
{image_path}")
        return
    if not os.path.exists(image_path):
        messagebox.showerror("이미지 오류", f"파일을 찾을 수 없습니다:
{image_path}")
        return
    popup = tk.Toplevel()
    popup.title("스크린샷 보기")
    popup.geometry("600x600")
    img = Image.open(image_path)
    img.thumbnail((580, 580))
    photo = ImageTk.PhotoImage(img)
    label = tk.Label(popup, image=photo)
    label.image = photo
    label.pack(expand=True)


# --- 첨부된 이미지 리스트 UI 갱신 ---
def update_uploaded_list():
    for widget in uploaded_frame.winfo_children():
        widget.destroy()

    for path in uploaded_files:
        row = tk.Frame(uploaded_frame)
        row.pack(anchor="w", pady=2)

        label = tk.Label(row, text=os.path.basename(path), fg="gray", cursor="hand2")
        label.bind("<Button-1>", lambda e, p=path: show_image_popup(p))
        label.pack(side="left")

        btn = tk.Button(row, text="❌", command=lambda p=path: remove_file(p), fg="red", bd=0)
        btn.pack(side="left", padx=5)

# --- 개별 파일 삭제 ---
def remove_file(path):
    if path in uploaded_files:
        uploaded_files.remove(path)
        update_uploaded_list()

# --- 구매 요청서 제출 ---
def submit_form():
    title = entry_title.get()
    amount = entry_amount.get()
    total = entry_total.get()
    name = entry_name.get()
    mall = mall_var.get()

    if not all([title, amount, total, name]) or not uploaded_files:
        messagebox.showwarning("입력 누락", "모든 항목을 입력하고 스크린샷도 첨부해주세요.")
        return

    messagebox.showinfo("요청 완료", f"{len(uploaded_files)}개의 이미지와 함께 구매 요청이 저장되었습니다.
(※ 업로드는 다음 단계에서 진행됩니다)")

# --- 2단계 요청서 창 ---
def open_request_window(event=None):
    global request_root
    global start_root
    start_root.destroy()
    # 구매 요청서는 캡처 이후에 띄워야 함, entry_title, entry_amount, entry_total, entry_name
    global mall_var, capture_mode, uploaded_frame

    request_root = tk.Tk()
    request_root.configure(bg="#f2f5f7")
    request_root.title("사주세요 - 구매 요청서")
    request_root.geometry("550x650")
    request_root.resizable(False, False)

    show_privacy_popup()

    mall_var = tk.StringVar(value="쿠팡")
    frame = tk.Frame(request_root, bg="#ffffff", bd=2, relief="groove", padx=15, pady=15)
    frame.pack(pady=5)
    capture_mode = tk.StringVar(value="drag")


    uploaded_frame = tk.Frame(request_root, bg="#ffffff", bd=2, relief="groove", padx=15, pady=15)
    uploaded_frame.pack(pady=5)

    tk.Label(frame, text="쇼핑몰", font=("맑은 고딕", 12, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="e")
    tk.OptionMenu(frame, mall_var, "쿠팡").grid(row=0, column=1)

    tk.Label(frame, text="품의 제목", font=("맑은 고딕", 12, "bold"), bg="#ffffff").grid(row=1, column=0, sticky="e")
    entry_title = tk.Entry(frame, width=44, font=("맑은 고딕", 12))
    entry_title.grid(row=1, column=1)

    tk.Label(frame, text="품의 금액", font=("맑은 고딕", 12, "bold"), bg="#ffffff").grid(row=2, column=0, sticky="e")
    entry_amount = tk.Entry(frame, width=44, font=("맑은 고딕", 12))
    entry_amount.grid(row=2, column=1)

    tk.Label(frame, text="총 구매 금액", font=("맑은 고딕", 12, "bold"), bg="#ffffff").grid(row=3, column=0, sticky="e")
    entry_total = tk.Entry(frame, width=44, font=("맑은 고딕", 12))
    entry_total.grid(row=3, column=1)

    tk.Label(frame, text="요청자(성함)", font=("맑은 고딕", 12, "bold"), bg="#ffffff").grid(row=4, column=0, sticky="e")
    entry_name = tk.Entry(frame, width=44, font=("맑은 고딕", 12))
    entry_name.grid(row=4, column=1)


    tk.Label(frame, text="구매 품목(스크린샷)", font=("맑은 고딕", 12, "bold")).grid(row=5, column=0, sticky="ne")

    style_frame = tk.Frame(frame)
    style_frame.grid(row=5, column=1, sticky="w")

    drag_btn = tk.Button(style_frame, text="🖱 드래그 캡처", command=start_drag_capture,
                         font=("맑은 고딕", 11, "bold"), bg="#e0e0e0", relief="raised", bd=2, padx=10, pady=5, cursor="hand2")
    drag_btn.pack(anchor="w", pady=3, fill="x")

    file_btn = tk.Button(style_frame, text="📁 저장 파일에서 선택", command=attach_from_file,
                         font=("맑은 고딕", 11, "bold"), bg="#e0e0e0", relief="raised", bd=2, padx=10, pady=5, cursor="hand2")
    file_btn.pack(anchor="w", pady=3, fill="x")


    tk.Button(request_root, text="📝 구매 요청 완료", font=("맑은 고딕", 13, "bold"), bg="#1d72b8", fg="white", padx=10, pady=6, relief="raised", command=submit_form).pack(pady=15)

    center_window(request_root)
    request_root.mainloop()

# --- 1단계 사이트 선택 화면 ---
start_root = tk.Tk()
start_root.title("사주세요 v1.0")
start_root.geometry("400x300")
start_root.resizable(False, False)

tk.Label(start_root, text="사주세요 v1.0", font=("맑은 고딕", 18, "bold")).pack(pady=10)
tk.Label(start_root, text="주문을 원하는 사이트 배너를 클릭하세요", font=("맑은 고딕", 12)).pack(pady=5)

img_path = os.path.join("assets", "coupang.png")
if os.path.exists(img_path):
    coupang_img = Image.open(img_path)
    coupang_img = coupang_img.resize((180, 70), Image.Resampling.LANCZOS)
    coupang_photo = ImageTk.PhotoImage(coupang_img)

    banner = tk.Label(start_root, image=coupang_photo, cursor="hand2")
    banner.image = coupang_photo
    banner.pack(pady=20)
    banner.bind("<Button-1>", open_request_window)
else:
    tk.Button(start_root, text="쿠팡", font=("맑은 고딕", 14), width=15, height=2, command=open_request_window).pack(pady=40)

try:
    center_window(start_root)
    start_root.mainloop()
except Exception as e:
    import traceback
    with open("error_log.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())

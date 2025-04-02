
from core.browser import get_driver
from core.ocr import extract_keywords
from core.matcher import match_items
from sites import coupang, gmarket
import sys
import traceback
import os

def main():
    try:
        site = sys.argv[1] if len(sys.argv) > 1 else "쿠팡"
        image_path = f"images/{site}.png"

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"📂 스크린샷 이미지가 없습니다: {image_path}")

        print(f"🚀 자동구매 시작 - 사이트: {site}, 이미지: {image_path}")
        driver = get_driver()

        keywords = extract_keywords(image_path)
        print(f"🔍 OCR 키워드: {keywords}")

        if site.lower() in ["쿠팡", "coupang"]:
            coupang.run(driver, keywords)
        elif site.lower() in ["지마켓", "gmarket"]:
            gmarket.run(driver, keywords)
        else:
            print(f"❌ 지원하지 않는 사이트: {site}")

    except Exception as e:
        print("❌ 실행 중 예외 발생:", e)
        traceback.print_exc()

    input("⏸️ 종료하려면 Enter를 누르세요...")

if __name__ == "__main__":
    main()

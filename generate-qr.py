# generate_qr_cloud.py
import qrcode
import os

# 1. Dán đường link Streamlit Cloud của bạn vào đây
CLOUD_URL = "https://qr-menu.streamlit.app/"  # <--- THAY LINK CỦA BẠN VÀO ĐÂY

print(f"🚀 Generating QR Codes for Cloud App: {CLOUD_URL}")

# 2. Tạo folder lưu QR
if not os.path.exists("qr_codes_cloud"):
    os.makedirs("qr_codes_cloud")

# 3. Tạo QR cho 10 bàn
for i in range(1, 11):
    # Link sẽ có dạng: https://smart-menu-ai.streamlit.app/?id=Table_1
    link = f"{CLOUD_URL}/?id=Table_{i}"
    
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"qr_codes_cloud/table_{i}.png"
    img.save(filename)
    print(f"✅ Generated: {filename}")

print("\n🎉 DONE! In các mã QR này ra và dán lên bàn.")
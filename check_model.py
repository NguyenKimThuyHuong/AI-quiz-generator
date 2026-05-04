import google.generativeai as genai

genai.configure(api_key="AIzaSyAapV_7fajRmM7RZWjZaFM_UcDHlgFQ-O4")

print("Danh sách các model bạn được phép dùng:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
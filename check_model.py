import google.generativeai as genai

genai.configure(api_key="AIzaSyCN6MtOlNhoat9tUNQ96hqtLPVpBNultHs")

print("Danh sách các model bạn được phép dùng:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
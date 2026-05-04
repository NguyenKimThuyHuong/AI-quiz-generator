import streamlit as st
import google.generativeai as genai
import PyPDF2
import json

# TẠM THỜI ĐỂ LỘ KEY ĐỂ TEST TRÊN LOCALHOST
# Ghi chú: Dán chuỗi API Key thật của bạn vào giữa 2 dấu ngoặc kép
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Sử dụng model mạnh và nhanh như yêu cầu
model = genai.GenerativeModel('gemini-2.5-flash')

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

st.set_page_config(page_title="AI Hỗ Trợ Tự Học", layout="wide")
st.title("🤖 Trợ Lý Trắc Nghiệm AI Từ Tài Liệu PDF")

# --- BƯỚC 1 & 2: THU THẬP VÀ TẠO CÂU HỎI ---
st.header("1. Tải tài liệu môn học (PDF)")
uploaded_file = st.file_uploader("Chọn file giáo trình, bài giảng của bạn:", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Đang đọc file PDF..."):
        document_text = extract_text_from_pdf(uploaded_file)
        short_text = document_text[:5000] 
        st.session_state['source_text'] = short_text 
    
    st.success("Đọc file thành công! Bạn có thể tạo bài kiểm tra ngay.")
    
    if st.button("Tạo bài kiểm tra"):
        with st.spinner("🤖 AI đang phân tích kiến thức và sinh câu hỏi..."):
            prompt_step2 = f"""Bạn là giảng viên đại học. Dựa vào văn bản sau, tạo 5 câu trắc nghiệm.
            CHỈ TRẢ VỀ ĐỊNH DẠNG JSON (mảng các object) theo đúng cấu trúc này:
            [
              {{
                "question": "Nội dung câu hỏi",
                "topic": "Từ khóa chính của phần kiến thức này (VD: Lịch sử mạng, Thuật toán, Vòng lặp...)",
                "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
                "answer": "A. ...",
                "explanation": "Giải thích ngắn gọn tại sao chọn đáp án này"
              }}
            ]
            Văn bản: {short_text}"""
            
            try:
                # Kiểm tra xem PDF có đọc được chữ không
                if not short_text.strip():
                    st.error("🚨 Không thể trích xuất chữ từ file PDF này (có thể đây là file scan/hình ảnh). Bạn hãy thử một file giáo trình dạng text nhé!")
                    st.stop() # Dừng chạy code bên dưới

                response = model.generate_content(prompt_step2)
                raw_text = response.text.replace('```json', '').replace('```', '').strip()
                
                # Cố gắng bóc tách JSON
                st.session_state['quiz_data'] = json.loads(raw_text)
                
            except json.decoder.JSONDecodeError:
                # Bắt lỗi chuẩn JSON
                st.error("🚨 AI không trả về đúng định dạng JSON. Dưới đây là những gì AI thực sự nói (chế độ Debug):")
                st.code(response.text) # In ra text gốc để bạn xem
            except Exception as e:
                st.error(f"🚨 Lỗi hệ thống khác: {e}")

# --- BƯỚC 3, 4, 5: ĐÁNH GIÁ VÀ PHẢN HỒI ---
if 'quiz_data' in st.session_state:
    st.markdown("---")
    st.header("2. Bài Kiểm Tra Năng Lực")
    
    user_answers = {}
    for i, q in enumerate(st.session_state['quiz_data']):
        st.markdown(f"**Câu {i+1} ({q['topic']}): {q['question']}**")
        user_answers[i] = st.radio("Chọn đáp án:", q['options'], key=f"ans_{i}", index=None)
        
    if st.button("Nộp bài & Phân tích kết quả"):
        st.markdown("---")
        st.header("🏆 Kết quả Đánh giá")
        score = 0
        weak_topics = [] 
        
        for i, q in enumerate(st.session_state['quiz_data']):
            if user_answers[i] == q['answer']:
                score += 1
                st.success(f"**Câu {i+1}: Chính xác!**\n*Giải thích:* {q['explanation']}")
            else:
                st.error(f"**Câu {i+1}: Sai.** Đáp án đúng: {q['answer']}\n*Giải thích:* {q['explanation']}")
                if q['topic'] not in weak_topics:
                    weak_topics.append(q['topic'])
                
        st.info(f"🏆 Tổng điểm: {score} / {len(st.session_state['quiz_data'])}")
        
        if score == len(st.session_state['quiz_data']):
            st.balloons()
            st.success("Tuyệt vời! Bạn đã nắm vững toàn bộ kiến thức trong tài liệu.")
        else:
            st.warning(f"⚠️ Phát hiện lỗ hổng kiến thức ở các chủ đề: **{', '.join(weak_topics)}**")
            
            with st.spinner("🤖 AI đang thiết kế lộ trình học bù cá nhân hóa..."):
                prompt_step4 = f"""Dựa vào bài học sau: '{st.session_state['source_text']}'.
                Sinh viên vừa làm bài kiểm tra và bị sai ở các kiến thức: {weak_topics}.
                Bạn là một gia sư. Hãy viết một lộ trình ôn tập ngắn gọn (3 gạch đầu dòng) để sinh viên vá lỗ hổng này.
                Đề xuất thêm 2 từ khóa mở rộng để sinh viên tự tìm hiểu thêm trên Google.
                Trả về văn bản trình bày đẹp bằng Markdown."""
                
                try:
                    feedback_response = model.generate_content(prompt_step4)
                    st.markdown("🤖🛠 Lộ Trình Học Bù Dành Riêng Cho Bạn")
                    st.write(feedback_response.text)
                except Exception as e:
                    st.error("Không thể tải lộ trình học bù lúc này. Bạn hãy ôn lại tài liệu nhé.")
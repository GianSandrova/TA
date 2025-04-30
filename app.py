# app.py

import streamlit as st
from search import process_query
from config import GROQ_API_KEY, GROQ_MODEL

# Konfigurasi halaman
st.set_page_config(
    page_title="Chatbot Tafsir Al-Quran",
    page_icon="📖",
    layout="centered"
)

# Inisialisasi state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header aplikasi
st.title("📖 Chatbot Al-Quran")
st.markdown("""
<style>
    .stChatInput input {
        background-color: #f8f9fa !important;
    }
    .assistant-message {
        background-color: #0078d4;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .user-message {
        background-color: #4a4a4a;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .error-message {
        background-color: #dc3545;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Tentang Aplikasi")
    st.markdown("""
    Aplikasi chatbot ini membantu Anda memahami Al-Quran dengan:
    - Tafsir ayat berdasarkan referensi terpercaya
    - Terjemahan resmi Kemenag RI
    - Penjelasan kontekstual menggunakan AI
    """)
    st.markdown("**Contoh Pertanyaan:**")
    st.markdown("- Jelaskan makna Surat Al-Fatihah ayat 1")
    st.markdown("- Apa hukum riba dalam Islam?")
    st.markdown("- Jelaskan tafsir Surat Al-Baqarah ayat 255")

# Tampilkan riwayat chat
for message in st.session_state.messages:
    avatar = "💡" if message["role"] == "assistant" else "💭"
    css_class = "assistant-message" if message["role"] == "assistant" else "user-message"

    if message["role"] == "assistant" and message["content"].startswith("❌"):
        css_class = "error-message"
        avatar = "❌"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(f'<div class="{css_class}">{message["content"]}</div>', unsafe_allow_html=True)

# Input pengguna
if prompt := st.chat_input("Masukkan pertanyaan Anda..."):
    # Tambahkan ke riwayat chat
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "avatar": "💭"
    })

    with st.chat_message("user", avatar="💭"):
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)

    # Proses pertanyaan
    with st.spinner("🔍 Mencari jawaban..."):
        try:
            answer = process_query(prompt)

            if answer.startswith("❌"):
                error_msg = answer.replace("❌", "").strip()
                with st.chat_message("assistant", avatar="❌"):
                    st.markdown(f'<div class="error-message">{error_msg}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "avatar": "❌"
                })
                st.stop()

            processed_answer = answer.replace('\n', '<br>')
            formatted_answer = f'<div class="assistant-message">{processed_answer}</div>'

            with st.chat_message("assistant", avatar="💡"):
                st.markdown(formatted_answer, unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "avatar": "💡"
            })

        except Exception as e:
            error_msg = f"❌ Terjadi kesalahan sistem: {str(e)}"
            with st.chat_message("assistant", avatar="❌"):
                st.markdown(f'<div class="error-message">{error_msg}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "avatar": "❌"
            })
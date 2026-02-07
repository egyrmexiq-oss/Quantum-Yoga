import streamlit as st
import google.generativeai as genai
import base64
from fpdf import FPDF
from elevenlabs.client import ElevenLabs # <--- NUEVO CEREBRO DE VOZ

# ==========================================
# ⚙️ 1. CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="Wellness Flow", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🧠 2. CONEXIONES (GOOGLE + ELEVENLABS)
# ==========================================
# A. Google Gemini
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key: st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash') 
except: st.stop()

# B. ElevenLabs (Voz)
eleven_key = st.secrets.get("ELEVEN_API_KEY")
client_eleven = None

if eleven_key:
    try:
        client_eleven = ElevenLabs(api_key=eleven_key)
    except: pass

# ID de la voz (Busca este ID en tu cuenta de ElevenLabs)
# Ejemplo: "21m00Tcm4TlvDq8ikWAM" (Rachel)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # <--- ¡CAMBIA ESTO POR TU ID FAVORITO!

INSTRUCCION_EXTRA = """
ERES "WENDY", INSTRUCTORA DE YOGA.
TONO: Calmado, suave, empático.
"""

# ==========================================
# 🎨 3. ESTILOS DARK ZEN
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0E1612 !important; color: #E0E0E0 !important; }
    [data-testid="stSidebar"] { background-color: #1A2F25 !important; border-right: 1px solid #344E41; }
    [data-testid="stSidebar"] * { color: #DAD7CD !important; }
    h1, h2, h3, p, label, .stMarkdown { color: #E8F5E9 !important; }
    div[data-testid="stChatMessage"]:nth-child(odd) { background-color: #1A2F25 !important; border: 1px solid #344E41; }
    div[data-testid="stChatMessage"]:nth-child(even) { background-color: #2D4035 !important; border: 1px solid #588157; }
    div[data-testid="stChatMessage"] p { color: #FFFFFF !important; }
    div[data-testid="stChatInput"] { background-color: #1A2F25 !important; border: 1px solid #588157 !important; border-radius: 25px !important; }
    div[data-testid="stChatInput"] textarea { color: #FFFFFF !important; }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    div.stButton > button { background-color: #588157 !important; color: white !important; border: none; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ 4. FUNCIONES (PDF + AUDIO)
# ==========================================
def limpiar_texto(texto):
    return texto.encode('latin-1', 'ignore').decode('latin-1')

def generar_pdf_yoga(usuario, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=limpiar_texto(f"Rutina: {usuario}"), ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    for msg in historial:
        role = "Wendy" if msg['role'] == 'assistant' else "Alumno"
        # Filtramos el audio del PDF (por si acaso guardamos bytes)
        if "audio" not in msg: 
            content = limpiar_texto(msg['content'])
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, txt=f"{role}:", ln=1)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 7, txt=content)
            pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

def generar_audio_elevenlabs(texto):
    """Convierte texto a audio usando ElevenLabs"""
    if not client_eleven: return None
    try:
        # Generamos el audio (stream=False para tener todo el archivo)
        audio_generator = client_eleven.text_to_speech.convert(
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2", # Mejor modelo para Español
            text=texto
        )
        # Convertimos el generador a bytes
        audio_bytes = b"".join(chunk for chunk in audio_generator)
        return audio_bytes
    except Exception as e:
        st.error(f"Error de Voz: {e}")
        return None

# ==========================================
# 🏡 5. APP PRINCIPAL
# ==========================================
if "usuario_activo" not in st.session_state:
    st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?q=80&w=2000&h=800&auto=format&fit=crop", use_container_width=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        clave = st.text_input("Clave:", type="password")
        if st.button("Entrar", use_container_width=True):
            if clave == "DEMO" or clave == st.secrets.get("CLAVE_MAESTRA", ""):
                st.session_state.usuario_activo = "Invitado"
                st.session_state.mensajes = []
                st.rerun()
    st.stop()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Namasté! Soy Wendy. ¿Cómo estás hoy?"}]

with st.sidebar:
    st.header("🧘 Wellness Flow")
    nivel = st.select_slider("Energía:", options=["Baja", "Media", "Alta"], value="Media")
    # TOGGLE PARA AHORRAR CRÉDITOS 💰
    usar_voz = st.toggle("🔊 Activar Voz de Wendy", value=True)
    
    if st.button("🔄 Nueva Sesión"):
        st.session_state.mensajes = []
        st.rerun()
        
    if len(st.session_state.mensajes) > 1:
        st.markdown("---")
        try:
            pdf_data = generar_pdf_yoga(st.session_state.usuario_activo, st.session_state.mensajes)
            b64 = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Rutina.pdf" style="text-decoration:none;color:#1B4D3E;background-color:#DAD7CD;padding:10px;border-radius:10px;display:block;text-align:center;">📥 PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
        except: pass

st.title("Wellness’s Flow 🌿")

# Mostrar historial
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Si el mensaje tiene audio guardado, lo mostramos
        if "audio_data" in msg:
            st.audio(msg["audio_data"], format="audio/mp3")

if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Meditando respuesta..."):
            # 1. TEXTO (Gemini)
            full_prompt = f"{INSTRUCCION_EXTRA}\nUsuario ({nivel}): {prompt}"
            response = model.generate_content(full_prompt)
            texto_wendy = response.text
            st.markdown(texto_wendy)
            
            # 2. AUDIO (ElevenLabs) - Solo si el switch está activo
            audio_bytes = None
            if usar_voz and client_eleven:
                with st.spinner("Generando voz... 🎙️"):
                    audio_bytes = generar_audio_elevenlabs(texto_wendy)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
            
            # Guardar en historial
            mensaje_guardar = {"role": "assistant", "content": texto_wendy}
            if audio_bytes:
                mensaje_guardar["audio_data"] = audio_bytes # Guardamos el audio en memoria
                
            st.session_state.mensajes.append(mensaje_guardar)
            st.rerun()
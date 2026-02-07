import streamlit as st
import google.generativeai as genai
import base64
from fpdf import FPDF

# ==========================================
# ⚙️ 1. CONFIGURACIÓN DE PÁGINA (PRIMERA LÍNEA OBLIGATORIA)
# ==========================================
st.set_page_config(
    page_title="Wellness Flow",
    page_icon="🌿",
    layout="wide"
)

# ==========================================
# 🧠 2. CONFIGURACIÓN DE LA IA (CEREBRO)
# ==========================================
api_key = st.secrets.get("GOOGLE_API_KEY")

#if not api_key:
    #st.error("🚨 Error: No se encontró la API Key en los Secrets.")
    #st.stop()

try:
    genai.configure(api_key=api_key)
    # Usamos tu modelo preferido
    model = genai.GenerativeModel('gemini-2.5-flash') 
except Exception as e:
    st.error(f"❌ Error de Conexión con Google: {e}")
    st.stop()

# Instrucción de Personalidad (El Alma de Wendy)
INSTRUCCION_EXTRA = """
ERES "WENDY", UNA INSTRUCTORA DE YOGA EXPERTA Y EMPÁTICA.
TU TONO: Sereno, alentador, profesional y cálido.
TUS REGLAS:
1. Siempre sugiere posturas seguras y advierte "escuchar al cuerpo".
2. Incluye nombres en Sánscrito cuando sea posible.
3. Si el usuario reporta dolor agudo, sugiere ver a un médico.
4. Tus respuestas deben ser estructuradas (Pasos 1, 2, 3...).
"""

# ==========================================
# 🎨 3. ESTILOS CSS (DISEÑO ZEN)
# ==========================================
st.markdown("""
    <style>
    /* 1. FONDO PRINCIPAL */
    .stApp { background-color: #E8F5E9 !important; }

    /* 2. BARRA LATERAL */
    [data-testid="stSidebar"] { background-color: #344E41 !important; }
    [data-testid="stSidebar"] * { color: #DAD7CD !important; }

    /* 3. TEXTOS GENERALES (Verde Oscuro) */
    h1, h2, h3, p, li, label, .stMarkdown { color: #1B4D3E !important; }

    /* 4. BOTONES */
    div.stButton > button {
        background-color: #588157 !important;
        color: white !important;
        border-radius: 20px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #3A5A40 !important;
    }

    /* 5. BURBUJAS DE CHAT */
    div[data-testid="stChatMessage"] {
        background-color: #1A2F25 !important; /* Fondo Verde Oscuro */
        border: 1px solid #588157;
    }
    div[data-testid="stChatMessage"] * {
        color: #FFFFFF !important; /* Texto BLANCO forzado */
        -webkit-text-fill-color: #FFFFFF !important;
    }
    
    /* Iconos de usuario/IA */
    div[data-testid="stChatMessage"] .st-emotion-cache-1p1m4t5 {
        background-color: #588157 !important;
    }

    /* 6. INPUT DEL CHAT (La caja blanca inferior) */
    .stChatFloatingInputContainer { background-color: #E8F5E9 !important; }
    
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border: 2px solid #588157 !important;
        border-radius: 20px !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #333333 !important; /* Texto oscuro al escribir sobre blanco */
        -webkit-text-fill-color: #333333 !important;
        caret-color: #333333 !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #888888 !important;
    }
    button[data-testid="stChatInputSubmitButton"] svg {
        fill: #588157 !important;
    }

    /* Ocultar menú de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ 4. FUNCIONES UTILITARIAS (PDF)
# ==========================================
def generar_pdf_yoga(usuario, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Rutina Personalizada para: {usuario}", ln=1, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    for msg in historial:
        role = "Instructor (Wendy)" if msg['role'] == 'assistant' else "Alumno"
        content = msg['content']
        
        # Limpieza básica de caracteres latinos para FPDF estándar
        content = content.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(200, 8, txt=f"{role}:", ln=1)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, txt=content)
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🚪 5. LÓGICA DE LOGIN
# ==========================================
if "usuario_activo" not in st.session_state:
    st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?q=80&w=2000&h=800&auto=format&fit=crop", use_container_width=True)
    st.markdown('<h1 style="text-align: center;">Wellness’s Flow 🌿</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center;">Tu santuario personal de equilibrio</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        clave_input = st.text_input("Clave de Acceso:", type="password")
        if st.button("Entrar a Sesión", use_container_width=True):
            if clave_input == "DEMO":
                st.session_state.usuario_activo = "Invitado"
                st.session_state.mensajes = [] # Inicializar chat vacío
                st.rerun()
            else:
                st.error("Clave incorrecta. Intenta con: DEMO")
    st.stop()

# ==========================================
# 🏡 6. LA APP PRINCIPAL (Adentro)
# ==========================================

# --- INICIALIZACIÓN DE HISTORIAL ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
    # Mensaje de bienvenida inicial
    msg_inicial = "¡Namasté! Soy Wendy. Cuéntame, ¿cómo te sientes hoy o qué zona te gustaría trabajar?"
    st.session_state.mensajes.append({"role": "assistant", "content": msg_inicial})

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🧘 Wellness Flow")
    st.success(f"Hola, {st.session_state.usuario_activo}")
    
    st.markdown("---")
    st.markdown("### ⚙️ Preferencias")
    nivel = st.radio("Nivel:", ["Básico", "Medio", "Avanzado"])
    
    st.markdown("---")
    if st.button("🍃 Nueva Sesión"):
        st.session_state.mensajes = []
        st.rerun()
        
    # BOTÓN PDF (Solo si hay charla)
    if len(st.session_state.mensajes) > 1:
        try:
            pdf_bytes = generar_pdf_yoga(st.session_state.usuario_activo, st.session_state.mensajes)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Mi_Rutina_Yoga.pdf" style="text-decoration:none; color:black; background-color:#DAD7CD; padding:10px; border-radius:10px; display:block; text-align:center;">📥 Descargar Rutina PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.warning("Escribe un poco más para generar el PDF.")

    st.markdown("---")
    if st.button("🔒 Salir"):
        del st.session_state["usuario_activo"]
        st.rerun()

# --- ZONA DE CHAT ---
st.title("Wellness’s Flow 🌿")
st.caption(f"Asistente IA - Nivel {nivel}")

# 1. Mostrar historial
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# 2. Input y Respuesta
if prompt := st.chat_input("Escribe aquí tus síntomas o deseos..."):
    
    # Usuario
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # IA (Wendy)
    with st.chat_message("assistant"):
        with st.spinner("Wendy está preparando tu secuencia... 🧘‍♀️"):
            try:
                # TRUCO PRO: Le enviamos la instrucción oculta + lo que dijo el usuario
                full_prompt = f"{INSTRUCCION_EXTRA}\n\nEl usuario es nivel {nivel}. Usuario dice: {prompt}"
                
                response = model.generate_content(full_prompt)
                texto_respuesta = response.text
                
                st.markdown(texto_respuesta)
                st.session_state.mensajes.append({"role": "assistant", "content": texto_respuesta})
            except Exception as e:
                st.error(f"⚠️ Error de conexión: {e}")
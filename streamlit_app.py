import streamlit as st
import google.generativeai as genai
import base64
from fpdf import FPDF

# ==========================================
# ⚙️ 1. CONFIGURACIÓN DE PÁGINA (SIEMPRE PRIMERO)
# ==========================================
st.set_page_config(
    page_title="Wellness Flow",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed" # En móvil ayuda a que no estorbe al inicio
)

# ==========================================
# 🧠 2. CEREBRO (GOOGLE API)
# ==========================================
api_key = st.secrets.get("GOOGLE_API_KEY")

#if not api_key:
    #st.error("🚨 Error: No se encontró la API Key en los Secrets.")
    #st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash') 
except Exception as e:
    st.error(f"❌ Error de Conexión: {e}")
    st.stop()

# Personalidad de Wendy
INSTRUCCION_EXTRA = """
ERES "WENDY", INSTRUCTORA DE YOGA Y MINDFULNESS.
TU TONO: Calmado, profundo, empático y profesional.
OBJETIVO: Guiar al usuario a un estado de bienestar.
REGLAS:
1. Usa lenguaje positivo y relajante.
2. Sugiere posturas seguras (asanas) y respiración (pranayama).
3. Si hay dolor, recomienda médico.
4. Sé concisa pero cálida.
"""

# ==========================================
# 🎨 3. ESTILOS "DARK ZEN" (CORREGIDO)
# ==========================================
st.markdown("""
    <style>
    /* --- 1. FONDO GENERAL (Vuelta a la oscuridad elegante) --- */
    .stApp {
        background-color: #0E1612 !important; /* Verde casi negro profundo */
        color: #E0E0E0 !important;
    }

    /* --- 2. BARRA LATERAL (Verde Bosque) --- */
    [data-testid="stSidebar"] {
        background-color: #1A2F25 !important;
        border-right: 1px solid #344E41;
    }
    [data-testid="stSidebar"] * {
        color: #DAD7CD !important;
    }

    /* --- 3. TEXTOS Y TÍTULOS --- */
    h1, h2, h3, p, label {
        color: #E8F5E9 !important; /* Blanco menta suave */
    }
    .stMarkdown {
        color: #E0E0E0 !important;
    }

    /* --- 4. BURBUJAS DE CHAT (Alto Contraste) --- */
    /* Usuario (Derecha) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1A2F25 !important;
        border: 1px solid #344E41;
    }
    /* IA Wendy (Izquierda) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #2D4035 !important; /* Un poco más claro para diferenciar */
        border: 1px solid #588157;
    }
    /* TEXTO DENTRO DEL CHAT (Blanco Puro) */
    div[data-testid="stChatMessage"] p {
        color: #FFFFFF !important;
    }
    
    /* --- 5. INPUT DEL CHAT (Adiós franjas negras) --- */
    .stChatFloatingInputContainer {
        background-color: #0E1612 !important; /* Mismo color que el fondo */
    }
    div[data-testid="stChatInput"] {
        background-color: #1A2F25 !important;
        border: 1px solid #588157 !important;
        border-radius: 25px !important;
    }
    div[data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
        caret-color: #FFFFFF !important;
    }
    
    /* --- 6. BOTONES --- */
    div.stButton > button {
        background-color: #588157 !important;
        color: white !important;
        border: none;
        border-radius: 12px;
    }
    div.stButton > button:hover {
        background-color: #3A5A40 !important;
    }

    /* --- 7. ARREGLO MÓVIL (MENU VISIBLE) --- */
    /* NO ocultamos el header completo, solo la decoración, para dejar el botón ☰ */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    /* Aseguramos que el botón de menú sea blanco para que se vea */
    button[kind="header"] {
        color: white !important;
    }
    #MainMenu {visibility: visible;} /* Necesario para ver opciones */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ 4. FUNCIÓN PDF
# ==========================================
def generar_pdf_yoga(usuario, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Rutina Personalizada: {usuario}", ln=1, align='C')
    pdf.ln(10)
    
    # Contenido
    pdf.set_font("Arial", size=11)
    for msg in historial:
        role = "Instructor (Wendy)" if msg['role'] == 'assistant' else "Alumno"
        content = msg['content']
        # Limpieza de caracteres para FPDF básico
        content = content.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, txt=f"{role}:", ln=1)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, txt=content)
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🚪 5. PANTALLA DE LOGIN
# ==========================================
if "usuario_activo" not in st.session_state:
    # Fondo e imagen minimalista
    st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?q=80&w=2000&h=800&auto=format&fit=crop", use_container_width=True)
    
    st.markdown("<h1 style='text-align: center;'>Wellness’s Flow 🌿</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Ingresa tu clave para acceder al santuario.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        clave = st.text_input("Clave de Acceso:", type="password")
        if st.button("Entrar", use_container_width=True):
            if clave == "DEMO" or clave == st.secrets.get("CLAVE_MAESTRA", ""):
                st.session_state.usuario_activo = "Invitado"
                st.session_state.mensajes = []
                st.rerun()
            else:
                st.error("Clave incorrecta.")
    st.stop()

# ==========================================
# 🏡 6. APLICACIÓN PRINCIPAL
# ==========================================

# Inicializar Chat
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
    st.session_state.mensajes.append({"role": "assistant", "content": "¡Namasté! Soy Wendy. ¿Cómo se siente tu cuerpo y mente hoy?"})

# --- BARRA LATERAL (MENU) ---
with st.sidebar:
    st.header("🧘 Wellness Flow")
    st.caption(f"Hola, {st.session_state.usuario_activo}")
    st.markdown("---")
    
    nivel = st.select_slider("Nivel de Energía:", options=["Baja", "Media", "Alta"], value="Media")
    
    if st.button("🔄 Nueva Sesión", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

    # BOTÓN PDF (Solo aparece si hay chat)
    if len(st.session_state.mensajes) > 1:
        st.markdown("---")
        st.markdown("### 📄 Tu Rutina")
        try:
            pdf_data = generar_pdf_yoga(st.session_state.usuario_activo, st.session_state.mensajes)
            b64 = base64.b64encode(pdf_data).decode()
            
            # Botón estilizado Dark
            href = f'''
            <a href="data:application/octet-stream;base64,{b64}" download="Rutina_Wellness.pdf" 
               style="text-decoration:none; color: #E8F5E9; background-color: #344E41; 
                      padding: 12px; border-radius: 10px; display: block; text-align: center; 
                      border: 1px solid #588157; font-weight: bold;">
               📥 Descargar PDF
            </a>
            '''
            st.markdown(href, unsafe_allow_html=True)
        except:
            pass

    st.markdown("---")
    if st.button("🔒 Salir", use_container_width=True):
        del st.session_state["usuario_activo"]
        st.rerun()

# --- ZONA DE CHAT ---
st.title("Wellness’s Flow 🌿")

# Mostrar Mensajes
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input de Usuario
if prompt := st.chat_input("Escribe aquí... (ej: Me duele el cuello)"):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Conectando..."):
            try:
                full_prompt = f"{INSTRUCCION_EXTRA}\nUsuario (Energía {nivel}): {prompt}"
                response = model.generate_content(full_prompt)
                texto = response.text
                st.markdown(texto)
                st.session_state.mensajes.append({"role": "assistant", "content": texto})
            except Exception as e:
                st.error(f"Error: {e}")
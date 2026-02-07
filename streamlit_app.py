import streamlit as st
import google.generativeai as genai
import base64
from fpdf import FPDF

# ==========================================
# ⚙️ 1. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Wellness Flow",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
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

INSTRUCCION_EXTRA = """
ERES "WENDY", INSTRUCTORA DE YOGA Y MINDFULNESS.
TU TONO: Calmado, profundo, empático y profesional.
OBJETIVO: Guiar al usuario a un estado de bienestar.
REGLAS:
1. Usa lenguaje positivo.
2. Sugiere posturas seguras y respiración.
3. Sé concisa.
"""

# ==========================================
# 🎨 3. ESTILOS "DARK ZEN" (MÓVIL + PC)
# ==========================================
st.markdown("""
    <style>
    /* --- 1. FONDO GENERAL --- */
    .stApp {
        background-color: #0E1612 !important;
        color: #E0E0E0 !important;
    }

    /* --- 2. BARRA LATERAL --- */
    [data-testid="stSidebar"] {
        background-color: #1A2F25 !important;
        border-right: 1px solid #344E41;
    }
    [data-testid="stSidebar"] * {
        color: #DAD7CD !important;
    }

    /* --- 3. TEXTOS --- */
    h1, h2, h3, p, label, .stMarkdown {
        color: #E8F5E9 !important;
    }

    /* --- 4. BURBUJAS DE CHAT --- */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1A2F25 !important;
        border: 1px solid #344E41;
    }
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #2D4035 !important;
        border: 1px solid #588157;
    }
    div[data-testid="stChatMessage"] p {
        color: #FFFFFF !important;
    }
    
    /* --- 5. INPUT DEL CHAT --- */
    .stChatFloatingInputContainer {
        background-color: #0E1612 !important;
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

    /* --- 7. ARREGLO MÓVIL --- */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    #MainMenu {visibility: visible;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ 4. FUNCIÓN PDF (¡AHORA LIMPIA EMOJIS!)
# ==========================================
def limpiar_texto(texto):
    # Esta función elimina caracteres que rompen el PDF (emojis, etc.)
    return texto.encode('latin-1', 'ignore').decode('latin-1')

def generar_pdf_yoga(usuario, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    clean_user = limpiar_texto(f"Rutina Personalizada: {usuario}")
    pdf.cell(0, 10, txt=clean_user, ln=1, align='C')
    pdf.ln(10)
    
    # Contenido
    pdf.set_font("Arial", size=11)
    for msg in historial:
        role = "Instructor (Wendy)" if msg['role'] == 'assistant' else "Alumno"
        content = msg['content']
        
        # LIMPIEZA CRÍTICA AQUÍ 👇
        clean_content = limpiar_texto(content)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, txt=f"{role}:", ln=1)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, txt=clean_content)
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🚪 5. PANTALLA DE LOGIN
# ==========================================
if "usuario_activo" not in st.session_state:
    st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?q=80&w=2000&h=800&auto=format&fit=crop", use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>Wellness’s Flow 🌿</h1>", unsafe_allow_html=True)
    
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

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
    st.session_state.mensajes.append({"role": "assistant", "content": "¡Namasté! Soy Wendy. ¿Cómo se siente tu cuerpo hoy?"})

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🧘 Wellness Flow")
    st.caption(f"Hola, {st.session_state.usuario_activo}")
    st.markdown("---")
    
    nivel = st.select_slider("Nivel de Energía:", options=["Baja", "Media", "Alta"], value="Media")
    
    if st.button("🔄 Nueva Sesión", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

    # --- BOTÓN PDF (CORREGIDO) ---
    # Solo aparece si hay más de 1 mensaje (es decir, el usuario ya habló)
    if len(st.session_state.mensajes) > 1:
        st.markdown("---")
        st.markdown("### 📄 Tu Rutina")
        st.caption("Descarga tu práctica personalizada.")
        
        # Generación del PDF
        try:
            pdf_data = generar_pdf_yoga(st.session_state.usuario_activo, st.session_state.mensajes)
            b64 = base64.b64encode(pdf_data).decode()
            
            # Botón VISIBLE
            href = f'''
            <a href="data:application/octet-stream;base64,{b64}" download="Rutina_Wellness.pdf" 
               style="text-decoration:none; color: #1B4D3E; background-color: #DAD7CD; 
                      padding: 12px; border-radius: 10px; display: block; text-align: center; 
                      border: 2px solid #A3B18A; font-weight: bold;">
               📥 DESCARGAR PDF
            </a>
            '''
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error PDF: {e}") # Si falla, ahora te dirá por qué

    st.markdown("---")
    if st.button("🔒 Salir", use_container_width=True):
        del st.session_state["usuario_activo"]
        st.rerun()

# --- ZONA DE CHAT ---
st.title("Wellness’s Flow 🌿")

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe aquí..."):
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
                # Forzamos recarga para que aparezca el botón en la barra lateral
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
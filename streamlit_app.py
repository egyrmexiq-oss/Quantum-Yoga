import streamlit as st
import google.generativeai as genai
import base64
from fpdf import FPDF
from elevenlabs.client import ElevenLabs

# ==========================================
# ⚙️ 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Wellness Flow", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🧠 2. CEREBRO Y VOZ (CONEXIONES)
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
    try: client_eleven = ElevenLabs(api_key=eleven_key)
    except: pass

# ID DE VOZ (Reemplaza con el tuyo si es diferente)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM" 

# ==========================================
# 🎨 3. ESTILOS "DARK ZEN" (Con Botón PDF arreglado)
# ==========================================
st.markdown("""
    <style>
    /* Fondo y Textos Generales */
    .stApp { background-color: #0E1612 !important; color: #E0E0E0 !important; }
    [data-testid="stSidebar"] { background-color: #1A2F25 !important; border-right: 1px solid #344E41; }
    [data-testid="stSidebar"] * { color: #DAD7CD !important; }
    h1, h2, h3, p, label, .stMarkdown { color: #E8F5E9 !important; }
    
    /* Chat */
    div[data-testid="stChatMessage"]:nth-child(odd) { background-color: #1A2F25 !important; border: 1px solid #344E41; }
    div[data-testid="stChatMessage"]:nth-child(even) { background-color: #2D4035 !important; border: 1px solid #588157; }
    div[data-testid="stChatMessage"] p { color: #FFFFFF !important; }
    div[data-testid="stChatInput"] { background-color: #1A2F25 !important; border: 1px solid #588157 !important; }
    div[data-testid="stChatInput"] textarea { color: #FFFFFF !important; }
    
    /* Botones Normales */
    div.stButton > button { background-color: #588157 !important; color: white !important; border: none; border-radius: 12px; }
    
    /* Ocultar header molesto pero dejar menú */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ 4. FUNCIONES DE APOYO
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
        if "audio" not in msg: # Ignorar mensajes técnicos
            content = limpiar_texto(msg['content'])
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, txt=f"{role}:", ln=1)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 7, txt=content)
            pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

def generar_audio_elevenlabs(texto):
    if not client_eleven: return None
    try:
        audio = client_eleven.text_to_speech.convert(
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            text=texto
        )
        return b"".join(chunk for chunk in audio)
    except: return None

# ==========================================
# 🚪 5. LOGIN INTELIGENTE (Define el Nivel)
# ==========================================
if "usuario_activo" not in st.session_state:
    st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?q=80&w=2000&h=800&auto=format&fit=crop", use_container_width=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        clave = st.text_input("Clave de Acceso:", type="password")
        if st.button("Entrar", use_container_width=True):
            # LÓGICA DE NIVELES
            clave_maestra = st.secrets.get("CLAVE_MAESTRA", "ADMIN123") # Usa ADMIN123 si no tienes secrets
            
            if clave == "DEMO":
                st.session_state.usuario_activo = "Invitado Demo"
                st.session_state.tipo_plan = "DEMO"
                st.session_state.mensajes = []
                st.rerun()
            elif clave == clave_maestra:
                st.session_state.usuario_activo = "Miembro Premium"
                st.session_state.tipo_plan = "PREMIUM"
                st.session_state.mensajes = []
                st.rerun()
            else:
                st.error("Clave incorrecta.")
    st.stop()

# ==========================================
# 🏡 6. APP PRINCIPAL (Lógica de Negocio)
# ==========================================

# Definir el Prompt según el plan
tipo_plan = st.session_state.get("tipo_plan", "DEMO")
nivel_seleccionado = "Básico" # Valor por defecto

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🧘 Wellness Flow")
    st.caption(f"Plan: {tipo_plan}")
    
    # SELECTOR DE NIVEL (Solo para Premium)
    if tipo_plan == "PREMIUM":
        st.markdown("### 🎚️ Nivel de Práctica")
        nivel_seleccionado = st.select_slider(
            "Intensidad:", 
            options=["Básico", "Medio", "Avanzado"],
            value="Básico"
        )
        if nivel_seleccionado == "Básico":
            st.info("💡 Ideal para principiantes. Explicaciones paso a paso.")
        elif nivel_seleccionado == "Avanzado":
            st.info("🔥 Alta intensidad y lenguaje técnico.")
    else:
        # Si es DEMO, no dejamos elegir
        st.warning("🔒 Modo DEMO (Funciones Limitadas)")
        nivel_seleccionado = "DEMO"

    st.markdown("---")
    
    # Toggle de Voz
    usar_voz = st.toggle("🔊 Voz de Wendy", value=True)
    
    if st.button("🔄 Nueva Sesión"):
        st.session_state.mensajes = []
        st.rerun()
        
    # --- BOTÓN PDF CORREGIDO (Visible y Grande) ---
    if len(st.session_state.mensajes) > 1:
        st.markdown("---")
        st.markdown("### 📄 Tu Rutina")
        try:
            pdf_data = generar_pdf_yoga(st.session_state.usuario_activo, st.session_state.mensajes)
            b64 = base64.b64encode(pdf_data).decode()
            
            # ESTILO CSS DIRECTO PARA QUE SE VEA SIEMPRE
            href = f'''
            <a href="data:application/octet-stream;base64,{b64}" download="Rutina_Wellness.pdf" 
               style="text-decoration:none; color: #1B4D3E; background-color: #DAD7CD; 
                      padding: 15px; border-radius: 10px; display: block; text-align: center; 
                      border: 2px solid #A3B18A; font-weight: bold; margin-top: 10px;">
               📥 DESCARGAR PDF
            </a>
            '''
            st.markdown(href, unsafe_allow_html=True)
        except: pass

    st.markdown("---")
    if st.button("🔒 Salir"):
        del st.session_state["usuario_activo"]
        st.rerun()

# --- CONSTRUCCIÓN DEL CEREBRO (PROMPT) ---
# Aquí es donde ocurre la magia de la diferenciación
if nivel_seleccionado == "DEMO":
    INSTRUCCION = """
    ERES WENDY. ESTÁS EN 'MODO DEMO'.
    Tus respuestas deben ser CORTAS (máximo 50 palabras).
    Da un consejo útil pero genérico.
    Al final, invita sutilmente al usuario a adquirir el Plan Premium para rutinas personalizadas.
    """
elif nivel_seleccionado == "Básico":
    INSTRUCCION = """
    ERES WENDY. NIVEL: BÁSICO (PRINCIPIANTE).
    El usuario no tiene experiencia. Necesita COACHING.
    1. Explica cada movimiento con mucho detalle y seguridad.
    2. No uses términos en Sánscrito sin traducirlos.
    3. Enfócate en aliviar dolor y relajación.
    4. Sé muy empática y maternal.
    """
elif nivel_seleccionado == "Medio":
    INSTRUCCION = """
    ERES WENDY. NIVEL: MEDIO.
    El usuario ya conoce lo básico.
    1. Puedes combinar posturas (Flow).
    2. Aumenta un poco la intensidad.
    3. Usa nombres técnicos pero mantén la claridad.
    """
elif nivel_seleccionado == "Avanzado":
    INSTRUCCION = """
    ERES WENDY. NIVEL: AVANZADO (EXPERTO).
    El usuario busca reto y profundidad técnica.
    1. Usa terminología correcta (Sánscrito).
    2. Enfócate en la alineación perfecta y la respiración avanzada (Pranayama).
    3. No pierdas tiempo en explicaciones básicas. Ve al grano.
    """

# --- ZONA DE CHAT ---
st.title("Wellness’s Flow 🌿")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
    saludo = "¡Namasté! Soy Wendy. ¿Cómo te sientes hoy?"
    if nivel_seleccionado == "DEMO": saludo += " (Modo Prueba)"
    st.session_state.mensajes.append({"role": "assistant", "content": saludo})

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "audio_data" in msg:
            st.audio(msg["audio_data"], format="audio/mp3")

if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Conectando..."):
            # 1. GENERAR TEXTO
            full_prompt = f"{INSTRUCCION}\nUsuario dice: {prompt}"
            try:
                response = model.generate_content(full_prompt)
                texto_wendy = response.text
                st.markdown(texto_wendy)

                # 2. GENERAR AUDIO (Solo si está activo)
                audio_bytes = None
                if usar_voz and client_eleven:
                    # En DEMO, limitamos el audio para ahorrar tus créditos si quieres
                    # O déjalo libre para enamorarlos
                    audio_bytes = generar_audio_elevenlabs(texto_wendy) 
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")

                # Guardar
                msg_save = {"role": "assistant", "content": texto_wendy}
                if audio_bytes: msg_save["audio_data"] = audio_bytes
                st.session_state.mensajes.append(msg_save)
                
                st.rerun() # Recarga para actualizar PDF y botón
            except Exception as e:
                st.error(f"Error: {e}")
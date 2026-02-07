import streamlit as st
import google.generativeai as genai
import base64
from fpdf import FPDF
from elevenlabs.client import ElevenLabs

# ==========================================
# ⚙️ 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Wellness Flow", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🧠 2. CONEXIONES (CEREBRO Y VOZ)
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
# 🎨 3. ESTILOS "DARK ZEN"
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
        if "audio" not in msg:
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
# 🚪 5. LOGIN INTELIGENTE
# ==========================================
if "usuario_activo" not in st.session_state:
    st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?q=80&w=2000&h=800&auto=format&fit=crop", use_container_width=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Bienvenido a Quantum</h2>", unsafe_allow_html=True)
        clave = st.text_input("Clave de Acceso:", type="password")
        if st.button("Entrar", use_container_width=True):
            
            llaves_validas = st.secrets.get("access_keys", {})
            
            if clave in llaves_validas:
                nombre_usuario = llaves_validas[clave]
                if clave == "DEMO":
                    st.session_state.usuario_activo = nombre_usuario
                    st.session_state.tipo_plan = "DEMO"
                else:
                    st.session_state.usuario_activo = nombre_usuario
                    st.session_state.tipo_plan = "PREMIUM"
                st.session_state.mensajes = []
                st.rerun()
            elif clave == "ADMIN123": # Backdoor
                st.session_state.usuario_activo = "Super Admin"
                st.session_state.tipo_plan = "PREMIUM"
                st.session_state.mensajes = []
                st.rerun()
            else:
                st.error("Clave incorrecta.")
    st.stop()

# ==========================================
# 🏡 6. APP PRINCIPAL (DISEÑO QUANTUM)
# ==========================================

tipo_plan = st.session_state.get("tipo_plan", "DEMO")
nivel_seleccionado = "Básico" 

# --- BARRA LATERAL RE-DISEÑADA ---
with st.sidebar:
    # 1. LOGO QUANTUM
    try:
        st.image("logo_quantum.png", use_container_width=True) 
    except:
        st.header("Quantum Yoga ⚛️")

    st.markdown("---")

    # 2. AVATAR DE WENDY
    st.markdown("**Tu Instructora:**")
    
    # --- ¿VIDEO O FOTO? (Descomenta el que quieras usar) ---
    try:
        # VIDEO (Si quieres video, quita los # de abajo y pon # en st.image)
        # st.video("wendy_intro.mp4", format="video/mp4", start_time=0, loop=True, autoplay=True, muted=True)
        
        # FOTO (Activa por defecto)
        st.image("Wendy v1.jpeg", caption="Wendy (IA)", use_container_width=True)
    except:
        st.write("🧘‍♀️")

    st.markdown("---")
    
    # 3. DATOS USUARIO
    st.caption(f"Hola, **{st.session_state.usuario_activo}**")
    
    if tipo_plan == "PREMIUM":
        st.success(f"💎 Plan: {tipo_plan}")
        st.markdown("### 🎚️ Intensidad")
        nivel_seleccionado = st.select_slider(
            "Nivel:", 
            options=["Básico", "Medio", "Avanzado"],
            value="Básico",
            label_visibility="collapsed"
        )
    else:
        st.warning(f"🔒 Plan: {tipo_plan}")
        nivel_seleccionado = "DEMO"

    st.markdown("---")
    
    # 4. HERRAMIENTAS (VOZ OFF POR DEFECTO) 🔇
    # Aquí está el cambio que pediste: value=False
    usar_voz = st.toggle("🔊 Voz de Wendy", value=True)
    
    if st.button("🔄 Nueva Sesión", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()
        
    # 5. PDF ALTO CONTRASTE
    if len(st.session_state.mensajes) > 1:
        st.markdown("---")
        st.markdown("### 📄 Tu Rutina")
        st.caption("Descarga tu práctica para imprimir.")

        try:
            pdf_data = generar_pdf_yoga(st.session_state.usuario_activo, st.session_state.mensajes)
            b64 = base64.b64encode(pdf_data).decode()
            href = f'''
            <a href="data:application/octet-stream;base64,{b64}" download="Rutina_Quantum.pdf" 
               style="text-decoration:none; color: #000000 !important; background-color: #E0E0E0 !important; 
                      padding: 15px; border-radius: 10px; display: block; text-align: center; 
                      border: 2px solid #000000; font-weight: 800; width: 100%;">
               📥 DESCARGAR PDF
            </a>
            '''
            st.markdown(href, unsafe_allow_html=True)
        except: pass

    st.markdown("---")
    if st.button("🔒 Cerrar Sesión", use_container_width=True):
        del st.session_state["usuario_activo"]
        st.rerun()

# --- PROMPTS ---
if nivel_seleccionado == "DEMO":
    INSTRUCCION = "ERES WENDY. MODO DEMO. Respuestas CORTAS (max 50 palabras). Consejos genéricos. Invita a Premium."
elif nivel_seleccionado == "Básico":
    INSTRUCCION = "ERES WENDY. NIVEL BÁSICO. El usuario es PRINCIPIANTE. Explica paso a paso con seguridad. Enfócate en alivio."
elif nivel_seleccionado == "Medio":
    INSTRUCCION = "ERES WENDY. NIVEL MEDIO. Flujo dinámico. Nombres técnicos moderados."
elif nivel_seleccionado == "Avanzado":
    INSTRUCCION = "ERES WENDY. NIVEL AVANZADO. Usa Sánscrito. Enfócate en alineación perfecta y Pranayama."

# --- CHAT LOOP (AQUÍ ESTABA EL PROBLEMA ANTES) ---
st.title("Wellness’s Flow 🌿")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
    saludo = f"¡Namasté, {st.session_state.usuario_activo}! Soy Wendy. ¿Cómo te sientes?"
    st.session_state.mensajes.append({"role": "assistant", "content": saludo})

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # REPRODUCTOR DE AUDIO RECUPERADO 🎵
        if "audio_data" in msg:
            st.audio(msg["audio_data"], format="audio/mp3")

if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Conectando..."):
            full_prompt = f"{INSTRUCCION}\nUsuario: {prompt}"
            try:
                response = model.generate_content(full_prompt)
                texto_wendy = response.text
                st.markdown(texto_wendy)

                # LÓGICA DE AUDIO (Solo si el switch está ON)
                audio_bytes = None
                if usar_voz and client_eleven:
                    audio_bytes = generar_audio_elevenlabs(texto_wendy) 
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")

                msg_save = {"role": "assistant", "content": texto_wendy}
                if audio_bytes: msg_save["audio_data"] = audio_bytes
                st.session_state.mensajes.append(msg_save)
                
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
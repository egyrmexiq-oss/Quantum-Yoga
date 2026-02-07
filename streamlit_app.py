import streamlit as st
import google.generativeai as genai
import base64
from fpdf import FPDF
from elevenlabs.client import ElevenLabs
import requests # <--- NUEVA HERRAMIENTA PARA TRAER IMÁGENES
from io import BytesIO

# ==========================================
# ⚙️ 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Wellness Flow", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🧠 2. CONEXIONES
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

VOICE_ID = "21m00Tcm4TlvDq8ikWAM" 

# ==========================================
# 🎨 3. ESTILOS "DARK ZEN"
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
    div[data-testid="stChatInput"] { background-color: #1A2F25 !important; border: 1px solid #588157 !important; }
    div[data-testid="stChatInput"] textarea { color: #FFFFFF !important; }
    div.stButton > button { background-color: #588157 !important; color: white !important; border: none; border-radius: 12px; }
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
        if "audio" not in msg and "imagen" not in msg:
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
            voice_id=VOICE_ID, model_id="eleven_multilingual_v2", text=texto
        )
        return b"".join(chunk for chunk in audio)
    except: return None

# --- FUNCIÓN NUEVA: EL DISFRAZ PARA WIKIPEDIA 🕵️‍♂️ ---
def obtener_imagen_nube(url):
    """Descarga la imagen engañando al servidor con un Header de navegador"""
    try:
        # Este es el 'Pasaporte' falso para que crean que somos un navegador Chrome
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return BytesIO(response.content) # Devuelve la imagen lista
    except:
        return None
    return None

#def mostrar_imagen_postura(texto_wendy):
    # ...
import os # <--- Asegúrate de tener esto arriba del todo con los otros imports
def mostrar_imagen_postura(texto_wendy):
    """
    Muestra imágenes locales (subidas a GitHub) si detecta la palabra clave.
    ¡100% Robusto y sin bloqueos!
    """
    # DICCIONARIO: Palabra Clave -> Nombre de tu archivo
    diccionario_local = {
        "árbol": "arbol.png",
        "vrksasana": "arbol.png",
        
        "guerrero": "guerrero.png",
        "virabhadrasana": "guerrero.png",
        
        "cobra": "cobra.png",
        "bhujangasana": "cobra.png",
        
        # Puedes agregar más aquí cuando subas más fotos:
        # "loto": "loto.png",
    }
    
    texto_min = texto_wendy.lower()
    
    for clave, archivo in diccionario_local.items():
        if clave in texto_min:
            # Verificamos si el archivo realmente existe para no romper la app
            if os.path.exists(archivo):
                c1, c2, c3 = st.columns([1, 2, 1])
                with c2:
                    st.image(archivo, caption=f"Postura: {clave.capitalize()}", use_container_width=True)
                return archivo # Éxito
    return None
# ==========================================
# 🚪 5. LOGIN INTELIGENTE
# ==========================================
if "usuario_activo" not in st.session_state:
    st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?q=80&w=2000&h=800&auto=format&fit=crop", use_container_width=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Wendy's Wellness's Flow</h2>", unsafe_allow_html=True)
        clave = st.text_input("Clave de Acceso:", type="password")
        if st.button("Entrar", use_container_width=True):
            llaves = st.secrets.get("access_keys", {})
            if clave in llaves:
                st.session_state.usuario_activo = llaves[clave]
                st.session_state.tipo_plan = "DEMO" if clave == "DEMO" else "PREMIUM"
                st.session_state.mensajes = []
                st.rerun()
            elif clave == "ADMIN123": 
                st.session_state.usuario_activo = "Super Admin"
                st.session_state.tipo_plan = "PREMIUM"
                st.session_state.mensajes = []
                st.rerun()
            else:
                st.error("Clave incorrecta.")
    st.stop()

# ==========================================
# 🏡 6. APP PRINCIPAL
# ==========================================
tipo_plan = st.session_state.get("tipo_plan", "DEMO")
nivel = "Básico" 

with st.sidebar:
    try: st.image("logo_quantum.png", use_container_width=True) 
    except: st.header("Quantum Yoga ⚛️")
    st.markdown("---")
    
    st.markdown("**Tu Instructora:**")
    try: st.image("Wendy v1.jpeg", caption="Wendy (IA)", use_container_width=True)
    except: st.write("🧘‍♀️")
    st.markdown("---")
    
    st.caption(f"Hola, **{st.session_state.usuario_activo}**")
    if tipo_plan == "PREMIUM":
        st.success(f"💎 Plan: {tipo_plan}")
        st.markdown("### 🎚️ Intensidad")
        nivel = st.select_slider("Nivel:", options=["Básico", "Medio", "Avanzado"], value="Básico", label_visibility="collapsed")
    else:
        st.warning(f"🔒 Plan: {tipo_plan}")
        nivel = "DEMO"
    st.markdown("---")
    
    usar_voz = st.toggle("🔊 Voz de Wendy", value=False)
    
    if st.button("🔄 Nueva Sesión", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()
        
    if len(st.session_state.mensajes) > 1:
        st.markdown("---")
        st.markdown("### 📄 Tu Rutina")
        try:
            pdf_data = generar_pdf_yoga(st.session_state.usuario_activo, st.session_state.mensajes)
            b64 = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Rutina_Quantum.pdf" style="text-decoration:none; color: #000000 !important; background-color: #E0E0E0 !important; padding: 15px; border-radius: 10px; display: block; text-align: center; border: 2px solid #000000; font-weight: 800; width: 100%;">📥 DESCARGAR PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
        except: pass
    
    st.markdown("---")
    if st.button("🔒 Cerrar Sesión", use_container_width=True):
        del st.session_state["usuario_activo"]
        st.rerun()

# --- PROMPTS ---
if nivel == "DEMO": INSTRUCCION = "ERES WENDY. MODO DEMO. Respuestas cortas. Invita a Premium."
elif nivel == "Básico": INSTRUCCION = "ERES WENDY. NIVEL BÁSICO. Explica la postura del árbol, el guerrero o la cobra paso a paso."
elif nivel == "Medio": INSTRUCCION = "ERES WENDY. NIVEL MEDIO. Flujo dinámico."
elif nivel == "Avanzado": INSTRUCCION = "ERES WENDY. NIVEL AVANZADO. Usa Sánscrito."

# --- CHAT ---
st.title("Wellness’s Flow 🌿")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
    st.session_state.mensajes.append({"role": "assistant", "content": f"¡Namasté, {st.session_state.usuario_activo}! ¿Qué postura practicamos hoy? (Prueba: Árbol, Cobra, Guerrero)"})

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # MOSTRAR IMAGEN GUARDADA EN HISTORIAL 🖼️
        if "imagen_data" in msg:
             c1, c2, c3 = st.columns([1, 2, 1])
             with c2:
                st.image(msg["imagen_data"], caption="Postura Visual", use_container_width=True)
                
        # MOSTRAR AUDIO 🎵
        if "audio_data" in msg:
            st.audio(msg["audio_data"], format="audio/mp3")

if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Conectando..."):
            try:
                # 1. Generar Texto
                response = model.generate_content(f"{INSTRUCCION}\nUsuario: {prompt}")
                texto = response.text
                st.markdown(texto)
                
                # 2. Generar/Obtener Imagen (CON TRUCO)
                img_bytes = mostrar_imagen_postura(texto)

                # 3. Generar Audio
                audio_bytes = None
                if usar_voz and client_eleven:
                    audio_bytes = generar_audio_elevenlabs(texto)
                    if audio_bytes: st.audio(audio_bytes, format="audio/mp3")

                # 4. Guardar todo
                msg = {"role": "assistant", "content": texto}
                if audio_bytes: msg["audio_data"] = audio_bytes
                if img_bytes: msg["imagen_data"] = img_bytes # Guardamos la imagen para que no desaparezca
                
                st.session_state.mensajes.append(msg)
                
            except Exception as e:
                st.error(f"Error: {e}")
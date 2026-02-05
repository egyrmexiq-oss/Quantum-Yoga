import streamlit as st
import google.generativeai as genai
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# ⚙️ CONFIGURACIÓN DE PÁGINA (AMBIENTE ZEN)
# ==========================================
# Cambié el icono por un cerebro 🧠 y el título
st.markdown('<h1 style="text-align: center;">Wellness’s Flow 🌿</h1>', unsafe_allow_html=True)
# Coloca esto justo después de st.set_page_config
# Coloca esto justo debajo de st.set_page_config
st.markdown("""
    <style>
    /* 1. EL FONDO PRINCIPAL (DERECHA) - Verde Menta Suave */
    .stApp {
        background-color: #E8F5E9 !important;
    }

    /* 2. LA BARRA LATERAL (IZQUIERDA) - Verde Bosque (El que te gustaba) */
    [data-testid="stSidebar"] {
        background-color: #344E41 !important;
    }
    
    /* 3. TEXTO DE LA BARRA LATERAL - Color Arena/Crema para contraste */
    [data-testid="stSidebar"] * {
        color: #DAD7CD !important;
    }

    /* 4. TEXTO GENERAL DE LA PANTALLA - Verde Oscuro para leer bien */
    .stApp, .stMarkdown, h1, h2, h3, p, li, label {
        color: #1B4D3E !important;
    }

    /* 5. BOTONES - Verde Medio con Texto Blanco */
    div.stButton > button {
        background-color: #588157 !important;
        color: white !important;
        border-radius: 20px;
        border: none;
    }
    
    /* 6. INPUT DE CHAT - Para que no se vea blanco brillante */
    .stChatFloatingInputContainer {
        background-color: #E8F5E9 !important;
    }
    </style>
    """, unsafe_allow_html=True)
# ==========================================
# 🔐 1. LOGIN (Igual que la otra App)
# ==========================================
if "usuario_activo" not in st.session_state: st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    # Reemplaza el título viejo por esto:
    st.markdown('<h3 style="text-align: center; color: #556B2F;">Tu santuario personal de equilibrio</h3>', unsafe_allow_html=True)
    # Animación diferente (más calmada si quieres, o la misma)
    try: st.components.v1.iframe("https://my.spline.design/claritystream-Vcf5uaN9MQgIR4VGFA5iU6Es/", height=400)
    except: pass
    
    # Música relajante (Piano/Ambient)
    st.audio("https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3", loop=True, autoplay=True)
    
    st.info("🔑 Clave de Acceso para Invitados: **DEMO**")
    
    c = st.text_input("Clave de Acceso:", type="password")
    if st.button("Entrar a Sesión"):
        #if c.strip() == "DEMO" or (c.strip() in st.secrets["access_keys"]):
        if c.strip() in st.secrets["access_keys"]:
            nombre = "Visitante" if c.strip() == "DEMO" else st.secrets["access_keys"][c.strip()]
            st.session_state.usuario_activo = nombre
            st.rerun()
        else: st.error("Acceso Denegado")
    st.stop()

# ==========================================
# 💎 2. CONEXIÓN (AQUÍ PONES LA NUEVA HOJA)
# ==========================================
try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except: st.error("Falta API Key")

# ⚠️ OJO: AQUÍ DEBES PEGAR EL LINK DE TU NUEVA HOJA DE PSICÓLOGOS 👇
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBFtqUTpPEcOvfXZteeYZJBEzcoucLwN9OYlLRvbAGx_ZjIoQsg1fzqE6lOeDjoSTm4LWnoAnV7C4q/pub?output=csv" 
URL_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSdaK-a8blh67PYxCGyREWOABEf96ZyV6PJnyetBggkymCCjRA/viewform?usp=header"

@st.cache_data(ttl=60)
def cargar_especialistas():
    try:
        df = pd.read_csv(URL_GOOGLE_SHEET)
        df.columns = [c.strip().lower() for c in df.columns]
        mapa = {}
        for col in df.columns:
            if "nombre" in col: mapa[col] = "nombre"
            elif "especialidad" in col: mapa[col] = "especialidad" # Ej: Terapia de Pareja, Infantil, Ansiedad
            elif "descripci" in col: mapa[col] = "descripcion"
            elif "tel" in col: mapa[col] = "telefono"
            elif "ciudad" in col: mapa[col] = "ciudad"
            elif "aprobado" in col: mapa[col] = "aprobado"
        df = df.rename(columns=mapa)
        if 'aprobado' in df.columns:
            return df[df['aprobado'].astype(str).str.upper().str.contains('SI')].to_dict(orient='records')
        return []
    except: return []

TODOS_LOS_PSICOLOGOS = cargar_especialistas()

# --- CEREBRO DE PSICOLOGÍA ---
if TODOS_LOS_PSICOLOGOS:
    ciudades = sorted(list(set(str(m.get('ciudad', 'General')).title() for m in TODOS_LOS_PSICOLOGOS)))
    ciudades.insert(0, "Todas las Ubicaciones")
    
    info_psi = [f"Nombre: {m.get('nombre')} | Especialidad: {m.get('especialidad')} | Ubicación: {m.get('ciudad')}" for m in TODOS_LOS_PSICOLOGOS]
    TEXTO_DIRECTORIO = "\n".join(info_psi)
    
    # 🌿 EL NUEVO MOTOR DE WENDY
INSTRUCCION_EXTRA = """
ERES "WELLNESS'S FLOW MASTER", EL AVATAR DIGITAL DE LA INSTRUCTORA CERTIFICADA WENDY GTZ. NIELSEN.
TU TONO: Sereno, alentador, técnico y profundamente equilibrado.

TUS TAREAS:
1. 🧘 ASANAS: Sugiere posturas basadas en el estado físico del usuario (ej: Balasana para descanso).
2. 🫁 PRANAYAMA: Integra ejercicios de respiración en cada respuesta.
3. 📝 SÁNSCRITO: Usa los nombres originales (ej: Adho Mukha Svanasana).
4. 🛡️ SEGURIDAD: Advierte siempre: "Escucha a tu cuerpo; la práctica debe ser sin dolor".
"""
# ==========================================
# 🧘 3. INTERFAZ ZEN (BARRA LATERAL)
# ==========================================
with st.sidebar:
    st.header("🧘 Wellness Flow")
    st.caption("By Wendy Gtz. Nielsen")
    st.success(f"Namasté, {st.session_state.usuario_activo}")
    
    # ... (Tu contador de alumnos está excelente) ...

    st.markdown("---")
    st.markdown("### 🕊️ Intención del Día")
    st.info("La práctica de hoy se enfoca en la apertura y la gratitud.")
    
    # Eliminamos la sección de "Encuentra Psicólogo" y dejamos espacio para el futuro
    
    st.markdown("---")
    st.markdown("### ⚙️ Preferencias")
    # Cambié los niveles para que sean más humanos
    nivel = st.radio("Entrenamiento:", ["Basico", "Medio", "Avanzado"])
    
    if st.button("🍃 Nueva Sesión"): st.session_state.mensajes = []; st.rerun()
    if st.button("🔒 Salir"): st.session_state.usuario_activo = None; st.rerun()

    st.markdown("---")
    st.markdown("### 🛋️ Encuentra Instructor/a")
    if TODOS_LOS_PSICOLOGOS:
        filtro = st.selectbox("📍 Ciudad:", ciudades)
        lista = TODOS_LOS_PSICOLOGOS if filtro == "Todas las Ubicaciones" else [m for m in TODOS_LOS_PSICOLOGOS if str(m.get('ciudad')).title() == filtro]
        
        if lista:
            if "idx" not in st.session_state: st.session_state.idx = 0
            m = lista[st.session_state.idx % len(lista)]
            
            # Tarjeta de Instructora (Estilo más suave, color Morado/Lila)
            tarjeta = (
                f'<div style="background-color: #2e1a47; padding: 15px; border-radius: 10px; border: 1px solid #5a3e7d; margin-bottom: 10px;">'
                f'<h4 style="margin:0; color:white;">{m.get("nombre","Lic.")}</h4>'
                f'<div style="color:#E0B0FF; font-weight:bold;">{m.get("especialidad")}</div>' # Color Lavanda
                f'<small style="color:#ccc;">{m.get("ciudad")}</small>'
                f'<div style="font-size: 0.9em; margin-top: 5px; color: white;">📞 {m.get("telefono","--")}</div>'
                f'</div>'
            )
            st.markdown(tarjeta, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            if c1.button("⬅️"): st.session_state.idx -= 1; st.rerun()
            if c2.button("➡️"): st.session_state.idx += 1; st.rerun()
        else: st.info("No hay especialistas en esta zona aún.")

    st.markdown("---")
    st.link_button("📝 Soy Psicólogo/a", URL_FORMULARIO)

# ==========================================
# 💬 4. CHAT TERAPÉUTICO
# ==========================================

# Título más suave
st.markdown('<h1 style="text-align: center; color: #E0B0FF;">Quantum Yoga</h1>', unsafe_allow_html=True)
st.caption("Espacio de práctica y orientación basado en IA")

if "mensajes" not in st.session_state: 
    # Saludo inicial diferente
    st.session_state.mensajes = [{"role": "assistant", "content": "Hola. Soy Quantum Yoga. Este es un espacio de práctica y orientacion de YOGA. ¿Qué quieres hacer hoy?"}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Cuéntame cómo te sientes..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    try:
        full_prompt = f"Eres Quantum Mind (Modo: {nivel}). {INSTRUCCION_EXTRA}. Usuario dice: {prompt}."
        # Usamos el modelo rápido 2.5 o Pro
        res = genai.GenerativeModel('gemini-2.5-flash').generate_content(full_prompt)
        st.session_state.mensajes.append({"role": "assistant", "content": res.text})
        st.rerun()
    except Exception as e: st.error(f"Error de conexión: {e}")
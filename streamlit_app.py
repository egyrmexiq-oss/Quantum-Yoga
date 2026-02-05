import streamlit as st
import google.generativeai as genai
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 🏗️ INICIALIZACIÓN DE ESTADO (PEGAR AL INICIO)
# ==========================================
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "usuario_activo" not in st.session_state:
    # Esto evita errores si intentas acceder al usuario antes del login
    # Pero no te loguea automáticamente, solo reserva el espacio.
    pass

# ==========================================
# ⚙️ CONFIGURACIÓN DE PÁGINA (AMBIENTE ZEN)
# ==========================================
# Cambié el icono por un cerebro 🧠 y el título
st.markdown('<h1 style="text-align: center;">Wellness’s Flow 🌿</h1>', unsafe_allow_html=True)
# Coloca esto justo después de st.set_page_config
# Coloca esto justo debajo de st.set_page_config
st.markdown("""
    <style>
    /* 1. FONDO PRINCIPAL */
    .stApp { background-color: #E8F5E9 !important; }

    /* 2. BARRA LATERAL */
    [data-testid="stSidebar"] { background-color: #344E41 !important; }
    [data-testid="stSidebar"] * { color: #DAD7CD !important; }

    /* 3. TEXTO GENERAL */
    .stApp, .stMarkdown, h1, h2, h3, p, li, label { color: #1B4D3E !important; }

    /* 4. BOTONES */
    div.stButton > button {
        background-color: #588157 !important;
        color: white !important;
        border-radius: 20px;
        border: none;
    }

    /* 5. LOGINS Y MÁRGENES */
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    [data-testid="stImage"] img { border-radius: 15px; }

    /* 6. CABECERA */
    header[data-testid="stHeader"] { background-color: #E8F5E9 !important; }

    /* 11. ZONA DE CHAT (CONTENEDOR) */
    .stChatFloatingInputContainer { background-color: #E8F5E9 !important; }

    /* --- 🚨 12. CORRECCIÓN DE INPUTS (LOGIN Y CHAT) 🚨 --- */
    
    /* A. Caja de Texto del LOGIN (Password) */
    div[data-testid="stTextInput"] input {
        background-color: #FFFFFF !important;
        color: #1B4D3E !important; /* Texto Verde Oscuro */
        border: 1px solid #588157 !important;
        border-radius: 10px;
    }
    
    /* B. Caja de Texto del CHAT (Abajo) */
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border: 2px solid #588157 !important;
        border-radius: 20px !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #1B4D3E !important; /* Texto Verde Oscuro */
        caret-color: #1B4D3E !important; /* Cursor Verde */
    }

    /* --- 🚨 13. BURBUJAS DE CHAT (LEER BIEN) 🚨 --- */
    
    /* A. Burbuja del USUARIO (Tú) -> Verde con letras BLANCAS */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #588157 !important;
        border-radius: 20px;
        color: #FFFFFF !important; /* ¡BLANCO IMPORTANTE! */
    }
    /* Forzar que el texto markdown dentro de la burbuja del usuario sea blanco */
    div[data-testid="stChatMessage"]:nth-child(odd) p {
        color: #FFFFFF !important;
    }

    /* B. Burbuja de la IA (Wendy) -> Blanca con letras VERDES */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #FFFFFF !important;
        border: 1px solid #A3B18A;
        border-radius: 20px;
        color: #1B4D3E !important;
    }
    </style>
    """, unsafe_allow_html=True)
# ==========================================
# 🔐 1. LOGIN (Igual que la otra App)
# ==========================================
# ... (Tus imports y configuraciones CSS van arriba) ...

# ==========================================
# 🚪 LÓGICA DE CONTROL DE ACCESO
# ==========================================
if "usuario_activo" not in st.session_state:
    # --- PANTALLA DE LOGIN (Si no ha entrado) ---
    
    # Imagen Panorámica
    st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?q=80&w=2000&h=800&auto=format&fit=crop", use_container_width=True)
    
    st.markdown('<h1 style="text-align: center;">Wellness’s Flow 🌿</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center;">Tu santuario personal de equilibrio</h3>', unsafe_allow_html=True)
    
    # Campo de contraseña
    clave_input = st.text_input("Clave de Acceso:", type="password")
    
    if st.button("Entrar a Sesión"):
        if clave_input == "DEMO" or clave_input == st.secrets["CLAVE_MAESTRA"]: # Ajusta según tu clave
            st.session_state.usuario_activo = "Invitado"
            st.rerun() # <--- Recarga para entrar a la app
        else:
            st.error("Clave incorrecta. Respira e intenta de nuevo.")
            
    st.stop() # 🛑 ¡IMPORTANTE! Esto detiene el código aquí para que NO cargue el chat abajo.

else:
    # ==========================================
    # 🧘 PANTALLA PRINCIPAL (APP)
    # ==========================================
    # (Aquí va TODO el resto: Barra lateral, Chat, PDF, etc.)
    
    #with st.sidebar:
        # ... Tu código de barra lateral ...
     #   if st.button("🔒 Salir"):
      #      del st.session_state["usuario_activo"]
       #     st.rerun()

    # ... Tu lógica de Chat y Mensajes ...
    # (Asegúrate de que todo el código del chat esté identado dentro de este 'else')
    # ==========================================
# 🎨 ESTILO VISUAL (CSS) - ARMONIZACIÓN TOTAL
# ==========================================
    st.markdown("""
    <style>
    /* 1. FONDO PRINCIPAL */
    .stApp { background-color: #E8F5E9 !important; }

    /* 2. BARRA LATERAL */
    [data-testid="stSidebar"] { background-color: #344E41 !important; }
    [data-testid="stSidebar"] * { color: #DAD7CD !important; }

    /* 3. TEXTO GENERAL */
    .stApp, .stMarkdown, h1, h2, h3, p, li, label { color: #1B4D3E !important; }

    /* 4. BOTONES */
    div.stButton > button {
        background-color: #588157 !important;
        color: white !important;
        border-radius: 20px;
        border: none;
    }

    /* 5. LOGINS Y MÁRGENES */
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    [data-testid="stImage"] img { border-radius: 15px; }

    /* 6. CABECERA */
    header[data-testid="stHeader"] { background-color: #E8F5E9 !important; }

    /* --- 🚨 11. OPERACIÓN "FRANJA VERDE" 🚨 --- */
    
    /* A. El contenedor flotante PRINCIPAL (La franja negra) */
    .stChatFloatingInputContainer {
        background-color: #E8F5E9 !important; /* Verde Menta */
        bottom: 0px !important;
        padding-bottom: 10px;
    }
    
    /* B. Asegurar que los hijos de ese contenedor también sean verdes */
    .stChatFloatingInputContainer > div {
        background-color: #E8F5E9 !important;
    }

    /* C. La caja de escritura (Blanca) */
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border: 2px solid #588157 !important;
        border-radius: 20px !important;
        color: #333333 !important;
    }

    /* D. El texto que escribes */
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #333333 !important;
    }
    
    /* E. El botón de enviar */
    div[data-testid="stChatInput"] button {
        color: #588157 !important;
    }
    </style>
    """, unsafe_allow_html=True)
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
        # 1. ENCABEZADO
        st.header("🧘 Wellness Flow")
        st.caption("By Wendy Gtz. Nielsen")
        st.success(f"Namasté, {st.session_state.usuario_activo}")
        
        st.markdown("---")

        # 2. PREFERENCIAS
        st.markdown("### ⚙️ Preferencias")
        nivel = st.radio("Entrenamiento:", ["Basico", "Medio", "Avanzado"])
        
        # 3. CONTROLES DE SESIÓN
        if st.button("🍃 Nueva Sesión"): 
            st.session_state.mensajes = []
            st.rerun()
            
        # El botón de salir corregido que ya funcionaba
        if st.button("🔒 Salir"):
            del st.session_state["usuario_activo"]
            st.rerun()

        st.markdown("---")

        # 4. 📥 BOTÓN DE DESCARGA PDF (El Rescate)
        # Solo aparece si hay mensajes en el chat
        if st.session_state.mensajes:
            try:
                # Generamos el PDF usando la función que ya tienes arriba
                pdf_bytes = generar_pdf_yoga(st.session_state.usuario_activo, st.session_state.mensajes)
                b64 = base64.b64encode(pdf_bytes).decode()
                
                # Botón con estilo personalizado
                href = f'''
                <a href="data:application/octet-stream;base64,{b64}" download="Rutina_Yoga_{st.session_state.usuario_activo}.pdf" 
                style="text-decoration:none; color: #1B4D3E; background-color: #DAD7CD; 
                padding: 10px; border-radius: 10px; display: block; text-align: center; border: 1px solid #588157;">
                📥 <b>Descargar Rutina PDF</b>
                </a>
                '''
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error("Escribe algo en el chat para habilitar el PDF.")
        else:
            st.caption("Inicia tu práctica para descargar la rutina.")

        st.markdown("---")

        # 5. 🧘 SECCIÓN DE INSTRUCTORES (Limpia y lista para tus enlaces)
        st.markdown("### 🧘 Encuentra Instructor/a")
        
        # Aquí eliminamos el bucle de "TODOS_LOS_PSICOLOGOS"
        # Y dejamos el espacio limpio para tus futuros enlaces.
        
        st.info("Directorio de Instructores Certificados en actualización.")
        
        # --- AQUÍ PEGARÁS TUS ENLACES EN EL FUTURO ---
        # Ejemplo:
        # st.markdown("[Ver Instructores en CDMX](https://docs.google.com/...)")
        
        st.markdown("---")
        st.caption("© 2025 Wellness Flow")
# ==========================================
# 💬 4. CHAT TERAPÉUTICO
# ==========================================

# Título más suave
#st.markdown('<h1 style="text-align: center; color: #E0B0FF;">Quantum Yoga</h1>', unsafe_allow_html=True)
st.caption("Espacio de práctica y orientación basado en IA")

if "mensajes" not in st.session_state: 
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Namasté! Soy Wellness Flow. Estoy aquí para guiar tu práctica de yoga y respiración. ¿Cómo se siente tu cuerpo hoy?"}]

    # ==========================================
# 💬 5. MOTOR DE CHAT (PEGAR AL FINAL DEL ARCHIVO)
# ==========================================

# Esta es la línea mágica que dibuja la caja blanca 👇
if prompt := st.chat_input("Cuéntame cómo te sientes o qué te duele..."):
    
    # 1. Guardar y mostrar el mensaje del usuario
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Pensamiento de la IA (Wendy)
    try:
        # Construimos el prompt con la personalidad de Yoga
        # Usamos el historial reciente para que tenga memoria
        historial_texto = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.mensajes[-5:]])
        full_prompt = f"{INSTRUCCION_EXTRA}\n\nDiálogo reciente:\n{historial_texto}"
        
        # Llamada al modelo (Usamos el '2.5' que te funciona bien)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(full_prompt)
        bot_response = response.text
        
        # 3. Guardar y mostrar la respuesta
        st.session_state.mensajes.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)
            
        # 4. Recargar para que se actualice el PDF
        st.rerun()
        
    except Exception as e:
        st.error(f"Ocurrió un error de conexión: {e}")
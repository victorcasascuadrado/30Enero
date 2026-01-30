import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de página y ocultar menús
st.set_page_config(page_title="Tasador Agrícola", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# Configuración API - Asegúrate de que en Secrets se llame GOOGLE_API_KEY
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⚠️ No se encontró la API Key en los Secrets de Streamlit.")

st.title("🚜 Tasador Agrícola Noroeste")
st.subheader("VCasas Mercado Europeo")

# Cuadro de texto único
datos_maquina = st.text_area("Detalles (Marca, Modelo, Extras, Estado...)*", 
                             placeholder="Ej: John Deere 6155M, 2019, 4500h, suspensión delantera...",
                             height=150)

# Subida de fotos (Mínimo 5)
fotos = st.file_uploader("Fotos (Mínimo 5)*", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

# Vista previa pequeña
if fotos:
    cols = st.columns(5)
    for idx, f in enumerate(fotos[:10]): # Muestra hasta 10 previas
        with cols[idx % 5]:
            st.image(f, use_container_width=True)

if st.button("Obtener Precio de Mercado"):
    if not datos_maquina or not fotos or len(fotos) < 5:
        st.error("❌ Falta información o el mínimo de 5 fotos.")
    else:
        with st.spinner("Consultando mercado europeo..."):
            try:
                # El modelo correcto para la versión gratuita es gemini-1.5-flash
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Preparar el contenido para el modelo
                # Incluimos el prompt y luego las imágenes procesadas
                contenido = []
                contenido.append(f"""
                Analiza esta máquina basándote en: {datos_maquina}.
                
                TAREA:
                1. Estima precios actuales basándote en portales europeos (Mascus, Agriaffaires, Traktorpool).Devuelve una tabla con unos 10 modelos que encuentres en estas webs, ajustate si puedes a las horas de la maquina
                2. Compara visualmente el estado de las fotos con el estándar de mercado.
                3. Devuelve solo la tasación escueta:
                   - Valor de mercado estimado (rango €).
                   - Precio medio en Europa para este modelo/año.
                   - Conclusión en 2 frases máximo sobre si es buen momento para vender/comprar según el stock europeo.
                
                NO escribas informes largos ni introducciones. Sé directo.
                """)
                
                for f in fotos:
                    img = Image.open(f)
                    contenido.append(img)
                
                # Llamada a la API
                response = model.generate_content(contenido)
                
                # Mostrar resultado
                st.divider()
                st.subheader("Resultado de Tasación:")
                st.success(response.text)
                
            except Exception as e:
                st.error(f"Hubo un problema con la consulta: {e}")

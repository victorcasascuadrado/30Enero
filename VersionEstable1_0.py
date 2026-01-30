import streamlit as st
import google.generativeai as genai
from PIL import Image
# main.py
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)
# Configuración API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("🚜 Tasador Agricola Noroeste: VCasas Mercado Europeo")

# Cuadro de texto único
datos_maquina = st.text_area("Detalles (Marca, Modelo, Extras, Estado...)*", height=150)

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
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Prompt enfocado en brevedad y comparación de mercado
                prompt = f"""
                Analiza esta máquina basándote en: {datos_maquina}.
                
                TAREA:
                1. Busca referencias de precios actuales en portales europeos de maquinaria agrícola (Mascus, Agriaffaires, Traktorpool).
                2. Compara el modelo de las fotos con los anuncios activos.
                3. Devuelve solo la tasación escueta:
                   - Valor de mercado estimado (rango €).
                   - Precio medio en Europa para este modelo/año.
                   - Conclusión en 2 frases máximo sobre si es buen momento para vender/comprar según el stock europeo.
                
                NO escribas informes largos ni introducciones.
                """
                
                contenido = [prompt]
                for f in fotos:
                    img = Image.open(f)
                    contenido.append(img)
                
                response = model.generate_content(contenido)
                
                # Mostrar resultado de forma muy limpia
                st.subheader("Resultado Escueto:")
                st.info(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")

"""
Interfaz Gráfica del Sistema Experto de Lanzamiento Espacial.
Desarrollada con Streamlit para permitir una interacción amigable con el motor CLIPS.
"""
import streamlit as st
from se_clipspy import crear_entorno, inferir_recomendacion  # Importamos las funciones del sistema experto

# Función para obtener el entorno CLIPS
def get_env():
    """Obtiene la instancia actual del motor de reglas configurado."""
    return crear_entorno()  # Retorna el entorno y la lista de reglas disparadas

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Sistema Experto – Lanzamiento Espacial",
    layout="centered"
)

# SIDEBAR
st.sidebar.title("Menú")  # Título de la barra lateral
# Radio para seleccionar la opción del menú
opcion = st.sidebar.radio(
    "Selecciona una opción",
    ["Diagnóstico de lanzamiento", "Acerca de"]
)

# VISTA ACERCA DE
if opcion == "Acerca de":
    st.title("Acerca de")
    st.write("""
    Esta aplicación implementa un **sistema experto** para la evaluación
    del estado de un lanzamiento espacial.

    El sistema utiliza **CLIPS** como motor de inferencia, integrado en Python
    mediante la librería **clipspy**, y una interfaz gráfica desarrollada
    con **Streamlit**.
    """)

    st.markdown("---")  # Separador visual
    st.write("👨‍💻 **Autor:** Juan José Arróniz Martínez")
    st.write("🎓 Asignatura: Ingeniería del Conocimiento")
    st.write("🏫 Universidad: UCAM")
    st.write("📅 Curso académico: 2025/2026")

# VISTA PRINCIPAL
if opcion == "Diagnóstico de lanzamiento":
    st.title("Sistema Experto de Lanzamiento Espacial 🚀")
    st.write("Seleccione el estado de los sistemas antes del lanzamiento:")

    # CONTROLES VISUALES
    # Organizamos los sliders y selectores para simular un panel de control
    with st.expander("Parámetros Técnicos", expanded=True):
        # Inputs para el usuario que representan el estado de cada sistema
        nivel_combustible_ui = st.slider("Nivel de combustible (%)", 0, 100, 100, 1)
        motor_ui = st.radio("Motor principal", ["Funciona", "Anomalía"])
        presion_ui = st.radio("Presión tanques", ["Correcta", "Baja"])
        navegacion_ui = st.radio("Navegación", ["Operativa", "Fallo"])
        comunicacion_ui = st.radio("Sistema de comunicación", ["Funcional", "Fallo"])
        electrico_ui = st.selectbox("Sistema eléctrico", ["Funcional", "Fallo"])
        software_ui = st.selectbox("Software de control", ["Funcional", "Fallo"])
        precipitaciones = st.slider("Probabilidad de precipitaciones (%)", 0, 100, 0, 1)
        clima_ui = st.radio("¿Clima actual?", ["Despejado", "Nublado"])
        sensores_ui = st.radio("¿Estado de sensores?", ["Correcto", "Anomalía"])
        aerodinamica_ui = st.radio("Estado de sistemas de aerodinámica", ["Correcto", "Fallo"])

    # BOTÓN PARA EVALUAR
    if st.button("Evaluar lanzamiento"):
        # Mapeo de los valores de la UI a símbolos que CLIPS entiende
        nivel_combustible_sim = nivel_combustible_ui
        motor_principal_sim = "yes" if motor_ui == "Funciona" else "no"
        presion_tanques_sim = "ok" if presion_ui == "Correcta" else "fail"
        sistema_navegacion_sim = "ok" if navegacion_ui == "Operativa" else "fail"
        sistema_comunicacion_sim = "ok" if comunicacion_ui == "Funcional" else "fail"
        sistema_electrico_sim = "ok" if electrico_ui == "Funcional" else "fail"
        software_control_sim = "ok" if software_ui == "Funcional" else "fail"
        prob_precipitaciones_sim = precipitaciones
        estado_clima_sim = "despejado" if clima_ui == "Despejado" else "nublado"
        sensores_sim = "ok" if sensores_ui == "Correcto" else "fail"
        aerodinamica_sim = "ok" if aerodinamica_ui == "Correcto" else "fail"

        # Crear entorno CLIPS, se llama al sistema experto
        env, disparadas = get_env()  # Crea y devuelve el entorno y lista de reglas disparadas

        # Ejecutar motor de inferencia pasando todos los valores del lanzamiento
        recomendacion, disparadas = inferir_recomendacion(
            env, disparadas,
            nivel_combustible=nivel_combustible_sim,
            motor_principal=motor_principal_sim,
            presion_tanques=presion_tanques_sim,
            sistema_navegacion=sistema_navegacion_sim,
            sistema_comunicacion=sistema_comunicacion_sim,
            sistema_electrico=sistema_electrico_sim,
            software_control=software_control_sim,
            prob_precipitaciones=prob_precipitaciones_sim,
            estado_clima=estado_clima_sim,
            sensores=sensores_sim,
            aerodinamica=aerodinamica_sim
        )

        # MÓDULO DE EXPLICACIÓN
        if disparadas:
            st.subheader("Trazabilidad: Razonamiento del Sistema")
            for item in disparadas:
                with st.expander(f"Regla: {item['regla']}"):
                    st.write(f"**Causa detectada:** {item['hecho']}")
                    st.write(f"**Justificación:** {item['detalle']}")

        # RESULTADO FINAL DEL SISTEMA EXPERTO
        st.subheader("Recomendacion final del Sistema Experto")

        # Mostrar la recomendación en un área de texto
        st.success("Análisis completado")
        st.text_area("Veredicto del Director de Vuelo", recomendacion, height=150)
import streamlit as st
import duckdb
import pandas as pd

# 1. Configuración inicial de la página
st.set_page_config(page_title="VCT 2025 Dashboard", layout="wide")
st.title("🏆 Dashboard Analítico - Valorant VCT 2025")
st.markdown("Conectado a la base de datos relacional local (`valorant_oficial.db`)")

# 2. Conectar a la base de datos (con caché para que sea ultra rápido)
@st.cache_resource
def obtener_conexion():
    return duckdb.connect('valorant_oficial.db', read_only=True)

conexion = obtener_conexion()

# 3. BARRA LATERAL - Filtros interactivos
st.sidebar.header("Filtros")

# Extraer nombres de equipos directamente de la dimensión para el menú desplegable
df_equipos = conexion.execute("SELECT Nombre_Equipo FROM Dim_Equipos ORDER BY Nombre_Equipo").df()
lista_equipos = ["Todos"] + df_equipos['Nombre_Equipo'].tolist()

equipo_seleccionado = st.sidebar.selectbox("Selecciona un Equipo:", lista_equipos)

# 4. CONSULTA SQL RELACIONAL (El corazón del dashboard)
# Cruzamos la tabla de hechos con las dimensiones usando las llaves foráneas
consulta_sql = """
    SELECT 
        j.Nombre_Jugador AS Jugador,
        e.Nombre_Equipo AS Equipo,
        t.Nombre_Torneo AS Torneo,
        SUM(h.Kills) AS Total_Bajas,
        SUM(h.Deaths) AS Total_Muertes
    FROM Hechos_Rendimiento h
    JOIN Dim_Jugadores j ON h.ID_Jugador = j.ID_Jugador
    JOIN Dim_Equipos e ON h.ID_Equipos = e.ID_Equipos  -- <-- AQUÍ agregamos la 's'
    JOIN Dim_Torneos t ON h.ID_Torneo = t.ID_Torneo
"""

# Inyectamos el filtro de la barra lateral si el usuario elige un equipo específico
if equipo_seleccionado != "Todos":
    consulta_sql += f" WHERE e.Nombre_Equipo = '{equipo_seleccionado}'"

# Terminamos la consulta agrupando y ordenando
consulta_sql += """
    GROUP BY j.Nombre_Jugador, e.Nombre_Equipo, t.Nombre_Torneo
    ORDER BY Total_Bajas DESC
    LIMIT 15
"""

try:
    # 5. Ejecutar la consulta
    df_resultados = conexion.execute(consulta_sql).df()
    
    # 6. Renderizar los gráficos
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Top Bajas (Kills)")
        
        # A. Creamos el selector de tipo de gráfico
        tipo_grafico = st.selectbox(
            "Visualización:", 
            ["Gráfico de Barras", "Gráfico de Líneas", "Gráfico de Área", "Gráfico de Dispersión"]
        )
        
        # B. Lógica condicional para renderizar el gráfico elegido
        if tipo_grafico == "Gráfico de Barras":
            st.bar_chart(data=df_resultados, x="Jugador", y="Total_Bajas", color="#ff4b4b")
            
        elif tipo_grafico == "Gráfico de Líneas":
            st.line_chart(data=df_resultados, x="Jugador", y="Total_Bajas", color="#ff4b4b")
            
        elif tipo_grafico == "Gráfico de Área":
            st.area_chart(data=df_resultados, x="Jugador", y="Total_Bajas", color="#ff4b4b")
            
        elif tipo_grafico == "Gráfico de Dispersión":
            st.scatter_chart(data=df_resultados, x="Jugador", y="Total_Bajas", color="#ff4b4b")
        
    with col2:
        st.subheader("Tabla de Resultados")
        st.dataframe(df_resultados, hide_index=True)

except Exception as e:
    st.error(f"Error en la consulta de base de datos: {e}")

# --- SECCIÓN DE CONSOLA INTERACTIVA ---
st.markdown("---") # Crea una línea divisoria visual
st.subheader("💻 Consola SQL Interactiva")
st.write("Escribe tus propias consultas SQL aquí para explorar la base de datos a tu gusto.")

# 1. Creamos un área de texto grande para escribir código
consulta_usuario = st.text_area(
    "Ingresa tu consulta SQL:", 
    height=150, 
    value="SELECT * FROM Dim_Jugadores LIMIT 5;" # Un valor por defecto para que no esté vacío
)

# 2. Creamos un botón para ejecutar
if st.button("Ejecutar Consulta"):
    try:
        # 3. Intentamos ejecutar lo que escribió el usuario
        df_usuario = conexion.execute(consulta_usuario).df()
        st.success("¡Consulta ejecutada con éxito!")
        
        # 4. Mostramos el resultado
        st.dataframe(df_usuario, use_container_width=True)
        
    except Exception as e:
        # Si el usuario escribe mal el SQL, capturamos el error y se lo mostramos en rojo
        st.error(f"Ocurrió un error en tu sintaxis SQL: {e}")
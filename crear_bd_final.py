import duckdb

print("Iniciando la construcción de la base de datos 3FN...")

# 1. Crear o conectarse al archivo de la base de datos local
conexion = duckdb.connect('valorant_oficial.db')

# 2. Lista exacta de tus archivos según la imagen
tablas = [
    "Dim_Agentes",
    "Dim_Equipos",
    "Dim_Etapas",
    "Dim_Jugadores",
    "Dim_Tipos_Partidas",
    "Dim_Torneos",
    "Hechos_Rendimiento",
    "Puente_Rendimiento_Agente"
]

try:
    # 3. Bucle para leer cada CSV y convertirlo en tabla de BD automáticamente
    for tabla in tablas:
        # Borramos la tabla si existe para evitar errores si lo corres varias veces
        conexion.execute(f"DROP TABLE IF EXISTS {tabla}")
        # Creamos la tabla leyendo el CSV desde la carpeta tablas_limpias
        conexion.execute(f"CREATE TABLE {tabla} AS SELECT * FROM read_csv_auto('tablas_limpias/{tabla}.csv')")
        print(f"✅ Tabla '{tabla}' creada con éxito.")

    print("\n🎉 ¡Fase 2 completada! Tu base de datos 'valorant_oficial.db' está lista para Streamlit.")

except Exception as e:
    print(f"❌ Ocurrió un error: {e}")

finally:
    conexion.close()
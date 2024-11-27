import streamlit as st
import pandas as pd
from notion_client import Client
import notion_df

# Conexión a Notion
notion = Client(auth="ntn_HS754119761gePqHfm7JpMo1bp27qxK8fI1TgG6Q5eHgAz")
PERSONAS_DB_ID = "14a02cf2f45180c1ad14ca69293b1bed"
TAREAS_DB_ID = '14a02cf2f45180ce9b05cdf609a4a424'

# Cargar datos desde Notion
# @st.cache_data
def cargar_datos():
    try:
        # Descargar datos desde Notion
        personas_df = notion_df.download(PERSONAS_DB_ID, api_key='ntn_HS754119761gePqHfm7JpMo1bp27qxK8fI1TgG6Q5eHgAz')
        tareas_df = notion_df.download(TAREAS_DB_ID, api_key='ntn_HS754119761gePqHfm7JpMo1bp27qxK8fI1TgG6Q5eHgAz')

        # Configurar MultiIndex para personas_df y tareas_df
        personas_df = personas_df.set_index([pd.Index(range(len(personas_df))), 'nombre'])
        tareas_df = tareas_df.set_index([pd.Index(range(len(tareas_df))), 'nombre'])

        # Obtener listas desde el nivel 'nombre' del índice
        lista_personas = personas_df.index.get_level_values('nombre').tolist()
        lista_tareas = tareas_df.index.get_level_values('nombre').tolist()

        return personas_df, tareas_df, lista_personas, lista_tareas
    except Exception as e:
        st.error(f"Error al cargar datos desde Notion: {e}")
        return None, None, [], []

    return personas_df, tareas_df, lista_personas, lista_tareas

def get_feature(db, name, feature):
    return db.xs(name, level='nombre')[feature].iloc[0]

def get_index(db, nombre):
    return db.index[db.index.get_level_values('nombre') == nombre][0][0]

def get_name(db, indx):
    return db.index[db.index.get_level_values(None) == indx][0][1]

def beneficio(personas_db, tareas_db, persona, tarea):
    # aptitudes = personas_db.loc[persona,'aptitud']
    aptitudes = get_feature(personas_db, persona,'aptitud')
    requisitos = get_feature(tareas_db, tarea,'aptitud')
    interseccion = [elemento for elemento in aptitudes if elemento in requisitos]
    restriccion = [requisito in aptitudes for requisito in requisitos]
    if not all(restriccion): return -100
    return len(interseccion)

def asignar_tareas(personas_df, tareas_df, personas, tareas):
    asignaciones = [[],[],[],[],[],[],[],[]]
    for persona in personas:
        best = -1
        aux = None
        indx = None
        for tarea in tareas:
            print(tarea)
            benef = beneficio(personas_df, tareas_df, persona, tarea)
            # print(benef, get_index(tareas_df,tarea),persona,tarea)
            pmax = get_feature(tareas_df,tarea,'npersonas')
            aux = get_index(tareas_df,tarea) #posicion en el array de tareas
            print(benef,best,len(asignaciones[aux])+1,pmax)
            if benef > best and len(asignaciones[aux])+1 <= pmax:
                best = benef
                # print('mejorado', benef, best)
                indx = aux
                print('asignado')
        if indx is not None:
            asignaciones[indx].append(persona)
        # print('asignado: ', persona)
    return asignaciones



#########################################################
#########################################################
#########################################################
#########################################################

# Interfaz de Streamlit
st.title("Gestor de Tareas del Show Choir")

# Mostrar los datos cargados
# # st.write("Personas DF (Con MultiIndex):")

# # st.write("Tareas DF (Con MultiIndex):")

# Selección de personas y tareas
st.subheader("Selecciona personas y tareas")

# Cargar datos cada vez que se actualiza la página o se asignan tareas
personas_df, tareas_df, lista_personas, lista_tareas = cargar_datos()
# st.dataframe(tareas_df.reset_index())
st.dataframe(personas_df.reset_index())

personas_seleccionadas = st.multiselect(
    "Selecciona las personas disponibles:",
    options=lista_personas
)

tareas_seleccionadas = st.multiselect(
    "Selecciona las tareas a asignar:",
    options=lista_tareas
)

# Ejecutar la asignación
if st.button("Asignar Tareas"):

    if personas_seleccionadas and tareas_seleccionadas:
        # Recargar datos para asegurarse de usar lo más actualizado
        personas_df, tareas_df, lista_personas, lista_tareas = cargar_datos()

        # Ejecutar el algoritmo
        asignaciones = asignar_tareas(
            personas_df, tareas_df, personas_seleccionadas, tareas_seleccionadas
        )

        # Preparar los resultados
        resultados = {'tarea': [], 'personas': []}
        for tarea in lista_tareas:
            resultados['tarea'].append(tarea)
            resultados['personas'].append(asignaciones[get_index(tareas_df,tarea)]) 
    

        resultados_df = pd.DataFrame(resultados)
        # Mostrar los resultados
        st.success("Asignaciones realizadas con éxito:")
        # st.write(resultados)
        # st.write(resultados_df)
        st.dataframe(resultados_df)
    else:
        st.error("Por favor, selecciona al menos una persona y una tarea.")
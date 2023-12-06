import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def calculate_concentration(Q, u, d, Z0, Cs):
    x, y = np.meshgrid(np.arange(50, 300, d), np.arange(-100, 101, d))
    by0 = 0.08 * x * (1 + 0.0001 * x) ** (-0.5)
    bz0 = 0.06 * x * (1 + 0.0015 * x) ** (-0.5)
    by = by0 * (1 + 0.38 * Z0)
    fz = (2.53 - 0.13 * np.log(x)) * (0.55 + 0.042 * np.log(x)) ** (-1) * Z0 ** (0.35 - 0.03 * np.log(x))
    bz = bz0 * fz
    tempy1 = -y**2 / (2 * by**2)
    tempy2 = np.exp(tempy1)
    c = Q / (np.pi * u) * ((by * bz) ** (-1)) * tempy2

    if Cs < np.min(c) or Cs > np.max(c):
        st.sidebar.warning("Advertencia: El valor de Cs buscado puede generar severos daños a la salud si se expone durante un tiempo prolongado.")
        Cs = np.max(c)

    return x, y, c

def plot_contour(x, y, c):
    num_levels = 20
    levels = np.linspace(np.min(c), np.max(c), num_levels)
    cmap = plt.get_cmap('viridis')
    contourf = plt.contourf(x, y, c, levels=levels, cmap=cmap)
    contour = plt.contour(x, y, c, levels=levels, linewidths=0.3, colors='black')
    cbar = plt.colorbar(contourf, ticks=np.linspace(np.min(c), np.max(c), 20))
    plt.grid()
    plt.xlabel('Distancia axial x (m)')
    plt.ylabel('Distancia axial y (m)')
    plt.title('Simulación de Nube de Amoníaco Tóxica')
    plt.show()

# Configuración del diseño de la página
st.set_page_config(page_title="Simulación de Contaminación", layout="wide")

# Encabezado
col1, col2 = st.columns([1, 3])
with col1:
    st.image("logo.png")  # Asegúrate de tener una imagen llamada 'logo.png' en el directorio
with col2:
    st.title('Simulación de la Dispersión de una Nube de Amoníaco Tóxico')

st.write('Introduce los parámetros para simular la dispersión de una nube de amoníaco tóxico.')

# Barra lateral para entradas del usuario
with st.sidebar:
    st.header("Parámetros de Entrada")
    Q = st.number_input("Intensidad de la fuente (mg/s)", min_value=0.0, format="%.2f")
    u = st.number_input("Velocidad del viento (m/s)", min_value=0.0, format="%.2f")
    d = st.number_input("Precisión del cálculo (m)", min_value=0.1, step=0.1, format="%.2f")
    Z0 = st.number_input("Rugosidad del suelo (m)", min_value=0.0, format="%.2f")
    Cs = st.number_input("Concentración de la solución (mg/m³)", min_value=0.0, format="%.2f")
    calculate_button = st.button('Calcular y Graficar')

# Realizar el cálculo y mostrar la gráfica
if calculate_button:
    x, y, c = calculate_concentration(Q, u, d, Z0, Cs)
    fig, ax = plt.subplots()
    plot_contour(x, y, c)
    st.pyplot(fig)

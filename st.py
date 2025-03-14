import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def calculate_concentration(Q, u, d, Z0):
    # Definir la malla en x e y
    x_vals = np.arange(50, 300, d)
    y_vals = np.arange(-100, 101, d)
    x, y = np.meshgrid(x_vals, y_vals)
    
    # Cálculo de sigma_y y sigma_z usando las fórmulas empíricas
    by0 = 0.08 * x * (1 + 0.0001 * x) ** (-0.5)
    bz0 = 0.06 * x * (1 + 0.0015 * x) ** (-0.5)
    sigma_y = by0 * (1 + 0.38 * Z0)
    fz = (2.53 - 0.13 * np.log(x)) / (0.55 + 0.042 * np.log(x)) * (Z0 ** (0.35 - 0.03 * np.log(x)))
    sigma_z = bz0 * fz
    
    # Concentración en nivel del suelo (asumiendo reflejo del suelo)
    c = Q / (np.pi * u * sigma_y * sigma_z) * np.exp(-y**2 / (2 * sigma_y**2))
    
    return x, y, c, x_vals, y_vals

def compute_reach(x, y, c, Cs):
    """
    Calcula el alcance lineal (máxima x) donde la concentración en la línea central (y=0) es >= Cs.
    """
    # Encontrar el índice de y que se aproxima a 0
    y_center_idx = np.argmin(np.abs(y[:,0]))
    c_center = c[y_center_idx, :]
    # Indices donde la concentración es mayor o igual que Cs
    valid = np.where(c_center >= Cs)[0]
    if valid.size > 0:
        reach = x[0, valid[-1]]
    else:
        reach = None
    return reach

def plot_contour(x, y, c, Cs=None, reach=None):
    fig, ax = plt.subplots()
    num_levels = 20
    levels = np.linspace(np.min(c), np.max(c), num_levels)
    
    # Contornos de la concentración
    contourf = ax.contourf(x, y, c, levels=levels, cmap='viridis')
    ax.contour(x, y, c, levels=levels, linewidths=0.3, colors='black')
    fig.colorbar(contourf, ax=ax, ticks=np.linspace(np.min(c), np.max(c), 20))
    
    ax.grid(True)
    ax.set_xlabel('Distancia axial x (m)')
    ax.set_ylabel('Distancia lateral y (m)')
    ax.set_title('Simulación de Nube de Amoníaco Tóxico')
    
    # Si se proporciona Cs, se dibuja el contorno de ese valor
    if Cs is not None:
        cs_contour = ax.contour(x, y, c, levels=[Cs], colors='red', linestyles='--', linewidths=2)
        ax.clabel(cs_contour, inline=True, fontsize=10, fmt=f'Cs = {Cs:.2f}')
    
    # Si se ha calculado el alcance, se marca con una línea vertical
    if reach is not None:
        ax.axvline(reach, color='red', linestyle='--', label=f'Alcance: {reach:.2f} m')
        ax.legend()
        
    return fig

# Configuración de la página en Streamlit
st.set_page_config(page_title="Simulación de Contaminación", layout="wide")
col1, col2 = st.columns([1, 3])
with col1:
    st.image("logo.png")  # Asegúrate de tener 'logo.png' en el directorio
with col2:
    st.title('Simulación de la Dispersión de una Nube de Amoníaco Tóxico')

st.write('Introduce los parámetros para simular la dispersión de una nube de amoníaco tóxico.')

# Barra lateral de entrada
with st.sidebar:
    st.header("Parámetros de Entrada")
    Q = st.number_input("Intensidad de la fuente (mg/s)", min_value=0.0, format="%.2f")
    u = st.number_input("Velocidad del viento (m/s)", min_value=0.0, format="%.2f")
    d = st.number_input("Precisión del cálculo (m)", min_value=0.1, step=0.1, format="%.2f", value=5.0)
    Z0 = st.number_input("Rugosidad del suelo (m)", min_value=0.0, format="%.2f")
    Cs = st.number_input("Concentración umbral (mg/m³)", min_value=0.0, format="%.2f")
    calculate_button = st.button('Calcular y Graficar')

if calculate_button:
    x, y, c, x_vals, y_vals = calculate_concentration(Q, u, d, Z0)
    
    # Verificación de que Cs esté dentro del rango calculado
    if Cs < np.min(c) or Cs > np.max(c):
        st.sidebar.warning("Advertencia: El valor de Cs buscado está fuera del rango calculado. Se usará el valor máximo de concentración.")
        Cs = np.max(c)
    
    # Cálculo del alcance (distancia máxima en la línea central donde c >= Cs)
    reach = compute_reach(x, y, c, Cs)
    
    fig = plot_contour(x, y, c, Cs, reach)
    st.pyplot(fig)

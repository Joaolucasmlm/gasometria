import streamlit as st
import os

# Configuração da página
st.set_page_config(page_title="Analisador Gasometria", layout="centered")
st.title("Analisador de Gasometria e Disturbios Acido-Base")

# Entradas
pH = st.number_input("pH", step=0.01, format="%.2f")
pCO2 = st.number_input("pCO2 (mmHg)", step=0.1)
HCO3 = st.number_input("HCO3- (mEq/L)", step=0.1)
Na = st.number_input("Na+ (mEq/L)", step=0.1)
K = st.number_input("K+ (mEq/L)", step=0.1)
Cl = st.number_input("Cl- (mEq/L)", step=0.1)
lactato = st.number_input("Lactato (mmol/L) [opcional]", step=0.1, format="%.1f")

resultado = []
disturbios_eletroliticos = []

# Funções auxiliares
def classificar_eletrolitos():
    if Na < 120:
        disturbios_eletroliticos.append("Hiponatremia grave")
    elif Na < 135:
        disturbios_eletroliticos.append("Hiponatremia")
    elif Na > 155:
        disturbios_eletroliticos.append("Hipernatremia grave")
    elif Na > 145:
        disturbios_eletroliticos.append("Hipernatremia")

    if K < 2.5:
        disturbios_eletroliticos.append("Hipocalemia grave")
    elif K < 3.5:
        disturbios_eletroliticos.append("Hipocalemia")
    elif K > 6.0:
        disturbios_eletroliticos.append("Hipercalemia grave")
    elif K > 5.0:
        disturbios_eletroliticos.append("Hipercalemia")

    if Cl < 90:
        disturbios_eletroliticos.append("Hipocloremia grave")
    elif Cl < 98:
        disturbios_eletroliticos.append("Hipocloremia")
    elif Cl > 115:
        disturbios_eletroliticos.append("Hipercloremia grave")
    elif Cl > 106:
        disturbios_eletroliticos.append("Hipercloremia")

    if lactato > 2.2:
        disturbios_eletroliticos.append("Lactato elevado: possivel acidose lática")

def avaliar_disturbio_acido_base():
    AG = Na - (Cl + HCO3)
    resultado.append(f"Anion gap: {AG:.1f} mEq/L")

    disturbios = []
    if pH < 7.35:
        if HCO3 < 22:
            disturbios.append("acidose metabolica")
        if pCO2 > 45:
            disturbios.append("acidose respiratoria")
    elif pH > 7.45:
        if HCO3 > 26:
            disturbios.append("alcalose metabolica")
        if pCO2 < 35:
            disturbios.append("alcalose respiratoria")
    else:
        if HCO3 < 22 and pCO2 < 35:
            disturbios.append("acidose metabolica")
            disturbios.append("alcalose respiratoria")
        elif HCO3 > 26 and pCO2 > 45:
            disturbios.append("alcalose metabolica")
            disturbios.append("acidose respiratoria")

    if not disturbios:
        resultado.append("Nenhuma alteracao identificada na gasometria arterial.")
        return

    if len(disturbios) == 1:
        resultado.append(f"Disturbio simples: {disturbios[0]}")
    elif len(disturbios) == 2:
        resultado.append(f"Disturbio misto: {disturbios[0]} + {disturbios[1]}")
    elif len(disturbios) == 3:
        resultado.append(f"Disturbio triplo identificado: {' + '.join(disturbios)}")

    if "metabolica" in ' '.join(disturbios):
        if "acidose" in ' '.join(disturbios):
            pCO2_esp = 1.5 * HCO3 + 8
        else:
            pCO2_esp = 0.7 * HCO3 + 21
        resultado.append(f"pCO2 esperado: {pCO2_esp:.1f} mmHg")
        if abs(pCO2 - pCO2_esp) > 5:
            resultado.append("Compensacao inadequada: considerar disturbio misto ou triplo")

    if AG > 12:
        resultado.append("AG aumentado: acidose metabolica com AG aumentado")
    elif AG < 8:
        resultado.append("AG reduzido: considerar hipoproteinemia ou erro analitico")
    else:
        resultado.append("AG normal")

if st.button("Analisar"):
    classificar_eletrolitos()
    avaliar_disturbio_acido_base()

    if disturbios_eletroliticos:
        resultado.append("Disturbios hidroeletroliticos identificados:")
        for d in disturbios_eletroliticos:
            resultado.append(f"- {d}")

    for linha in resultado:
        st.write(linha)

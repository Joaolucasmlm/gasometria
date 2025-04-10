import streamlit as st 
import os

# Caminho local para a fonte (sem necessidade de download)
FONT_PATH = os.path.join("fonts", "DejaVuSans.ttf")

if not os.path.exists(FONT_PATH):
    st.error("Arquivo de fonte DejaVuSans.ttf não encontrado na pasta 'fonts'.")
    st.stop()

st.set_page_config(page_title="Analisador Gasométrico", layout="centered")

st.title("🧪 Analisador de Gasometria e Distúrbios Ácido-Base")

# Entradas dos parâmetros laboratoriais
pH = st.number_input("pH", step=0.01, format="%.2f")
pCO2 = st.number_input("pCO₂ (mmHg)", step=0.1)
HCO3 = st.number_input("HCO₃⁻ (mEq/L)", step=0.1)
Na = st.number_input("Na⁺ (mEq/L)", step=0.1)
K = st.number_input("K⁺ (mEq/L)", step=0.1)
Cl = st.number_input("Cl⁻ (mEq/L)", step=0.1)
lactato = st.number_input("Lactato (mmol/L) [opcional]", step=0.1, format="%.1f")

resultado = []
disturbios_eletroliticos = []

# Análise de distúrbios hidroeletrolíticos
if Na < 135:
    disturbios_eletroliticos.append("Hiponatremia")
elif Na > 145:
    disturbios_eletroliticos.append("Hipernatremia")
if Na < 120:
    disturbios_eletroliticos.append("Hiponatremia grave")
if Na > 155:
    disturbios_eletroliticos.append("Hipernatremia grave")

if K < 2.5:
    disturbios_eletroliticos.append("Hipocalemia grave")
if K > 6.0:
    disturbios_eletroliticos.append("Hipercalemia grave")
if K < 3.5:
    disturbios_eletroliticos.append("Hipocalemia")
elif K > 5.0:
    disturbios_eletroliticos.append("Hipercalemia")

if Cl < 90:
    disturbios_eletroliticos.append("Hipocloremia grave")
if Cl > 115:
    disturbios_eletroliticos.append("Hipercloremia grave")
if Cl < 98:
    disturbios_eletroliticos.append("Hipocloremia")
elif Cl > 106:
    disturbios_eletroliticos.append("Hipercloremia")

if lactato > 2.2:
    disturbios_eletroliticos.append("Lactato elevado: possível acidose lática")

if st.button("Analisar"):
    st.subheader("📊 Resultado da Análise")

    dist_secundario = ""
    caracterizacao = ""

    if pH < 7.35:
        if HCO3 < 22 and pCO2 > 45:
            dist = "Distúrbio triplo: acidose metabólica + acidose respiratória com compensação inadequada"
            caracterizacao = "Três distúrbios coexistem: acidose metabólica (HCO₃⁻ < 22), acidose respiratória (pCO₂ > 45) e ausência de compensação eficaz, levando a pH < 7,35."
        elif HCO3 < 22:
            dist = "Acidose metabólica"
            if pCO2 < 35:
                dist_secundario = "com alcalose respiratória"
                caracterizacao = "Distúrbio misto com acidose metabólica e hiperventilação (alcalose respiratória)."
        elif pCO2 > 45:
            dist = "Acidose respiratória"
            if HCO3 > 26:
                dist_secundario = "com alcalose metabólica"
                caracterizacao = "Distúrbio misto com acidose respiratória e alcalose metabólica."
        else:
            dist = "Acidose não específica"
    elif pH > 7.45:
        if HCO3 > 26 and pCO2 < 35:
            dist = "Distúrbio triplo: alcalose metabólica + alcalose respiratória com compensação inadequada"
            caracterizacao = "Três distúrbios coexistem: alcalose metabólica (HCO₃⁻ > 26), alcalose respiratória (pCO₂ < 35) e falha compensatória com pH > 7,45."
        elif HCO3 > 26:
            dist = "Alcalose metabólica"
            if pCO2 > 45:
                dist_secundario = "com acidose respiratória"
                caracterizacao = "Distúrbio misto com alcalose metabólica e retenção de CO₂ (acidose respiratória)."
        elif pCO2 < 35:
            dist = "Alcalose respiratória"
            if HCO3 < 22:
                dist_secundario = "com acidose metabólica"
                caracterizacao = "Distúrbio misto com alcalose respiratória e acidose metabólica associada."
        else:
            dist = "Alcalose não específica"
    else:
        if HCO3 > 26 and pCO2 > 45:
            dist = "pH normal: distúrbio misto (alcalose metabólica + acidose respiratória)"
            caracterizacao = "Dois distúrbios contrários coexistem e se compensam, mantendo pH normal."
        elif HCO3 < 22 and pCO2 < 35:
            dist = "pH normal: distúrbio misto (acidose metabólica + alcalose respiratória)"
            caracterizacao = "Dois distúrbios opostos se equilibram, resultando em pH normal."
        else:
            dist = "pH normal: compensação adequada ou estado normal"

    # Classificação do tipo de distúrbio
    if "triplo" in dist.lower():
        tipo_disturbio = "triplo"
    elif "misto" in dist.lower():
        tipo_disturbio = "misto"
    else:
        tipo_disturbio = "simples"

    resultado.append(f"Distúrbio principal: {dist}")
    if tipo_disturbio in ["misto", "triplo"] and dist_secundario:
        resultado.append(f"Distúrbio secundário associado: {dist_secundario}")
    if caracterizacao:
        resultado.append(f"Caracterização: {caracterizacao}")

    AG = Na - (Cl + HCO3)
    resultado.append(f"Ânion gap: {AG:.1f} mEq/L")

    if AG > 12:
        resultado.append("AG aumentado: acidose metabólica com AG aumentado")
    elif AG < 8:
        resultado.append("AG reduzido: considerar hipoproteinemia ou erro analítico")
    else:
        resultado.append("AG normal")

    if "metabólica" in dist:
        if "acidose" in dist:
            pCO2_exp = 1.5 * HCO3 + 8
        else:
            pCO2_exp = 0.7 * HCO3 + 21
        resultado.append(f"pCO₂ esperado: {pCO2_exp:.1f} mmHg")
        if abs(pCO2 - pCO2_exp) > 5:
            resultado.append("Compensação inadequada: considerar distúrbio misto ou triplo")
            if pCO2 < pCO2_exp:
                dist_secundario = "com alcalose respiratória"
            elif pCO2 > pCO2_exp:
                dist_secundario = "com acidose respiratória"

    if disturbios_eletroliticos:
        resultado.append("")
        resultado.append("🔍 Distúrbios hidroeletrolíticos identificados:")
        for d in disturbios_eletroliticos:
            resultado.append(f"• {d}")

    for linha in resultado:
        st.markdown(f"<div style='background-color:#f9f9f9;color:black;padding:8px;border-left:5px solid #0a58ca;'>{linha}</div>", unsafe_allow_html=True)

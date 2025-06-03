import streamlit as st
import matplotlib.pyplot as plt
import os
import re
import json
from datetime import datetime
import pandas as pd
from urllib.parse import urlparse

st.set_page_config(page_title="Analisador de Gasometria", layout="centered")

idioma = st.sidebar.selectbox("Idioma / Language", ["Português", "English"])
modo_estudante = st.sidebar.checkbox("Modo estudante" if idioma == "Português" else "Student mode")

with open("traducao.json", encoding="utf-8") as f:
    traducoes = json.load(f)

T = traducoes[idioma]

if modo_estudante:
    st.sidebar.info("Modo estudante ativado: explicações adicionais e recursos visuais serão exibidos.")

def input_decimal(label, **kwargs):
    valor = st.text_input(label, **kwargs)
    if valor:
        valor = valor.replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            st.warning(f"Valor inválido para {label}")
    return None

# Entradas principais
pH = input_decimal(T["ph"])
pCO2 = input_decimal(T["pco2"])
HCO3 = input_decimal(T["hco3"])
Na = input_decimal(T["na"])
K = input_decimal(T["k"])
Cl = input_decimal(T["cl"])
lactato = input_decimal(T["lactato"])
albumina = input_decimal(T["albumina"])

resultado = []
disturbios_eletroliticos = []

def entradas_validas():
    return all(x is not None for x in [pH, pCO2, HCO3, Na, K, Cl])

def explicar(texto):
    if modo_estudante:
        st.info(texto)

def verificar_inconsistencias():
    erros = []
    if pH < 6.8 or pH > 7.8:
        erros.append("pH fora dos limites compatíveis com a vida.")
    if pCO2 < 10 or pCO2 > 100:
        erros.append("pCO₂ fora dos limites fisiológicos.")
    if HCO3 < 5 or HCO3 > 45:
        erros.append("HCO₃⁻ fora dos limites fisiológicos.")
    return erros

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

    if lactato and lactato > 2.2:
        disturbios_eletroliticos.append("Lactato elevado: possível acidose lática")

def avaliar_disturbio_acido_base():
    AG = Na - (Cl + HCO3)
    AG_txt = f"Anion gap: {AG:.1f} mEq/L"
    if albumina:
        AG_corr = AG + 2.5 * (4.0 - albumina)
        AG_txt += f" | Corrigido pela albumina: {AG_corr:.1f} mEq/L"
        AG = AG_corr
    resultado.append(AG_txt)
    explicar("AG = Na - (Cl + HCO3). Corrigir pela albumina melhora a acurácia do diagnóstico.")

    disturbios = []
    if pH < 7.35:
        if HCO3 < 22:
            disturbios.append("acidose metabólica")
        if pCO2 > 45:
            disturbios.append("acidose respiratória")
    elif pH > 7.45:
        if HCO3 > 26:
            disturbios.append("alcalose metabólica")
        if pCO2 < 35:
            disturbios.append("alcalose respiratória")
    else:
        if HCO3 < 22 and pCO2 < 35:
            disturbios.append("acidose metabólica")
            disturbios.append("alcalose respiratória")
        elif HCO3 > 26 and pCO2 > 45:
            disturbios.append("alcalose metabólica")
            disturbios.append("acidose respiratória")

    if not disturbios:
        resultado.append("Nenhuma alteração identificada na gasometria arterial.")
        return

    resultado.append(f"{'Distúrbio simples' if len(disturbios) == 1 else 'Distúrbio misto'}: {' + '.join(disturbios)}")

    if "metabólica" in ' '.join(disturbios):
        if "acidose" in ' '.join(disturbios):
            pCO2_esp = 1.5 * HCO3 + 8
            explicar("pCO2 esperado em acidose metabólica = 1.5 × HCO3 + 8")
        else:
            pCO2_esp = 0.7 * HCO3 + 21
            explicar("pCO2 esperado em alcalose metabólica = 0.7 × HCO3 + 21")
        resultado.append(f"pCO2 esperado: {pCO2_esp:.1f} mmHg")
        if abs(pCO2 - pCO2_esp) > 5:
            resultado.append("Compensação inadequada: considerar distúrbio misto ou triplo")
    elif "respiratória" in ' '.join(disturbios):
        delta_pco2 = abs(pCO2 - 40)
        if "acidose" in ' '.join(disturbios):
            if delta_pco2 <= 10:
                hco3_esp = 24 + 1 * delta_pco2
            else:
                hco3_esp = 24 + 3.5 * delta_pco2 / 10
            resultado.append(f"HCO3 esperado: {hco3_esp:.1f} mEq/L")
        elif "alcalose" in ' '.join(disturbios):
            if delta_pco2 <= 10:
                hco3_esp = 24 - 2 * delta_pco2 / 10
            else:
                hco3_esp = 24 - 5 * delta_pco2 / 10
            resultado.append(f"HCO3 esperado: {hco3_esp:.1f} mEq/L")

    if AG > 12:
        resultado.append("AG aumentado: acidose metabólica com AG aumentado")
    elif AG < 8:
        resultado.append("AG reduzido: considerar hipoproteinemia ou erro analítico")
    else:
        resultado.append("AG normal")

    delta_ag = AG - 12
    delta_hco3 = 24 - HCO3
    if HCO3 != 0:
        delta_ratio = delta_ag / delta_hco3
        resultado.append(f\"Delta gap: {delta_ag:.1f} | Delta-HCO3: {delta_hco3:.1f} | Delta-ratio: {delta_ratio:.2f}\")
        explicar(\"Delta ratio = (AG - 12) / (24 - HCO3). Pode sugerir distúrbio adicional.\")
        if delta_ratio < 0.4:
            resultado.append(\"Delta-ratio < 0.4: acidose hiperclorêmica pura (ex: diarreia)\")
        elif delta_ratio < 0.8:
            resultado.append(\"Delta-ratio baixo: possível acidose mista\")
        elif delta_ratio <= 2.0:
            resultado.append(\"Delta-ratio normal: AG aumentado isolado (ex: cetoacidose)\")
        else:
            resultado.append(\"Delta-ratio alto: AG aumentado + alcalose metabólica coexistente\")

    if \"acidose metabólica\" in disturbios and lactato and lactato > 4:
        resultado.append(\"Possível acidose lática (lactato > 4 mmol/L)\")
    if \"alcalose metabólica\" in disturbios and Cl < 95:
        resultado.append(\"Possível alcalose metabólica hipoclorêmica (ex: vômitos)\")
    if \"acidose respiratória\" in disturbios and HCO3 > 30 and pH < 7.35:
        resultado.append(\"Sugestivo de acidose respiratória crônica compensada (ex: DPOC)\")

    be = 0.93 * (HCO3 - 24.4) + (14.83 * (pH - 7.4))
    resultado.append(f\"Excesso de base (estimado): {be:.1f} mEq/L\")
    explicar(\"Excesso de base estimado usando fórmula de Siggaard-Andersen.\")

def grafico_acido_base():
    fig, ax = plt.subplots()
    ax.set_xlim(6.8, 7.8)
    ax.set_ylim(10, 90)
    ax.set_xlabel(\"pH\")
    ax.set_ylabel(\"pCO2 (mmHg)\")
    ax.grid(True)
    ax.axvspan(7.35, 7.45, color='green', alpha=0.1, label=\"pH normal\")
    ax.axhspan(35, 45, color='blue', alpha=0.1, label=\"pCO2 normal\")
    if pH and pCO2:
        ax.plot(pH, pCO2, 'ro', label='Paciente')
        ax.annotate(\"Paciente\", (pH, pCO2), textcoords=\"offset points\", xytext=(5,5), ha='left')
    ax.legend()
    st.subheader(T[\"grafico\"])
    st.pyplot(fig)

if st.button(T[\"botao\"]):
    if entradas_validas():
        erros_internos = verificar_inconsistencias()
        if erros_internos:
            st.error(\"🚨 Inconsistência nos dados! Verifique os valores inseridos:\")
            for erro in erros_internos:
                st.write(f\"• {erro}\")
        else:
            classificar_eletrolitos()
            avaliar_disturbio_acido_base()
            if disturbios_eletroliticos:
                resultado.append(\"Distúrbios hidroeletrolíticos identificados:\")
                for d in disturbios_eletroliticos:
                    resultado.append(f\"- {d}\")
            st.subheader(T[\"resultado\"])
            output = \"\\n\".join(resultado)
            st.text_area(\"Resultado:\", output, height=300)
            st.download_button(T[\"baixar\"], data=output, file_name=\"resultado_gasometria.txt\")
            grafico_acido_base()
    else:
        st.warning(T[\"erro\"])

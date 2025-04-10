import streamlit as st
import matplotlib.pyplot as plt
import os
import re

st.set_page_config(page_title="Analisador de Gasometria", layout="centered")

# Idioma
idioma = st.selectbox("Idioma / Language", ["Português", "English"])
modo_estudante = st.checkbox("Modo estudante" if idioma == "Português" else "Student mode")

# Traduções
T = {
    "Português": {
        "titulo": "Analisador de Gasometria e Distúrbios Ácido-Base",
        "ph": "pH",
        "pco2": "pCO2 (mmHg)",
        "hco3": "HCO3- (mEq/L)",
        "na": "Na+ (mEq/L)",
        "k": "K+ (mEq/L)",
        "cl": "Cl- (mEq/L)",
        "lactato": "Lactato (mmol/L) [opcional]",
        "albumina": "Albumina (g/dL) [opcional]",
        "botao": "Analisar",
        "resultado": "Resultado da análise",
        "baixar": "Baixar resultado como TXT",
        "erro": "Preencha todos os campos obrigatórios (pH, pCO2, HCO3, Na, K, Cl).",
        "grafico": "Gráfico ácido-base"
    },
    "English": {
        "titulo": "Arterial Blood Gas Analyzer",
        "ph": "pH",
        "pco2": "pCO2 (mmHg)",
        "hco3": "HCO3- (mEq/L)",
        "na": "Na+ (mEq/L)",
        "k": "K+ (mEq/L)",
        "cl": "Cl- (mEq/L)",
        "lactato": "Lactate (mmol/L) [optional]",
        "albumina": "Albumin (g/dL) [optional]",
        "botao": "Analyze",
        "resultado": "Analysis Result",
        "baixar": "Download result as TXT",
        "erro": "Please fill in all required fields (pH, pCO2, HCO3, Na, K, Cl).",
        "grafico": "Acid-base graph"
    }
}[idioma]


# Entrada com suporte a vírgula

def input_decimal(label, **kwargs):
    valor = st.text_input(label, **kwargs)
    if valor:
        valor = valor.replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            st.warning(f"Valor inválido para {label}")
    return None

# Entradas
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

# Validação básica
def entradas_validas():
    return all(x is not None for x in [pH, pCO2, HCO3, Na, K, Cl])

def explicar(texto):
    if modo_estudante:
        st.info(texto)

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

    if len(disturbios) == 1:
        resultado.append(f"Distúrbio simples: {disturbios[0]}")
    elif len(disturbios) == 2:
        resultado.append(f"Distúrbio misto: {disturbios[0]} + {disturbios[1]}")
    elif len(disturbios) == 3:
        resultado.append(f"Distúrbio triplo identificado: {' + '.join(disturbios)}")

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
        resultado.append(f"Delta gap: {delta_ag:.1f} | Delta-HCO3: {delta_hco3:.1f} | Delta-ratio: {delta_ratio:.2f}")
        explicar("Delta ratio = (AG - 12) / (24 - HCO3). Pode sugerir distúrbio adicional.")

    be = 0.93 * (HCO3 - 24.4) + (14.83 * (pH - 7.4))
    resultado.append(f"Excesso de base (estimado): {be:.1f} mEq/L")
    explicar("Excesso de base estimado usando fórmula de Siggaard-Andersen.")

def grafico_acido_base():
    fig, ax = plt.subplots()
    ax.set_xlim(6.8, 7.8)
    ax.set_ylim(10, 90)
    ax.set_xlabel("pH")
    ax.set_ylabel("pCO2 (mmHg)")
    ax.grid(True)
    ax.axvspan(7.35, 7.45, color='green', alpha=0.1, label="pH normal")
    ax.axhspan(35, 45, color='blue', alpha=0.1, label="pCO2 normal")
    if pH and pCO2:
        ax.plot(pH, pCO2, 'ro', label='Paciente')
        ax.annotate("Você", (pH, pCO2), textcoords="offset points", xytext=(5,5), ha='left')
    ax.legend()
    st.subheader(T["grafico"])
    st.pyplot(fig)

if st.button(T["botao"]):
    if entradas_validas():
        classificar_eletrolitos()
        avaliar_disturbio_acido_base()
        if disturbios_eletroliticos:
            resultado.append("Distúrbios hidroeletrolíticos identificados:" if idioma == "Português" else "Identified electrolyte disturbances:")
            for d in disturbios_eletroliticos:
                resultado.append(f"- {d}")
        st.subheader(T["resultado"])
        output = "\n".join(resultado)
        st.text_area("Resultado:" if idioma == "Português" else "Result:", output, height=300)
        st.download_button(T["baixar"], data=output, file_name="resultado_gasometria.txt")
        grafico_acido_base()
    else:
        st.warning(T["erro"])

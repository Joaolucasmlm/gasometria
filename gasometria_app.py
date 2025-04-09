import streamlit as st 
import base64
from fpdf import FPDF
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

# Checkboxes para contexto clínico
st.subheader("🩺 Contexto Clínico")
context_dpo = st.checkbox("DPOC")
context_vomitos = st.checkbox("Vômitos prolongados")
context_sepse = st.checkbox("Suspeita de sepse")
context_diarreia = st.checkbox("Diarreia intensa")

resultado = []

if st.button("Analisar"):
    st.subheader("📊 Resultado da Análise")
    if pH < 7.35:
        if HCO3 < 22 and pCO2 > 45:
            dist = "Distúrbio misto (provável acidose metabólica + respiratória)"
        elif HCO3 < 22:
            dist = "Acidose metabólica"
        elif pCO2 > 45:
            dist = "Acidose respiratória"
        else:
            dist = "Acidose não específica"
    elif pH > 7.45:
        if HCO3 > 26 and pCO2 < 35:
            dist = "Distúrbio misto (provável alcalose metabólica + respiratória)"
        elif HCO3 > 26:
            dist = "Alcalose metabólica"
        elif pCO2 < 35:
            dist = "Alcalose respiratória"
        else:
            dist = "Alcalose não específica"
    else:
        if HCO3 > 26 and pCO2 > 45:
            dist = "pH normal: possível distúrbio misto (alcalose metabólica + acidose respiratória)"
        elif HCO3 < 22 and pCO2 < 35:
            dist = "pH normal: possível distúrbio misto (acidose metabólica + alcalose respiratória)"
        else:
            dist = "Provável compensação ou normalidade"

    resultado.append(f"Distúrbio principal: {dist}")

    AG = Na - (Cl + HCO3)
    resultado.append(f"Ânion gap: {AG:.1f} mEq/L")

    if AG > 12:
        if HCO3 < 22:
            if lactato > 2.2:
                resultado.append("AG aumentado: possível acidose lática")
            else:
                resultado.append("AG aumentado: acidose metabólica com AG aumentado")
        else:
            resultado.append("AG discretamente elevado, mas HCO₃⁻ alto — sem acidose aparente")
    elif AG < 8:
        resultado.append("AG reduzido: possível hipoproteinemia ou erro analítico")
    else:
        resultado.append("AG normal")

    if "metabólica" in dist:
        if "acidose" in dist:
            pCO2_exp = 1.5 * HCO3 + 8
        else:
            pCO2_exp = 0.7 * HCO3 + 21
        resultado.append(f"pCO₂ esperado: {pCO2_exp:.1f} mmHg")
        if abs(pCO2 - pCO2_exp) > 5:
            resultado.append("Compensação inadequada: possível distúrbio misto")

    resultado.append("")
    resultado.append("Sugestão terapêutica:")

    if "Acidose metabólica" in dist:
        if lactato > 2.2 or context_sepse:
            resultado.append("→ Tratar causa base da acidose lática: hidratação, antibióticos, suporte hemodinâmico.")
        elif context_diarreia:
            resultado.append("→ Repor bicarbonato e líquidos se acidose grave. Tratar diarreia.")
        else:
            resultado.append("→ Considerar reposição de bicarbonato se pH < 7.1. Corrigir causas renais ou digestivas.")

    elif "Alcalose metabólica" in dist:
        if context_vomitos:
            resultado.append("→ Repor volume com SF 0,9% + KCl. Tratar causa dos vômitos.")
        else:
            resultado.append("→ Corrigir perdas, suspender diuréticos, usar SF 0,9% com KCl.")

    elif "Acidose respiratória" in dist:
        if context_dpo:
            resultado.append("→ Avaliar suporte ventilatório. Oxigenoterapia com cautela. Tratar exacerbação do DPOC.")
        else:
            resultado.append("→ Tratar causa base. Avaliar necessidade de suporte ventilatório.")

    elif "Alcalose respiratória" in dist:
        resultado.append("→ Tratar hiperventilação: dor, ansiedade, hipóxia. Orientar respiração controlada.")

    elif "mist" in dist.lower():
        resultado.append("→ Corrigir causas combinadas. Monitorar eletrólitos e gasometria seriada.")

    if K < 3.5:
        resultado.append("→ Hipocalemia: Repor potássio. Monitorar ECG.")
    elif K > 5.0:
        resultado.append("→ Hipercalemia: Dieta pobre em K⁺. Medidas de emergência se > 6.0.")

    if Cl < 98:
        resultado.append("→ Hipocloremia: Reposição com SF 0,9%. Corrigir perdas.")
    elif Cl > 106:
        resultado.append("→ Hipercloremia: Considerar troca de fluidos por soluções balanceadas.")

    if lactato > 2.2:
        resultado.append("→ Lactato elevado: Tratar causa de hipoperfusão. Hidratação e suporte circulatório.")

    for linha in resultado:
        if "→" in linha:
            st.markdown(f"<div style='background-color:#f9f9f9;color:black;padding:8px;border-left:5px solid #0a58ca;'>{linha}</div>", unsafe_allow_html=True)

        else:
            st.markdown(f"**{linha}**")

    # Gerar PDF com suporte a Unicode
    st.subheader("📄 Exportar relatório")

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, txt="Relatório Gasométrico", ln=True, align="C")
    pdf.ln()

    for linha in resultado:
        pdf.multi_cell(0, 10, txt=linha)

    pdf_output = "relatorio_gasometria.pdf"
    pdf.output(pdf_output)

    with open(pdf_output, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="relatorio_gasometria.pdf">📥 Baixar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

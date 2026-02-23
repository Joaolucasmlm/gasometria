import streamlit as st
from domain.models import BloodGasData
from core.analyzers.acid_base import AcidBaseAnalyzer

st.set_page_config(page_title="GasoScan Professional", layout="wide")
st.title("🩸 GasoScan: Clinical Engine")

with st.sidebar:
    st.header("Dados da Gasometria")
    ph = st.number_input("pH", 6.8, 7.8, 7.40, 0.01)
    pco2 = st.number_input("pCO2", 10.0, 130.0, 40.0, 0.1)
    hco3 = st.number_input("HCO3-", 5.0, 50.0, 24.0, 0.1)
    
    st.header("Eletrólitos (Opcional)")
    na = st.number_input("Sódio", value=None)
    cl = st.number_input("Cloro", value=None)
    alb = st.number_input("Albumina", value=4.5)

if st.button("Executar Análise Clínica"):
    data = BloodGasData(ph=ph, pco2=pco2, hco3=hco3, na=na, cl=cl, albumina=alb)
    result = AcidBaseAnalyzer(data).analyze()
    
    st.subheader("📋 Diagnóstico Final")
    for d in result['disorders']:
        st.error(f"**{d}**")
    
    if result['notes']:
        st.info("💡 **Notas de Interpretação:**")
        for n in result['notes']: st.write(n)

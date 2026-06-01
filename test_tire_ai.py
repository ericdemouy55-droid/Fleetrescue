import streamlit as st
import json
from ai_tire_analysis import analyser_pneu

st.set_page_config(page_title="FleetRescue - Analyse IA Pneu", layout="wide")

st.title("🛞 FleetRescue - Analyse IA pneumatique")

st.write("Charge deux photos : une du flanc du pneu, une de l'avarie.")

col1, col2 = st.columns(2)

with col1:
    photo_flanc = st.file_uploader("Photo 1 - Flanc du pneu", type=["jpg", "jpeg", "png"])

with col2:
    photo_avarie = st.file_uploader("Photo 2 - Avarie du pneu", type=["jpg", "jpeg", "png"])

if photo_flanc and photo_avarie:
    st.subheader("Aperçu des photos")
    c1, c2 = st.columns(2)
    with c1:
        st.image(photo_flanc, caption="Flanc du pneu", use_container_width=True)
    with c2:
        st.image(photo_avarie, caption="Avarie", use_container_width=True)

    if st.button("Analyser avec l'IA"):
        with st.spinner("Analyse en cours..."):
            resultat = analyser_pneu(photo_flanc, photo_avarie)

        st.success("Analyse terminée")

        st.subheader("Résultat JSON")
        st.json(resultat)

        st.subheader("Résumé superviseur")

        flanc = resultat.get("flanc", {})
        avarie = resultat.get("avarie", {})
        decision = resultat.get("decision", {})

        st.write(f"**Marque :** {flanc.get('marque', 'non visible')}")
        st.write(f"**Dimension :** {flanc.get('dimension', 'non visible')}")
        st.write(f"**Profil :** {flanc.get('profil', 'non visible')}")
        st.write(f"**Type d'avarie :** {avarie.get('type', 'non visible')}")
        st.write(f"**Gravité :** {avarie.get('gravite', 'non visible')}")
        st.write(f"**Réparation possible :** {avarie.get('reparation_possible', 'non déterminé')}")
        st.write(f"**Action recommandée :** {decision.get('action', 'à confirmer par opérateur')}")
else:
    st.info("Ajoute les deux photos pour lancer l'analyse.")

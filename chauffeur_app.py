import streamlit as st

from common import (
    init_data, creer_demande, get_demande, get_latest_demande,
    statut_confirme_cote_chauffeur, ui_safe,
    STATUT_CLOTUREE, STATUT_ANNULEE
)

try:
    from ai_tire_analysis import analyser_pneu
except Exception:
    analyser_pneu = None


st.set_page_config(
    page_title="FleetRescue Chauffeur",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 20% 0%, rgba(37,99,235,.28), transparent 32%),
        linear-gradient(160deg, #050b16 0%, #07111f 48%, #0b1220 100%) !important;
    color: #e5eefb;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 760px !important; padding-top: 1rem !important; }
h1, h2, h3, p, label, .stMarkdown { color: #e5eefb !important; }
.hero {
    padding: 22px;
    border: 1px solid rgba(148,163,184,.16);
    border-radius: 28px;
    background: linear-gradient(180deg, rgba(15,23,42,.88), rgba(15,23,42,.58));
    box-shadow: 0 24px 70px rgba(0,0,0,.32);
    margin-bottom: 18px;
}
.logo { font-size: 30px; font-weight: 950; letter-spacing: -.04em; }
.sub { color:#9fb0c8; font-size:14px; margin-top:2px; }
.mobile-card {
    background: linear-gradient(180deg, rgba(15,23,42,.88), rgba(15,23,42,.60));
    border: 1px solid rgba(148,163,184,.16);
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 18px 55px rgba(0,0,0,.25);
    margin-bottom: 16px;
}
.success-pill, .warning-pill {
    display:inline-flex; padding:7px 12px; border-radius:999px;
    font-weight:850; font-size:13px;
}
.success-pill { background:rgba(34,197,94,.14); color:#86efac; border:1px solid rgba(34,197,94,.25); }
.warning-pill { background:rgba(245,158,11,.14); color:#fcd34d; border:1px solid rgba(245,158,11,.28); }
.info-row { display:flex; justify-content:space-between; gap:14px; border-bottom:1px solid rgba(148,163,184,.10); padding:9px 0; }
.info-label { color:#94a3b8; font-weight:700; }
.info-value { color:#f8fafc; font-weight:900; text-align:right; }

.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: #f8f3e8 !important; color: #111827 !important;
    border: 1px solid #d6cfc2 !important; border-radius: 16px !important;
    font-weight: 750 !important;
}
div[data-baseweb="select"] > div {
    background-color: #f8f3e8 !important; color: #111827 !important;
    border: 1px solid #d6cfc2 !important; border-radius: 16px !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] div {
    color: #111827 !important; font-weight: 750 !important;
}
[data-testid="stNumberInput"] button {
    background-color: #f1eadc !important; color: #111827 !important;
}
.stRadio > div {
    background: rgba(248,243,232,.08) !important;
    border-radius: 16px !important; padding: 8px 12px !important;
}
.stButton>button, .stDownloadButton>button, .stLinkButton>a {
    border-radius: 18px !important;
    font-weight: 950 !important;
    min-height: 52px;
}
.stButton>button {
    background: linear-gradient(135deg, #ef4444 0%, #f97316 100%) !important;
    color:white !important;
    border:0 !important;
    box-shadow:0 16px 40px rgba(239,68,68,.28) !important;
}
.stFileUploader section {
    background-color: rgba(248,243,232,.95) !important;
    color:#111827 !important;
    border:1px dashed #d6cfc2 !important;
    border-radius:18px !important;
}
</style>
""", unsafe_allow_html=True)


def header():
    st.markdown("""
    <div class="hero">
        <div class="logo">🛡️ FleetRescue</div>
        <div class="sub">Orane Roadside Assistance • App chauffeur</div>
    </div>
    """, unsafe_allow_html=True)


def afficher_suivi(demande):
    statut = demande.get("statut", "")
    confirmed = statut_confirme_cote_chauffeur(statut)
    pill = "success-pill" if confirmed else "warning-pill"

    depanneur = ui_safe(demande.get("depanneur_nom", ""), "Dépanneur IA sollicité — en attente d’acceptation")
    if not confirmed:
        depanneur = "Dépanneur IA sollicité — en attente d’acceptation"

    eta = ui_safe(demande.get("eta_minutes", ""), "En attente")
    if confirmed and eta != "—" and "min" not in str(eta):
        eta = f"{eta} min"

    st.markdown(f"""
    <div class="mobile-card">
        <span class="{pill}">{statut}</span>
        <h2 style="margin-top:14px;">🚛 Votre dépannage</h2>
        <div class="info-row"><div class="info-label">Demande</div><div class="info-value">{ui_safe(demande.get('id'))}</div></div>
        <div class="info-row"><div class="info-label">Véhicule</div><div class="info-value">{ui_safe(demande.get('immatriculation'))}</div></div>
        <div class="info-row"><div class="info-label">Panne</div><div class="info-value">{ui_safe(demande.get('type_panne'))}</div></div>
        <div class="info-row"><div class="info-label">Dépanneur</div><div class="info-value">{depanneur}</div></div>
        <div class="info-row"><div class="info-label">ETA</div><div class="info-value">{eta}</div></div>
    </div>
    """, unsafe_allow_html=True)

    if confirmed:
        tel = ui_safe(demande.get("depanneur_telephone", ""), "")
        tracking = ui_safe(demande.get("tracking_url", ""), "")
        if tel:
            st.link_button("📞 Appeler le dépanneur", f"tel:{tel}", use_container_width=True)
        if tracking:
            st.link_button("🗺️ Voir l’itinéraire", tracking, use_container_width=True)
    else:
        st.info("Votre demande est transmise. Le dépanneur sélectionné par l’IA doit maintenant accepter la mission.")


def formulaire_demande():
    st.subheader("Créer une demande de dépannage")
    st.caption("Mode démo mobile : GPS, photos, analyse IA pneu et suivi du statut.")

    with st.form("form_demande"):
        c1, c2 = st.columns(2)
        with c1:
            client = st.text_input("Client / société", "Transport Demo")
            telephone = st.text_input("Téléphone chauffeur", "+33612345678")
            type_panne = st.selectbox("Type de panne", ["Crevaison", "Éclatement", "Valve / pression", "Permutation", "Autre"])
            lieu = st.radio("Lieu", ["Route", "Autoroute"], horizontal=True)
            longitude = st.number_input("Longitude panne", value=2.650000, format="%.6f")
        with c2:
            chauffeur = st.text_input("Nom chauffeur", "Jean Martin")
            immatriculation = st.text_input("Immatriculation", "AB-123-CD")
            dimension = st.selectbox("Dimension pneu", ["315/80 R22.5", "315/70 R22.5", "385/65 R22.5", "295/80 R22.5", "Autre / inconnue"])
            latitude = st.number_input("Latitude panne", value=49.250000, format="%.6f")
            urgence = st.selectbox("Niveau d'urgence", ["Standard", "Urgent", "Danger immédiat / voie rapide"])

        mode_paiement = st.radio("Paiement", ["Client en compte", "CB / Apple Pay"], horizontal=True)
        commentaire = st.text_area("Commentaire", "Véhicule immobilisé. Demande urgente.")
        photo_flanc = st.file_uploader("Photo flanc pneu", type=["jpg", "jpeg", "png"])
        photo_incident = st.file_uploader("Photo incident", type=["jpg", "jpeg", "png"])

        submitted = st.form_submit_button("🚨 DEMANDER UN DÉPANNAGE", use_container_width=True)

    if photo_flanc and photo_incident:
        st.markdown("### 🛞 Analyse IA pneumatique")
        p1, p2 = st.columns(2)
        with p1:
            st.image(photo_flanc, caption="Photo flanc pneu", use_column_width=True)
        with p2:
            st.image(photo_incident, caption="Photo incident", use_column_width=True)

        if analyser_pneu:
            if st.button("🔍 Analyser les photos avec IA", use_container_width=True):
                with st.spinner("Analyse IA en cours..."):
                    try:
                        resultat = analyser_pneu(photo_flanc, photo_incident)
                        st.success("Analyse terminée")
                        st.json(resultat)
                    except Exception as e:
                        st.warning(f"Analyse IA indisponible en démo : {e}")
        else:
            st.info("Module IA non détecté dans cette app démo. Le flux de dépannage reste fonctionnel.")

    if submitted:
        demande_id = creer_demande({
            "client": client, "chauffeur": chauffeur, "telephone_chauffeur": telephone,
            "immatriculation": immatriculation, "latitude": latitude, "longitude": longitude,
            "type_panne": type_panne, "lieu": lieu, "dimension": dimension, "urgence": urgence,
            "mode_paiement": mode_paiement, "commentaire": commentaire,
            "photo_1": photo_flanc.name if photo_flanc else "",
            "photo_2": photo_incident.name if photo_incident else "",
        })
        st.session_state["chauffeur_demande_id"] = demande_id
        st.success(f"Demande créée : {demande_id}")
        st.rerun()


init_data()
header()

selected_id = st.session_state.get("chauffeur_demande_id", "")
demande = get_demande(selected_id) if selected_id else None

if demande and demande.get("statut") not in [STATUT_CLOTUREE, STATUT_ANNULEE]:
    afficher_suivi(demande)
    a, b = st.columns(2)
    if a.button("🔄 Rafraîchir", use_container_width=True):
        st.rerun()
    if b.button("➕ Nouvelle demande", use_container_width=True):
        st.session_state["chauffeur_demande_id"] = ""
        st.rerun()
    st.divider()
elif get_latest_demande():
    with st.expander("Reprendre la dernière demande de démo"):
        latest = get_latest_demande()
        st.write(f"**{latest['id']}** — {latest['immatriculation']} — {latest['statut']}")
        if st.button("Reprendre ce suivi", use_container_width=True):
            st.session_state["chauffeur_demande_id"] = latest["id"]
            st.rerun()

formulaire_demande()

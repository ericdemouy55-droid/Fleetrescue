import streamlit as st

from common import (
    init_data, load_csv, DEMANDES_FILE,
    get_active_tentative, get_tentatives, accepter_tentative, passer_au_suivant,
    update_demande_status, generate_google_maps_link, ui_safe, to_bool,
    STATUT_PROPOSEE, STATUT_ACCEPTEE, STATUT_EN_ROUTE, STATUT_SUR_PLACE,
    STATUT_CLOTUREE, STATUT_MANUEL
)


st.set_page_config(
    page_title="FleetRescue Dépanneur",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 15% 0%, rgba(37,99,235,.30), transparent 35%),
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
    background: linear-gradient(180deg, rgba(15,23,42,.90), rgba(15,23,42,.62));
    box-shadow: 0 24px 70px rgba(0,0,0,.32);
    margin-bottom: 18px;
}
.logo { font-size: 30px; font-weight: 950; letter-spacing: -.04em; }
.sub { color:#9fb0c8; font-size:14px; margin-top:2px; }
.card {
    background: linear-gradient(180deg, rgba(15,23,42,.90), rgba(15,23,42,.62));
    border: 1px solid rgba(148,163,184,.16);
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 18px 55px rgba(0,0,0,.25);
    margin-bottom: 16px;
}
.urgent, .blue, .green {
    display:inline-flex; padding:7px 12px; border-radius:999px;
    font-weight:850; font-size:13px;
}
.urgent { background:rgba(239,68,68,.14); color:#fca5a5; border:1px solid rgba(239,68,68,.28); }
.blue { background:rgba(37,99,235,.16); color:#93c5fd; border:1px solid rgba(59,130,246,.28); }
.green { background:rgba(34,197,94,.14); color:#86efac; border:1px solid rgba(34,197,94,.25); }
.row { display:flex; justify-content:space-between; gap:14px; border-bottom:1px solid rgba(148,163,184,.10); padding:10px 0; }
.label { color:#94a3b8; font-weight:700; }
.value { color:#f8fafc; font-weight:900; text-align:right; }
.metric-grid { display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-top:12px; }
.metric { background:rgba(2,6,23,.34); border:1px solid rgba(148,163,184,.12); border-radius:16px; padding:12px; }
.metric small { color:#94a3b8; font-weight:800; font-size:11px; text-transform:uppercase; }
.metric b { display:block; color:white; font-size:19px; margin-top:4px; }
.stButton>button, .stLinkButton>a {
    border-radius: 18px !important;
    font-weight: 950 !important;
    min-height: 54px;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%) !important;
}
</style>
""", unsafe_allow_html=True)


def header():
    st.markdown("""
    <div class="hero">
        <div class="logo">🛡️ FleetRescue</div>
        <div class="sub">Orane Roadside Assistance • App dépanneur</div>
    </div>
    """, unsafe_allow_html=True)


def mission_card(demande, active):
    statut = ui_safe(demande.get("statut"))
    urgence = ui_safe(demande.get("urgence"))
    depanneur = ui_safe(demande.get("depanneur_nom"))

    if active:
        depanneur = ui_safe(active.get("depanneur_nom"), depanneur)
        distance = ui_safe(active.get("distance_km"), ui_safe(demande.get("distance_km")))
        stock_ok = active.get("stock_disponible", False)
        score = ui_safe(active.get("score_ia"), "—")
        decision = ui_safe(active.get("decision_ia"), "—")
    else:
        distance = ui_safe(demande.get("distance_km"))
        stock_ok = demande.get("stock_disponible", False)
        score = ui_safe(demande.get("score_ia"), "—")
        decision = ui_safe(demande.get("decision_ia"), "—")

    stock_label = "Oui" if to_bool(stock_ok) else "Non confirmé"
    eta = ui_safe(demande.get("eta_minutes"), "—")
    if eta != "—" and "min" not in eta:
        eta = f"{eta} min"

    st.markdown(f"""
    <div class="card">
        <span class="urgent">⚠️ {urgence}</span>
        <span class="blue" style="float:right;">{statut}</span>
        <h2 style="margin-top:18px;">{ui_safe(demande.get('id'))}</h2>

        <div class="row"><div class="label">Client</div><div class="value">{ui_safe(demande.get('client'))}</div></div>
        <div class="row"><div class="label">Chauffeur</div><div class="value">{ui_safe(demande.get('chauffeur'))}</div></div>
        <div class="row"><div class="label">Véhicule</div><div class="value">{ui_safe(demande.get('immatriculation'))}</div></div>
        <div class="row"><div class="label">Panne</div><div class="value">{ui_safe(demande.get('type_panne'))}</div></div>
        <div class="row"><div class="label">Dimension</div><div class="value">{ui_safe(demande.get('dimension'))}</div></div>
        <div class="row"><div class="label">Dépanneur sélectionné</div><div class="value">{depanneur}</div></div>

        <div class="metric-grid">
            <div class="metric"><small>Distance</small><b>{distance} km</b></div>
            <div class="metric"><small>ETA</small><b>{eta}</b></div>
            <div class="metric"><small>Stock</small><b>{stock_label}</b></div>
            <div class="metric"><small>Score IA</small><b>{score}</b></div>
        </div>
        <br>
        <span class="green">🧠 {decision}</span>
    </div>
    """, unsafe_allow_html=True)

    maps = generate_google_maps_link(demande.get("latitude", ""), demande.get("longitude", ""))
    st.link_button("🗺️ Ouvrir le lieu de panne", maps, use_container_width=True)


def app():
    init_data()
    header()

    demandes = load_csv(DEMANDES_FILE)
    if demandes.empty:
        st.info("Aucune mission disponible. Crée une demande depuis l'app chauffeur.")
        return

    statuts = [STATUT_PROPOSEE, STATUT_ACCEPTEE, STATUT_EN_ROUTE, STATUT_SUR_PLACE, STATUT_MANUEL]
    missions = demandes[demandes["statut"].isin(statuts)].copy()

    if missions.empty:
        st.success("Aucune mission active côté dépanneur.")
        with st.expander("Voir les dernières demandes"):
            st.dataframe(demandes.sort_values("date_creation", ascending=False).head(10), use_container_width=True, hide_index=True)
        return

    missions = missions.sort_values("date_creation", ascending=False)
    mission_id = st.selectbox(
        "Mission",
        missions["id"].tolist(),
        format_func=lambda x: f"{x} — {missions[missions['id'] == x].iloc[0]['immatriculation']} — {missions[missions['id'] == x].iloc[0]['statut']}"
    )

    demande = missions[missions["id"] == mission_id].iloc[0].to_dict()
    active = get_active_tentative(mission_id)
    mission_card(demande, active)

    statut = demande.get("statut", "")

    if statut == STATUT_PROPOSEE:
        a, b = st.columns(2)
        if a.button("✅ Accepter la mission", type="primary", use_container_width=True):
            accepter_tentative(mission_id)
            st.rerun()
        if b.button("❌ Refuser / indisponible", use_container_width=True):
            passer_au_suivant(mission_id)
            st.rerun()
    elif statut == STATUT_ACCEPTEE:
        if st.button("🚚 Je pars / En route", type="primary", use_container_width=True):
            update_demande_status(mission_id, STATUT_EN_ROUTE)
            st.rerun()
    elif statut == STATUT_EN_ROUTE:
        if st.button("📍 Je suis sur place", type="primary", use_container_width=True):
            update_demande_status(mission_id, STATUT_SUR_PLACE)
            st.rerun()
    elif statut == STATUT_SUR_PLACE:
        if st.button("🏁 Intervention terminée", type="primary", use_container_width=True):
            update_demande_status(mission_id, STATUT_CLOTUREE)
            st.rerun()
    elif statut == STATUT_MANUEL:
        st.warning("Cette mission est en traitement manuel. L'opérateur doit intervenir.")

    st.markdown("### Étapes de la mission")
    progress = {
        STATUT_PROPOSEE: 20,
        STATUT_ACCEPTEE: 40,
        STATUT_EN_ROUTE: 65,
        STATUT_SUR_PLACE: 85,
        STATUT_CLOTUREE: 100,
    }.get(statut, 10)
    st.progress(progress)

    with st.expander("Voir la cascade IA"):
        st.dataframe(get_tentatives(mission_id), use_container_width=True, hide_index=True)


app()

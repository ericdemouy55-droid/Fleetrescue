import math
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DEPANNEURS_FILE = DATA_DIR / "depanneurs_demo.csv"
DEMANDES_FILE = DATA_DIR / "demandes_demo.csv"
TENTATIVES_FILE = DATA_DIR / "tentatives_demo.csv"
STOCKS_FILE = DATA_DIR / "stocks_demo.csv"

STATUT_PROPOSEE = "Mission proposée au dépanneur"
STATUT_ACCEPTEE = "Accepté par dépanneur"
STATUT_EN_ROUTE = "Dépanneur en route"
STATUT_SUR_PLACE = "Dépanneur sur place"
STATUT_CLOTUREE = "Clôturé"
STATUT_MANUEL = "A traiter manuellement"
STATUT_ANNULEE = "Annulé"

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_csv(path):
    if not Path(path).exists():
        return pd.DataFrame()
    return pd.read_csv(path)

def save_csv(df, path):
    Path(path).parent.mkdir(exist_ok=True)
    df.to_csv(path, index=False)

def to_bool(value):
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in ["true", "1", "yes", "oui", "vrai"]

def ui_safe(value, default="—"):
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    value = str(value).strip()
    if value == "" or value.lower() in ["nan", "none", "null"]:
        return default
    return value

def distance_km(lat1, lon1, lat2, lon2):
    r = 6371
    p1 = math.radians(float(lat1))
    p2 = math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def normalize_dimension(value):
    return str(value).upper().replace(" ", "").strip()

def generate_google_maps_link(latitude, longitude):
    return f"https://www.google.com/maps?q={latitude},{longitude}"

def generate_google_maps_directions_link(origin_lat, origin_lon, dest_lat, dest_lon):
    return f"https://www.google.com/maps/dir/{origin_lat},{origin_lon}/{dest_lat},{dest_lon}"

def estimate_eta_minutes(distance_value, average_speed_kmh=60):
    try:
        distance = float(distance_value)
        return max(5, int(round((distance / average_speed_kmh) * 60)))
    except Exception:
        return ""

def init_data():
    if not DEPANNEURS_FILE.exists():
        pd.DataFrame([
            ["D001", "BestDrive Roissy", "Roissy-en-France", 49.0040, 2.5170, "+33600000001", 90, True, True, True, True, 4.7],
            ["D002", "BestDrive Compiègne", "Compiègne", 49.4179, 2.8261, "+33600000002", 100, True, True, True, True, 4.8],
            ["D003", "BestDrive Lille", "Lille", 50.6292, 3.0573, "+33600000003", 120, True, True, True, True, 4.5],
            ["D004", "BestDrive Amiens", "Amiens", 49.8941, 2.2958, "+33600000004", 100, True, True, True, True, 4.3],
            ["D005", "BestDrive Rouen", "Rouen", 49.4431, 1.0993, "+33600000005", 100, True, True, True, True, 4.2],
            ["D006", "BestDrive Paris Nord", "Saint-Denis", 48.9362, 2.3574, "+33600000006", 80, True, True, True, False, 4.1],
            ["D007", "BestDrive Reims", "Reims", 49.2583, 4.0317, "+33600000007", 110, True, True, True, True, 4.6],
        ], columns=[
            "id", "nom", "ville", "latitude", "longitude", "telephone", "zone_km",
            "route", "autoroute", "pl", "disponible", "score"
        ]).to_csv(DEPANNEURS_FILE, index=False)

    if not STOCKS_FILE.exists():
        pd.DataFrame([
            ["D001", "315/80 R22.5", "Continental", "Conti Hybrid HS3", 4, now_str()],
            ["D002", "315/80 R22.5", "Continental", "Conti Hybrid HD3", 6, now_str()],
            ["D002", "295/80 R22.5", "Uniroyal", "FH40", 3, now_str()],
            ["D003", "315/70 R22.5", "Continental", "Conti EcoRegional HS3", 5, now_str()],
            ["D003", "385/65 R22.5", "Continental", "Conti Hybrid HT3", 2, now_str()],
            ["D004", "315/80 R22.5", "Barum", "BF200R", 1, now_str()],
            ["D005", "315/80 R22.5", "Continental", "Conti Hybrid HS3", 2, now_str()],
            ["D007", "315/80 R22.5", "Continental", "Conti Hybrid HD3", 4, now_str()],
        ], columns=["depanneur_id", "dimension", "marque", "profil", "quantite", "last_update"]).to_csv(STOCKS_FILE, index=False)

    if not DEMANDES_FILE.exists():
        pd.DataFrame(columns=[
            "id", "date_creation", "client", "chauffeur", "telephone_chauffeur",
            "immatriculation", "latitude", "longitude", "type_panne", "lieu",
            "dimension", "urgence", "mode_paiement", "commentaire", "photo_1", "photo_2",
            "statut", "depanneur_nom", "depanneur_telephone", "depanneur_latitude",
            "depanneur_longitude", "distance_km", "eta_minutes", "tracking_url",
            "date_prise_en_charge", "date_cloture", "stock_disponible", "stock_quantite",
            "stock_marque", "stock_profil", "score_ia", "decision_ia", "date_mise_a_jour_statut"
        ]).to_csv(DEMANDES_FILE, index=False)

    if not TENTATIVES_FILE.exists():
        pd.DataFrame(columns=[
            "id", "demande_id", "rang", "depanneur_id", "depanneur_nom", "depanneur_telephone",
            "depanneur_latitude", "depanneur_longitude", "distance_km", "canal", "statut",
            "date_tentative", "stock_disponible", "stock_quantite", "stock_marque",
            "stock_profil", "score_ia", "decision_ia"
        ]).to_csv(TENTATIVES_FILE, index=False)

def get_stock_for_depanneur(depanneur_id, dimension):
    stocks = load_csv(STOCKS_FILE)
    if stocks.empty or not dimension or dimension == "Autre / inconnue":
        return {"available": False, "quantity": 0, "brand": "", "profile": ""}
    dim_norm = normalize_dimension(dimension)
    stocks = stocks.copy()
    stocks["dimension_norm"] = stocks["dimension"].apply(normalize_dimension)
    rows = stocks[(stocks["depanneur_id"] == depanneur_id) & (stocks["dimension_norm"] == dim_norm)]
    if rows.empty:
        return {"available": False, "quantity": 0, "brand": "", "profile": ""}
    row = rows.sort_values("quantite", ascending=False).iloc[0]
    quantity = int(row.get("quantite", 0))
    return {
        "available": quantity > 0,
        "quantity": quantity,
        "brand": row.get("marque", ""),
        "profile": row.get("profil", ""),
    }

def scorer_depanneur(depanneur, demande, distance_value, stock_info):
    score = 100.0 - float(distance_value) * 1.2
    if stock_info["available"]:
        score += 45 + min(int(stock_info["quantity"]), 6) * 2
    else:
        score -= 70
    if demande.get("urgence") == "Danger immédiat / voie rapide":
        score += 20 if to_bool(depanneur.get("autoroute", False)) else -80
    elif demande.get("urgence") == "Urgent":
        score += 10
    score += float(depanneur.get("score", 0)) * 8
    score += 20 if to_bool(depanneur.get("disponible", False)) else -200
    return round(score, 1)

def trouver_depanneurs(demande):
    depanneurs = load_csv(DEPANNEURS_FILE)
    rows = []
    for _, d in depanneurs.iterrows():
        if not to_bool(d.get("disponible", False)) or not to_bool(d.get("pl", False)):
            continue
        if demande["lieu"] == "Autoroute" and not to_bool(d.get("autoroute", False)):
            continue
        if demande["lieu"] == "Route" and not to_bool(d.get("route", False)):
            continue

        dist = distance_km(demande["latitude"], demande["longitude"], d["latitude"], d["longitude"])
        if dist <= float(d["zone_km"]):
            row = d.to_dict()
            row["distance_km"] = round(dist, 1)
            stock = get_stock_for_depanneur(row["id"], demande.get("dimension", ""))
            row["stock_disponible"] = stock["available"]
            row["stock_quantite"] = stock["quantity"]
            row["stock_marque"] = stock["brand"]
            row["stock_profil"] = stock["profile"]
            row["score_ia"] = scorer_depanneur(row, demande, row["distance_km"], stock)
            row["decision_ia"] = "Recommandé : stock disponible" if stock["available"] else "Dégradé : stock non confirmé"
            rows.append(row)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(sorted(rows, key=lambda x: (-float(x["score_ia"]), x["distance_km"])))

def creer_tentatives(demande_id, candidats):
    tentatives = load_csv(TENTATIVES_FILE)
    new_rows = []
    for rang, (_, d) in enumerate(candidats.head(5).iterrows(), start=1):
        new_rows.append({
            "id": str(uuid.uuid4())[:8],
            "demande_id": demande_id,
            "rang": rang,
            "depanneur_id": d["id"],
            "depanneur_nom": d["nom"],
            "depanneur_telephone": d.get("telephone", ""),
            "depanneur_latitude": d.get("latitude", ""),
            "depanneur_longitude": d.get("longitude", ""),
            "distance_km": d.get("distance_km", ""),
            "canal": "App dépanneur + SMS démo",
            "statut": "En attente" if rang == 1 else "En file",
            "date_tentative": now_str(),
            "stock_disponible": d.get("stock_disponible", False),
            "stock_quantite": d.get("stock_quantite", 0),
            "stock_marque": d.get("stock_marque", ""),
            "stock_profil": d.get("stock_profil", ""),
            "score_ia": d.get("score_ia", 0),
            "decision_ia": d.get("decision_ia", ""),
        })
    save_csv(pd.concat([tentatives, pd.DataFrame(new_rows)], ignore_index=True), TENTATIVES_FILE)

def creer_demande(data):
    demandes = load_csv(DEMANDES_FILE)
    demande_id = "REQ-" + str(uuid.uuid4())[:8].upper()
    demande = {
        "id": demande_id, "date_creation": now_str(),
        "client": data["client"], "chauffeur": data["chauffeur"],
        "telephone_chauffeur": data["telephone_chauffeur"],
        "immatriculation": data["immatriculation"],
        "latitude": data["latitude"], "longitude": data["longitude"],
        "type_panne": data["type_panne"], "lieu": data["lieu"],
        "dimension": data["dimension"], "urgence": data["urgence"],
        "mode_paiement": data["mode_paiement"], "commentaire": data["commentaire"],
        "photo_1": data.get("photo_1", ""), "photo_2": data.get("photo_2", ""),
        "statut": "Recherche dépanneur",
        "depanneur_nom": "", "depanneur_telephone": "", "depanneur_latitude": "",
        "depanneur_longitude": "", "distance_km": "", "eta_minutes": "",
        "tracking_url": "", "date_prise_en_charge": "", "date_cloture": "",
        "stock_disponible": False, "stock_quantite": 0, "stock_marque": "",
        "stock_profil": "", "score_ia": 0, "decision_ia": "",
        "date_mise_a_jour_statut": now_str(),
    }
    candidats = trouver_depanneurs(demande)
    if candidats.empty:
        demande["statut"] = STATUT_MANUEL
    else:
        best = candidats.iloc[0].to_dict()
        demande["statut"] = STATUT_PROPOSEE
        demande["depanneur_nom"] = best.get("nom", "")
        demande["depanneur_telephone"] = best.get("telephone", "")
        demande["depanneur_latitude"] = best.get("latitude", "")
        demande["depanneur_longitude"] = best.get("longitude", "")
        demande["distance_km"] = best.get("distance_km", "")
        demande["eta_minutes"] = estimate_eta_minutes(best.get("distance_km", ""))
        demande["tracking_url"] = generate_google_maps_directions_link(
            best.get("latitude", ""), best.get("longitude", ""), demande["latitude"], demande["longitude"]
        )
        for col in ["stock_disponible", "stock_quantite", "stock_marque", "stock_profil", "score_ia", "decision_ia"]:
            demande[col] = best.get(col, demande.get(col, ""))
        creer_tentatives(demande_id, candidats)
    save_csv(pd.concat([demandes, pd.DataFrame([demande])], ignore_index=True), DEMANDES_FILE)
    return demande_id

def get_demande(demande_id):
    demandes = load_csv(DEMANDES_FILE)
    if demandes.empty:
        return None
    rows = demandes[demandes["id"] == demande_id]
    return None if rows.empty else rows.iloc[0].to_dict()

def get_latest_demande():
    demandes = load_csv(DEMANDES_FILE)
    if demandes.empty:
        return None
    return demandes.sort_values("date_creation", ascending=False).iloc[0].to_dict()

def get_active_tentative(demande_id):
    tentatives = load_csv(TENTATIVES_FILE)
    if tentatives.empty:
        return None
    rows = tentatives[(tentatives["demande_id"] == demande_id) & (tentatives["statut"] == "En attente")]
    return None if rows.empty else rows.sort_values("rang").iloc[0].to_dict()

def get_tentatives(demande_id):
    tentatives = load_csv(TENTATIVES_FILE)
    if tentatives.empty:
        return pd.DataFrame()
    return tentatives[tentatives["demande_id"] == demande_id].sort_values("rang")

def accepter_tentative(demande_id):
    tentatives = load_csv(TENTATIVES_FILE)
    demandes = load_csv(DEMANDES_FILE)
    active = tentatives[(tentatives.demande_id == demande_id) & (tentatives.statut == "En attente")].index
    d_idx = demandes[demandes.id == demande_id].index
    if len(active) == 0 or len(d_idx) == 0:
        return False
    idx, d_idx = active[0], d_idx[0]
    tentatives.loc[idx, "statut"] = "Accepté"
    tentatives.loc[(tentatives.demande_id == demande_id) & (tentatives.statut == "En file"), "statut"] = "Annulé"
    dist = tentatives.loc[idx, "distance_km"]
    dep_lat = tentatives.loc[idx, "depanneur_latitude"]
    dep_lon = tentatives.loc[idx, "depanneur_longitude"]
    demandes.loc[d_idx, "statut"] = STATUT_ACCEPTEE
    for col in ["depanneur_nom", "depanneur_telephone", "depanneur_latitude", "depanneur_longitude",
                "distance_km", "stock_disponible", "stock_quantite", "stock_marque", "stock_profil",
                "score_ia", "decision_ia"]:
        demandes.loc[d_idx, col] = tentatives.loc[idx, col]
    demandes.loc[d_idx, "eta_minutes"] = estimate_eta_minutes(dist)
    demandes.loc[d_idx, "tracking_url"] = generate_google_maps_directions_link(
        dep_lat, dep_lon, demandes.loc[d_idx, "latitude"], demandes.loc[d_idx, "longitude"]
    )
    demandes.loc[d_idx, "date_prise_en_charge"] = now_str()
    demandes.loc[d_idx, "date_mise_a_jour_statut"] = now_str()
    save_csv(tentatives, TENTATIVES_FILE)
    save_csv(demandes, DEMANDES_FILE)
    return True

def passer_au_suivant(demande_id):
    tentatives = load_csv(TENTATIVES_FILE)
    demandes = load_csv(DEMANDES_FILE)
    active = tentatives[(tentatives.demande_id == demande_id) & (tentatives.statut == "En attente")].index
    if len(active):
        tentatives.loc[active[0], "statut"] = "Refusé / indisponible"
    queued = tentatives[(tentatives.demande_id == demande_id) & (tentatives.statut == "En file")].sort_values("rang")
    d_idx = demandes[demandes.id == demande_id].index
    if len(queued) and len(d_idx):
        next_idx, d_idx = queued.index[0], d_idx[0]
        tentatives.loc[next_idx, "statut"] = "En attente"
        demandes.loc[d_idx, "statut"] = STATUT_PROPOSEE
        for col in ["depanneur_nom", "depanneur_telephone", "depanneur_latitude", "depanneur_longitude",
                    "distance_km", "stock_disponible", "stock_quantite", "stock_marque", "stock_profil",
                    "score_ia", "decision_ia"]:
            demandes.loc[d_idx, col] = tentatives.loc[next_idx, col]
        demandes.loc[d_idx, "eta_minutes"] = estimate_eta_minutes(tentatives.loc[next_idx, "distance_km"])
        demandes.loc[d_idx, "date_mise_a_jour_statut"] = now_str()
    elif len(d_idx):
        demandes.loc[d_idx[0], "statut"] = STATUT_MANUEL
        demandes.loc[d_idx[0], "date_mise_a_jour_statut"] = now_str()
    save_csv(tentatives, TENTATIVES_FILE)
    save_csv(demandes, DEMANDES_FILE)
    return True

def update_demande_status(demande_id, statut):
    demandes = load_csv(DEMANDES_FILE)
    idx = demandes[demandes.id == demande_id].index
    if len(idx) == 0:
        return False
    idx = idx[0]
    demandes.loc[idx, "statut"] = statut
    demandes.loc[idx, "date_mise_a_jour_statut"] = now_str()
    if statut == STATUT_CLOTUREE:
        demandes.loc[idx, "date_cloture"] = now_str()
    save_csv(demandes, DEMANDES_FILE)
    return True

def statut_confirme_cote_chauffeur(statut):
    return str(statut).strip() in [STATUT_ACCEPTEE, STATUT_EN_ROUTE, STATUT_SUR_PLACE, STATUT_CLOTUREE]

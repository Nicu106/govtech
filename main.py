from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import json
import os

app = FastAPI()

USERS_JSON_FILE = "users.json"
PROGRAMARI_JSON_FILE = "programari.json"

def load_users():
    if not os.path.exists(USERS_JSON_FILE):
        raise HTTPException(status_code=500, detail="User data file not found.")
    with open(USERS_JSON_FILE, "r") as f:
        return json.load(f)

def load_programari():
    if not os.path.exists(PROGRAMARI_JSON_FILE):
        raise HTTPException(status_code=500, detail="Programari data file not found.")
    with open(PROGRAMARI_JSON_FILE, "r") as f:
        return json.load(f).get("programari", [])

@app.get("/check_user")
def check_user(idnp: Optional[str] = Query(None), phone: Optional[str] = Query(None)):
    if not idnp and not phone:
        raise HTTPException(status_code=400, detail="Provide either idnp or phone")

    users = load_users()
    for user in users:
        if idnp and user["idnp"] == idnp:
            return {"exists": True, "user": user}
        if phone and user["phone"] == phone:
            return {"exists": True, "user": user}

    return {"exists": False}

INSP_JSON_FILE = "insp.json"

def load_insp_data():
    if not os.path.exists(INSP_JSON_FILE):
        raise HTTPException(status_code=500, detail="INSP data file not found.")
    with open(INSP_JSON_FILE, "r") as f:
        return json.load(f)

@app.get("/get_patient_data")
def get_patient_data(idnp: Optional[str] = Query(None), phone: Optional[str] = Query(None)):
    if not idnp and not phone:
        raise HTTPException(status_code=400, detail="Provide either idnp or phone")

    users = load_users()
    user_found = None
    for user in users:
        if idnp and user["idnp"] == idnp:
            user_found = user
            break
        if phone and user["phone"] == phone:
            user_found = user
            break

    if not user_found:
        raise HTTPException(status_code=404, detail="User not found in users.json")

    insp_data = load_insp_data()
    for patient in insp_data:
        if patient["idnp"] == user_found["idnp"]:
            return {"status": "found", "data": patient}

    raise HTTPException(status_code=404, detail="Patient data not found in insp.json")

DOCTORS_JSON_FILE = "sirius.json"

def load_doctors():
    if not os.path.exists(DOCTORS_JSON_FILE):
        raise HTTPException(status_code=500, detail="Doctor data file not found.")
    with open(DOCTORS_JSON_FILE, "r") as f:
        return json.load(f).get("medici", [])

@app.get("/recommend_doctors")
def recommend_doctors(specialitate: str = Query(...), tip_institutie: Optional[str] = Query(None)):
    doctors = load_doctors()
    filtered = [
        doc for doc in doctors
        if specialitate.lower() in doc["specialitate"].lower()
        and (tip_institutie is None or tip_institutie.lower() in doc["tip_institutie"].lower())
    ]
    return {"recommended": filtered}

RECIPE_JSON_FILE = "e-reteta.json"

def load_retete():
    if not os.path.exists(RECIPE_JSON_FILE):
        raise HTTPException(status_code=500, detail="Reteta data file not found.")
    with open(RECIPE_JSON_FILE, "r") as f:
        return json.load(f).get("retete", [])

@app.get("/get_reteta_by_id")
def get_reteta_by_id(reteta_id: int = Query(...)):
    retete = load_retete()
    for reteta in retete:
        if reteta["id"] == reteta_id:
            return {"reteta": reteta}
    raise HTTPException(status_code=404, detail="Reteta not found")

@app.get("/search_programari")
def search_programari(id: Optional[int] = Query(None), ora: Optional[str] = Query(None)):
    programari = load_programari()

    if id is not None:
        for p in programari:
            if p["id"] == id:
                return {"match": p}
        raise HTTPException(status_code=404, detail="Programare not found with given ID")

    if ora:
        results = [p for p in programari if ora in p.get("intervale", [])]
        return {"matches": results}

    raise HTTPException(status_code=400, detail="Provide either id or ora to search.")

@app.get("/check_orar_libertate")
def check_orar_libertate(id: int = Query(...), ora: str = Query(...)):
    programari = load_programari()

    for p in programari:
        if p["id"] == id:
            if ora in p.get("intervale", []):
                return {"id": id, "ora": ora, "disponibil": True}
            else:
                return {"id": id, "ora": ora, "disponibil": False}

    raise HTTPException(status_code=404, detail="Programare not found with given ID")

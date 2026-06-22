"""
Copa Mundial de la FIFA 2026 - Aplicación Web
Ejecutar: python app.py
Luego abrir: http://localhost:5000
"""
import json
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template, request

from scraper import load_matches, run_scrape, MATCHES_FILE

app = Flask(__name__)

# Última actualización en memoria
_last_update: str = ""
_scraping: bool = False


def _refresh_bg():
    global _last_update, _scraping
    _scraping = True
    try:
        run_scrape()
        _last_update = datetime.now().strftime("%d/%m/%Y %H:%M")
    finally:
        _scraping = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/matches")
def api_matches():
    matches = load_matches()
    return jsonify(matches)


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    global _scraping
    if _scraping:
        return jsonify({"status": "already_running"})
    t = threading.Thread(target=_refresh_bg, daemon=True)
    t.start()
    return jsonify({"status": "started"})


@app.route("/api/status")
def api_status():
    matches = load_matches()
    return jsonify({
        "total": len(matches),
        "last_update": _last_update or (
            datetime.fromtimestamp(MATCHES_FILE.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
            if MATCHES_FILE.exists() else "nunca"
        ),
        "scraping": _scraping,
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("RAILWAY_ENVIRONMENT") is None
    # Siempre actualizar al arrancar en Railway para tener datos frescos
    print("Actualizando datos al arrancar…")
    threading.Thread(target=_refresh_bg, daemon=True).start()
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)

from flask import Flask, render_template

app = Flask(__name__)

# 🔹 Ajoute les URLs de tes graphiques ici
GRAFANA_GRAPHS = [
    {"title": "Évolution des cas", "url": "http://localhost:3000/d/YOUR_DASHBOARD_ID?orgId=1&panelId=2"},
    {"title": "Taux de mortalité", "url": "http://localhost:3000/d/YOUR_DASHBOARD_ID?orgId=1&panelId=3"},
    {"title": "Récupération vs Décès", "url": "http://localhost:3000/d/YOUR_DASHBOARD_ID?orgId=1&panelId=4"}
]

@app.route("/")
def home():
    return render_template("index.html", graphs=GRAFANA_GRAPHS)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

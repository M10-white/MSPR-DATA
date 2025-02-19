import requests
import pandas as pd
import matplotlib.pyplot as plt

# 🔥 Récupérer les données JSON de ton API
url = "http://127.0.0.1:8000/predict/?country=France&disease=covid"
response = requests.get(url)
data = response.json()

# 📌 Transformer le JSON en DataFrame
df = pd.DataFrame(data["predictions"])

# 📊 Tracer l'évolution des cas prédits
plt.figure(figsize=(10,5))
plt.plot(df["ds"], df["yhat"], marker="o", linestyle="-", label="Prédictions covid")

plt.xlabel("Date")
plt.ylabel("Nombre de cas prédits")
plt.title("Prédiction des cas de covid en France")
plt.xticks(rotation=45)
plt.legend()
plt.grid()
plt.show()

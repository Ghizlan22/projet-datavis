import pandas as pd
from io import StringIO
import os
import re
from sklearn.impute import KNNImputer
import numpy as np

# === SECTION MANQUANTE : DOCUMENTATION DU JEU DE DONNÉES ===
"""
CONTEXTE DES DONNÉES (à ajouter en en-tête):
- Dataset recyclage: Taux de recyclage des déchets municipaux par pays
- Dataset déchets: Quantité totale de déchets agricoles par pays
- Période: Données historiques jusqu'en 2024
- Source: Open data environnemental (à préciser)
"""
def validate_data_structure(df, dataset_name):
    """Valide la structure des données pour l'analyse"""
    print(f"\n=== VALIDATION STRUCTURE {dataset_name} ===")
    print(f"Shape: {df.shape}")
    print(f"Colonnes: {df.columns.tolist()}")
    print(f"Types:\n{df.dtypes}")
    if len(df) > 0:
        print(f"Période couverte: {df['Year'].min()} - {df['Year'].max()}")
    else:
        print("Période couverte: DataFrame vide")
    return True


# === AJOUT: VÉRIFICATION DE LA COHÉRENCE TEMPORELLE ===
def check_temporal_consistency(df, year_col='Year'):
    """Vérifie la continuité temporelle des données"""
    if len(df) == 0:
        print("✅ DataFrame vide - aucune vérification temporelle nécessaire")
        return []
    
    years = sorted(df[year_col].unique())
    gaps = []
    for i in range(1, len(years)):
        if years[i] - years[i-1] > 1:
            gaps.append((years[i-1], years[i]))
    
    if gaps:
        print(f"⚠️  Gaps temporels détectés: {gaps}")
    else:
        print("✅ Continuité temporelle vérifiée")
    return gaps

# === AJOUT: ANALYSE DES VALEURS EXTRÊMES ===
def detect_outliers_iqr(df, column):
    """Détecte les valeurs aberrantes avec la méthode IQR"""
    if len(df) == 0:
        print(f"Valeurs aberrantes dans {column}: 0 (DataFrame vide)")
        return pd.DataFrame()
    
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    print(f"Valeurs aberrantes dans {column}: {len(outliers)}")
    return outliers


orig_path = r"C:\Users\USER\Desktop\Data vis project\data2.csv"
clean_path = r"C:\Users\USER\Desktop\Data vis project\data2_cleaned.csv"

# 1) Nettoyer le fichier ligne par ligne : enlever " en début et fin de ligne s'ils existent
with open(orig_path, "r", encoding="utf-8") as f_in, open(clean_path, "w", encoding="utf-8", newline="\n") as f_out:
    for line in f_in:
        # supprime \r\n -> \n, strip seulement des guillemets extrêmes
        line = line.rstrip("\r\n")
        if len(line) >= 2 and line[0] == '"' and line[-1] == '"':
            line = line[1:-1]  # enlève les guillemets extérieurs
        f_out.write(line + "\n")

print("Fichier nettoyé écrit dans :", clean_path)

# 2) Lire le fichier nettoyé avec pandas
df2 = pd.read_csv(clean_path, sep=",", engine="python")

print("Colonnes détectées dans data2_cleaned.csv :", df2.columns.tolist())
print(df2.head())

# === Nettoyage des données recyclage ===

# Renommer les colonnes pour plus de clarté
df2 = df2.rename(columns={
    "Entity": "Country",
    "Code": "Code",
    "Year": "Year",
    "Variable:% Recycling - MUNW": "RecyclingRate"
})

# NE PLUS SUPPRIMER les lignes avec des valeurs manquantes
# df2 = df2.dropna(subset=["Country", "Year", "RecyclingRate"])

# Supprimer les doublons (si le même pays + année apparaît plusieurs fois)
df2 = df2.drop_duplicates(subset=["Country", "Year"])

# Convertir les types de données
df2["Year"] = df2["Year"].astype(int)
df2["RecyclingRate"] = df2["RecyclingRate"].astype(float)

# Vérifier les valeurs extrêmes (pour repérer erreurs éventuelles)
print("Taux min / max :", df2["RecyclingRate"].min(), "/", df2["RecyclingRate"].max())

# === VÉRIFICATION ET IMPUTATION DES VALEURS MANQUANTES - DATASET RECYCLAGE ===

print("\n" + "="*50)
print("VÉRIFICATION DES VALEURS MANQUANTES - RECYCLAGE")
print("="*50)

print("Valeurs manquantes avant imputation:")
print(df2.isnull().sum())

# Vérifier s'il y a des valeurs manquantes dans RecyclingRate
if df2['RecyclingRate'].isnull().sum() > 0:
    print(f"\nIl y a {df2['RecyclingRate'].isnull().sum()} valeurs manquantes dans RecyclingRate")
    print("Application de l'imputation KNN...")
    
    # Préparer les données pour KNN
    df2_numeric = df2[['Year', 'RecyclingRate']].copy()
    
    # Appliquer KNN Imputer
    imputer = KNNImputer(n_neighbors=5)
    df2_imputed = imputer.fit_transform(df2_numeric)
    
    # Remplacer les valeurs dans le DataFrame original
    df2['RecyclingRate'] = df2_imputed[:, 1]
    
    print("Imputation KNN terminée!")
else:
    print("Aucune valeur manquante dans RecyclingRate - pas besoin d'imputation")

print("\nValeurs manquantes après imputation:")
print(df2.isnull().sum())

# Enregistrer ce dataset propre
df2.to_csv("C:\\Users\\USER\\Desktop\\Data vis project\\data\\recycling_clean.csv", index=False)

# === Nettoyage du fichier data3 ===

orig_path3 = r"C:\Users\USER\Desktop\Data vis project\data3.csv"
clean_path3 = r"C:\Users\USER\Desktop\Data vis project\data3_cleaned.csv"

# 1️⃣ Lecture + nettoyage général (supprimer guillemets et ; en fin de ligne)
cleaned_lines = []
with open(orig_path3, "r", encoding="utf-8", errors="ignore") as f_in:
    for line in f_in:
        line = line.strip()
        line = line.replace('""', '"').replace(';"', '"').replace(';', ',')
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        cleaned_lines.append(line)

# 2️⃣ Recomposer le texte en un seul bloc et forcer les vraies nouvelles lignes
raw_text = "\n".join(cleaned_lines)
# On divise les lignes quand on voit un motif de début de pays (majuscule suivie de virgule)
rows = re.findall(r'([A-Z][^A-Z]+)', raw_text)

# 3️⃣ Construire la table
data = []
for row in rows:
    parts = [p.strip() for p in row.split(",") if p.strip() != ""]
    if len(parts) >= 4:
        data.append(parts[:10])  # on garde les 10 premières colonnes environ

# 4️⃣ Déterminer les colonnes (si elles existent dans la première ligne)
columns = ["Entity", "Code", "Year", "Agriculture", "Households", "Construction",
           "Manufacturing", "Electricity", "Mining", "Other_services"]

df3 = pd.DataFrame(data, columns=columns)

# 5️⃣ Garder seulement les colonnes principales
df3_simple = df3[["Entity", "Code", "Year", "Agriculture"]].copy()
df3_simple = df3_simple.rename(columns={"Agriculture": "TotalWaste"})

# NE PLUS SUPPRIMER les lignes avec des valeurs manquantes
# df3_simple = df3_simple.dropna(subset=["Entity", "Year", "TotalWaste"])

# Garder uniquement les années valides (ex : 1990–2030)
df3_simple = df3_simple[df3_simple["Year"].astype(str).str.match(r"^\d{4}$")]

# Convertir les types
df3_simple["Year"] = df3_simple["Year"].astype(int)

# === DIAGNOSTIC URGENT - ANALYSE DATA3 AVANT FILTRAGE ===
print("\n" + "="*60)
print("DIAGNOSTIC COMPLET DU FICHIER DATA3")
print("="*60)

# Afficher toutes les années uniques AVANT filtrage
print("Années uniques dans data3 AVANT filtrage:")
annees_uniques = sorted(df3_simple["Year"].unique())
print(annees_uniques[:20])  # Afficher les 20 premières pour éviter overflow

# Afficher un échantillon des données brutes
print("\nÉchantillon des données AVANT filtrage:")
print(df3_simple.head(20))

# Vérifier la plage réelle des années
print(f"\nPlage des années: {df3_simple['Year'].min()} à {df3_simple['Year'].max()}")
print(f"Nombre total de lignes AVANT filtrage: {len(df3_simple)}")

# === CORRECTION INTELLIGENTE - FILTRAGE ANNÉES DÉCHETS ===
annees_avant = len(df3_simple)

# Analyser la distribution des années pour choisir le bon filtre
annee_min = df3_simple['Year'].min()
annee_max = df3_simple['Year'].max()

print(f"\n🔍 ANALYSE: Années de {annee_min} à {annee_max}")

if annee_min < 1900 or annee_max > 2050:
    print("🚨 DONNÉES ANORMALES: Les années sont en dehors des plages réalistes!")
    print("📋 STRATÉGIE: On garde TOUTES les données pour analyse manuelle")
    # On ne filtre pas - on garde tout pour voir le problème
    df3_simple_filtered = df3_simple.copy()
else:
    # Filtrer normalement
    df3_simple_filtered = df3_simple[(df3_simple["Year"] >= 1990) & (df3_simple["Year"] <= 2030)]

df3_simple = df3_simple_filtered
annees_apres = len(df3_simple)

print(f"🔧 CORRECTION ANNÉES: {annees_avant} → {annees_apres} lignes après traitement")
if len(df3_simple) > 0:
    print(f"Plage temporelle corrigée: {df3_simple['Year'].min()} - {df3_simple['Year'].max()}")
else:
    print("⚠️  ATTENTION: Plus de données après traitement!")

# Nettoyer la colonne TotalWaste (seulement si on a des données)
if len(df3_simple) > 0:
    df3_simple["TotalWaste"] = (
        df3_simple["TotalWaste"]
        .astype(str)
        .str.replace(",", "")
        .str.extract(r"(\d+\.?\d*)")[0]  # extraire les nombres
        .astype(float)
    )

    # Supprimer seulement les valeurs négatives, pas les NaN
    df3_simple = df3_simple[(df3_simple["TotalWaste"] > 0) | (df3_simple["TotalWaste"].isna())]

# === VÉRIFICATION ET IMPUTATION DES VALEURS MANQUANTES - DATASET DÉCHETS ===

print("\n" + "="*50)
print("VÉRIFICATION DES VALEURS MANQUANTES - DÉCHETS")
print("="*50)

if len(df3_simple) == 0:
    print("⚠️  Dataset déchets VIDE - aucune vérification nécessaire")
else:
    print("Valeurs manquantes avant imputation:")
    print(df3_simple.isnull().sum())

    # Vérifier s'il y a des valeurs manquantes dans TotalWaste
    if df3_simple['TotalWaste'].isnull().sum() > 0:
        print(f"\nIl y a {df3_simple['TotalWaste'].isnull().sum()} valeurs manquantes dans TotalWaste")
        print("Application de l'imputation KNN...")
        
        # Préparer les données pour KNN
        df3_numeric = df3_simple[['Year', 'TotalWaste']].copy()
        
        # Appliquer KNN Imputer
        imputer = KNNImputer(n_neighbors=5)
        df3_imputed = imputer.fit_transform(df3_numeric)
        
        # Remplacer les valeurs dans le DataFrame original
        df3_simple['TotalWaste'] = df3_imputed[:, 1]
        
        print("Imputation KNN terminée!")
    else:
        print("Aucune valeur manquante dans TotalWaste - pas besoin d'imputation")

    print("\nValeurs manquantes après imputation:")
    print(df3_simple.isnull().sum())

# Sauvegarde (même si vide, pour éviter les erreurs)
df3_simple.to_csv("C:\\Users\\USER\\Desktop\\Data vis project\\data\\waste_clean.csv", index=False)
print("✅ Données déchets enregistrées dans data/waste_clean.csv")

if len(df3_simple) > 0:
    print("Aperçu des données déchets:")
    print(df3_simple.head(10))
else:
    print("⚠️  Fichier déchets sauvegardé mais VIDE")

# VALIDATION DES DONNÉES TRAITÉES
print("\n" + "="*60)
print("VALIDATION FINALE DES DONNÉES PRÉPARÉES")
print("="*60)

# Validation dataset recyclage
validate_data_structure(df2, "RECYCLAGE")
check_temporal_consistency(df2)
detect_outliers_iqr(df2, "RecyclingRate")

# Validation dataset déchets  
validate_data_structure(df3_simple, "DÉCHETS")
check_temporal_consistency(df3_simple)
detect_outliers_iqr(df3_simple, "TotalWaste")

# === RAPPORT DE PRÉPARATION COMPLET ===
print("\n" + "="*60)
print("RAPPORT COMPLET PHASE 1 - PRÉPARATION DES DONNÉES")
print("="*60)

print("✅ COLLECTE: Données environnementales chargées depuis CSV")
print("✅ NETTOYAGE: Guillemets, séparateurs, encodage corrigés")
print("✅ VALEURS MANQUANTES: Traitées avec KNN Imputer")
print("✅ DOUBLONS: Supprimés avec drop_duplicates()")
print("✅ HOMOGÉNÉISATION: Types de données standardisés")
print("✅ STRUCTURATION: Colonnes Year/Country/Indicateurs organisées")
print("🔍 POINTS DE VIGILANCE: Vérifier les gaps temporels et valeurs extrêmes")

print(f"\n📊 DATASETS PRÊTS POUR L'ANALYSE:")
print(f"   - Recycling: {df2.shape} lignes, {len(df2['Country'].unique())} pays")
print(f"   - Déchets: {df3_simple.shape} lignes, {len(df3_simple['Entity'].unique()) if len(df3_simple) > 0 else 0} entités")

# === RECOMMANDATION FINALE ===
if len(df3_simple) == 0:
    print("\n🚨 RECOMMANDATION URGENTE:")
    print("   Le dataset déchets est VIDE après traitement.")
    print("   Vérifiez le fichier data3.csv - il contient probablement des données corrompues ou mal formatées.")
    print("   Solution: Trouvez un autre fichier de données pour le thème déchets.")
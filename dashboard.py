import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Environnemental - Gestion des Déchets",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .section-header {
        color: #2E8B57;
        border-bottom: 2px solid #2E8B57;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class EnvironmentalDashboard:
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        """Charge les données préparées"""
        try:
           # Chemins corrigés - soit en remontant d'un niveau, soit en utilisant le bon chemin
           self.df_recycling = pd.read_csv("../data/recycling_clean.csv")
           self.df_waste = pd.read_csv("../data/waste_clean.csv")
           st.sidebar.success("✅ Données chargées avec succès")
        except FileNotFoundError:
            st.error("❌ Fichiers de données non trouvés. Vérifiez les chemins.")
            # Afficher le chemin actuel pour debug
            import os
            st.write(f"Répertoire actuel: {os.getcwd()}")
            st.write(f"Fichiers dans data/: {os.listdir('../data') if os.path.exists('../data') else 'Dossier data non trouvé'}")
            st.stop()
    
    def calculate_kpis(self):
        """Calcule les indicateurs clés"""
        # Recyclage KPIs
        latest_year_recycling = self.df_recycling['Year'].max()
        latest_recycling = self.df_recycling[self.df_recycling['Year'] == latest_year_recycling]
        
        kpis = {
            # Recyclage
            'moyenne_recyclage': latest_recycling['RecyclingRate'].mean(),
            'meilleur_pays': latest_recycling.loc[latest_recycling['RecyclingRate'].idxmax()]['Country'],
            'meilleur_taux': latest_recycling['RecyclingRate'].max(),
            'pire_pays': latest_recycling.loc[latest_recycling['RecyclingRate'].idxmin()]['Country'],
            'pire_taux': latest_recycling['RecyclingRate'].min(),
            'pays_etudies': self.df_recycling['Country'].nunique(),
            'annees_etudiees': f"{self.df_recycling['Year'].min()}-{self.df_recycling['Year'].max()}",
            
            # Déchets (si disponibles)
            'donnees_dechets': len(self.df_waste) > 0
        }
        
        if kpis['donnees_dechets']:
            latest_year_waste = self.df_waste['Year'].max()
            latest_waste = self.df_waste[self.df_waste['Year'] == latest_year_waste]
            kpis.update({
                'total_dechets': latest_waste['TotalWaste'].sum(),
                'max_dechets': latest_waste['TotalWaste'].max(),
                'pays_dechets': latest_waste.loc[latest_waste['TotalWaste'].idxmax()]['Entity']
            })
        
        return kpis
    
    def display_kpi_cards(self, kpis):
        """Affiche les cartes KPI"""
        st.markdown("### 📊 Indicateurs Clés")
        
        if kpis['donnees_dechets']:
            cols = st.columns(4)
        else:
            cols = st.columns(3)
        
        with cols[0]:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>♻️ {kpis['moyenne_recyclage']:.1f}%</h3>
                <p>Moyenne Recyclage Mondial</p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>🥇 {kpis['meilleur_taux']:.1f}%</h3>
                <p>Meilleur: {kpis['meilleur_pays']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>📈 {kpis['pays_etudies']}</h3>
                <p>Pays étudiés ({kpis['annees_etudiees']})</p>
            </div>
            """, unsafe_allow_html=True)
        
        if kpis['donnees_dechets']:
            with cols[3]:
                st.markdown(f"""
                <div class="kpi-card">
                    <h3>🗑️ {kpis['total_dechets']:,.0f}</h3>
                    <p>Total Déchets</p>
                </div>
                """, unsafe_allow_html=True)
    
    def create_recycling_visualizations(self):
        """Crée les visualisations recyclage"""
        st.markdown('<div class="section-header">📈 ANALYSE DU RECYCLAGE</div>', unsafe_allow_html=True)
        
        # Layout en colonnes
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Évolution temporelle mondiale
            df_global = self.df_recycling.groupby('Year')['RecyclingRate'].mean().reset_index()
            fig1 = px.line(df_global, x='Year', y='RecyclingRate',
                          title='Évolution du Taux de Recyclage Mondial',
                          labels={'RecyclingRate': 'Taux (%)', 'Year': 'Année'})
            fig1.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig1, use_container_width=True)
            
            # 3. Carte mondiale
            latest_year = self.df_recycling['Year'].max()
            df_latest = self.df_recycling[self.df_recycling['Year'] == latest_year]
            fig3 = px.choropleth(df_latest, locations="Code", color="RecyclingRate",
                               hover_name="Country", title="Carte Mondiale du Recyclage",
                               color_continuous_scale="Viridis")
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # 2. Top 10 pays
            latest_year = self.df_recycling['Year'].max()
            df_latest = self.df_recycling[self.df_recycling['Year'] == latest_year]
            df_top10 = df_latest.nlargest(10, 'RecyclingRate')
            fig2 = px.bar(df_top10, y='Country', x='RecyclingRate', orientation='h',
                         title='Top 10 Pays - Taux de Recyclage',
                         color='RecyclingRate')
            fig2.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
            st.plotly_chart(fig2, use_container_width=True)
            
            # 4. Répartition par catégorie
            categories = {
                'Très faible (<20%)': len(df_latest[df_latest['RecyclingRate'] < 20]),
                'Faible (20-40%)': len(df_latest[(df_latest['RecyclingRate'] >= 20) & (df_latest['RecyclingRate'] < 40)]),
                'Moyen (40-60%)': len(df_latest[(df_latest['RecyclingRate'] >= 40) & (df_latest['RecyclingRate'] < 60)]),
                'Élevé (≥60%)': len(df_latest[df_latest['RecyclingRate'] >= 60])
            }
            df_cat = pd.DataFrame({'Catégorie': list(categories.keys()), 
                                 'Nombre': list(categories.values())})
            fig4 = px.pie(df_cat, values='Nombre', names='Catégorie',
                         title='Répartition par Niveau de Recyclage')
            st.plotly_chart(fig4, use_container_width=True)
    
    def create_waste_visualizations(self, kpis):
        """Crée les visualisations déchets"""
        if not kpis['donnees_dechets']:
            st.warning("📝 Note: Aucune donnée déchets disponible. Seules les données recyclage sont affichées.")
            return
        
        st.markdown('<div class="section-header">🗑️ ANALYSE DES DÉCHETS</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 5. Évolution des déchets
            df_global_waste = self.df_waste.groupby('Year')['TotalWaste'].sum().reset_index()
            fig5 = px.line(df_global_waste, x='Year', y='TotalWaste',
                          title='Évolution des Déchets Totaux',
                          labels={'TotalWaste': 'Volume Déchets', 'Year': 'Année'})
            st.plotly_chart(fig5, use_container_width=True)
            
            # 7. Comparaison pays
            latest_year = self.df_waste['Year'].max()
            df_latest_waste = self.df_waste[self.df_waste['Year'] == latest_year]
            fig7 = px.bar(df_latest_waste, x='Entity', y='TotalWaste',
                         title='Comparaison Déchets par Pays',
                         labels={'TotalWaste': 'Volume', 'Entity': 'Pays'})
            fig7.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig7, use_container_width=True)
        
        with col2:
            # 6. Top producteurs
            latest_year = self.df_waste['Year'].max()
            df_latest_waste = self.df_waste[self.df_waste['Year'] == latest_year]
            df_top10_waste = df_latest_waste.nlargest(10, 'TotalWaste')
            fig6 = px.bar(df_top10_waste, y='Entity', x='TotalWaste', orientation='h',
                         title='Top 10 Producteurs de Déchets',
                         color='TotalWaste')
            fig6.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig6, use_container_width=True)
            
            # 8. Corrélation déchets-recyclage
            latest_year = min(self.df_recycling['Year'].max(), self.df_waste['Year'].max())
            df_recent_recycling = self.df_recycling[self.df_recycling['Year'] == latest_year]
            df_recent_waste = self.df_waste[self.df_waste['Year'] == latest_year]
            
            df_merged = pd.merge(df_recent_recycling, df_recent_waste, 
                                left_on='Country', right_on='Entity', how='inner')
            
            if len(df_merged) > 0:
                fig8 = px.scatter(df_merged, x='TotalWaste', y='RecyclingRate',
                                hover_name='Country', size='TotalWaste',
                                title='Corrélation: Déchets vs Recyclage',
                                labels={'TotalWaste': 'Volume Déchets', 
                                       'RecyclingRate': 'Taux Recyclage (%)'})
                st.plotly_chart(fig8, use_container_width=True)
    
    def create_comparative_analysis(self):
        """Analyse comparative avancée"""
        st.markdown('<div class="section-header">🔍 ANALYSE COMPARATIVE</div>', unsafe_allow_html=True)
        
        # Filtres interactifs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_year = st.slider("Sélectionnez l'année:", 
                                    min_value=int(self.df_recycling['Year'].min()),
                                    max_value=int(self.df_recycling['Year'].max()),
                                    value=int(self.df_recycling['Year'].max()))
        
        with col2:
            min_recycling = st.slider("Filtre recyclage min (%):", 0, 100, 0)
        
        with col3:
            top_n = st.selectbox("Nombre de pays à afficher:", [5, 10, 15, 20], index=1)
        
        # Données filtrées
        df_year = self.df_recycling[self.df_recycling['Year'] == selected_year]
        df_filtered = df_year[df_year['RecyclingRate'] >= min_recycling]
        
        # Visualisations comparatives
        col1, col2 = st.columns(2)
        
        with col1:
            # Top N pays pour l'année sélectionnée
            df_top = df_filtered.nlargest(top_n, 'RecyclingRate')
            fig_comp1 = px.bar(df_top, x='RecyclingRate', y='Country', orientation='h',
                              title=f'Top {top_n} Pays - {selected_year}',
                              color='RecyclingRate')
            st.plotly_chart(fig_comp1, use_container_width=True)
        
        with col2:
            # Évolution d'un pays spécifique
            selected_country = st.selectbox("Choisir un pays:", 
                                          options=sorted(self.df_recycling['Country'].unique()))
            
            df_country = self.df_recycling[self.df_recycling['Country'] == selected_country]
            fig_comp2 = px.line(df_country, x='Year', y='RecyclingRate',
                               title=f'Évolution du Recyclage - {selected_country}',
                               markers=True)
            st.plotly_chart(fig_comp2, use_container_width=True)
    
    def display_recommendations(self, kpis):
        """Affiche les recommandations"""
        st.markdown('<div class="section-header">💡 RECOMMANDATIONS</div>', unsafe_allow_html=True)
        
        recommendations = []
        
        # Recommandations basées sur les données
        if kpis['moyenne_recyclage'] < 30:
            recommendations.append("🌱 **Augmenter les efforts mondiaux** : Le taux moyen de recyclage est inférieur à 30%, indiquant un besoin crucial d'amélioration des infrastructures.")
        
        if kpis['pire_taux'] < 10:
            recommendations.append("🎯 **Cibler les pays en difficulté** : Certains pays ont des taux de recyclage très bas (<10%), nécessitant un support international.")
        
        if len(self.df_recycling[self.df_recycling['RecyclingRate'] > 60]) < 10:
            recommendations.append("⭐ **Étudier les meilleures pratiques** : Peu de pays dépassent 60% de recyclage. Analyser leurs méthodes pourrait bénéficier à tous.")
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    
    def run(self):
        """Exécute le dashboard complet"""
        # En-tête
        st.markdown('<h1 class="main-header">♻️ Dashboard Environnemental - Gestion des Déchets</h1>', unsafe_allow_html=True)
        
        # Sidebar
        st.sidebar.title("📊 Navigation")
        section = st.sidebar.radio("Sections:", 
                                 ["Tableau de Bord", "Analyse Recyclage", "Analyse Déchets", 
                                  "Analyse Comparative", "Recommandations"])
        
        # Calcul des KPI
        kpis = self.calculate_kpis()
        
        # Affichage des sections
        if section == "Tableau de Bord":
            self.display_kpi_cards(kpis)
            self.create_recycling_visualizations()
            if kpis['donnees_dechets']:
                self.create_waste_visualizations(kpis)
        
        elif section == "Analyse Recyclage":
            self.create_recycling_visualizations()
        
        elif section == "Analyse Déchets":
            self.create_waste_visualizations(kpis)
        
        elif section == "Analyse Comparative":
            self.create_comparative_analysis()
        
        elif section == "Recommandations":
            self.display_recommendations(kpis)
        
        # Footer
        # Ligne 328-335 - CORRIGÉ :
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📝 Informations")
        st.sidebar.info(f"""
        **Données disponibles:**
        - ♻️ Recyclage: {kpis['pays_etudies']} pays
        - 🗑️ Déchets: {'Oui' if kpis['donnees_dechets'] else 'Non'}
        - 📅 Période: {kpis['annees_etudiees']}
        """)

# Ligne 338-339 - CORRIGÉ :
if __name__ == "__main__":
    dashboard = EnvironmentalDashboard()
    dashboard.run()
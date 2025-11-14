import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Environnemental - Gestion des Déchets",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS adapté aux exigences académiques
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        border-bottom: 3px solid #2E8B57;
        padding-bottom: 1rem;
    }
    .section-header {
        color: #2E8B57;
        border-left: 4px solid #2E8B57;
        padding-left: 1rem;
        margin: 2rem 0 1rem 0;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .kpi-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
        border: 2px solid #2E8B57;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #2E8B57;
    }
    .metric-label {
        font-size: 1rem;
        color: #555;
    }
    .recommendation-box {
        background-color: #e8f5e8;
        border: 1px solid #2E8B57;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .critical-box {
        background-color: #ffe8e8;
        border: 1px solid #dc3545;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class EnvironmentalDashboard:
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        """Charge les données avec gestion d'erreur"""
        try:
            self.df_recycling = pd.read_csv("../data/recycling_clean.csv")
            self.df_waste = pd.read_csv("../data/waste_clean.csv")
            st.sidebar.success("✅ Données chargées avec succès")
        except FileNotFoundError:
            st.warning("📊 Génération de données de démonstration pour la présentation")
            self.generate_demo_data()
    
    def generate_demo_data(self):
        """Génère des données de démonstration réalistes"""
        np.random.seed(42)
        
        countries = ['France', 'Allemagne', 'Italie', 'Espagne', 'Royaume-Uni', 
                    'Pays-Bas', 'Belgique', 'Suisse', 'Suède', 'Norvège',
                    'Pologne', 'Autriche', 'Portugal', 'Danemark', 'Finlande']
        
        years = list(range(2000, 2021))
        recycling_data = []
        waste_data = []
        
        for country in countries:
            base_rate = np.random.normal(40, 12)
            base_waste = np.random.normal(500, 150)
            
            for year in years:
                # Données recyclage
                trend = (year - 2000) * 0.5
                noise = np.random.normal(0, 2)
                rate = max(5, min(80, base_rate + trend + noise))
                
                recycling_data.append({
                    'Country': country,
                    'Code': country[:3].upper(),
                    'Year': year,
                    'RecyclingRate': round(rate, 1)
                })
                
                # Données déchets
                waste_trend = (year - 2000) * 10
                waste_noise = np.random.normal(0, 20)
                total_waste = max(100, base_waste + waste_trend + waste_noise) * 1000000
                
                waste_data.append({
                    'Entity': country,
                    'Year': year,
                    'TotalWaste': total_waste,
                    'PlasticWaste': total_waste * 0.15,
                    'OrganicWaste': total_waste * 0.40
                })
        
        self.df_recycling = pd.DataFrame(recycling_data)
        self.df_waste = pd.DataFrame(waste_data)
    
    def calculate_kpis(self):
        """Calcule les indicateurs clés selon la Phase 2"""
        latest_year = self.df_recycling['Year'].max()
        latest_data = self.df_recycling[self.df_recycling['Year'] == latest_year]
        
        # KPI 1-5 : Indicateurs de base
        avg_recycling = latest_data['RecyclingRate'].mean()
        best_country = latest_data.loc[latest_data['RecyclingRate'].idxmax()]
        worst_country = latest_data.loc[latest_data['RecyclingRate'].idxmin()]
        
        # KPI 6-8 : Indicateurs avancés
        countries_above_50 = len(latest_data[latest_data['RecyclingRate'] > 50])
        countries_below_20 = len(latest_data[latest_data['RecyclingRate'] < 20])
        
        # Tendances
        trend_data = self.df_recycling.groupby('Year')['RecyclingRate'].mean().reset_index()
        trend_slope = np.polyfit(trend_data['Year'], trend_data['RecyclingRate'], 1)[0]
        
        kpis = {
            # KPI de performance
            'avg_recycling': avg_recycling,
            'best_country': best_country['Country'],
            'best_rate': best_country['RecyclingRate'],
            'worst_country': worst_country['Country'],
            'worst_rate': worst_country['RecyclingRate'],
            
            # KPI de distribution
            'countries_above_50': countries_above_50,
            'countries_below_20': countries_below_20,
            'total_countries': latest_data['Country'].nunique(),
            
            # KPI de tendance
            'trend_slope': trend_slope,
            
            # Métadonnées
            'latest_year': latest_year,
            'has_waste_data': len(self.df_waste) > 0
        }
        
        return kpis
    
    def display_kpi_dashboard(self, kpis):
        """Affiche le tableau de bord KPI selon Phase 3"""
        st.markdown('<div class="main-title">DASHBOARD ENVIRONNEMENTAL - GESTION DES DÉCHETS</div>', unsafe_allow_html=True)
        
        # Ligne 1 : KPI principaux
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['avg_recycling']:.1f}%</div>
                <div class="metric-label">Taux de Recyclage Moyen</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['best_rate']:.1f}%</div>
                <div class="metric-label">Meilleur: {kpis['best_country']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['worst_rate']:.1f}%</div>
                <div class="metric-label">Plus faible: {kpis['worst_country']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            trend_icon = "📈" if kpis['trend_slope'] > 0 else "📉"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{trend_icon}</div>
                <div class="metric-label">Tendance: {kpis['trend_slope']:.3f}/an</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Ligne 2 : KPI secondaires
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['countries_above_50']}</div>
                <div class="metric-label">Pays > 50% recyclage</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['countries_below_20']}</div>
                <div class="metric-label">Pays < 20% recyclage</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col7:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['total_countries']}</div>
                <div class="metric-label">Pays analysés</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col8:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['latest_year']}</div>
                <div class="metric-label">Année de référence</div>
            </div>
            """, unsafe_allow_html=True)
    
    def create_visualizations(self):
        """Crée les visualisations selon la Phase 2"""
        st.markdown('<div class="section-header">VISUALISATIONS DES DONNÉES ENVIRONNEMENTALES</div>', unsafe_allow_html=True)
        
        # Contrôles interactifs
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎛️ FILTRES INTERACTIFS")
        
        years = sorted(self.df_recycling['Year'].unique())
        selected_year = st.sidebar.selectbox(
            "Sélectionner l'année:",
            options=years,
            index=len(years)-1
        )
        
        countries = sorted(self.df_recycling['Country'].unique())
        selected_countries = st.sidebar.multiselect(
            "Sélectionner les pays:",
            options=countries,
            default=countries[:8]
        )
        
        # Onglets pour organiser les visualisations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Évolution Temporelle", 
            "📊 Comparaison par Pays", 
            "🗺️ Répartition Spatiale", 
            "🔍 Composition et Corrélations",
            "📋 Analyse des Tendances"
        ])
        
        with tab1:
            self._create_temporal_visualizations(selected_year, selected_countries)
        
        with tab2:
            self._create_comparison_visualizations(selected_year, selected_countries)
        
        with tab3:
            self._create_spatial_visualizations(selected_year)
        
        with tab4:
            self._create_composition_correlation_visualizations(selected_year)
        
        with tab5:
            self._create_trend_analysis_visualizations(selected_countries)
    
    def _create_temporal_visualizations(self, year, countries):
        """Visualisations d'évolution temporelle - Courbes et lignes"""
        st.markdown("#### ÉVOLUTION TEMPORELLE DES TAUX DE RECYCLAGE")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Évolution globale
            global_trend = self.df_recycling.groupby('Year')['RecyclingRate'].mean().reset_index()
            fig_global = px.line(global_trend, x='Year', y='RecyclingRate',
                               title='Évolution du Taux de Recyclage Mondial (Moyenne)',
                               markers=True)
            fig_global.update_layout(yaxis_title="Taux de Recyclage (%)")
            st.plotly_chart(fig_global, use_container_width=True)
        
        with col2:
            # Évolution des pays sélectionnés
            if countries:
                country_data = self.df_recycling[self.df_recycling['Country'].isin(countries)]
                fig_countries = px.line(country_data, x='Year', y='RecyclingRate', color='Country',
                                      title='Évolution par Pays Sélectionné',
                                      markers=True)
                fig_countries.update_layout(yaxis_title="Taux de Recyclage (%)")
                st.plotly_chart(fig_countries, use_container_width=True)
            else:
                st.info("Sélectionnez des pays pour voir leur évolution")
    
    def _create_comparison_visualizations(self, year, countries):
        """Visualisations de comparaison - Diagrammes en barres"""
        st.markdown("#### COMPARAISON DES PERFORMANCES PAR PAYS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 pays
            year_data = self.df_recycling[self.df_recycling['Year'] == year]
            top_countries = year_data.nlargest(10, 'RecyclingRate')
            
            fig_top = px.bar(top_countries, x='RecyclingRate', y='Country', orientation='h',
                           title=f'Top 10 Pays - Taux de Recyclage {year}',
                           color='RecyclingRate',
                           color_continuous_scale='Viridis')
            fig_top.update_layout(xaxis_title="Taux de Recyclage (%)", yaxis_title="Pays")
            st.plotly_chart(fig_top, use_container_width=True)
        
        with col2:
            # Comparaison des pays sélectionnés
            if countries:
                selected_data = year_data[year_data['Country'].isin(countries)]
                fig_comparison = px.bar(selected_data, x='Country', y='RecyclingRate',
                                      title=f'Comparaison des Pays Sélectionnés - {year}',
                                      color='RecyclingRate',
                                      color_continuous_scale='Viridis')
                fig_comparison.update_layout(yaxis_title="Taux de Recyclage (%)")
                st.plotly_chart(fig_comparison, use_container_width=True)
            else:
                st.info("Sélectionnez des pays pour les comparer")
    
    def _create_spatial_visualizations(self, year):
        """Visualisations de répartition spatiale - Carte choroplèthe"""
        st.markdown("#### RÉPARTITION SPATIALE DU RECYCLAGE")
        
        year_data = self.df_recycling[self.df_recycling['Year'] == year]
        
        fig_map = px.choropleth(year_data, 
                              locations="Code", 
                              color="RecyclingRate",
                              hover_name="Country", 
                              hover_data={"RecyclingRate": ":.1f%", "Code": False},
                              title=f"Carte Mondiale du Taux de Recyclage - {year}",
                              color_continuous_scale="Viridis",
                              range_color=[0, 80])
        
        fig_map.update_layout(geo=dict(showframe=False, showcoastlines=True))
        st.plotly_chart(fig_map, use_container_width=True)
    
    def _create_composition_correlation_visualizations(self, year):
        """Visualisations de composition et corrélations"""
        st.markdown("#### COMPOSITION ET CORRÉLATIONS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Diagramme circulaire - Répartition par performance
            year_data = self.df_recycling[self.df_recycling['Year'] == year]
            year_data['PerformanceCategory'] = pd.cut(year_data['RecyclingRate'],
                                                    bins=[0, 20, 40, 60, 80, 100],
                                                    labels=['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'])
            
            performance_dist = year_data['PerformanceCategory'].value_counts()
            fig_pie = px.pie(values=performance_dist.values, 
                           names=performance_dist.index,
                           title=f"Répartition des Pays par Niveau de Performance - {year}")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Analyse de corrélation avec données déchets (si disponibles)
            if len(self.df_waste) > 0:
                # Fusion des données
                merged_data = pd.merge(self.df_recycling, self.df_waste, 
                                     left_on=['Country', 'Year'], 
                                     right_on=['Entity', 'Year'], 
                                     how='inner')
                
                if len(merged_data) > 0:
                    latest_merged = merged_data[merged_data['Year'] == year]
                    fig_scatter = px.scatter(latest_merged, x='TotalWaste', y='RecyclingRate',
                                           hover_name='Country',
                                           title=f'Corrélation: Déchets vs Recyclage - {year}',
                                           trendline="ols")
                    fig_scatter.update_layout(xaxis_title="Volume Total de Déchets",
                                            yaxis_title="Taux de Recyclage (%)")
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.info("Données insuffisantes pour l'analyse de corrélation")
            else:
                st.info("Données déchets non disponibles pour l'analyse de corrélation")
    
    def _create_trend_analysis_visualizations(self, countries):
        """Analyse avancée des tendances"""
        st.markdown("#### ANALYSE DES TENDANCES")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Box plot par période
            self.df_recycling['Période'] = pd.cut(self.df_recycling['Year'],
                                                bins=[1999, 2005, 2010, 2015, 2020],
                                                labels=['2000-2005', '2006-2010', '2011-2015', '2016-2020'])
            
            fig_box = px.box(self.df_recycling, x='Période', y='RecyclingRate',
                           title='Distribution des Taux de Recyclage par Période')
            fig_box.update_layout(yaxis_title="Taux de Recyclage (%)")
            st.plotly_chart(fig_box, use_container_width=True)
        
        with col2:
            # Heatmap des performances
            if countries:
                pivot_data = self.df_recycling[self.df_recycling['Country'].isin(countries)]
                pivot_table = pivot_data.pivot_table(values='RecyclingRate', 
                                                   index='Country', 
                                                   columns='Year', 
                                                   aggfunc='mean')
                
                fig_heatmap = px.imshow(pivot_table, aspect="auto",
                                      title='Heatmap des Performances par Pays et Année',
                                      color_continuous_scale="Viridis")
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.info("Sélectionnez des pays pour la heatmap")
    
    def generate_interpretation_recommendations(self, kpis):
        """Phase 4 - Interprétation et recommandations"""
        st.markdown('<div class="section-header">INTERPRÉTATION ET RECOMMANDATIONS</div>', unsafe_allow_html=True)
        
        # Analyse des tendances principales
        st.markdown("### 📈 ANALYSE DES TENDANCES PRINCIPALES")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Tendances Positives")
            positive_trends = []
            
            if kpis['trend_slope'] > 0:
                positive_trends.append(f"• Tendance mondiale positive : **+{kpis['trend_slope']:.3f}%** par an")
            if kpis['countries_above_50'] > kpis['total_countries'] * 0.3:
                positive_trends.append(f"• **{kpis['countries_above_50']} pays** dépassent 50% de recyclage")
            if kpis['avg_recycling'] > 30:
                positive_trends.append(f"• Performance moyenne **au-dessus de 30%**")
            
            if positive_trends:
                for trend in positive_trends:
                    st.markdown(trend)
            else:
                st.markdown("• Aucune tendance positive significative détectée")
        
        with col2:
            st.markdown("#### Tendances Préoccupantes")
            concerns = []
            
            if kpis['countries_below_20'] > 0:
                concerns.append(f"• **{kpis['countries_below_20']} pays** en dessous de 20% de recyclage")
            if kpis['avg_recycling'] < 40:
                concerns.append(f"• Performance moyenne **inférieure aux objectifs internationaux**")
            if kpis['trend_slope'] < 0:
                concerns.append(f"• Tendance mondiale **négative**")
            
            if concerns:
                for concern in concerns:
                    st.markdown(concern)
            else:
                st.markdown("• Aucun problème majeur détecté")
        
        # Identification des zones critiques
        st.markdown("### 🚨 IDENTIFICATION DES ZONES CRITIQUES")
        
        latest_data = self.df_recycling[self.df_recycling['Year'] == kpis['latest_year']]
        critical_zones = latest_data[latest_data['RecyclingRate'] < 20]
        
        if len(critical_zones) > 0:
            st.markdown(f"**Pays avec taux de recyclage critique (< 20%) :**")
            for _, country in critical_zones.iterrows():
                st.markdown(f"• **{country['Country']}** : {country['RecyclingRate']}%")
            
            st.markdown("""
            <div class="critical-box">
                <strong>Attention requise :</strong> Ces pays nécessitent une intervention urgente 
                pour améliorer leurs infrastructures de recyclage et leurs politiques environnementales.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("✅ Aucune zone critique identifiée (tous les pays > 20%)")
        
        # Recommandations environnementales
        st.markdown("### 💡 RECOMMANDATIONS ENVIRONNEMENTALES")
        
        recommendations = []
        
        # Recommandation 1 : Performance moyenne
        if kpis['avg_recycling'] < 35:
            recommendations.append({
                "titre": "Amélioration des Infrastructures",
                "description": "Investir dans des centres de tri modernes et des systèmes de collecte sélective",
                "priorité": "Élevée"
            })
        
        # Recommandation 2 : Zones critiques
        if len(critical_zones) > 0:
            recommendations.append({
                "titre": "Programmes d'Aide Internationale",
                "description": "Développer des partenariats avec les pays en difficulté pour transférer technologies et bonnes pratiques",
                "priorité": "Élevée"
            })
        
        # Recommandation 3 : Tendances
        if kpis['trend_slope'] > 0.5:
            recommendations.append({
                "titre": "Capitaliser sur la Dynamique Positive",
                "description": "Renforcer les politiques qui fonctionnent et les étendre à d'autres régions",
                "priorité": "Moyenne"
            })
        elif kpis['trend_slope'] < 0:
            recommendations.append({
                "titre": "Revue des Politiques Environnementales",
                "description": "Analyser les causes de la baisse et ajuster les stratégies",
                "priorité": "Élevée"
            })
        
        # Recommandation générale
        recommendations.append({
            "titre": "Sensibilisation et Éducation",
            "description": "Développer des campagnes de sensibilisation sur l'importance du recyclage",
            "priorité": "Moyenne"
        })
        
        # Affichage des recommandations
        for i, rec in enumerate(recommendations, 1):
            priority_color = "🔴" if rec["priorité"] == "Élevée" else "🟡" if rec["priorité"] == "Moyenne" else "🟢"
            
            st.markdown(f"""
            <div class="recommendation-box">
                <strong>Recommandation {i} : {rec['titre']}</strong> {priority_color}<br>
                {rec['description']}<br>
                <em>Priorité : {rec['priorité']}</em>
            </div>
            """, unsafe_allow_html=True)
        
        # Synthèse pour la soutenance
        st.markdown("### 📋 SYNTHÈSE POUR SOUTENANCE")
        
        st.markdown(f"""
        **Points clés à présenter :**
        
        1. **Performance globale** : Taux de recyclage moyen de **{kpis['avg_recycling']:.1f}%**
        2. **Dynamique** : Tendance {'**positive**' if kpis['trend_slope'] > 0 else '**négative**'} 
        3. **Répartition** : **{kpis['countries_above_50']} pays performants** vs **{kpis['countries_below_20']} pays en difficulté**
        4. **Recommandations prioritaires** : {len([r for r in recommendations if r['priorité'] == 'Élevée'])} actions urgentes
        
        **Message principal** : {'Des progrès significatifs mais des efforts restent nécessaires' if kpis['avg_recycling'] < 50 else 'Bonne performance globale à maintenir'}
        """)
    
    def run(self):
        """Exécute le dashboard complet"""
        # Calcul des KPIs
        kpis = self.calculate_kpis()
        
        # Navigation principale
        st.sidebar.markdown("### 🧭 NAVIGATION PRINCIPALE")
        page = st.sidebar.radio("", 
                              ["🏠 Tableau de Bord", 
                               "📊 Visualisations", 
                               "📈 Analyse et Recommandations"])
        
        # Affichage des sections selon la navigation
        if page == "🏠 Tableau de Bord":
            self.display_kpi_dashboard(kpis)
            
        elif page == "📊 Visualisations":
            self.create_visualizations()
            
        elif page == "📈 Analyse et Recommandations":
            self.generate_interpretation_recommendations(kpis)
        
        # Footer académique
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        **USTOMB/FMI/INF/ING4/SD/DataViz**  
        **Enseignante : F.Guerroudji**  
        **Dashboard Environnemental**  
        *Phase 3 & 4 - Visualisation et Interprétation*
        """)

# Lancement de l'application
if __name__ == "__main__":
    dashboard = EnvironmentalDashboard()
    dashboard.run()

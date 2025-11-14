import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Environnemental - Gestion des Déchets",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé avancé
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .section-header {
        color: #2E8B57;
        border-bottom: 3px solid #2E8B57;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedEnvironmentalDashboard:
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        """Charge les données préparées"""
        try:
            self.df_recycling = pd.read_csv("../data/recycling_clean.csv")
            self.df_waste = pd.read_csv("../data/waste_clean.csv")
            st.sidebar.success("✅ Données chargées avec succès")
        except FileNotFoundError:
            st.error("❌ Fichiers de données non trouvés. Exécutez d'abord data_prep.py")
            st.stop()
    
    def calculate_advanced_kpis(self):
        """Calcule des indicateurs avancés avec analyses critiques"""
        latest_year = self.df_recycling['Year'].max()
        latest_data = self.df_recycling[self.df_recycling['Year'] == latest_year]
        
        # KPIs de base
        avg_recycling = latest_data['RecyclingRate'].mean()
        best_country = latest_data.loc[latest_data['RecyclingRate'].idxmax()]
        worst_country = latest_data.loc[latest_data['RecyclingRate'].idxmin()]
        
        # Analyses avancées
        countries_above_50 = len(latest_data[latest_data['RecyclingRate'] > 50])
        countries_below_20 = len(latest_data[latest_data['RecyclingRate'] < 20])
        
        # Tendances temporelles
        trend_data = self.df_recycling.groupby('Year')['RecyclingRate'].mean().reset_index()
        trend_slope = np.polyfit(trend_data['Year'], trend_data['RecyclingRate'], 1)[0]
        
        # Zones critiques
        critical_zones = latest_data[latest_data['RecyclingRate'] < 15]
        
        kpis = {
            # Indicateurs de base
            'avg_recycling': avg_recycling,
            'best_country': best_country['Country'],
            'best_rate': best_country['RecyclingRate'],
            'worst_country': worst_country['Country'],
            'worst_rate': worst_country['RecyclingRate'],
            'total_countries': latest_data['Country'].nunique(),
            
            # Analyses critiques
            'countries_above_50': countries_above_50,
            'countries_below_20': countries_below_20,
            'trend_slope': trend_slope,
            'critical_zones_count': len(critical_zones),
            'critical_zones': critical_zones,
            
            # Données déchets
            'has_waste_data': len(self.df_waste) > 0
        }
        
        if kpis['has_waste_data']:
            latest_waste = self.df_waste[self.df_waste['Year'] == self.df_waste['Year'].max()]
            kpis.update({
                'total_waste': latest_waste['TotalWaste'].sum(),
                'max_waste': latest_waste['TotalWaste'].max(),
                'top_waste_producer': latest_waste.loc[latest_waste['TotalWaste'].idxmax()]['Entity']
            })
        
        return kpis
    
    def display_advanced_kpi_dashboard(self, kpis):
        """Affiche un tableau de bord KPI avancé"""
        st.markdown('<div class="main-header">📊 TABLEAU DE BORD ENVIRONNEMENTAL AVANCÉ</div>', unsafe_allow_html=True)
        
        # Première ligne de KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['avg_recycling']:.1f}%</div>
                <div class="metric-label">♻️ Taux Recyclage Moyen</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            trend_icon = "📈" if kpis['trend_slope'] > 0 else "📉"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{trend_icon} {kpis['trend_slope']:.3f}</div>
                <div class="metric-label">Tendance Annuelle</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['countries_above_50']}</div>
                <div class="metric-label">✅ Pays > 50%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['countries_below_20']}</div>
                <div class="metric-label">⚠️ Pays < 20%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Deuxième ligne de KPIs
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['best_rate']:.1f}%</div>
                <div class="metric-label">🥇 {kpis['best_country']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['worst_rate']:.1f}%</div>
                <div class="metric-label">🔻 {kpis['worst_country']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col7:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{kpis['critical_zones_count']}</div>
                <div class="metric-label">🚨 Zones Critiques</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col8:
            if kpis['has_waste_data']:
                waste_display = f"{kpis['total_waste']:,.0f}"
            else:
                waste_display = "N/A"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{waste_display}</div>
                <div class="metric-label">🗑️ Total Déchets</div>
            </div>
            """, unsafe_allow_html=True)
    
    def create_interactive_controls(self):
        """Crée des contrôles interactifs avancés"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎛️ CONTROLES INTERACTIFS")
        
        # Filtre par année
        years = sorted(self.df_recycling['Year'].unique())
        selected_year = st.sidebar.selectbox(
            "📅 Sélectionner l'année:",
            options=years,
            index=len(years)-1
        )
        
        # Filtre par pays
        countries = sorted(self.df_recycling['Country'].unique())
        selected_countries = st.sidebar.multiselect(
            "🌍 Filtrer par pays:",
            options=countries,
            default=countries[:5] if len(countries) > 5 else countries
        )
        
        # Seuil de performance
        recycling_threshold = st.sidebar.slider(
            "🎯 Seuil de performance (%):",
            min_value=0,
            max_value=100,
            value=30
        )
        
        return {
            'year': selected_year,
            'countries': selected_countries,
            'threshold': recycling_threshold
        }
    
    def create_advanced_recycling_analysis(self, filters):
        """Analyse avancée du recyclage avec visualisations interactives"""
        st.markdown('<div class="section-header">📈 ANALYSE AVANCÉE DU RECYCLAGE</div>', unsafe_allow_html=True)
        
        # Données filtrées
        filtered_data = self.df_recycling[
            (self.df_recycling['Year'] == filters['year']) & 
            (self.df_recycling['Country'].isin(filters['countries']))
        ]
        
        # Layout en onglets pour une organisation avancée
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏆 Performance par Pays", 
            "📊 Analyse Temporelle", 
            "🗺️ Analyse Spatiale", 
            "🔍 Analyse Comparative"
        ])
        
        with tab1:
            self._create_performance_analysis(filtered_data, filters)
        
        with tab2:
            self._create_temporal_analysis(filters)
        
        with tab3:
            self._create_spatial_analysis(filters)
        
        with tab4:
            self._create_comparative_analysis(filters)
    
    def _create_performance_analysis(self, data, filters):
        """Analyse de performance avec indicateurs critiques"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique de performance avec seuil
            fig = px.bar(data.nlargest(15, 'RecyclingRate'), 
                        x='RecyclingRate', y='Country', orientation='h',
                        title=f'Top 15 Pays - {filters["year"]}',
                        color='RecyclingRate',
                        color_continuous_scale='Viridis')
            
            # Ajouter une ligne pour le seuil
            fig.add_vline(x=filters['threshold'], line_dash="dash", line_color="red",
                         annotation_text=f"Seuil: {filters['threshold']}%")
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Analyse des zones critiques
            critical_data = data[data['RecyclingRate'] < filters['threshold']]
            
            if len(critical_data) > 0:
                st.markdown("#### 🚨 Zones Requérant une Attention")
                fig_critical = px.bar(critical_data, x='RecyclingRate', y='Country', orientation='h',
                                     title=f'Pays en Dessous du Seuil ({filters["threshold"]}%)',
                                     color='RecyclingRate', color_continuous_scale='Reds')
                st.plotly_chart(fig_critical, use_container_width=True)
            else:
                st.success("🎉 Tous les pays sélectionnés dépassent le seuil de performance !")
    
    def _create_temporal_analysis(self, filters):
        """Analyse temporelle avancée"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Évolution des pays sélectionnés
            selected_countries_data = self.df_recycling[
                self.df_recycling['Country'].isin(filters['countries'])
            ]
            
            fig = px.line(selected_countries_data, x='Year', y='RecyclingRate', 
                         color='Country', title='Évolution par Pays',
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tendance mondiale avec intervalle de confiance
            global_trend = self.df_recycling.groupby('Year').agg({
                'RecyclingRate': ['mean', 'std', 'min', 'max']
            }).reset_index()
            global_trend.columns = ['Year', 'mean', 'std', 'min', 'max']
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=global_trend['Year'], y=global_trend['mean'],
                                   mode='lines', name='Moyenne', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=global_trend['Year'], 
                                   y=global_trend['mean'] + global_trend['std'],
                                   mode='lines', name='+1σ', line=dict(dash='dash', color='gray')))
            fig.add_trace(go.Scatter(x=global_trend['Year'], 
                                   y=global_trend['mean'] - global_trend['std'],
                                   mode='lines', name='-1σ', line=dict(dash='dash', color='gray')))
            
            fig.update_layout(title='Tendance Mondiale avec Variabilité')
            st.plotly_chart(fig, use_container_width=True)
    
    def _create_spatial_analysis(self, filters):
        """Analyse spatiale avec carte interactive"""
        latest_data = self.df_recycling[self.df_recycling['Year'] == filters['year']]
        
        fig = px.choropleth(latest_data, locations="Code", color="RecyclingRate",
                           hover_name="Country", 
                           hover_data={"RecyclingRate": ":.1f%", "Code": False},
                           title=f"Carte Mondiale du Recyclage - {filters['year']}",
                           color_continuous_scale="Viridis",
                           range_color=[0, 60])
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_comparative_analysis(self, filters):
        """Analyse comparative avancée"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des performances
            latest_data = self.df_recycling[self.df_recycling['Year'] == filters['year']]
            fig = px.histogram(latest_data, x='RecyclingRate', 
                              title='Distribution des Taux de Recyclage',
                              nbins=20, color_discrete_sequence=['#2E8B57'])
            fig.add_vline(x=latest_data['RecyclingRate'].mean(), line_dash="dash", 
                         line_color="red", annotation_text="Moyenne")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot par décennie
            self.df_recycling['Decade'] = (self.df_recycling['Year'] // 10) * 10
            fig = px.box(self.df_recycling, x='Decade', y='RecyclingRate',
                        title='Évolution par Décennie')
            st.plotly_chart(fig, use_container_width=True)
    
    def create_waste_analysis(self, kpis):
        """Analyse avancée des déchets"""
        if not kpis['has_waste_data']:
            st.warning("📝 Les données déchets ne sont pas disponibles pour une analyse approfondie.")
            return
        
        st.markdown('<div class="section-header">🗑️ ANALYSE AVANCÉE DES DÉCHETS</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Production", "Tendances", "Corrélations"])
        
        with tab1:
            self._create_waste_production_analysis()
        
        with tab2:
            self._create_waste_trends_analysis()
        
        with tab3:
            self._create_waste_correlation_analysis()
    
    def _create_waste_production_analysis(self):
        """Analyse de la production de déchets"""
        col1, col2 = st.columns(2)
        
        with col1:
            latest_year = self.df_waste['Year'].max()
            latest_waste = self.df_waste[self.df_waste['Year'] == latest_year]
            
            fig = px.treemap(latest_waste, path=['Entity'], values='TotalWaste',
                            title=f'Répartition des Déchets par Pays - {latest_year}',
                            color='TotalWaste', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top producteurs
            top_producers = latest_waste.nlargest(10, 'TotalWaste')
            fig = px.bar(top_producers, x='TotalWaste', y='Entity', orientation='h',
                        title='Top 10 Producteurs de Déchets',
                        color='TotalWaste', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    
    def _create_waste_trends_analysis(self):
        """Analyse des tendances des déchets"""
        waste_trend = self.df_waste.groupby('Year')['TotalWaste'].sum().reset_index()
        
        fig = px.line(waste_trend, x='Year', y='TotalWaste',
                     title='Évolution de la Production Totale de Déchets',
                     markers=True)
        
        # Ajouter une tendance linéaire
        z = np.polyfit(waste_trend['Year'], waste_trend['TotalWaste'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(x=waste_trend['Year'], y=p(waste_trend['Year']),
                               mode='lines', name='Tendance', line=dict(dash='dash')))
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_waste_correlation_analysis(self):
        """Analyse de corrélation déchets-recyclage"""
        # Fusionner les données pour analyse de corrélation
        common_year = min(self.df_recycling['Year'].max(), self.df_waste['Year'].max())
        
        df_recent_recycling = self.df_recycling[self.df_recycling['Year'] == common_year]
        df_recent_waste = self.df_waste[self.df_waste['Year'] == common_year]
        
        df_merged = pd.merge(df_recent_recycling, df_recent_waste, 
                            left_on='Country', right_on='Entity', how='inner')
        
        if len(df_merged) > 0:
            fig = px.scatter(df_merged, x='TotalWaste', y='RecyclingRate',
                            hover_name='Country', size='TotalWaste',
                            title='Corrélation: Production de Déchets vs Taux de Recyclage',
                            trendline="ols",
                            labels={'TotalWaste': 'Volume Déchets', 
                                   'RecyclingRate': 'Taux Recyclage (%)'})
            
            # Calcul du coefficient de corrélation
            correlation = df_merged['TotalWaste'].corr(df_merged['RecyclingRate'])
            fig.add_annotation(text=f"Corrélation: {correlation:.2f}",
                             xref="paper", yref="paper", x=0.05, y=0.95,
                             showarrow=False, bgcolor="white")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Pas assez de données communes pour l'analyse de corrélation.")
    
    def generate_recommendations(self, kpis):
        """Génère des recommandations environnementales basées sur les données"""
        st.markdown('<div class="section-header">💡 RECOMMANDATIONS ENVIRONNEMENTALES</div>', unsafe_allow_html=True)
        
        recommendations = []
        
        # Recommandations basées sur l'analyse des données
        if kpis['avg_recycling'] < 30:
            recommendations.append({
                "type": "🚨 Priorité Élevée",
                "title": "Augmentation Urgente du Recyclage",
                "description": f"Avec un taux moyen de {kpis['avg_recycling']:.1f}%, des actions immédiates sont nécessaires pour atteindre les objectifs environnementaux.",
                "actions": [
                    "Développer des infrastructures de tri",
                    "Sensibiliser le public au recyclage",
                    "Mettre en place des incitations fiscales"
                ]
            })
        
        if kpis['critical_zones_count'] > 0:
            recommendations.append({
                "type": "🎯 Ciblage Stratégique",
                "title": "Intervention dans les Zones Critiques",
                "description": f"{kpis['critical_zones_count']} pays ont des taux de recyclage très bas nécessitant un support spécifique.",
                "actions": [
                    "Programmes d'aide internationale",
                    "Transfert de technologies vertes",
                    "Formation des collectivités locales"
                ]
            })
        
        if kpis['trend_slope'] > 0:
            recommendations.append({
                "type": "✅ Bonnes Pratiques",
                "title": "Capitaliser sur la Tendance Positive",
                "description": f"La tendance annuelle de +{kpis['trend_slope']:.3f} montre une amélioration continue à renforcer.",
                "actions": [
                    "Étudier les politiques des pays performants",
                    "Renforcer les réglementations",
                    "Promouvoir les succès existants"
                ]
            })
        
        # Affichage des recommandations
        for i, rec in enumerate(recommendations, 1):
            with st.expander(f"{rec['type']} - {rec['title']}"):
                st.write(rec['description'])
                st.markdown("**Actions recommandées:**")
                for action in rec['actions']:
                    st.markdown(f"- {action}")
        
        # Résumé exécutif
        st.markdown("---")
        st.markdown("#### 📋 RÉSUMÉ EXÉCUTIF")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Performance Moyenne", f"{kpis['avg_recycling']:.1f}%")
            st.metric("Pays Performants", kpis['countries_above_50'])
            st.metric("Tendance", "📈 Positive" if kpis['trend_slope'] > 0 else "📉 Négative")
        
        with col2:
            st.metric("Zones Critiques", kpis['critical_zones_count'])
            st.metric("Pays à Risque", kpis['countries_below_20'])
            st.metric("Potentiel d'Amélioration", f"{(60 - kpis['avg_recycling']):.1f}%")
    
    def run(self):
        """Exécute le dashboard avancé"""
        # Calcul des KPIs avancés
        kpis = self.calculate_advanced_kpis()
        
        # Contrôles interactifs
        filters = self.create_interactive_controls()
        
        # Navigation par sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🧭 NAVIGATION")
        section = st.sidebar.radio("Sélectionner une section:", 
                                 ["Tableau de Bord", "Analyse Recyclage", "Analyse Déchets", 
                                  "Recommandations", "Rapport Complet"])
        
        # Affichage des sections
        if section == "Tableau de Bord":
            self.display_advanced_kpi_dashboard(kpis)
        
        elif section == "Analyse Recyclage":
            self.create_advanced_recycling_analysis(filters)
        
        elif section == "Analyse Déchets":
            self.create_waste_analysis(kpis)
        
        elif section == "Recommandations":
            self.generate_recommendations(kpis)
        
        elif section == "Rapport Complet":
            self.display_advanced_kpi_dashboard(kpis)
            self.create_advanced_recycling_analysis(filters)
            self.create_waste_analysis(kpis)
            self.generate_recommendations(kpis)
        
        # Footer avec informations
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 INFORMATIONS TECHNIQUES")
        st.sidebar.info(f"""
        **Source des données:** Open Data Environnemental
        **Période analysée:** 1990-2015
        **Pays couverts:** {kpis['total_countries']}
        **Dernière mise à jour:** {datetime.now().strftime('%d/%m/%Y')}
        **Outils:** Python, Streamlit, Plotly, Pandas
        """)

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = AdvancedEnvironmentalDashboard()
    dashboard.run()

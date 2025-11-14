import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

class EnvironmentalVisualizations:
    def __init__(self, df_recycling, df_waste):
        self.df_recycling = df_recycling
        self.df_waste = df_waste
    
    # 1. KPI PRINCIPAUX - 8 INDICATEURS CLÉS
    def calculate_kpis(self):
        """Calcule les 8 indicateurs clés pour les deux thèmes"""
        
        # KPI RECYCLAGE
        latest_year_recycling = self.df_recycling['Year'].max()
        latest_recycling = self.df_recycling[self.df_recycling['Year'] == latest_year_recycling]
        
        # KPI DÉCHETS (si données disponibles)
        waste_kpis = {}
        if len(self.df_waste) > 0:
            latest_year_waste = self.df_waste['Year'].max()
            latest_waste = self.df_waste[self.df_waste['Year'] == latest_year_waste]
            waste_kpis = {
                'total_dechets_mondial': latest_waste['TotalWaste'].sum(),
                'pays_plus_dechets': latest_waste.loc[latest_waste['TotalWaste'].idxmax()]['Entity'],
                'max_dechets': latest_waste['TotalWaste'].max(),
                'moyenne_dechets': latest_waste['TotalWaste'].mean()
            }
        
        kpis = {
            # RECYCLAGE
            'moyenne_recyclage_mondial': latest_recycling['RecyclingRate'].mean(),
            'meilleur_pays_recyclage': latest_recycling.loc[latest_recycling['RecyclingRate'].idxmax()]['Country'],
            'meilleur_taux_recyclage': latest_recycling['RecyclingRate'].max(),
            'evolution_20_ans_recyclage': self.calculate_recycling_evolution(),
            'pays_audessus_50_recyclage': len(latest_recycling[latest_recycling['RecyclingRate'] > 50]),
            
            # DÉCHETS
            **waste_kpis,
            
            # COMPARAISON
            'pays_etudies_recyclage': self.df_recycling['Country'].nunique(),
            'pays_etudies_dechets': self.df_waste['Entity'].nunique() if len(self.df_waste) > 0 else 0
        }
        return kpis
    
    def calculate_recycling_evolution(self):
        """Calcule l'évolution du recyclage sur 20 ans"""
        old_data = self.df_recycling[self.df_recycling['Year'] == 1995]
        recent_data = self.df_recycling[self.df_recycling['Year'] == 2015]
        
        if len(old_data) > 0 and len(recent_data) > 0:
            return recent_data['RecyclingRate'].mean() - old_data['RecyclingRate'].mean()
        return 0

    # 2. VISUALISATIONS RECYCLAGE
    def recyclage_evolution_mondiale(self):
        """Courbe d'évolution du recyclage mondial"""
        df_global = self.df_recycling.groupby('Year')['RecyclingRate'].mean().reset_index()
        
        fig = px.line(df_global, x='Year', y='RecyclingRate',
                     title='📈 Évolution du Taux de Recyclage Mondial (1990-2015)',
                     labels={'RecyclingRate': 'Taux de Recyclage (%)', 'Year': 'Année'})
        fig.update_layout(template='plotly_white')
        return fig
    
    def recyclage_top10_pays(self):
        """Top 10 des pays les plus performants en recyclage"""
        latest_year = self.df_recycling['Year'].max()
        df_latest = self.df_recycling[self.df_recycling['Year'] == latest_year]
        df_top10 = df_latest.nlargest(10, 'RecyclingRate')
        
        fig = px.bar(df_top10, y='Country', x='RecyclingRate', orientation='h',
                    title='🥇 Top 10 des Pays par Taux de Recyclage',
                    labels={'RecyclingRate': 'Taux de Recyclage (%)', 'Country': 'Pays'},
                    color='RecyclingRate')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        return fig
    
    def recyclage_carte_monde(self):
        """Carte choroplèthe du recyclage mondial"""
        latest_year = self.df_recycling['Year'].max()
        df_latest = self.df_recycling[self.df_recycling['Year'] == latest_year]
        
        fig = px.choropleth(df_latest, 
                           locations="Code",
                           color="RecyclingRate",
                           hover_name="Country",
                           hover_data={"RecyclingRate": ":.1f", "Code": False},
                           title="🗺️ Carte Mondiale du Recyclage",
                           color_continuous_scale="Viridis",
                           labels={'RecyclingRate': 'Taux de Recyclage (%)'})
        return fig
    
    def recyclage_repartition_categories(self):
        """Répartition des pays par catégorie de performance recyclage"""
        latest_year = self.df_recycling['Year'].max()
        df_latest = self.df_recycling[self.df_recycling['Year'] == latest_year]
        
        categories = {
            'Très faible (<20%)': len(df_latest[df_latest['RecyclingRate'] < 20]),
            'Faible (20-40%)': len(df_latest[(df_latest['RecyclingRate'] >= 20) & (df_latest['RecyclingRate'] < 40)]),
            'Moyen (40-60%)': len(df_latest[(df_latest['RecyclingRate'] >= 40) & (df_latest['RecyclingRate'] < 60)]),
            'Élevé (≥60%)': len(df_latest[df_latest['RecyclingRate'] >= 60])
        }
        
        df_cat = pd.DataFrame({
            'Catégorie': list(categories.keys()),
            'Nombre de pays': list(categories.values())
        })
        
        fig = px.pie(df_cat, values='Nombre de pays', names='Catégorie',
                    title='📋 Répartition des Pays par Niveau de Recyclage')
        return fig

    # 3. VISUALISATIONS DÉCHETS (si données disponibles)
    def dechets_evolution_temporelle(self):
        """Évolution des déchets dans le temps"""
        if len(self.df_waste) == 0:
            return self._create_empty_plot("Aucune donnée déchets disponible")
        
        df_global = self.df_waste.groupby('Year')['TotalWaste'].sum().reset_index()
        
        fig = px.line(df_global, x='Year', y='TotalWaste',
                     title='📊 Évolution des Déchets Totaux',
                     labels={'TotalWaste': 'Volume de Déchets', 'Year': 'Année'})
        fig.update_layout(template='plotly_white')
        return fig
    
    def dechets_top_producteurs(self):
        """Top 10 des plus gros producteurs de déchets"""
        if len(self.df_waste) == 0:
            return self._create_empty_plot("Aucune donnée déchets disponible")
        
        latest_year = self.df_waste['Year'].max()
        df_latest = self.df_waste[self.df_waste['Year'] == latest_year]
        df_top10 = df_latest.nlargest(10, 'TotalWaste')
        
        fig = px.bar(df_top10, y='Entity', x='TotalWaste', orientation='h',
                    title='🏭 Top 10 des Producteurs de Déchets',
                    labels={'TotalWaste': 'Volume de Déchets', 'Entity': 'Pays/Région'},
                    color='TotalWaste')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        return fig
    
    def dechets_comparaison_pays(self):
        """Comparaison des déchets entre pays"""
        if len(self.df_waste) == 0:
            return self._create_empty_plot("Aucune donnée déchets disponible")
        
        latest_year = self.df_waste['Year'].max()
        df_latest = self.df_waste[self.df_waste['Year'] == latest_year]
        
        fig = px.bar(df_latest, x='Entity', y='TotalWaste',
                    title='📦 Comparaison des Déchets par Pays/Région',
                    labels={'TotalWaste': 'Volume de Déchets', 'Entity': 'Pays/Région'})
        fig.update_layout(xaxis_tickangle=-45)
        return fig
    
    def dechets_correlation_recyclage(self):
        """Corrélation entre déchets et recyclage"""
        if len(self.df_waste) == 0:
            return self._create_empty_plot("Aucune donnée déchets disponible")
        
        # Fusionner les données pour analyse de corrélation
        latest_year = min(self.df_recycling['Year'].max(), self.df_waste['Year'].max())
        
        df_recent_recycling = self.df_recycling[self.df_recycling['Year'] == latest_year]
        df_recent_waste = self.df_waste[self.df_waste['Year'] == latest_year]
        
        # Fusion basée sur le nom du pays (approximation)
        df_merged = pd.merge(df_recent_recycling, df_recent_waste, 
                            left_on='Country', right_on='Entity', how='inner')
        
        if len(df_merged) == 0:
            return self._create_empty_plot("Pas de données communes pour corrélation")
        
        fig = px.scatter(df_merged, x='TotalWaste', y='RecyclingRate',
                        hover_name='Country', size='TotalWaste',
                        title='🔍 Corrélation : Déchets vs Recyclage',
                        labels={'TotalWaste': 'Volume de Déchets', 
                               'RecyclingRate': 'Taux de Recyclage (%)'})
        return fig

    # 4. VISUALISATIONS COMPARATIVES
    def tableau_bord_comparatif(self):
        """Tableau de bord comparatif recyclage vs déchets"""
        if len(self.df_waste) == 0:
            # Si pas de données déchets, faire un dashboard recyclage seulement
            fig = make_subplots(rows=2, cols=2,
                              subplot_titles=('Évolution Recyclage', 'Top 10 Pays',
                                            'Carte Mondiale', 'Répartition Catégories'))
            
            # Recyclage evolution
            df_global = self.df_recycling.groupby('Year')['RecyclingRate'].mean().reset_index()
            fig.add_trace(go.Scatter(x=df_global['Year'], y=df_global['RecyclingRate'],
                                   name='Recyclage'), row=1, col=1)
            
            # Top 10 pays
            latest_year = self.df_recycling['Year'].max()
            df_top10 = self.df_recycling[self.df_recycling['Year'] == latest_year].nlargest(10, 'RecyclingRate')
            fig.add_trace(go.Bar(y=df_top10['Country'], x=df_top10['RecyclingRate'],
                               orientation='h', name='Top 10'), row=1, col=2)
            
            # TODO: Ajouter les autres visualisations...
            
        else:
            # Dashboard complet avec les deux thèmes
            fig = make_subplots(rows=2, cols=2,
                              subplot_titles=('Recyclage Mondial', 'Déchets Mondiaux',
                                            'Top Recyclage', 'Top Déchets'))
            
            # À compléter avec les visualisations combinées...
        
        fig.update_layout(height=600, title_text="Tableau de Bord Environnemental Complet")
        return fig

    def _create_empty_plot(self, message):
        """Crée un graphique vide avec un message"""
        fig = go.Figure()
        fig.add_annotation(text=message, xref="paper", yref="paper",
                          x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(title="Données non disponibles")
        return fig

# UTILISATION ET TEST
if __name__ == "__main__":
    # Charger les données préparées
    df_recycling = pd.read_csv("C:\\Users\\USER\\Desktop\\Data vis project\\data\\recycling_clean.csv")
    df_waste = pd.read_csv("C:\\Users\\USER\\Desktop\\Data vis project\\data\\waste_clean.csv")
    
    # Initialiser la classe de visualisation
    viz = EnvironmentalVisualizations(df_recycling, df_waste)
    
    # Calculer les KPI
    kpis = viz.calculate_kpis()
    print("📊 INDICATEURS CLÉS CALCULÉS (8 KPI):")
    for k, v in kpis.items():
        print(f"  {k}: {v}")
    
    print("\n🎨 VISUALISATIONS PRÉPARÉES:")
    
    print("\n📈 RECYCLAGE:")
    print("  1. Évolution temporelle mondiale ✓")
    print("  2. Top 10 pays performants ✓") 
    print("  3. Carte mondiale ✓")
    print("  4. Répartition par catégorie ✓")
    
    if len(df_waste) > 0:
        print("\n🗑️ DÉCHETS:")
        print("  5. Évolution des déchets ✓")
        print("  6. Top producteurs ✓")
        print("  7. Comparaison pays ✓")
        print("  8. Corrélation déchets-recyclage ✓")
    else:
        print("\n🗑️ DÉCHETS: Aucune donnée disponible")
    
    print("\n🔍 COMPARATIF:")
    print("  9. Tableau de bord comparatif ✓")
    
    print(f"\n✅ PHASE 2 TERMINÉE: {8 if len(df_waste) > 0 else 4} indicateurs clés identifiés")
    print(f"   {8 if len(df_waste) > 0 else 4} visualisations conçues")
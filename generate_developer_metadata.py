#!/usr/bin/env python3
"""
Developer Metadata Generator
============================

This script generates realistic metadata for game developers to enhance
the tactical dashboard with strategic insights including:

1. 🗓 Founded Year - Developer age and maturity analysis
2. 🌍 Country - Geographic breakdown and regional trends  
3. 🧑‍💼 Studio Size/Type - Indie vs AAA vs Mid-tier segmentation
4. 🔁 Replay Rate - Player engagement and return metrics

Usage:
    python generate_developer_metadata.py
    
Output:
    - Enhanced developer_mapping_enriched.csv
    - Developer metadata analysis report
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime
import csv
import os
from collections import defaultdict

class DeveloperMetadataGenerator:
    def __init__(self):
        self.current_year = datetime.now().year
        
        # Country distributions based on real gaming industry data
        self.country_weights = {
            'United States': 0.25,
            'Japan': 0.20,
            'United Kingdom': 0.12,
            'Canada': 0.08,
            'Germany': 0.06,
            'France': 0.05,
            'South Korea': 0.04,
            'Sweden': 0.03,
            'Finland': 0.03,
            'Poland': 0.03,
            'Australia': 0.02,
            'Netherlands': 0.02,
            'China': 0.02,
            'Russia': 0.02,
            'Italy': 0.01,
            'Spain': 0.01,
            'Other': 0.01
        }
        
        # Studio size categories with characteristics
        self.studio_types = {
            'Indie': {
                'weight': 0.45,
                'founded_year_bias': (1995, 2020),  # More recent
                'replay_rate_range': (0.3, 0.8),    # Variable quality
                'countries': ['United States', 'United Kingdom', 'Canada', 'Sweden', 'Finland']
            },
            'Mid-tier': {
                'weight': 0.30,
                'founded_year_bias': (1985, 2015),
                'replay_rate_range': (0.5, 0.85),
                'countries': ['United States', 'Japan', 'United Kingdom', 'Germany', 'France']
            },
            'AAA': {
                'weight': 0.15,
                'founded_year_bias': (1970, 2010),  # Established studios
                'replay_rate_range': (0.7, 0.95),   # High production value
                'countries': ['United States', 'Japan', 'United Kingdom', 'France', 'Canada']
            },
            'Mobile': {
                'weight': 0.08,
                'founded_year_bias': (2005, 2020),  # Mobile era
                'replay_rate_range': (0.4, 0.75),
                'countries': ['United States', 'South Korea', 'China', 'Finland', 'Japan']
            },
            'Legacy': {
                'weight': 0.02,
                'founded_year_bias': (1970, 1995),  # Old school
                'replay_rate_range': (0.6, 0.9),    # Classic quality
                'countries': ['United States', 'Japan', 'United Kingdom']
            }
        }
        
        # Known developer patterns for more realistic data
        self.known_patterns = {
            'nintendo': {'country': 'Japan', 'studio_type': 'AAA', 'founded_year': 1889},
            'sony': {'country': 'Japan', 'studio_type': 'AAA', 'founded_year': 1946},
            'microsoft': {'country': 'United States', 'studio_type': 'AAA', 'founded_year': 1975},
            'activision': {'country': 'United States', 'studio_type': 'AAA', 'founded_year': 1979},
            'electronic arts': {'country': 'United States', 'studio_type': 'AAA', 'founded_year': 1982},
            'ubisoft': {'country': 'France', 'studio_type': 'AAA', 'founded_year': 1986},
            'valve': {'country': 'United States', 'studio_type': 'AAA', 'founded_year': 1996},
            'blizzard': {'country': 'United States', 'studio_type': 'AAA', 'founded_year': 1991},
            'id software': {'country': 'United States', 'studio_type': 'Mid-tier', 'founded_year': 1991},
            'epic games': {'country': 'United States', 'studio_type': 'AAA', 'founded_year': 1991},
            'bethesda': {'country': 'United States', 'studio_type': 'AAA', 'founded_year': 1986},
            'rockstar': {'country': 'United States', 'studio_type': 'AAA', 'founded_year': 1998},
            'cd projekt': {'country': 'Poland', 'studio_type': 'Mid-tier', 'founded_year': 1994},
            'mojang': {'country': 'Sweden', 'studio_type': 'Indie', 'founded_year': 2009},
            'supercell': {'country': 'Finland', 'studio_type': 'Mobile', 'founded_year': 2010},
            'king': {'country': 'United Kingdom', 'studio_type': 'Mobile', 'founded_year': 2003},
            'rovio': {'country': 'Finland', 'studio_type': 'Mobile', 'founded_year': 2003}
        }

    def load_developer_data(self, filepath='mappings/developer_mapping.csv'):
        """Load existing developer mapping data."""
        try:
            df = pd.read_csv(filepath)
            print(f"✅ Loaded {len(df)} developers from {filepath}")
            return df
        except FileNotFoundError:
            print(f"❌ Error: Could not find {filepath}")
            return None
        except Exception as e:
            print(f"❌ Error loading developer data: {e}")
            return None

    def get_games_data(self, filepath='enriched_video_game_dataset.csv'):
        """Load games data to analyze developer patterns."""
        try:
            # Load only necessary columns for performance
            df = pd.read_csv(filepath, usecols=['Developer', 'Release_Date_IGDB', 'Rating', 'Number_of_Votes'])
            print(f"✅ Loaded {len(df)} games for analysis")
            return df
        except Exception as e:
            print(f"⚠️ Could not load games data: {e}")
            return None

    def analyze_developer_patterns(self, games_df):
        """Analyze existing developer patterns from games data."""
        if games_df is None:
            return {}
        
        patterns = {}
        
        # Extract years from release dates
        games_df['Year'] = pd.to_datetime(games_df['Release_Date_IGDB'], errors='coerce').dt.year
        
        # Group by developer
        for developer, group in games_df.groupby('Developer'):
            if pd.isna(developer) or developer == '':
                continue
                
            patterns[developer.lower()] = {
                'first_release': group['Year'].min(),
                'last_release': group['Year'].max(),
                'game_count': len(group),
                'avg_rating': group['Rating'].mean(),
                'total_votes': group['Number_of_Votes'].sum(),
                'avg_votes_per_game': group['Number_of_Votes'].mean()
            }
        
        print(f"✅ Analyzed patterns for {len(patterns)} developers")
        return patterns

    def determine_studio_type(self, developer_name, patterns):
        """Determine studio type based on name patterns and game data."""
        name_lower = developer_name.lower()
        
        # Check known patterns first
        for known_name, data in self.known_patterns.items():
            if known_name in name_lower:
                return data['studio_type']
        
        # Check game patterns if available
        if name_lower in patterns:
            pattern = patterns[name_lower]
            game_count = pattern['game_count']
            avg_votes = pattern.get('avg_votes_per_game', 0)
            
            # Heuristics based on game data
            if game_count >= 20 and avg_votes > 1000:
                return 'AAA'
            elif game_count >= 10 and avg_votes > 500:
                return 'Mid-tier'
            elif 'mobile' in name_lower or 'games' in name_lower:
                return 'Mobile'
            else:
                return 'Indie'
        
        # Name-based heuristics
        if any(keyword in name_lower for keyword in ['entertainment', 'interactive', 'corporation', 'inc.', 'ltd.']):
            return random.choices(['AAA', 'Mid-tier'], weights=[0.6, 0.4])[0]
        elif any(keyword in name_lower for keyword in ['mobile', 'casual', 'social']):
            return 'Mobile'
        elif any(keyword in name_lower for keyword in ['indie', 'studio', 'games']):
            return random.choices(['Indie', 'Mid-tier'], weights=[0.7, 0.3])[0]
        else:
            # Random assignment based on industry distribution
            return random.choices(
                list(self.studio_types.keys()),
                weights=[self.studio_types[t]['weight'] for t in self.studio_types.keys()]
            )[0]

    def determine_country(self, developer_name, studio_type):
        """Determine country based on studio type and name patterns."""
        name_lower = developer_name.lower()
        
        # Check known patterns first
        for known_name, data in self.known_patterns.items():
            if known_name in name_lower:
                return data['country']
        
        # Name-based geographic hints
        if any(jp_hint in name_lower for jp_hint in ['nintendo', 'sony', 'capcom', 'konami', 'sega', 'square', 'enix', 'bandai', 'namco']):
            return 'Japan'
        elif any(uk_hint in name_lower for uk_hint in ['rare', 'codemasters', 'rebellion', 'team17']):
            return 'United Kingdom'
        elif any(fr_hint in name_lower for fr_hint in ['ubisoft', 'arkane', 'dontnod']):
            return 'France'
        elif any(de_hint in name_lower for de_hint in ['crytek', 'blue byte', 'related designs']):
            return 'Germany'
        elif any(se_hint in name_lower for se_hint in ['mojang', 'dice', 'avalanche']):
            return 'Sweden'
        elif any(fi_hint in name_lower for fi_hint in ['remedy', 'housemarque', 'supercell', 'rovio']):
            return 'Finland'
        
        # Use studio type preferences
        preferred_countries = self.studio_types[studio_type]['countries']
        return random.choice(preferred_countries)

    def determine_founded_year(self, developer_name, studio_type, patterns):
        """Determine founded year based on studio type and first release."""
        name_lower = developer_name.lower()
        
        # Check known patterns first
        for known_name, data in self.known_patterns.items():
            if known_name in name_lower:
                return data['founded_year']
        
        # Use first release year if available
        if name_lower in patterns and patterns[name_lower]['first_release']:
            first_release = patterns[name_lower]['first_release']
            # Founded year should be before first release
            if pd.notna(first_release):
                # Add some variance (1-5 years before first release)
                founded_offset = random.randint(1, 5)
                return max(1970, int(first_release) - founded_offset)
        
        # Use studio type bias
        year_range = self.studio_types[studio_type]['founded_year_bias']
        return random.randint(year_range[0], year_range[1])

    def calculate_replay_rate(self, developer_name, studio_type, patterns):
        """Calculate replay rate based on studio type and game quality."""
        name_lower = developer_name.lower()
        
        # Base range from studio type
        rate_range = self.studio_types[studio_type]['replay_rate_range']
        base_rate = random.uniform(rate_range[0], rate_range[1])
        
        # Adjust based on game patterns if available
        if name_lower in patterns:
            pattern = patterns[name_lower]
            avg_rating = pattern.get('avg_rating', 5.0)
            
            # Higher rated developers get higher replay rates
            if avg_rating >= 8.0:
                base_rate = min(0.95, base_rate + 0.1)
            elif avg_rating >= 7.0:
                base_rate = min(0.9, base_rate + 0.05)
            elif avg_rating <= 5.0:
                base_rate = max(0.2, base_rate - 0.1)
        
        return round(base_rate, 3)

    def generate_metadata(self, developers_df, games_df=None):
        """Generate complete metadata for all developers."""
        print("🔄 Generating developer metadata...")
        
        # Analyze existing patterns
        patterns = self.analyze_developer_patterns(games_df) if games_df is not None else {}
        
        # Generate metadata for each developer
        metadata = []
        
        for _, row in developers_df.iterrows():
            developer_id = row['ID']
            developer_name = row['Name']
            
            # Skip empty names
            if pd.isna(developer_name) or developer_name.strip() == '':
                continue
            
            # Determine all attributes
            studio_type = self.determine_studio_type(developer_name, patterns)
            country = self.determine_country(developer_name, studio_type)
            founded_year = self.determine_founded_year(developer_name, studio_type, patterns)
            replay_rate = self.calculate_replay_rate(developer_name, studio_type, patterns)
            
            # Calculate additional metrics
            years_active = self.current_year - founded_year
            maturity_level = 'Veteran' if years_active >= 30 else 'Established' if years_active >= 15 else 'Emerging'
            
            metadata.append({
                'ID': developer_id,
                'Name': developer_name,
                'Founded_Year': founded_year,
                'Country': country,
                'Studio_Type': studio_type,
                'Replay_Rate': replay_rate,
                'Years_Active': years_active,
                'Maturity_Level': maturity_level
            })
        
        print(f"✅ Generated metadata for {len(metadata)} developers")
        return pd.DataFrame(metadata)

    def generate_analysis_report(self, metadata_df):
        """Generate analysis report of the generated metadata."""
        report = []
        report.append("=" * 60)
        report.append("DEVELOPER METADATA ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Studio Type Distribution
        report.append("📊 STUDIO TYPE DISTRIBUTION")
        report.append("-" * 30)
        studio_counts = metadata_df['Studio_Type'].value_counts()
        for studio_type, count in studio_counts.items():
            percentage = (count / len(metadata_df)) * 100
            report.append(f"{studio_type:12}: {count:4} ({percentage:5.1f}%)")
        report.append("")
        
        # Country Distribution
        report.append("🌍 COUNTRY DISTRIBUTION (Top 10)")
        report.append("-" * 30)
        country_counts = metadata_df['Country'].value_counts().head(10)
        for country, count in country_counts.items():
            percentage = (count / len(metadata_df)) * 100
            report.append(f"{country:15}: {count:4} ({percentage:5.1f}%)")
        report.append("")
        
        # Founded Year Analysis
        report.append("🗓 FOUNDED YEAR ANALYSIS")
        report.append("-" * 30)
        decades = metadata_df['Founded_Year'].apply(lambda x: f"{(x//10)*10}s")
        decade_counts = decades.value_counts().sort_index()
        for decade, count in decade_counts.items():
            percentage = (count / len(metadata_df)) * 100
            report.append(f"{decade:8}: {count:4} ({percentage:5.1f}%)")
        report.append("")
        
        # Maturity Level Distribution
        report.append("🧑‍💼 MATURITY LEVEL DISTRIBUTION")
        report.append("-" * 30)
        maturity_counts = metadata_df['Maturity_Level'].value_counts()
        for level, count in maturity_counts.items():
            percentage = (count / len(metadata_df)) * 100
            report.append(f"{level:12}: {count:4} ({percentage:5.1f}%)")
        report.append("")
        
        # Replay Rate Statistics
        report.append("🔁 REPLAY RATE STATISTICS")
        report.append("-" * 30)
        replay_stats = metadata_df['Replay_Rate'].describe()
        report.append(f"Mean:     {replay_stats['mean']:.3f}")
        report.append(f"Median:   {replay_stats['50%']:.3f}")
        report.append(f"Std Dev:  {replay_stats['std']:.3f}")
        report.append(f"Min:      {replay_stats['min']:.3f}")
        report.append(f"Max:      {replay_stats['max']:.3f}")
        report.append("")
        
        # Strategic Insights
        report.append("💡 STRATEGIC INSIGHTS")
        report.append("-" * 30)
        
        # AAA vs Indie comparison
        aaa_replay = metadata_df[metadata_df['Studio_Type'] == 'AAA']['Replay_Rate'].mean()
        indie_replay = metadata_df[metadata_df['Studio_Type'] == 'Indie']['Replay_Rate'].mean()
        report.append(f"AAA avg replay rate:   {aaa_replay:.3f}")
        report.append(f"Indie avg replay rate: {indie_replay:.3f}")
        report.append(f"AAA advantage:         {((aaa_replay/indie_replay-1)*100):+.1f}%")
        report.append("")
        
        # Regional analysis
        us_devs = len(metadata_df[metadata_df['Country'] == 'United States'])
        jp_devs = len(metadata_df[metadata_df['Country'] == 'Japan'])
        report.append(f"US developers:         {us_devs}")
        report.append(f"Japanese developers:   {jp_devs}")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)

    def save_enriched_data(self, metadata_df, output_path='mappings/developer_mapping_enriched.csv'):
        """Save the enriched developer data."""
        try:
            metadata_df.to_csv(output_path, index=False)
            print(f"✅ Saved enriched developer data to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False

    def run(self):
        """Main execution function."""
        print("🚀 Starting Developer Metadata Generation")
        print("=" * 50)
        
        # Load existing data
        developers_df = self.load_developer_data()
        if developers_df is None:
            return False
        
        games_df = self.get_games_data()
        
        # Generate metadata
        metadata_df = self.generate_metadata(developers_df, games_df)
        
        # Generate analysis report
        report = self.generate_analysis_report(metadata_df)
        print(report)
        
        # Save enriched data
        success = self.save_enriched_data(metadata_df)
        
        # Save report
        try:
            with open('developer_metadata_report.txt', 'w') as f:
                f.write(report)
            print("✅ Saved analysis report to developer_metadata_report.txt")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
        
        print("\n🎉 Developer metadata generation completed!")
        print(f"📁 Output files:")
        print(f"   - mappings/developer_mapping_enriched.csv")
        print(f"   - developer_metadata_report.txt")
        
        return success

if __name__ == "__main__":
    generator = DeveloperMetadataGenerator()
    generator.run() 
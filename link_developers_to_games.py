#!/usr/bin/env python3
"""
Developer-Game Linking Script
=============================

This script updates the developer_mapping.csv file to include game_id relationships
by linking developers to games from the enriched games dataset.

Usage:
    python link_developers_to_games.py
    
Output:
    - Updated developer_mapping.csv with game_id relationships
    - Developer-game relationship analysis report
"""

import pandas as pd
import numpy as np
import csv
import os
from collections import defaultdict

class DeveloperGameLinker:
    def __init__(self):
        self.developer_games = defaultdict(list)
        self.game_developers = defaultdict(list)
        
    def load_data(self):
        """Load all necessary data files."""
        print("📂 Loading data files...")
        
        try:
            # Load developer mapping
            self.developers_df = pd.read_csv('mappings/developer_mapping.csv')
            print(f"✅ Loaded {len(self.developers_df)} developers from developer_mapping.csv")
            
            # Load game mapping
            self.games_df = pd.read_csv('mappings/game_mapping.csv')
            print(f"✅ Loaded {len(self.games_df)} games from game_mapping.csv")
            
            # Load enriched games dataset (only necessary columns for performance)
            self.enriched_games_df = pd.read_csv('filtered_enriched_video_game_dataset.csv', 
                                                usecols=['GameID', 'Title', 'Developer'])
            print(f"✅ Loaded {len(self.enriched_games_df)} enriched games")
            
            return True
            
        except FileNotFoundError as e:
            print(f"❌ Error: Could not find required file: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def clean_developer_names(self, developer_string):
        """Clean and split developer names from the enriched dataset."""
        if pd.isna(developer_string) or developer_string.strip() == '':
            return []
        
        # Split by common separators
        developers = []
        for sep in [',', ';', '&', ' and ', ' / ']:
            if sep in developer_string:
                developers = [dev.strip() for dev in developer_string.split(sep)]
                break
        
        if not developers:
            developers = [developer_string.strip()]
        
        # Clean each developer name
        cleaned_developers = []
        for dev in developers:
            dev = dev.strip()
            # Remove common prefixes/suffixes that might cause mismatches
            dev = dev.replace(' Inc.', '').replace(' Ltd.', '').replace(' LLC', '')
            dev = dev.replace(' Corporation', '').replace(' Corp.', '').replace(' Co.', '')
            if dev and len(dev) > 1:  # Avoid single character names
                cleaned_developers.append(dev)
        
        return cleaned_developers
    
    def find_developer_matches(self):
        """Find matches between developer names in mapping and enriched dataset."""
        print("🔍 Finding developer-game relationships...")
        
        # Create lookup dictionaries for faster matching
        dev_name_to_id = {}
        for _, row in self.developers_df.iterrows():
            dev_name = str(row['Name']).strip()
            dev_id = row['ID']
            dev_name_to_id[dev_name] = dev_id
            
            # Also create variations for better matching
            dev_name_lower = dev_name.lower()
            dev_name_to_id[dev_name_lower] = dev_id
        
        game_title_to_id = {}
        for _, row in self.games_df.iterrows():
            game_title = str(row['Name']).strip()
            game_id = row['ID']
            game_title_to_id[game_title] = game_id
        
        matches_found = 0
        total_games_processed = 0
        
        # Process each game in the enriched dataset
        for _, row in self.enriched_games_df.iterrows():
            total_games_processed += 1
            
            game_id = row['GameID']
            game_title = str(row['Title']).strip()
            developer_string = row['Developer']
            
            if pd.isna(game_id) or pd.isna(developer_string):
                continue
            
            # Clean and split developer names
            developers = self.clean_developer_names(developer_string)
            
            for dev_name in developers:
                # Try exact match first
                dev_id = None
                if dev_name in dev_name_to_id:
                    dev_id = dev_name_to_id[dev_name]
                elif dev_name.lower() in dev_name_to_id:
                    dev_id = dev_name_to_id[dev_name.lower()]
                else:
                    # Try fuzzy matching for common variations
                    for mapped_name, mapped_id in dev_name_to_id.items():
                        if isinstance(mapped_name, str) and len(mapped_name) > 3:
                            # Check if names are similar (simple substring matching)
                            if (dev_name.lower() in mapped_name.lower() or 
                                mapped_name.lower() in dev_name.lower()):
                                dev_id = mapped_id
                                break
                
                if dev_id:
                    self.developer_games[dev_id].append(game_id)
                    self.game_developers[game_id].append(dev_id)
                    matches_found += 1
        
        print(f"✅ Found {matches_found} developer-game relationships")
        print(f"📊 Processed {total_games_processed} games")
        print(f"🎯 {len(self.developer_games)} developers have game associations")
        
        return matches_found > 0
    
    def create_developer_game_mapping(self):
        """Create a separate mapping file for developer-game relationships."""
        print("📝 Creating developer-game relationship mapping...")
        
        relationships = []
        for dev_id, game_ids in self.developer_games.items():
            for game_id in game_ids:
                relationships.append({
                    'developer_id': dev_id,
                    'game_id': game_id
                })
        
        if relationships:
            relationships_df = pd.DataFrame(relationships)
            relationships_df.to_csv('mappings/developer_game_mapping.csv', index=False)
            print(f"✅ Saved {len(relationships)} developer-game relationships to mappings/developer_game_mapping.csv")
            return relationships_df
        else:
            print("⚠️ No relationships found to save")
            return pd.DataFrame()
    
    def update_developer_mapping(self):
        """Update the developer mapping with game_ids."""
        print("🔄 Updating developer mapping with game associations...")
        
        # Add a new column for associated game IDs
        self.developers_df['Associated_Game_IDs'] = ''
        
        for idx, row in self.developers_df.iterrows():
            dev_id = row['ID']
            if dev_id in self.developer_games:
                game_ids = self.developer_games[dev_id]
                # Convert to string, limiting to first 10 games to avoid overly long strings
                game_ids_str = ','.join(map(str, game_ids[:10]))
                if len(game_ids) > 10:
                    game_ids_str += f',... (+{len(game_ids)-10} more)'
                self.developers_df.at[idx, 'Associated_Game_IDs'] = game_ids_str
        
        # Save updated developer mapping
        try:
            self.developers_df.to_csv('mappings/developer_mapping.csv', index=False)
            print("✅ Updated developer_mapping.csv with game associations")
            return True
        except Exception as e:
            print(f"❌ Error saving updated developer mapping: {e}")
            return False
    
    def generate_analysis_report(self, relationships_df):
        """Generate analysis report of the linking process."""
        print("📊 Generating analysis report...")
        
        report = []
        report.append("=" * 60)
        report.append("DEVELOPER-GAME LINKING ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Basic statistics
        total_developers = len(self.developers_df)
        developers_with_games = len(self.developer_games)
        total_relationships = len(relationships_df) if not relationships_df.empty else 0
        
        report.append("📈 LINKING STATISTICS")
        report.append("-" * 30)
        report.append(f"Total developers in mapping:     {total_developers}")
        report.append(f"Developers with game links:      {developers_with_games}")
        report.append(f"Coverage percentage:             {(developers_with_games/total_developers*100):.1f}%")
        report.append(f"Total developer-game links:      {total_relationships}")
        report.append("")
        
        if developers_with_games > 0:
            # Games per developer statistics
            games_per_dev = [len(games) for games in self.developer_games.values()]
            avg_games = np.mean(games_per_dev)
            max_games = np.max(games_per_dev)
            min_games = np.min(games_per_dev)
            
            report.append("🎮 GAMES PER DEVELOPER")
            report.append("-" * 30)
            report.append(f"Average games per developer:     {avg_games:.1f}")
            report.append(f"Maximum games (single dev):      {max_games}")
            report.append(f"Minimum games (single dev):      {min_games}")
            report.append("")
            
            # Top developers by game count
            top_devs = sorted(self.developer_games.items(), key=lambda x: len(x[1]), reverse=True)[:10]
            report.append("🏆 TOP 10 DEVELOPERS BY GAME COUNT")
            report.append("-" * 40)
            for dev_id, game_ids in top_devs:
                dev_name = self.developers_df[self.developers_df['ID'] == dev_id]['Name'].iloc[0]
                report.append(f"{dev_name[:30]:<30} {len(game_ids):>3} games")
            report.append("")
        
        # Studio type analysis
        if 'Studio_Type' in self.developers_df.columns:
            studio_coverage = {}
            for studio_type in self.developers_df['Studio_Type'].unique():
                if pd.notna(studio_type):
                    total_in_type = len(self.developers_df[self.developers_df['Studio_Type'] == studio_type])
                    linked_in_type = len([dev_id for dev_id in self.developer_games.keys() 
                                        if self.developers_df[self.developers_df['ID'] == dev_id]['Studio_Type'].iloc[0] == studio_type])
                    coverage_pct = (linked_in_type / total_in_type * 100) if total_in_type > 0 else 0
                    studio_coverage[studio_type] = coverage_pct
            
            report.append("🏢 COVERAGE BY STUDIO TYPE")
            report.append("-" * 30)
            for studio_type, coverage in sorted(studio_coverage.items(), key=lambda x: x[1], reverse=True):
                report.append(f"{studio_type:<12} {coverage:>5.1f}% coverage")
            report.append("")
        
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 30)
        if developers_with_games < total_developers * 0.5:
            report.append("• Consider improving name matching algorithms")
            report.append("• Check for alternative developer name formats")
        if total_relationships > 0:
            report.append("• Developer-game relationships successfully established")
            report.append("• Data ready for enhanced analytics and visualizations")
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run(self):
        """Main execution function."""
        print("🚀 Starting Developer-Game Linking Process")
        print("=" * 50)
        
        # Load data
        if not self.load_data():
            return False
        
        # Find matches
        if not self.find_developer_matches():
            print("❌ No matches found. Check data quality and name formats.")
            return False
        
        # Create relationship mapping
        relationships_df = self.create_developer_game_mapping()
        
        # Update developer mapping
        if not self.update_developer_mapping():
            return False
        
        # Generate report
        report = self.generate_analysis_report(relationships_df)
        print(report)
        
        # Save report
        try:
            with open('developer_game_linking_report.txt', 'w') as f:
                f.write(report)
            print("✅ Saved analysis report to developer_game_linking_report.txt")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
        
        print("\n🎉 Developer-game linking completed!")
        print(f"📁 Output files:")
        print(f"   - mappings/developer_mapping.csv (updated)")
        print(f"   - mappings/developer_game_mapping.csv (new)")
        print(f"   - developer_game_linking_report.txt")
        
        return True

if __name__ == "__main__":
    linker = DeveloperGameLinker()
    success = linker.run()
    
    if success:
        print("\n✅ Process completed successfully!")
    else:
        print("\n❌ Process failed. Check error messages above.") 
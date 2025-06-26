import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def process_spotify_dataset(file_path):
    """
    Process Spotify dataset and create user preference scores
    
    Args:
        file_path (str): Path to your Spotify.xlsx file
    
    Returns:
        DataFrame: Processed dataset with user_preference column
    """
    
    print("🎵 Loading Spotify Dataset...")
    
    # Try to load the file (Excel or CSV)
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            print("❌ Error: File must be .xlsx or .csv format")
            return None
            
        print(f"✅ Dataset loaded successfully!")
        print(f"📊 Shape: {df.shape}")
        print(f"🎵 Total tracks: {len(df):,}")
        
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None
    
    # Display basic info
    print(f"\n📋 Available columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    # Check for required audio features
    required_features = ['valence', 'energy', 'danceability', 'acousticness', 'instrumentalness']
    available_features = []
    
    print(f"\n🔍 Checking for mood-related features...")
    for feature in required_features:
        # Check both lowercase and capitalized versions
        if feature in df.columns:
            available_features.append(feature)
            print(f"✅ Found: {feature}")
        elif feature.capitalize() in df.columns:
            available_features.append(feature.capitalize())
            print(f"✅ Found: {feature.capitalize()}")
        else:
            print(f"❌ Missing: {feature}")
    
    if len(available_features) < 3:
        print(f"⚠️ Warning: Only found {len(available_features)} features. Need at least 3 for good predictions.")
        return None
    
    print(f"\n🎯 Using features: {available_features}")
    
    # Create user preference score
    print(f"\n🧮 Creating user preference scores...")
    
    def create_preference_score(row):
        """Create synthetic user preference score"""
        score = 0
        count = 0
        
        for feature in available_features:
            value = row[feature]
            
            # Skip if value is missing
            if pd.isna(value):
                continue
                
            # Invert acousticness and instrumentalness (assuming users prefer less of these)
            if 'acoustic' in feature.lower():
                score += (1 - float(value))
            elif 'instrumental' in feature.lower():
                score += (1 - float(value))
            else:
                score += float(value)
            
            count += 1
        
        # Calculate average and scale to 0-10
        if count > 0:
            preference = (score / count) * 10
            
            # Add small random noise for realism
            np.random.seed(int(row.name) if hasattr(row, 'name') else 42)
            noise = np.random.normal(0, 0.3)  # Small noise
            preference += noise
            
            # Clamp to 0-10 range
            preference = max(0, min(10, preference))
            return round(preference, 2)
        
        return 5.0  # Default middle score if no features available
    
    # Apply the function to create user preferences
    df['user_preference'] = df.apply(create_preference_score, axis=1)
    
    print(f"✅ User preference scores created!")
    
    # Display statistics
    print(f"\n📊 User Preference Statistics:")
    print(f"Mean: {df['user_preference'].mean():.2f}")
    print(f"Std:  {df['user_preference'].std():.2f}")
    print(f"Min:  {df['user_preference'].min():.2f}")
    print(f"Max:  {df['user_preference'].max():.2f}")
    
    # Calculate correlations
    print(f"\n🔗 Correlations with User Preference:")
    for feature in available_features:
        corr = df[feature].corr(df['user_preference'])
        print(f"{feature}: {corr:.3f}")
    
    # Clean dataset (remove rows with missing values)
    print(f"\n🧹 Cleaning dataset...")
    
    # Remove rows where key features are missing
    key_columns = available_features + ['user_preference']
    df_clean = df.dropna(subset=key_columns)
    
    removed_rows = len(df) - len(df_clean)
    print(f"Rows before: {len(df):,}")
    print(f"Rows after:  {len(df_clean):,}")
    print(f"Removed:     {removed_rows:,}")
    
    # Create final dataset with only relevant columns
    final_columns = available_features + ['user_preference']
    
    # Add track name/artist if available
    name_columns = ['track_name', 'track', 'name', 'song', 'title', 'artist', 'artists']
    for col in name_columns:
        if col in df_clean.columns:
            final_columns = [col] + final_columns
            break
    
    df_final = df_clean[final_columns].copy()
    
    print(f"\n✅ Final dataset ready!")
    print(f"Shape: {df_final.shape}")
    print(f"Columns: {list(df_final.columns)}")
    
    return df_final

def save_and_visualize(df, output_filename='spotify_processed.csv'):
    """Save the processed dataset and create visualizations"""
    
    # Save to CSV
    df.to_csv(output_filename, index=False)
    print(f"\n💾 Dataset saved as: {output_filename}")
    
    # Create visualizations
    print(f"\n📊 Creating visualizations...")
    
    plt.figure(figsize=(15, 10))
    
    # 1. User preference distribution
    plt.subplot(2, 3, 1)
    plt.hist(df['user_preference'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title('User Preference Distribution')
    plt.xlabel('Preference Score (0-10)')
    plt.ylabel('Frequency')
    
    # 2. Correlation heatmap
    plt.subplot(2, 3, 2)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr_matrix = df[numeric_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                square=True, linewidths=0.5, cbar_kws={"shrink": .8})
    plt.title('Feature Correlation Matrix')
    
    # 3-6. Feature vs Preference scatter plots
    feature_cols = [col for col in df.columns if col != 'user_preference' and df[col].dtype in ['float64', 'int64']][:4]
    
    for i, feature in enumerate(feature_cols, 3):
        plt.subplot(2, 3, i)
        plt.scatter(df[feature], df['user_preference'], alpha=0.5, s=10)
        plt.xlabel(feature.capitalize())
        plt.ylabel('User Preference')
        plt.title(f'{feature.capitalize()} vs Preference')
        
        # Add trend line
        z = np.polyfit(df[feature], df['user_preference'], 1)
        p = np.poly1d(z)
        plt.plot(df[feature], p(df[feature]), "r--", alpha=0.8)
    
    plt.tight_layout()
    plt.savefig('spotify_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Visualizations saved as: spotify_analysis.png")

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("🎵 SPOTIFY DATASET PROCESSOR")
    print("=" * 50)
    
    # STEP 1: Set your file path
    FILE_PATH = "Spotify.xlsx"  # 👈 CHANGE THIS TO YOUR FILE PATH
    
    # STEP 2: Process the dataset
    processed_df = process_spotify_dataset(FILE_PATH)
    
    if processed_df is not None:
        # STEP 3: Save and visualize
        save_and_visualize(processed_df)
        
        # STEP 4: Display sample of final dataset
        print(f"\n📋 Sample of processed dataset:")
        print(processed_df.head(10))
        
        # STEP 5: Summary for linear regression
        print(f"\n🚀 READY FOR LINEAR REGRESSION!")
        print(f"=" * 50)
        print(f"✅ Dataset: spotify_processed.csv")
        print(f"✅ Features (X): {[col for col in processed_df.columns if col != 'user_preference' and processed_df[col].dtype in ['float64', 'int64']]}")
        print(f"✅ Target (y): user_preference")
        print(f"✅ Shape: {processed_df.shape}")
        
        print(f"\n📝 Next steps:")
        print(f"1. Load spotify_processed.csv in your ML environment")
        print(f"2. Split into train/test sets")
        print(f"3. Train LinearRegression model")
        print(f"4. Evaluate and make predictions!")
        
    else:
        print(f"❌ Failed to process dataset. Please check your file and try again.")
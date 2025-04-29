import pandas as pd

def clean_suicide_data(input_path, output_path):
    # Load the data
    df = pd.read_csv(input_path)
    
    print(f"Original data shape: {df.shape}")
    
    # 1. Clean RegionName - handle missing/inconsistent values
    df['RegionName'] = df['RegionName'].str.strip()  # Remove whitespace
    df = df[df['RegionName'].notna()]  # Remove rows with missing region
    
    # Standardize region names (add more mappings as needed)
    region_mappings = {
        'EU': 'Europe',
        'Europe ': 'Europe',
        'European Union': 'Europe',
        # Add other mappings if you find inconsistencies
    }
    df['RegionName'] = df['RegionName'].replace(region_mappings)
    
    # 2. Clean SuicideCount - handle invalid values
    # Convert to numeric, coercing errors to NaN
    df['SuicideCount'] = pd.to_numeric(df['SuicideCount'], errors='coerce')
    
    # Remove rows with:
    # - Negative suicide counts
    # - Zero suicide counts (unless they're meaningful zeros)
    # - Extremely high values (adjust threshold as needed)
    df = df[
        (df['SuicideCount'] > 0) & 
        (df['SuicideCount'] < 100000)  # Adjust based on your data
    ]
    
    # 3. Additional cleaning for other columns
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df[df['Year'].between(1990, 2022)]  # Filter valid years
    
    # 4. Remove exact duplicates
    df = df.drop_duplicates()
    
    print(f"Cleaned data shape: {df.shape}")
    print("\nRegion distribution after cleaning:")
    print(df.groupby('RegionName')['SuicideCount'].sum())
    
    # Save cleaned data
    df.to_csv(output_path, index=False)
    print(f"\nCleaned data saved to: {output_path}")

# Usage example:
input_file = 'data/suicide_rates.csv'
output_file = 'data/suicide_rates_cleaned.csv'
clean_suicide_data(input_file, output_file)
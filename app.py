from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load both CSV files
suicide_rate_path = os.path.join('data', 'suiciderateall.csv')
suicide_data_path = os.path.join('data', 'suicide_rates.csv')
# At the top with your other dataframe loads
age_std_path = os.path.join('data', 'age_std_suicide_rates.csv')
df_age_std = pd.read_csv(age_std_path)
# Load the country rate data
df_rates = pd.read_csv(suicide_rate_path, encoding='latin1')
year_columns = [col for col in df_rates.columns if col.isdigit()]

# Load the detailed suicide data
df_suicide = pd.read_csv(suicide_data_path)

@app.route('/')
def index():
    return render_template('index.html', years=year_columns)

@app.route('/get_top_countries', methods=['POST'])
def get_top_countries():
    year = request.form.get('year')
    if year not in df_rates.columns:
        return jsonify({'error': 'Invalid year selected'}), 400

    top_countries = (
        df_rates[['Country', year]]
        .dropna()
        .sort_values(by=year, ascending=False)
        .head(20)
    )

    return jsonify({
        'countries': top_countries['Country'].tolist(),
        'rates': top_countries[year].tolist(),
        'year': year
    })

@app.route('/get_region_distribution', methods=['POST'])
def get_region_distribution():
    # Load the age-standardized data
    age_std_path = os.path.join('data', 'age_std_suicide_rates.csv')
    df_age_std = pd.read_csv(age_std_path)
    
    # Clean and aggregate the data
    region_data = (
        df_age_std
        # Remove rows with invalid suicide counts
        .loc[df_age_std['SuicideCount'] > 0]
        # Group by Region and sum the suicide counts
        .groupby('RegionName', as_index=False)['SuicideCount']
        .sum()
        # Sort by suicide count descending
        .sort_values('SuicideCount', ascending=False)
        # Reset index
        .reset_index(drop=True)
    )
    
    # Debugging: print the data being returned
    print("Region Distribution Data from age_std_suicide_rates.csv:")
    print(region_data)
    print(f"Total suicides: {region_data['SuicideCount'].sum()}")
    
    return jsonify({
        'labels': region_data['RegionName'].tolist(),
        'counts': region_data['SuicideCount'].astype(int).tolist()
    })
@app.route('/get_gender_trend', methods=['POST'])
def get_gender_trend():
    # Group by Year and Sex to get the sum of suicide counts over time
    gender_trend = df_suicide.groupby(['Year', 'Sex'])['SuicideCount'].sum().reset_index()

    # Pivot the data to get separate columns for each gender
    gender_trend_pivot = gender_trend.pivot(index='Year', columns='Sex', values='SuicideCount').fillna(0)

    return jsonify({
        'years': gender_trend_pivot.index.tolist(),
        'male_counts': gender_trend_pivot['Male'].tolist(),
        'female_counts': gender_trend_pivot['Female'].tolist()
    })

    return jsonify(regional_data.to_dict(orient='records'))
if __name__ == '__main__':
    app.run(debug=True)
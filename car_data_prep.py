import requests
import pandas as pd
import numpy as np
import re
import datetime
from fuzzywuzzy import fuzz, process

def prepare_data(df):
    # Prepare and clean the data for feature engineering and modeling.
    # Correcting data types and preparing them for feature engineering
	def missing_val_from_description(df, column, description, keyword_lst):
		# Fill missing values in a specified column based on keywords in the 'Description' column.
		condition = df[column].isna() | ~df[column].isin(keyword_lst)
		for keyword in keyword_lst:
			 df.loc[condition & df[description].str.contains(keyword, na=False), column] = keyword
		return df
	def match_closest_val(value, choices, threshold=80):
		# This function find the closest matching string from a list of choices based on a given value.
		best_match, best_score = process.extractOne(value, choices, scorer=fuzz.partial_ratio)
		if best_score>=threshold:
			return best_match
		else:
			return value

	def get_supply_info_for_model_year(supply_info, manufactor, model, year):
		# This function returns the supply score for a given car model and year, using fuzzy matching to find the best match. 
		# Since the car model provided by the writer in a freeform manner, the '=' was replaced with 'similar to'to avoid spelling mistakes
		matching_supply = [supply for supply in supply_info if (supply['manufactor'] == manufactor) and 
						(fuzz.partial_ratio(model.lower(), supply['model'].lower()) >= 70) and (supply['Year'] == int(year))]
		if matching_supply:
			return matching_supply[0]['Supply_score']
		return None

	def get_supply_info(keyword):
		# This function returns a list of dictionaries containing the car model, year, and supply score from the gov API page.
		supply_info = []
		try:
			url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=5e87a7a1-2f6f-41c1-8aec-7216d52a6cf6'
			response = requests.get(url)
			if not response.status_code == 200:
				print (f"Could not fetch data from API website. Got status code: {response.status_code}")
			results_page = response.json() 
			for item in results_page['result']['records']:
				if item['tozar'] in keyword:
					supply_info.append({'manufactor': item['tozar'], 'Year': item['shnat_yitzur'], 'model': item['kinuy_mishari'], 'Supply_score': item['mispar_rechavim_pailim']})
			return supply_info
		except Exception as e:
			print(f"Could not get Supply info for {keyword}. Got error: {str(e)}")
			return []

	def get_Cre_date_in_days(cre_date):
		# This function takes a date and returns the number of days that have passed since that date.
		try:
			if not cre_date == None:
				cre_date = pd.to_datetime(cre_date, dayfirst=True)
				delta = (datetime.datetime.now() - cre_date).days
				return int(delta)
		except ValueError:
			return None

	def sale_score(description, good_keywords_lst, bad_keywords_lst):
		# This function return a score based on words mentiond in the description
		try:
			score = 0
			for Gword in good_keywords_lst:
				if Gword in description:
					score += 1
			for Bword in bad_keywords_lst:
				if Bword in description:
					score -= 1
			return score
		except ValueError:
			return None

	categoricals = ['Prev_ownership', 'Curr_ownership', 'Engine_type', 'Gear']
	strings = ['Area','City','Color','Description','manufactor','model']
	integers = ['Year','Hand', 'capacity_Engine', 'Pic_num', 'Km', 'Test', 'Supply_score']
    
	df[categoricals] = df[categoricals].astype('category')
	df[strings] = df[strings].astype(pd.StringDtype())
	df[integers] = df[integers].replace({',': ''}, regex=True).apply(pd.to_numeric, errors='coerce').astype('Int64')
    
    # Fill missing values in 'Curr_ownership' based on keywords in the 'Description' column
	ownership_lst = ['פרטית', 'ליסינג', 'חברה', 'השכרה']
	df = missing_val_from_description(df, 'Curr_ownership', 'Description', ownership_lst)
	df['Curr_ownership'].replace({'פרטית':'private', 'ליסינג':'leasing', 'חברה':'company', 'השכרה':'renting','אחר':'other', 'לא מוגדר':'other'},inplace = True)
	df['Curr_ownership'] = df['Curr_ownership'].fillna('other') #fill none values as 'other'
    
   	 # Fill missing values in 'Engine_type' based on keywords in the 'Description' column
	Engine_type_lst = ['דיזל','גז', 'בנזין', 'חשמלי', 'היברידי']
	df = missing_val_from_description(df, 'Engine_type', 'Description', Engine_type_lst)
	df['Engine_type'].replace({'היברידי':'hybrid','היבריד':'hybrid','בנזין':'gasoline','דיזל':'diesel','גז':'gas','טורבו דיזל':'turbo diesel','חשמלי':'electric'}, inplace = True)
    
    # Add new categories to 'Gear' and fill missing values based on keywords in the 'Description' column
	new_categories = ['ידני', 'הילוכים'] # Adding common words describing gear type to the list of categories. 
	df['Gear'] = df['Gear'].cat.add_categories(new_categories)
	Gear_type_lst = ['הילוכים', 'אוטומט','רובוטית','אוטומטית','טיפטרוניק','ידני','ידנית']
	df = missing_val_from_description(df, 'Gear', 'Description', Gear_type_lst)
	df['Gear'].replace({'הילוכים':'Manual','ידני':'Manual', 'אוטומט':'Automatic','רובוטית':'Automatic','אוטומטית':'Automatic','טיפטרוניק':'Tiptronic','ידנית':'Manual','לא מוגדר':None}, inplace = True)
	df['Gear'] = df['Gear'].fillna(df['Gear'].mode()[0]) # Empty vals wes filled using the most frequent val
    
    # Normalize city and area names and correct values based on frequency
	df['City'] = df['City'].str.replace('[,\\.]', '', regex=True)
	df['City'] = df['City'].str.replace('יי', 'י', regex=True)
	frequent_areas = df['Area'].value_counts()
	correct_areas = frequent_areas[frequent_areas > 5].index.tolist()
	df['Area'] = df['Area'].apply(lambda x: match_closest_val(x, correct_areas) if pd.notna(x) else x)
    
	# Create a dictionary of cities by area to fill missing 'Area' values based on 'City'
	city_dict = {area: list(group['City'].dropna().unique()) for area, group in df.groupby('Area')}
	df['Area'] = df.apply(lambda row: next((area for area, cities in city_dict.items() if row['City'] in cities), row['Area']), axis=1)

    # Fill missing 'Km' and 'capacity_Engine' values based on group by method
	df['Km'] = df.groupby(['Year'])['Km'].transform(lambda x: x.fillna(round(x.mean())))
	df['capacity_Engine']=df.groupby(['manufactor','model', 'Year'])['capacity_Engine'].fillna(df['capacity_Engine'].mode()[0])

    # Correct frequent values in 'model' column
	df['model'] = df['model'].str.strip()
	df['model'] = df.apply(lambda row: re.sub(r'\(.*?\)', '', row['model']).strip(), axis=1)
	df['model'] = df.apply(lambda row: row['model'].replace(row['manufactor'], '').strip(), axis=1)
	df.loc[(df['manufactor'] == 'מיני') & (df['model'] == 'קופר'), 'manufactor'] = 'ב מ וו'
	df.loc[(df['manufactor'] == 'מיני') & (df['model'] == 'קופר'), 'model'] = 'MINI COOPER'
	df.loc[(df['manufactor'] == 'מיני') & (df['model'] != 'קופר'), 'manufactor'] = 'ב מ וו'
	df.loc[(df['manufactor'] == 'מיני') & (df['model'] != 'קופר'), 'model'] = 'MINI ' + df['model']
	df['manufactor'].replace({'Lexsus':'לקסוס','מאזדה':'מזדה'},inplace = True)
	df['model'].replace({'אוקטביה':'octavia','פיקנטו':'picanto','גולף':'golf','קורולה':'corolla','ספארק':'spark'}, inplace = True)
    
    # Add supply score for missing rows based on model name similarity
	suplly_df = df.loc[pd.isna(df['Supply_score'])]
	model_dict = {manufactor: list(group['model'].dropna().unique()) for manufactor, group in suplly_df.groupby('manufactor')}
	supply_info= get_supply_info(model_dict.keys())
	df['Supply_score'] = df.apply(lambda row: get_supply_info_for_model_year(supply_info, row['manufactor'], row['model'], row['Year'])
                               if pd.isna(row['Supply_score']) else row['Supply_score'], axis=1)
	df['Supply_score'] = df.groupby(['manufactor', 'Year'])['Supply_score'].transform(lambda x: x.fillna(x.mean()))
    
    # Add a column for the count of each 'Area'
	df['Cre_days'] = df['Cre_date'].apply(get_Cre_date_in_days)
	df['Cre_days'] = df['Cre_days'].transform(lambda x: x.fillna(x.median()))
    
    # Add a new score column based on keywords in the 'Description'
	good_keywords_lst = ['ללא','מתוחזק','מצב מצויין','מצב טוב', 'חדש', 'ללא תקלות', 'שמור','אמין']
	bad_keywords_lst = ['תקול','תיקון','רועד','רעידות','שריטה','מכה','לא תקין','ישן','לא עובד','מקולקל','שרוט','שבר','מעט']
	df['own_Score'] = df['Description'].apply(lambda x: sale_score(x, good_keywords_lst, bad_keywords_lst))
    
    # Add indication to the num of ads in the area
	df['Area_Count'] = df.groupby('Area')['Area'].transform('count')
    
    # Drop unnecessary columns and rows with missing values
	df = df.drop(columns=['Prev_ownership','Repub_date','Color','Test','Pic_num','Cre_date','Description'])
	df = df.dropna()
	return df
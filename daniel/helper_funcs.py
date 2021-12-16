import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def get_redfin_csv(upper_lim=12000000):
    '''
    Imports scraped Redfin CSV data and:
        1 renames & drops unwanted columns, 
        2 drops unwanted States, 
        3 drops unwanted Prop_Types
        4 drops Squarefootage, Beds, Baths NaN rows
        5 removes outliers for SF, Price, YearBuilt, Days_on_Market
            Price outlier can be set with 'upper_lim' param: default = $12 mil
        6 fills NaNs for Lot_Size, YearBuilt
    '''

    print('----pulling Redfin data from Azure storage----')
    redfin = pd.read_csv('https://nycdsacapstone2021.blob.core.windows.net/additionaldata/redfin_cleaned_stage_1.csv', index_col='MLS#')
    # drop unwanted columns
    redfin.drop(['Unnamed: 0',
        'NEXT OPEN HOUSE START TIME', 
        'NEXT OPEN HOUSE END TIME', 'ZIP OR POSTAL CODE',
        'URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)',
        'SOURCE','FAVORITE','INTERESTED'],
        axis=1, inplace=True)
    # rename columns
    redfin.rename(columns={
        'SALE TYPE':'Sale_Type',
        'SOLD DATE':'Sold_Date',
        'PROPERTY TYPE':'Prop_Type',
        'STATE OR PROVINCE':'State', 
        'SQUARE FEET':'SF', 
        'LOT SIZE':'Lot_Size', 
        'YEAR BUILT':'YearBuilt',
        'DAYS ON MARKET':'Days_on_Mkt', 
        '$/SQUARE FEET':'px_perSF', 
        'HOA/MONTH':'HOA_perMonth'
    }, inplace=True)
    # Fix State Names & remove unwanted States
    redfin.State.replace({'Fl':'FL','fl':'FL','sc':'SC',}, inplace=True)
    redfin.drop(redfin[redfin.State.isin(['TX','NV','BI'])].index, inplace=True)
    # Remove unwanted Property Types
    unwanted_types = ['Vacant Land','Unknown','Moorage','Other','Timeshare','Parking','Mobile/Manufactured Home']
    redfin.drop(
        redfin[redfin.Prop_Type.isin(unwanted_types)].index, inplace=True)
    # Need to drop properties with SquareFootage == NaN as its the most important feature...
    redfin.drop(redfin[redfin.SF.isna()].index, inplace=True)
    # Need to drop properties with BOTH Beds & Baths == NaN as its the most important feature...
    redfin.drop(redfin[(redfin.BEDS.isna() | (redfin.BEDS==0)) | \
        (redfin.BATHS.isna() | (redfin.BATHS==0))].index, inplace=True)

    # # Remove above SF 19999 and PRICE above 5mil
    redfin.drop(redfin[(redfin.SF>19999) | (redfin.PRICE>upper_lim)].index, inplace=True)
    # Remove SF below 150 and PRICE below 10000
    redfin.drop(redfin[(redfin.SF<101) | (redfin.PRICE<10000)].index, inplace=True)

    # Remove extreme outliers for YearBuilt & Days on Market
    redfin.drop(redfin[(redfin.YearBuilt<1800) | (redfin.Days_on_Mkt>365)].index, inplace=True)

    # Fill NaN values
    nan_filler = redfin.groupby(['zip','Prop_Type']).agg('mean')
    nan_filler['sf_lot_ratio'] = nan_filler.SF / nan_filler.Lot_Size

    # For lot_size, determine sf to lot ratio per zip+Prop_Type
    redfin.loc[redfin.Lot_Size.isna(),'Lot_Size'] = \
    redfin[redfin.Lot_Size.isna()].apply(lambda r: r.SF / nan_filler.loc[(r.zip,r.Prop_Type),'sf_lot_ratio'], axis=1)
    # Fill rest with 0
    redfin.loc[redfin.Lot_Size.isna(),'Lot_Size'] = 0
    # For year built, use avg per zip+Prop_Type
    redfin.loc[redfin.YearBuilt.isna(),'YearBuilt'] = \
    redfin[redfin.YearBuilt.isna()].apply(lambda r: nan_filler.loc[(r.zip,r.Prop_Type),'YearBuilt'], axis=1)
    # Fill rest with 1990
    redfin.loc[redfin.YearBuilt.isna(),'YearBuilt'] = 1990

    # Create "Detached" feature (==SingleFam or Ranch)
    redfin['Detached'] = redfin.Prop_Type.apply(lambda x: 1 if (x=='Single Family Residential') | (x=='Ranch') else 0)

    print('----Done----')
    return redfin

def get_schools():
    '''
    Imports scraped GreatSchools data and:
        drops unwanted States, 
    '''

    print('----pulling schools data from Azure storage----')
    schools = pd.read_json('https://nycdsacapstone2021.blob.core.windows.net/additionaldata/great_schools.json')
    schools = schools[schools.state.isin(['FL','NC','GA','VA','MD','SC','WV','DC'])]

    print('----Done----')
    return schools

def get_hosp():
    '''
    Imports hospital data:
    '''
    hosp = pd.read_csv('https://nycdsacapstone2021.blob.core.windows.net/additionaldata/Hospitals_geocoded.csv')
    hosp = hosp[hosp.Overall_Rating>3]
    return hosp

def get_all(upper_lim=12000000):
    '''
    Imports Redfin and Schools and Hosp data and:
        joins average school rating per zip code with redfin data
    '''
    redfin = get_redfin_csv(upper_lim)
    schools = get_schools()
    hosp = get_hosp()

    print('----merging all data----')
    av_ratings = schools.groupby('zip').agg("mean")['overallRating']
    redfin = redfin.merge(av_ratings, how='left', left_on='zip', right_index=True)
    redfin.rename(columns={'overallRating':'school_rating'}, inplace=True)

    redfin = redfin.merge(hosp.groupby('ZIP_Code').agg('count')['Facility_Name'], how='left', left_on='zip', right_index=True)
    redfin.rename(columns={'Facility_Name':'Hosp_count'}, inplace=True)
    redfin.loc[redfin.Hosp_count.isna(),'Hosp_count'] = 0

    print('----Done----')
    print(f'Shape: {redfin.shape}')

    return redfin

def get_zipdata():
    '''
    Pulls Zipcode Level Data
    '''
    print('----pulling ZipCode data from Azure storage----')
    zipdata = pd.read_csv('https://nycdsacapstone2021.blob.core.windows.net/additionaldata/final_zip_data.csv', index_col=0)
    unwanted = ['Zip_count','Survey_Date', 'FIPS_State', 'FIPS_County', 'Region_Code', 
              'Division_Code', 'State_y', 'state_abbrev', 'County_Name']
    zipdata.drop(columns=unwanted, inplace=True)

    # Fill NaN values with 0 or mean_value()
    zipdata.loc[zipdata.over_65_ratio.isna(),'over_65_ratio'] = 0
    zipdata.loc[zipdata.Hosp_count.isna(),'Hosp_count'] = 0
    zipdata.loc[zipdata.HPI.isna(),'HPI'] = 0
    zipdata.loc[zipdata.Demand_score.isna(),'Demand_score'] = 0
    zipdata.loc[zipdata.Supply_score.isna(),'Supply_score'] = 0
    zipdata.loc[zipdata.listviews_vs_US.isna(),'listviews_vs_US'] = 0
    zipdata.loc[zipdata.med_days_on_mkt.isna(),'med_days_on_mkt'] = 0
    zipdata.loc[zipdata.nielson_rank.isna(),'nielson_rank'] = 0
    zipdata.loc[zipdata.Zillow_HVF.isna(),'Zillow_HVF'] = 0
    zipdata.loc[zipdata.school_rating.isna(),'school_rating'] = 5
    zipdata.loc[zipdata.UE_rate.isna(),'UE_rate'] = zipdata.UE_rate.mean()
    zipdata.loc[zipdata.BEA_percap_income.isna(),'BEA_percap_income'] = zipdata.BEA_percap_income.mean()

    # Remove unused & redundant columns
    zipdata.drop(columns=zipdata.columns[-12:], inplace=True)
    zipdata.drop(columns=zipdata.columns[:5], inplace=True)

    # Generate population features
    zipdata['Blacks_ratio'] = zipdata.BlackPopulation / zipdata.Population
    zipdata['Hispanics_ratio'] = zipdata.HispanicPopulation / zipdata.Population
    zipdata['Asians_ratio'] = zipdata.AsianPopulation / zipdata.Population
    zipdata['Indians_ratio'] = zipdata.IndianPopulation / zipdata.Population
    zipdata['Others_ratio'] = zipdata.OtherPopulation / zipdata.Population
    zipdata['Male_ratio'] = zipdata.MalePopulation / zipdata.Population
    zipdata.loc[zipdata.Blacks_ratio.isna(),'Blacks_ratio'] = 0
    zipdata.loc[zipdata.Hispanics_ratio.isna(),'Hispanics_ratio'] = 0
    zipdata.loc[zipdata.Asians_ratio.isna(),'Asians_ratio'] = 0
    zipdata.loc[zipdata.Indians_ratio.isna(),'Indians_ratio'] = 0
    zipdata.loc[zipdata.Others_ratio.isna(),'Others_ratio'] = 0
    zipdata.loc[zipdata.Male_ratio.isna(),'Male_ratio'] = 0

    zipdata.drop(columns=['BlackPopulation','HispanicPopulation','AsianPopulation','WhitePopulation',
                        'IndianPopulation','OtherPopulation','MalePopulation','FemalePopulation'], inplace=True)

    print('----Done----')
    return zipdata

def get_modelzip():
    all_feats = ['Population', 'Blacks_ratio', 'Hispanics_ratio', 'Asians_ratio', 
             'Indians_ratio', 'Others_ratio', 'Male_ratio', 'HouseholdsPerZipCode', 
             'MedianAge', 'school_rating','over_65_ratio', 'IncomePerHousehold', 
             'NumberOfBusinesses', 'UE_rate', 'HPI', 'Demand_score', 'Supply_score', 
             'listviews_vs_US', 'med_days_on_mkt', 'nielson_rank']
    return get_zipdata()[all_feats]
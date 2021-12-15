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
    redfin.drop(redfin[(redfin.BEDS.isna() | (redfin.BEDS==0)) & \
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

    redfin = redfin.merge(hosp.groupby('ZIP_Code').agg('count')['Facility_Name'], how='left', left_on='zip', right_index=True)
    redfin.rename(columns={'Facility_Name':'Hosp_count'}, inplace=True)
    redfin.loc[redfin.Hosp_count.isna(),'Hosp_count'] = 0

    print('----Done----')
    print(f'Shape: {redfin.shape}')

    return redfin

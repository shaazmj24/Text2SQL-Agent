from faker import Faker
import psycopg2
import os
import random
from datetime import timedelta
from dotenv import load_dotenv


Faker.seed(42)
fake = Faker()  

load_dotenv()   

conn = psycopg2.connect(os.getenv("database_url"))                    #connect to postgrelSQL
cursor = conn.cursor()                                                #command pointer -> database 

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#user table 

north_amercia = [
    "United States", "Canada"
] 
europe = [
    "United Kingdom", "Germany", "France", "Netherlands", "Spain",
    "Italy", "Sweden", "Norway", "Denmark", "Switzerland", "Poland", "Ireland", "Portugal",  
    "Findland", "Austria"
]
others = [
    "Pakistan", "India", "China", "Bangladesh", "Indonesia",
    "Nigeria", "Philippines", "Vietnam", "Egypt", "Kenya",
    "Brazil", "Colombia", "Nepal", "South Africa", "Thailand", "Japan"
]

def generate_country(): 
    region = random.choices(
        ["north_america", "europe", "developing"],  
        weights=[0.6, 0.3, 0.1], 
        k=1
    )[0]   
    
    if region == "north_amercia":   
        return random.choice(north_amercia) 
    elif region == "europe": 
        return random.choice(europe) 
    else:  
        return random.choice(others)
    
def get_country_tier(country): 
    if country in north_amercia or country in europe: 
        return 'rich' 
    elif country in ["India", "China", "Thialand", "South Africa", "Japan"]: 
        return 'mid'
    else:
        return 'developing'

user_data = []

#create table 
#40k rows / users 
for i in range(40000): 
    created_at = fake.date_time_between(start_date='-3y', end_date='now')
    last_seen = fake.date_time_between(start_date=created_at, end_date='now') 
    country = generate_country 
    source = random.choice(['google', 'social media', 'direct', 'youtube', 'referral']) 
    is_paying = random.random() < 0.3
    
    cursor.execute("""
        INSERT INTO users (name, email, country, source, is_paying, is_active, created_at, last_seen_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        fake.name(),
        fake.email(),
        country,      
        source, 
        is_paying,                                                         # 30% users are paying . avoided random.choice(TRUE, FALSE) cuz 50/50 or 50% distribution which is unrealistic 
        random.random() < 0.85,                                                       # 85 percent users r active   
        created_at, 
        last_seen
    ))
    user_id = cursor.fetchone()[0]                                          # grabs the id postgreSQL just generated through RETURNING ID
    
    user_data.append({                                                        #store everything that affects other tables 
        'id': user_id,  
        'created_at' : created_at, 
        'source': source, 
        'country_tier': get_country_tier(country),  
        'is_paying': is_paying 
                      })                                                           # adds it to the user_list 
    
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#order table 

# define all patterns as data 
source_plan_weights = {
    'referral':   {'free': 20, 'pro_monthly': 60, 'enterprise_annual': 20},            #more likely to pay . trust friend/family 
    'direct':     {'free': 25, 'pro_monthly': 55, 'enterprise_annual': 20},
    'youtube':    {'free': 40, 'pro_monthly': 55, 'enterprise_annual': 5},
    'social_media':  {'free': 60, 'pro_monthly': 35, 'enterprise_annual': 5},
    'google':     {'free': 60, 'pro_monthly': 35, 'enterprise_annual': 5}
}

country_plan_weights = {
    'rich':       {'free': 10, 'pro_monthly': 55, 'enterprise_annual': 35},
    'mid':        {'free': 35, 'pro_monthly': 55, 'enterprise_annual': 10},
    'developing': {'free': 70, 'pro_monthly': 28, 'enterprise_annual': 2},
}


def generate_plan(source, country_tier):   
    plan_type = ['free', 'pro_monthly', 'enterprise_annual']                #plan_type depends on country_tier and source so p1 * p2 
    
    source_w = source_plan_weights[source] 
    country_w = country_plan_weights[country_tier]    
    
    combined_w = [
        source_w[p] * country_w[p] for p in plan 
    ] 
    return random.choices(plan, weights=combined_w, k=1)[0]

#orders table 
for i in range(200000):   
    rand_user = random.choice(user_data) 
    user_id = rand_user['id'] 
    signedup_at = rand_user['created_at']   
    plan = generate_plan(rand_user['source'], rand_user['country_tier'])
    plan_map = {
        'free': 0, 
        'pro_monthly': 29.99, 
        'enterprise_annual': 299.99 
        }  
    created_at = fake.date_time_between(start_date=signedup_at, end_date='now')  
    is_refunded = random.random() < 0.1
    if is_refunded: 
        refunded_at = fake.date_time_between(start_date=created_at, end_date='now')
    else: 
        refunded_at = None 
    
    cursor.execute("""
        INSERT INTO orders (user_id, plan_type, price, order_status, is_refunded, refunded_at, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,          
        plan,      
        plan_map[plan], 
        random.choice(
            ['pending', 'completed', 'cancelled'], 
            weights=[10, 70, 20], 
            k=1)[0], 
        is_refunded, 
        refunded_at, 
        created_at, 
    ))  
    
    

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#subscrip table 

source_churn_rate = {
    'referral':   0.05,                    # 5% churn ; best customers
    'direct':     0.08,
    'youtube':    0.25,                    # excited but leave fast
    'social_media':  0.30,
    'google':     0.15
} 

plan_churn_rate = {
    'free':               0.30,
    'pro_monthly':        0.15,
    'enterprise_annual':  0.05,             # almost never churn
}
  
user_lookup = {u['id']: u for u in user_data}

for user_id in user_lookup:   
    signedup_at = user_lookup[user_id]['created_at'] 
    started = fake.date_time_between(start_data=signedup_at, end_date='now')      
    cursor.execute("""
        INSERT INTO subscrip (user_id, plan_type, price, sub_status, auto_renew, started_at, ends_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s. %s)
    """, (
        user_id,  
        
    ))






















conn.commit()        #saves everything permanently
cursor.close() 
conn.close()










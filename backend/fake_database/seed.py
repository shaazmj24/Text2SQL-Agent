from faker import Faker
import psycopg2
import os
import random
from datetime import timedelta , datetime 
from dotenv import load_dotenv


Faker.seed(42)
fake = Faker()  

load_dotenv()   

conn = psycopg2.connect(os.getenv("database_url"))                      #connect to postgrelSQL
cursor = conn.cursor()                                                  #command pointer -> database 

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#user table 

north_america = [
    "United States", "Canada"
] 
europe = [
    "United Kingdom", "Germany", "France", "Netherlands", "Spain",
    "Italy", "Sweden", "Norway", "Denmark", "Switzerland", "Poland", "Ireland", "Portugal",  
    "Finland", "Austria"
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
    
    if region == "north_america":   
        return random.choice(north_america) 
    elif region == "europe": 
        return random.choice(europe) 
    else:  
        return random.choice(others)
    
def get_country_tier(country): 
    if country in north_america or country in europe: 
        return 'rich' 
    elif country in ["India", "China", "Thailand", "South Africa", "Japan"]: 
        return 'mid'
    else:
        return 'developing' 
    
#seasonality pattern  
#jan-march more people pay cuz new year motivation etc 
#may-july people r inactive. holidays etc  
#1.3, 0.7 etc after seasonality. before, each month was equally given 1 so no effect 
def season_multiplier(month):  
    if month in [1, 2, 3]: 
        return {
            'free': 0.7, 
            'pro_monthly': 1.3, 
            'enterprise_annual': 1.4
                } 
    elif month in [5, 6, 7]:  
        return {
            'free': 1.3, 
            'pro_monthly': 0.8, 
            'enterprise_annual': 0.7
                }  
    else: 
        return {
            'free': 1.0, 
            'pro_monthly': 1.0, 
            'enterprise_annual': 1.0
                } 


# define all patterns as data 
source_plan_weights = {
    'referral':   {'free': 20, 'pro_monthly': 60, 'enterprise_annual': 20},            #more likely to pay . trust friend/family 
    'direct':     {'free': 25, 'pro_monthly': 55, 'enterprise_annual': 20},
    'youtube':    {'free': 68, 'pro_monthly': 27 , 'enterprise_annual': 5},
    'social_media':  {'free': 70, 'pro_monthly': 25, 'enterprise_annual': 5},
    'google':     {'free': 60, 'pro_monthly': 35, 'enterprise_annual': 5}
}

country_plan_weights = {
    'rich':       {'free': 10, 'pro_monthly': 55, 'enterprise_annual': 35},
    'mid':        {'free': 35, 'pro_monthly': 55, 'enterprise_annual': 10},
    'developing': {'free': 70, 'pro_monthly': 28, 'enterprise_annual': 2},
}


def generate_plan(source, country_tier, month):   
    plans = ['free', 'pro_monthly', 'enterprise_annual']                #plan_type depends on country_tier, source, month, seasonality expected plan p1 * p2 * p3
    
    source_w = source_plan_weights[source] 
    country_w = country_plan_weights[country_tier]  
    season_w = season_multiplier(month)    
    
    combined_w = [
        source_w[p] * country_w[p] * season_w[p] for p in plans
    ]  
    return random.choices(plans, weights=combined_w, k=1)[0] 

user_data = []

#create user table 
#5k rows / users 
for i in range(5000): 
    created_at = fake.date_time_between(start_date='-3y', end_date='now') 
    country = generate_country()
    source = random.choice(['google', 'social_media', 'direct', 'youtube', 'referral'])  
    plan = generate_plan(source, get_country_tier(country), created_at.month) 
    is_paying = plan != 'free'  
    if is_paying:  
        is_active = random.random() < 0.85                                     #85 percent of users r active 
    else: 
        is_active = random.random() < 0.60
     
    if is_active: 
        last_seen = fake.date_time_between(start_date='-30d', end_date='now') 
    else: 
        last_seen = fake.date_time_between(start_date=created_at, end_date='-60d')
    
    cursor.execute("""
        INSERT INTO users (name, email, country, source, plan, is_paying, is_active, created_at, last_seen_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)                     
        RETURNING id
    """, (
        fake.name(),
        fake.unique.email(),
        country,      
        source, 
        plan, 
        is_paying,                                                         
        is_active,                                                          
        created_at, 
        last_seen
    ))
    user_id = cursor.fetchone()[0]                                          # grabs the id postgreSQL just generated through RETURNING ID
    
    user_data.append({                                                        #store everything that affects other tables 
        'id': user_id,  
        'created_at' : created_at, 
        'source': source, 
        'country_tier': get_country_tier(country),   
        'plan': plan,
        'is_paying': is_paying, 
        'is_active': is_active
                      })                                                           # adds it to the user_list 
    
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#order table 
 
 
price_map = {
    'pro_monthly': 29.99,
    'enterprise_annual': 299.99
}

# stronger yearly growth + seasonal dips
monthly_order_targets = {
    (2023, 1): 450,
    (2023, 2): 500,
    (2023, 3): 550,
    (2023, 4): 480,
    # summer dip
    (2023, 5): 350,
    (2023, 6): 320,
    (2023, 7): 340,
    # recovery
    (2023, 8): 450,
    (2023, 9): 520,
    (2023, 10): 600,
    (2023, 11): 650,
    (2023, 12): 620,

    (2024, 1): 850,
    (2024, 2): 920,
    (2024, 3): 980,
    (2024, 4): 820,
    # summer dip
    (2024, 5): 620,
    (2024, 6): 580,
    (2024, 7): 600,
    # recovery
    (2024, 8): 760,
    (2024, 9): 900,
    (2024, 10): 980,
    (2024, 11): 1050,
    (2024, 12): 1010,

    (2025, 1): 1300,
    (2025, 2): 1400,
    (2025, 3): 1500,
    (2025, 4): 1250,
    # summer dip
    (2025, 5): 950,
    (2025, 6): 880,
    (2025, 7): 920,
    # recovery
    (2025, 8): 1180,
    (2025, 9): 1380,
    (2025, 10): 1480,
    (2025, 11): 1560,
    (2025, 12): 1520,

    (2026, 1): 1650,
    (2026, 2): 1750,
    (2026, 3): 1850,
    (2026, 4): 1550,
    # current summer slowdown
    (2026, 5): 1200
}

# only paying users can generate orders
paying_users = [
    user for user in user_data
    if user['plan'] != 'free'
] 

for (year, month), count in monthly_order_targets.items():

    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, 28)

    for i in range(count):

        rand_user = random.choice(paying_users)

        user_id = rand_user['id']
        signedup_at = rand_user['created_at']

        # prevent orders before signup
        if signedup_at > month_end:
            continue

        created_at = fake.date_time_between(
            start_date=max(month_start, signedup_at),
            end_date=month_end
        )
        order_plan = rand_user['plan']

        order_status = random.choices(
            ['completed', 'pending', 'cancelled'],
            weights=[75, 5, 20],
            k=1
        )[0]

        # refunds only for completed orders
        if order_status == 'completed':
            refund_rate = (
                0.05 if order_plan == 'enterprise_annual'
                else 0.12
            )
            is_refunded = random.random() < refund_rate
        else:
            is_refunded = False

        refunded_at = (
            fake.date_time_between(start_date=created_at, end_date='now') 
            if is_refunded else None
        )
        cursor.execute("""
            INSERT INTO orders (
                user_id,
                plan_type,
                price,
                order_status,
                is_refunded,
                refunded_at,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            order_plan,
            price_map[order_plan],
            order_status,
            is_refunded,
            refunded_at,
            created_at
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
    'enterprise_annual':  0.05,                             # almost never churn
} 

plan_map = {
    'free': 0,
    'pro_monthly': 29.99,
    'enterprise_annual': 299.99
} 

def generate_sub_status(p, s): 
    plan_churn = plan_churn_rate[p] 
    source_churn = source_churn_rate[s] 
    final_churn =  0.7*plan_churn + 0.3*source_churn          #average churn rate or expected churn rate . plan matters more or dominates 
    
    if random.random() < final_churn:  
        return 'cancelled' 
    else: 
        return 'active'  
    

for user in user_data:

    user_id = user['id']
    signedup_at = user['created_at']
    source = user['source']
    plan = user['plan']
    started_at = fake.date_time_between(
        start_date=signedup_at,
        end_date='now'
    )

    sub_status = generate_sub_status(plan, source)

    if plan == 'enterprise_annual':
        ends_at = started_at + timedelta(days=365)
    elif plan == 'pro_monthly':
        ends_at = started_at + timedelta(days=30)
    else:
        ends_at = None

    if sub_status == 'cancelled':
        cancelled_at = fake.date_time_between(
            start_date=started_at,
            end_date='now'
        )
        updated_at = cancelled_at
        auto_renew = False
    else:
        cancelled_at = None
        updated_at = started_at
        auto_renew = random.random() < 0.9 if plan != 'free' else False

    cursor.execute("""
        INSERT INTO subscrip (
            user_id,
            plan_type,
            price,
            sub_status,
            auto_renew,
            started_at,
            ends_at,
            updated_at,
            cancelled_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        plan,
        price_map.get(plan, 0),
        sub_status,
        auto_renew,
        started_at,
        ends_at,
        updated_at,
        cancelled_at
    ))



#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#event table 

event_weights = {
    'login': 30,
    'view_dashboard': 25,
    'view_report': 18,
    'run_query': 12,
    'export_csv': 7,
    'invite_team_member': 4,
    'upgrade_clicked': 4
}

event_page_map = {
    'login': 'login',
    'view_dashboard': 'dashboard',
    'view_report': 'reports',
    'run_query': 'analytics',
    'export_csv': 'reports',
    'invite_team_member': 'settings',
    'upgrade_clicked': 'billing'
}

for user in user_data:

    user_id = user['id']
    signedup_at = user['created_at']
    is_active = user['is_active']
    plan = user['plan']

    if is_active:
        if plan == 'enterprise_annual':
            event_count = random.randint(80, 180)
        elif plan == 'pro_monthly':
            event_count = random.randint(40, 120)
        else:
            event_count = random.randint(10, 60)
    else:
        event_count = random.randint(0, 10)

    for i in range(event_count):

        event_type = random.choices(
            list(event_weights.keys()),
            weights=list(event_weights.values()),
            k=1
        )[0]

        page = event_page_map[event_type]

        created_at = fake.date_time_between(
            start_date=signedup_at,
            end_date='now'
        )

        cursor.execute("""
            INSERT INTO events (
                user_id,
                event_type,
                page,
                created_at
            )
            VALUES (%s, %s, %s, %s)
        """, (
            user_id,
            event_type,
            page,
            created_at
        ))




conn.commit()        #saves everything permanently
cursor.close() 
conn.close()










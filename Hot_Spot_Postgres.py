import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
from IPython.display import display

# Step 1: Connect & Query
conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='HOTSPOT',
    user='postgres',
    password='12554661'
)

query = """
SELECT acq_date, pv_en, re_nesdb
FROM public.hotspot 
WHERE acq_date BETWEEN '2023-11-01' AND '2024-10-31';
"""
df = pd.read_sql_query(query, conn)
display(df) 
conn.close()

# Step 2: Clean and Prepare
df.columns = df.columns.str.strip()
df['acq_date'] = pd.to_datetime(df['acq_date'])
df['acq_date_STR'] = df['acq_date'].dt.strftime('%d/%m/%Y')

# Show only every 15 days
#df = df[df['acq_date'].dt.day.isin([1, 15])]

# Show only every 5 days
df = df[df['acq_date'].dt.day % 5 == 0]

# Step 3: Group by region/province/date/pv_en
grouped = df.groupby(['re_nesdb', 'acq_date_STR', 'pv_en']).size().reset_index(name='Count')

# Step 4: Pivot with counts per region-province-date
pivot_counts = df.groupby(['re_nesdb', 'pv_en', 'acq_date_STR']).size().reset_index(name='Total')
pivot_counts['Region_Province'] = pivot_counts['re_nesdb'] + ' / ' + pivot_counts['pv_en']

# Convert 'acq_date_STR' back to datetime for sorting columns
pivot_counts['acq_date'] = pd.to_datetime(pivot_counts['acq_date_STR'], format='%d/%m/%Y')
heatmap_df = pivot_counts.pivot(index='Region_Province', columns='acq_date_STR', values='Total').fillna(0)

# Sort columns (dates) in ascending order
heatmap_df = heatmap_df[sorted(heatmap_df.columns, key=lambda x: pd.to_datetime(x, format='%d/%m/%Y'))]


# Step 5: Custom colormap
boundaries = [0, 3, 40, heatmap_df.to_numpy().max()+1]
colors = ['green', 'lightblue', 'red']
cmap = ListedColormap(colors)
norm = BoundaryNorm(boundaries, cmap.N, clip=True)

plt.figure(figsize=(22, 14))  # Slightly larger to fit text
sns.heatmap(
    heatmap_df,
    cmap=cmap,
    norm=norm,
    annot=True,
    fmt='.0f',
    annot_kws={"size": 8},  # Smaller, more compact font size
    linewidths=0.3,          # Slightly thinner lines
    cbar_kws={'label': 'Total Count'}
)

plt.title("Heatmap of Hotspots Every 5 Days (Grouped by Region & Province) from November 01, 2023 to October 31, 2024", fontsize=16)
plt.xlabel("Date (Every 15 Days)", fontsize=12)
plt.ylabel("Region / Province", fontsize=12, labelpad=10)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()

plt.savefig('hotspot_heatmap.png')
plt.show()

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm
from IPython.display import display

# Step 1: Connect & Query
conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='HOTSPOT',
    user='____',
    password='____'
)

query = """
SELECT acq_date, pv_en
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

# Filter every 5 days
df = df[df['acq_date'].dt.day % 5 == 0]

# Step 3: Group by province and date
grouped = df.groupby(['pv_en', 'acq_date_STR']).size().reset_index(name='Total')

# Convert 'acq_date_STR' back to datetime for sorting columns
grouped['acq_date'] = pd.to_datetime(grouped['acq_date_STR'], format='%d/%m/%Y')

# Step 4: Pivot table (Province vs. Date)
heatmap_df = grouped.pivot(index='pv_en', columns='acq_date_STR', values='Total').fillna(0)

# Sort date columns
heatmap_df = heatmap_df[sorted(heatmap_df.columns, key=lambda x: pd.to_datetime(x, format='%d/%m/%Y'))]

# Step 5: Custom colormap
boundaries = [0, 3, 40, heatmap_df.to_numpy().max() + 1]
colors = ['green', 'lightblue', 'red']
cmap = ListedColormap(colors)
norm = BoundaryNorm(boundaries, cmap.N, clip=True)

# Step 6: Plot Heatmap
plt.figure(figsize=(22, 14))
sns.heatmap(
    heatmap_df,
    cmap=cmap,
    norm=norm,
    annot=True,
    fmt='.0f',
    annot_kws={"size": 8},
    linewidths=0.3,
    cbar_kws={'label': 'Total Count'}
)

plt.title("Heatmap of Hotspots Every 5 Days by Province (Nov 01, 2023 – Oct 31, 2024)", fontsize=16)
plt.xlabel("Date (Every 5 Days)", fontsize=12)
plt.ylabel("Province", fontsize=12, labelpad=10)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()

plt.savefig('hotspot_heatmap_by_province.png')
plt.show()

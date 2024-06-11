import pandas as pd

from data import area_df
import matplotlib.pyplot as plt
import seaborn as sns
import os


#####################################################################
# Adding the freaking calibri font
import matplotlib.font_manager as font_manager

font_path = '../../calibri-font-family/calibri-regular.ttf'
font_manager.fontManager.addfont(font_path)

#####################################################################
# Df manipulation

def make_cfg_string(row):
    #avoiding the use of f-strings for compatibility with python 3.5
    return "w{:,.0f}_t{:,.0f}".format(row['warps'], row['threads'], row['ports'])

area_df['cfg'] = area_df.apply(make_cfg_string, axis=1)

#make area in mm^2
area_df['area'] = area_df['area'] / 1e6


#####################################################################
# Plotting

cm = 1/2.54  # centimeters in inches
scale = 5
#subdividing the plot into 4 subplots

fig, axs = plt.subplots(3, 2, figsize=(8.45/3*cm*scale, 8.45/2.5*cm*scale))

#plot area, y axis is area, x axis is cfg, and we have a vertical plot for each memory configuration
#filter l2cache==0
sns.lineplot(x='cfg', y='area', hue='ports', data=area_df.loc[area_df['l2cache'] == 0], ax=axs[0, 0])
for tick in axs[0,0].get_xticklabels():
    tick.set_rotation(30)
#plot name
axs[0, 0].set_title('Core Area')
#change axis name
axs[0, 0].set_yscale('log')
axs[0, 0].set_ylabel('Area (mm^2)')
#remove x axis name
axs[0, 0].set_xlabel('')
#remove legend
axs[0, 0].get_legend().remove()

#filter l2cache==1 && l3cache==0
sns.lineplot(x='cfg', y='area', hue='ports', markers='ports',data=area_df.loc[(area_df['l2cache'] == 1) & (area_df['l3cache'] == 0)], ax=axs[1, 0])
for tick in axs[1,0].get_xticklabels():
    tick.set_rotation(30)
#plot name
axs[1, 0].set_title('Core + L2 Area')
#make y axis log scale
axs[1, 0].set_yscale('log')
#change axis name
axs[1, 0].set_ylabel('Area (mm^2)')
#remove x axis name
axs[1, 0].set_xlabel('')
#remove legend
axs[1, 0].get_legend().remove()

#filter l3cache==1
sns.lineplot(x='cfg', y='area', hue='ports', data=area_df.loc[area_df['l3cache'] == 1], ax=axs[2, 0])
for tick in axs[2,0].get_xticklabels():
    tick.set_rotation(30)
#plot name
axs[2, 0].set_title('Core + L2 + L3 Area')
#change axis name
axs[2, 0].set_yscale('log')
axs[2, 0].set_ylabel('Area (mm^2)')
#remove x axis name
axs[2, 0].set_xlabel('')
#remove legend
axs[2, 0].get_legend().remove()

#plot area_ratio, y axis is area_ratio, x axis is cfg, and we have a vertical plot for each memory configuration
child_area_df = area_df[area_df['area_ratio'] != 1.0]

#filter l2cache==0
sns.lineplot(x='cfg', y='area_ratio', hue='ports', data=child_area_df.loc[child_area_df['l2cache'] == 0], ax=axs[0, 1])
for tick in axs[0,1].get_xticklabels():
    tick.set_rotation(30)
#plot name
axs[0, 1].set_title('Core Area Ratio')
#change axis name
axs[0, 1].set_ylabel('Area Ratio')
#remove x axis name
axs[0, 1].set_xlabel('')
#remove legend
axs[0, 1].get_legend().remove()

#filter l2cache==1 && l3cache==0
sns.lineplot(x='cfg', y='area_ratio', hue='ports', markers='ports', data=child_area_df.loc[(child_area_df['l2cache'] == 1) & (child_area_df['l3cache'] == 0)], ax=axs[1, 1])
for tick in axs[1,1].get_xticklabels():
    tick.set_rotation(30)
#plot name
axs[1, 1].set_title('Core + L2 Area Ratio')
#change axis name
axs[1, 1].set_ylabel('Area Ratio')
#remove x axis name
axs[1, 1].set_xlabel('')
#remove legend
axs[1, 1].get_legend().remove()

#filter l3cache==1
sns.lineplot(x='cfg', y='area_ratio', hue='ports', data=child_area_df.loc[child_area_df['l3cache'] == 1], ax=axs[2, 1])
for tick in axs[2,1].get_xticklabels():
    tick.set_rotation(30)
#plot name
axs[2, 1].set_title('Core + L2 + L3 Area Ratio')
#change axis name
axs[2, 1].set_ylabel('Area Ratio')
#remove x axis name
axs[2, 1].set_xlabel('')
#remove legend
axs[2, 1].get_legend().remove()



#change font to calibi and increase size
for ax in axs.flat:
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontname('Calibri')
        size = item.get_fontsize()
        item.set_fontsize(size * 1.15)

plt.tight_layout()

#####################################################################
# Save the plot

output_dir = "./scripts/outputs/00_area/"
os.makedirs(output_dir, exist_ok=True)
output_file = output_dir + "05_02_AREA"

plt.savefig(output_file + ".pdf", format='pdf', bbox_inches='tight',pad_inches=0)
plt.savefig(output_file + ".svg", format='svg', bbox_inches='tight',pad_inches=0)

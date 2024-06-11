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

fig, axs = plt.subplots(1, 2, figsize=(8.45/3*cm*scale, 8.45/7*cm*scale))

#plot area, y axis is area, x axis is cfg, and we have a vertical plot for each memory configuration
#add markers to each point
sns.lineplot(x='cfg', y='area', hue='ports', hue_order=[2,3,1], markers=True, style='ports', style_order=[2,3,1], data=area_df.loc[area_df['l3cache'] == 1], ax=axs[0], palette='tab10')
for tick in axs[0].get_xticklabels():
    tick.set_rotation(30)
#plot name
#axs[0].set_title('Core Area')
#change axis name
axs[0].set_yscale('log')
axs[0].set_ylabel('Area (mm^2)')
#remove x axis name
axs[0].set_xlabel('')
#remove legend
axs[0].get_legend().remove()
#add grid with minor ticks, but minor ticks are dotted
axs[0].grid(which='minor', linestyle=':', linewidth='0.5')
axs[0].grid(which='major')
#make guideline x lines dotted
axs[0].grid(axis='x', linestyle=':', linewidth='0.5')

#plot area_ratio, y axis is area_ratio, x axis is cfg, and we have a vertical plot for each memory configuration
child_area_df = area_df[area_df['area_ratio'] != 1.0]

#filter l3cache==1
# make port=2 have the same color as previous plot

sns.lineplot(x='cfg', y='area_ratio', hue='ports', style='ports', markers=True, data=child_area_df.loc[child_area_df['l3cache'] == 1], ax=axs[1],palette='tab10')
for tick in axs[1].get_xticklabels():
    tick.set_rotation(30)
#plot name
#axs[1].set_title('Area Overhead')
#change axis name
axs[1].set_ylabel('Area Overhead (%)')
#remove x axis name
axs[1].set_xlabel('')
#remove legend
axs[1].get_legend().remove()
#add grid
axs[1].grid()
axs[1].grid(axis='x', linestyle=':', linewidth='0.5')

#change font to calibi and increase size
for ax in axs.flat:
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontname('Calibri')
        size = item.get_fontsize()
        item.set_fontsize(size * 1.05)

#add common legend
handles, labels = axs[0].get_legend_handles_labels()
#make handles and labels start from the third element and then the other elements
handles = handles[2:] + handles[:2]
labels = ["1 port", "2 ports", "3 ports"]
fig.legend(handles, labels, loc=8, bbox_to_anchor=(0.5, - 0.06), ncol=3)

plt.tight_layout()

#####################################################################
# Save the plot

output_dir = "./scripts/outputs/00_area/"
os.makedirs(output_dir, exist_ok=True)
output_file = output_dir + "05_02_AREA_"

plt.savefig(output_file + ".pdf", format='pdf', bbox_inches='tight',pad_inches=0)
plt.savefig(output_file + ".svg", format='svg', bbox_inches='tight',pad_inches=0)

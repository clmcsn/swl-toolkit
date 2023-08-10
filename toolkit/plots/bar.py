from plots.utils import init_plot
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set(style="ticks")

def gen_plot(path):
    plt.grid()
    #font = {'fontname':'Serif'}
    #plt.xlabel(plt.get_xlabel(), **font)
    #plt.ylabel("cycles", **font)
    #plt.gca.set_xticklabels(plt.get_xticks(), **font)
    #plt.gca.set_yticklabels(plt.get_yticks(), **font)
    if path:
        plt.savefig(path, dpi =300, bbox_inches = "tight")
    else:
        plt.show()
    plt.clf()

def gen_bar(df, height, bar_names, hue=None, path=None, size=None, log=False, **kwargs):
    init_plot()
    if size : sns.set(rc={'figure.figsize': size})
    ax = sns.barplot(x = bar_names, y= height, data=df, dodge=True, hue=hue)
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right", rotation_mode="anchor")
    if log: ax.set_yscale('log')
    gen_plot(path)
    

#Each bar will have their axes
def gen_dualbar(df, h1, h2, bar_names, path=None, **kwargs):
    #generating new dataframe
    c_df = df[[h1, h2, bar_names]]
    #separating hue info
    c_df = c_df.melt(id_vars=bar_names, value_vars=[h1,h2])
    #making hue info categorical
    c_df['variable'] = pd.Categorical(c_df['variable'], [h1, h2])
    #making axes
    fig, ax1 = plt.subplots(figsize=(16, 6))
    ax2 = ax1.twinx()
    #plotting
    for ax, category in zip((ax1, ax2), c_df['variable'].cat.categories):
        sns.barplot(data=c_df[c_df['variable'] == category], x=bar_names, y='value', hue='variable', palette='Blues', ax=ax)
        ax.set_ylabel(f'{category}')
    gen_plot(path)
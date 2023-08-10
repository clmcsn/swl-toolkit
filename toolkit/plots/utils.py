import matplotlib.pyplot as plt

def init_plot():
    #setup
    SMALL_SIZE = 4
    MEDIUM_SIZE = 7
    BIGGER_SIZE = 10
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

def gen_bar_name(df_line, param_list, template, separator="_"):
    try:
        l = []
        for p in param_list:
            l.append(template[p].format(**{p:df_line[p]}))
        return separator.join(l)
    except Exception as e: print(e)
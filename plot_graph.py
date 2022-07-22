import matplotlib.pyplot as plt

def plot_frame(subplot_rows=2, subplot_cols=1, title='', xlabel='xlabel', ylabel='ylabel', log_scale=False, share_xaxis:str or bool=True, share_yaxis:str or bool=True):
    font_size = 25
    label_size = 20

    if subplot_rows == 1 and subplot_cols == 1 :
        fig, ax = plt.subplots(subplot_rows, subplot_cols, figsize=(7, 6), constrained_layout=True)
        plt.xticks(fontsize=font_size)
        plt.yticks(fontsize=font_size)
    else :
        fig, ax = plt.subplots(subplot_rows, subplot_cols, figsize=(7*subplot_cols, 6*subplot_rows), constrained_layout=True, sharex=share_xaxis, sharey=share_yaxis)
        #plt.ticklabel_format(axis='x', scilimits=(4,4))

        for i in range(subplot_rows):
            if subplot_cols > 1:
                for j in range(subplot_cols):
                    ax[i][j].tick_params(labelsize=label_size)
            else:
                ax[i].tick_params(labelsize=label_size)

    if title != '':
        plt.suptitle(title, fontsize = font_size + 10)
    #plt.ylim([0.5,1e7])

    if log_scale:
        plt.xscale('log')
        plt.yscale('log')

    fig.supxlabel(xlabel, fontsize=font_size)
    fig.supylabel(ylabel, fontsize=font_size)

    return fig, ax
def linfit(x, y, fig_name, xlabel='x', ylabel='y', title='scatter plot'):
    """Fit and plot a linear regression model through the data."""

    x = np.asanyarray(x)
    y = np.asanyarray(y)
    
    # fit a linear regression model
    model = ols(y, x, ylabel, xlabel)
    b, a = model.b
    y_hat = a*x + b

    if b < 0:
        info = u'Fitted line: %2.3fx - %2.3f \nR\N{SUPERSCRIPT TWO} = %2.3f' % (a, abs(b), model.R2)
    elif b == 0:
        info = u'Fitted line: %2.3fx \nR\N{SUPERSCRIPT TWO} = %2.3f' % (a, model.R2)
    else:
        info = u'Fitted line: %2.3fx + %2.3f \nR\N{SUPERSCRIPT TWO} = %2.3f' % (a, abs(b), model.R2)


    # plot the results
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111)
    ax.set_title(title)

    # 1:1 line
    ax.plot([0, 100], [0, 100], '--', color='lightgrey')

    ax.plot(x , y_hat, '-', c='gray', linewidth=2)
    ax.scatter(x, y, s=20, c='k')

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.yaxis.grid(True, linestyle='-',
                  which='major', color='lightgrey', alpha=0.4)
    ax.xaxis.grid(True, linestyle='-',
                  which='major', color='lightgrey', alpha=0.4)

    # Hide grid behind plot objects
    ax.set_axisbelow(True)

    maxm = 100
    minm = 0
    ax.set_xlim(minm, maxm)
    ax.set_ylim(minm, maxm)

    ax.text((0.05*maxm) + minm, 0.875*maxm,
            info, fontweight='bold', fontsize=12)

    # save figure
    base, name = os.path.split(fig_name)
    if not os.path.isdir(base) and base != '':
        os.makedirs(base)

    fig.savefig(fig_name)

"""
A collection of par-cooked plots. Just add data and textual seasoning
to your taste.

"""
import os

import numpy as np
import matplotlib.pyplot as plt

def regression_plot(x, y, fig_name,
                    xlabel='x', ylabel='y', title='scatter plot'):
    """Fit and plot a linear regression model through the data."""
    import scikits.statsmodels as sm

    x = np.asanyarray(x)
    X = sm.add_constant(x)
    y = np.asanyarray(y)
    Y = np.array(y)
    
    # fit a linear regression model
    model = sm.OLS(Y, X)
    results = model.fit()
    a, b = results.params

    x = np.unique(x) # avoid MPL path simplification bug
    y_hat = a*x + b

    if b < 0:
        info = u'Fitted line: %2.3fx - %2.3f \nR\N{SUPERSCRIPT TWO} = %2.3f' % (a, abs(b), results.rsquared)
    elif b == 0:
        info = u'Fitted line: %2.3fx \nR\N{SUPERSCRIPT TWO} = %2.3f' % (a, results.rsquared)
    else:
        info = u'Fitted line: %2.3fx + %2.3f \nR\N{SUPERSCRIPT TWO} = %2.3f' % (a, abs(b), results.rsquared)


    # plot the results
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111)
    ax.set_title(title)

    maxm = max(x.max(), y.max())
    minm = min(x.min(), y.min())

    maxm += 0.1*maxm
    minm -= 0.1*maxm

    # 1:1 line
    ax.plot([minm, maxm], [minm, maxm], '--', color='lightgrey')

    ax.plot(x , y_hat, '-', c='gray', linewidth=2)
    ax.scatter(X[:, 0], y, s=15, c='k')

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.yaxis.grid(True, linestyle='-',
                  which='major', color='lightgrey', alpha=0.4)
    ax.xaxis.grid(True, linestyle='-',
                  which='major', color='lightgrey', alpha=0.4)

    # Hide grid behind plot objects
    ax.set_axisbelow(True)

    ax.set_xlim(minm, maxm)
    ax.set_ylim(minm, maxm)

    ax.text((0.05*maxm) + minm, 0.875*maxm,
            info, fontweight='bold', fontsize=12)

    # save figure
    base, name = os.path.split(fig_name)
    if not os.path.isdir(base) and base != '':
        os.makedirs(base)

    fig.savefig(fig_name)

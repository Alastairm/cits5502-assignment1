#!../env/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


data = pd.read_csv('./data.csv')

x = data['Week'].values
hb = data['HB'].values
hs = data['HS'].values
eb = data['EB'].values
es = data['ES'].values
total = data['Total'].values


def stacked_histogram():
    plt.figure()

    p1 = plt.bar(x, es)
    p2 = plt.bar(x, eb, bottom=es)
    p3 = plt.bar(x, hs, bottom=es+eb)
    p4 = plt.bar(x, hb, bottom=es+eb+hs)

    plt.title('Defects found per week by type')
    plt.ylabel('Defects')
    plt.xlabel('Week')
    plt.legend((p4[0], p3[0], p2[0], p1[0]), ('Hard Major', 'Hard Minor', 'Easy Major', 'Easy Minor'))
    plt.xticks([5,10,15,20])

    plt.show()


def log_plot(x, y, linear=True):
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    y_reg = lambda x : slope * x + intercept

    # Plot points
    plt.figure()

    if linear:
        plt.plot(x, y_reg(x))
        plt.scatter(x, y)
        # Graph labels
        plt.title('Defects found per week by type (log linear)')
        plt.ylabel('ln( Defects )')
        plt.xlabel('Week')
        plt.legend((f'{slope:.3f}x + {intercept:.3f}', 'ln( Total Defects )'))
    
    elif not linear:
        plt.plot(x, np.e ** y_reg(x))
        plt.scatter(x, np.e ** y)
        # Graph labels
        plt.title('Defects found per week by type')
        plt.ylabel('Defects')
        plt.xlabel('Week')
        plt.legend((f'{np.e ** intercept:.1f}e^({slope:.2f}x)', 'Total Defects'))

    plt.show()

log_plot(x, np.log(total), linear=False)

def change_in_total(x):
    c_x = []
    for i in range(1, len(x)):
        c_x.append(x[i] - x[i-1])
    return np.array(c_x)


def defect_rate_of_change(x, y):
    plt.figure()

    p1 = plt.scatter(x[1:], change_in_total(y))

    plt.title('Change in defects found from previous week')
    plt.ylabel('Defects')
    plt.xlabel('Week')
    plt.legend((['Defects found less previous week\'s total']))
    plt.xticks([5,10,15,20])
    plt.xlim((0.5,20.5))

    plt.show()
    
defect_rate_of_change(w, total)
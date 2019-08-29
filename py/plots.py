#!../env/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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


def log_plot():
    plt.figure()

    p1 = plt.scatter(x, np.log(total))

    plt.show()

log_plot()

# 'Black box' fit (nonlinear regression)
# Log linear fit
# Rate fit
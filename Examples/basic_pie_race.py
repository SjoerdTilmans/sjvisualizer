from sjvisualizer import plot as plt

plt.pie(excel="data/browsers.xlsx",
        title="Desktop Browser Market Share",
        unit="%",
        duration=0.5)
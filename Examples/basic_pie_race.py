from sjvisualizer import plot as plt

plt.pie(excel="data/browsers.xlsx",
        title="Desktop Browser Market Share",
        unit="%",
        record=True,
        output_video="Browser Market Share.mp4")
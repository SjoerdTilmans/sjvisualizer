from sjvisualizer import plot as plt

plt.bar(excel="data/DesktopOS.xlsx",
        title="Desktop Operating System Market Share",
        unit="%",
        record=True,
        output_video="Desktop_OS.mp4")
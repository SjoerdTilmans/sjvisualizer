from sjvisualizer import plot as plt

colors = {
    "United States": [
        23,
        60,
        154
    ],
	"Russia": [
        255,
        50,
        50
    ]
}

plt.line(excel="data/military budget.xlsx",
        title="Military Budget of Selected Countries",
        sub_title="in millions of US$",
        colors=colors,
        duration=0.25)
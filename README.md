# sjvisualizer 📊
sjvisualizer is a data visualization and animation library for Python. It currently supports the following:
- Bar races
- Animated pie charts

To learn more about sjvisualizer and see additional examples and full documentation, please visit my website https://www.sjdataviz.com/software.

If you find sjvisualizer useful, please consider starring ⭐ the project on GitHub!

## Installation
To install sjvisualizer, you can download the latest wheel file from the dist folder of this repository and install it using pip:

```
pip install sjvisualizer-<version>-py3-none-any.whl
```
Replace <version> with the actual version number of the wheel file.

## Usage
```python
from sjvisualizer import Canvas
from sjvisualizer import DataHandler
from sjvisualizer import PieRace
import time
import json

def main(fps = 60, duration = 0.35):

    number_of_frames = duration*60*fps

    # load data from Excel file
    df = DataHandler.DataHandler(excel_file="<Path to EXCEL DATA FILE>", number_of_frames=number_of_frames).df

    # create canvas object, we will use this to draw our elements to
    canvas = Canvas.canvas()

    # add bar chart
    bar_chart = PieRace.pie_plot(canvas=canvas.canvas, df=df)
    canvas.add_sub_plot(bar_chart)

    # add static text
    canvas.add_title("TITLE", color=(0,132,255))
    canvas.add_sub_title("SUB-TITLE", color=(0,132,255))

    # add time indication
    canvas.add_time(df=df, time_indicator="month")

    canvas.play(fps=fps)

if __name__ == "__main__":
    main()
```

## Contributing
Contributions are always welcome! Here are some ways to get involved:

Create an issue to report a bug or suggest a new feature.
Fork the repository and create a new branch to work on.
Submit a pull request to request a merge of your changes.
Please make sure to write clear commit messages.

## License
sjvisualizer is released under the MIT License. See the LICENSE file for more details.

## Contact
If you have any questions or suggestions regarding sjvisualizer, please don't hesitate to contact us at info@sjdataviz.com.
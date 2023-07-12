# sjvisualizer 📊
sjvisualizer is a data visualization and animation library for Python. 

https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/a9a01f5b-50f4-411f-8e7c-dcd4a805501b

Please find the catalogue example [here](https://github.com/SjoerdTilmans/sjvisualizer/blob/main/Examples/Catalogue.py) to run the above animation. sjvisualizer currently supports the following chart types:
- Bar races
- Animated pie charts
- Animated stacked bar charts
- Animated line charts

More chart types to follow! 

There are two ways of learning sjvisualizer:
- Find additional examples and full documentation on my [website](https://www.sjdataviz.com/software)
- Or follow my course on [Udemy](https://www.sjdataviz.com/course-link)

If you find sjvisualizer useful, please consider starring ⭐ the project on GitHub!

## Installation
sjvisualizer is now available on pypi! Simply use pip to install it:

```
pip install sjvisualizer
```

## Usage
sjvisualizer is a free and open-source data animation library, please include the following attribution in any publications you use it in.
```
Made with sjvisualizer, the open-source data animation library for Python
```
## Sample code
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

## Support this project
If you like this project, please consider buying me a cup of coffee on [buymeacoffee](https://www.buymeacoffee.com/SjoerdTilmans).
    
## Contributing
Contributions are always welcome! Here are some ways to get involved:

Create an issue to report a bug or suggest a new feature.
Fork the repository and create a new branch to work on.
Submit a pull request to request a merge of your changes.
Please make sure to write clear commit messages.

## License
sjvisualizer is released under the MIT License. See the LICENSE file for more details.

## Contact
If you have any questions or suggestions regarding sjvisualizer, post it on my [forum](https://www.sjdataviz.com/howto-sjvisualizer).

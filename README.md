[![Downloads](https://static.pepy.tech/badge/sjvisualizer)](https://pepy.tech/project/sjvisualizer)
# sjvisualizer 📊
sjvisualizer is a data visualization and animation library for Python for time-series data. 

Like this project? Please consider starring ⭐ the project on GitHub!

Or buying me a coffee. It will make my day! [Buy me a Coffee](https://www.buymeacoffee.com/sjoerdtilmans)

## Installation
sjvisualizer is now available on pypi! Simply use pip to install it:

```
pip install sjvisualizer
```

## Basic examples
Using sjvisualizer, you can create a basic data animation with one simple line of code.

### Bar Race


https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/9340572c-56f8-4abd-97c5-e8ed674a6751


```python
from sjvisualizer import plot as plt

plt.bar(excel="data/DesktopOS.xlsx", 
        title="Desktop Operating System Market Share", 
        unit="%")
```

### Pie Race


https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/5db0d056-578e-4070-b1ba-713e590acd3d


```python
from sjvisualizer import plot as plt

plt.pie(excel="data/browsers.xlsx", 
        title="Desktop Browser Market Share", 
        unit="%")
```

### Animated Line Chart
https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/deae9c3c-8a90-4e64-a036-39fd636746a7
```python
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
        colors=colors)
```

### Animated Area Chart


https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/6304bb63-1076-4da8-b044-595f763d3546



```python
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

plt.stacked_area(excel="data/Nuclear.xlsx",
        title="Nuclear Warheads by Country",
        colors=colors)
```
## Data format
Currently sjvisualizer reads data from an Excel file. The format should be as shown in the picture below:

<img width="377" alt="example data format" src="https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/fb5b0665-77f0-4d08-81d5-05c84e02804e">

In this file the first column should contain the dates, and each subsequent column holds the data for the data categories, in this example the different countries.

The date can either be shown as just the year, or as a full date as shown below. In this case, please make sure that Excel recognises the cell as a date.

<img width="651" alt="example data format_long" src="https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/999d1f19-60d6-4a16-a5fb-ea2d17671013">


## More advanced animations
Using sjvisualizer, you can also mix and match chart types and positions like in the following example:


https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/420ed4a0-5bfb-436a-8f61-4e77c640f78f


## Learn sjvisualizer

Want to learn more about sjvisualizer:
- Find additional examples and full documentation on my [website](https://www.sjdataviz.com/software)
- Or follow my course on [Udemy](https://www.sjdataviz.com/course-link)

## Roadmap

![Purple Colorful Modern Roadmap Timeline Infographic (1)](https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/542e02ec-113c-4fb7-a46a-fc3b65abddd2)


## Usage
sjvisualizer is a free and open-source data animation library, please include the following attribution in any publications you use it in.
```
Made with sjvisualizer, the open-source data animation library for Python
```


## Support this project
If you like this project, please concider supporting me using PayPal [Buy me a Coffee](https://www.buymeacoffee.com/sjoerdtilmans).

## SJVisualizer Supporters

Do you like what we are doing and want to support this project, get in touch at info@sjdataviz.com

## Contributing
Contributions are always welcome! A couple of ideas to contribute:
- Improve documentation of this project. I have been thinking of setting up a readthedocs page.
- Add additional example scripts. If you do so, please includy any data files and image files so that the example is fully running
- Add new chart types. I have uploaded an example skeleton of new chart types in Empty.py, this is a setup that should serve as a good starting point. (https://github.com/SjoerdTilmans/sjvisualizer/blob/main/sjvisualizer/Empty.py)

Before making any changes, please create your own development branch here on GitHub. Once ready submit a pull request and set me as reviewer!

## License
sjvisualizer is released under the MIT License. See the LICENSE file for more details.

## Contact
If you have any questions or suggestions regarding sjvisualizer, post it on my [forum](https://www.sjdataviz.com/howto-sjvisualizer).

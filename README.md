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

```python
from sjvisualizer import plot as plt

plt.bar(excel="data/DesktopOS.xlsx", 
        title="Desktop Operating System Market Share", 
        unit="%")
```

### Pie Race

```python
from sjvisualizer import plot as plt

plt.pie(excel="data/browsers.xlsx", 
        title="Desktop Browser Market Share", 
        unit="%")
```

### Animated Line Chart

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

## More advanced animations
Using sjvisualizer, you can also mix and match chart types and positions like in the following example:

## Roadmap

![Purple Colorful Modern Roadmap Timeline Infographic (1)](https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/a45ab7f0-ea16-4230-be56-d2fdb2af3bc3)

If you like this project, please concider supporting me using PayPal [PayPal](https://www.paypal.com/donate/?hosted_button_id=YMN9G93CTNLD2).

## Learn sjvisualizer

Want to learn more about sjvisualizer:
- Find additional examples and full documentation on my [website](https://www.sjdataviz.com/software)
- Or follow my course on [Udemy](https://www.sjdataviz.com/course-link)


## Usage
sjvisualizer is a free and open-source data animation library, please include the following attribution in any publications you use it in.
```
Made with sjvisualizer, the open-source data animation library for Python
```


## Support this project
If you like this project, please concider supporting me using PayPal [PayPal](https://www.paypal.com/donate/?hosted_button_id=YMN9G93CTNLD2).
    
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

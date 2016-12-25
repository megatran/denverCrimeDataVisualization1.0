<p align = "center">
    <img src="/denver_crime_screenshot.jpg" />
</p>

<br>
# Denver Crime Data Visualization 1.0

The dataset, provided by the City and County of Denver, records crimes from the previous five calendar years and until the current calendar date.  The data was obtained on December 1, 2016 making the dataset cover five years and 11 months time.   It is updated five days a week (Monday to Friday), which provides a bit of a hurdle in terms of this project being up to date, although for the purposes of this project there really isn’t a huge difference between data from one week ago compared to data today; most of the queries and visual representations should stay fairly accurate, at least proportionally.

# Install and Requirements
The application, written in Python and utilizing Tkinter and Matplotlib, displays a variety of graphs based on SQL queries of the data; the graphs range from entry-dependent to pre-made for especially interesting queries
* [Denver’s Open Data Catalog in CSV format](https://www.denvergov.org/opendata/dataset/city-and-county-of-denver-crime)
* Python 3.5
    * [pg8000](https://pypi.python.org/pypi/pg8000)
    * [matplotlib](http://matplotlib.org/users/installing.html)
    * [Tkinter](https://docs.python.org/2/library/tkinter.html)

All Python dependencies can be installed with pip:

```
pip install matplotlib pg8000 tkinter
```

## Usage
```
python3 crimeVisualization.py
```
<br>

## Contributors:
[Nhan Tran](http://www.trannhan.com), Reece Hughes, Nicholas Miller

## License
The data is distributed under an Open Data License allowing free copying, distribution, transmission, etc. of the data.

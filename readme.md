### Terbine Static Location Map

This project has several components, one to mine the data from Terbine, one to preprocess the data, and one to visualize the data on a world map.


Map Specifications
- The map currently includes fixed coordinate points, bounding boxes, and polygons.
- Zoom can get down to street level in major cities, as the map is based on the public USGS imagery map available on their tile server, and subject to its limitations.
- Independant traces can be selected using the legend, where a double click resets the map to show all traces.

Tools Used:
- Data mining was done using selenium in python in conjunction with headless chrome.
- Preprocessing of the data files was also done in python using a jupyter notebook.
- The data visualization was accomplished using plotly and mapbox in R.

To run and assemble the data, run the miner, then the formatting .ipynb, and then run the R script.

![](mapex2.gif)

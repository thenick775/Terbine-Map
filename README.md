### Terbine Static Location Map

This project was a fun exercise that has two main components, one to mine the data from Terbine, and one to preprocess and visualize the data on a world map.


Map Specifications
- The map currently includes fixed coordinate points, bounding boxes, and polygons.
- Zoom can get down to street level globally, as the map is now using the Open Street Map style.
- Independant traces can be selected using the legend, where a double click resets the map to show all traces.

Tools Used:
- Data mining was done using Selenium in conjunction with headless chrome.
- Preprocessing of the data files was also done in python.
- The data visualization was accomplished using plotly and mapbox in R.

To run and assemble the data, run the miner, then the assemble_widget.sh to process and visualize the data. 
All scripts expect to be run in the directory where the resulting files are placed.

To launch this project, simply click potestaticmapboxv1.4.html and open it with your preferred browser.

![](mapex3v3.gif)

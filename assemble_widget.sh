#!/bin/bash
#short script to generate widget after scraper has been run

python bboxformatmapbox1.py; #parse and reformat for plotly vectors
Rscript terbinestaticmapbox.R; #create layers and generate htmlwidget

echo "widget generation complete"
rm *.csv

library(plotly)
library(readr)
library(dplyr)
library(lubridate)
latlntable<- read_csv("latlondatloc.csv")         #read coordinates (points) file
bboxtable<- read_csv("latlonbboxwvecreduced.csv") #read bbox file
polytable<- read_csv("latlonpolywvecreduced.csv") #read polygon file

bboxvec<- mutate( bboxtable,LatVec = lapply(strsplit(bboxtable$LatVec, ",", TRUE), as.numeric)) %>% #columns from string to numeric
mutate( LonVec = lapply(strsplit(bboxtable$LonVec, ",", TRUE), as.numeric))

polyvec<- mutate( polytable,LatVec = lapply(strsplit(polytable$LatVec, ",", TRUE), as.numeric)) %>% #columns from string to numeric
mutate( LonVec = lapply(strsplit(polytable$LonVec, ",", TRUE), as.numeric))

llatall<-c()
llonall<-c()
namefill<-c()
datefill<-c()
for (v in 1:length(bboxvec$LonVec)){ #accumulate bounding boxes in a vector
  tmplat<-c(bboxvec$LatVec[[v]],NA)
  tmplon<-c(bboxvec$LonVec[[v]],NA)
  llatall<-c(llatall,tmplat)
  llonall<-c(llonall,tmplon)
  namefilltmp<-c(rep(bboxvec$Name[[v]],4),NA)
  datefilltmp<-c(rep(bboxvec$Date[[v]],4),NA)
  namefill<-c(namefill,namefilltmp)
  datefill<-c(datefill,datefilltmp)
}

polyllatall<-c()
polyllonall<-c()
polynamefill<-c()
polydatefill<-c()
for (v in 1:length(polyvec$LonVec)){ #accumulate bounding boxes in a vector
  polytmplat<-c(polyvec$LatVec[[v]],NA)
  polytmplon<-c(polyvec$LonVec[[v]],NA)
  polyllatall<-c(polyllatall,polytmplat)
  polyllonall<-c(polyllonall,polytmplon)
  polynamefilltmp<-c(rep(polyvec$Name[[v]],length(polyvec$LonVec[[v]])),NA)
  polydatefilltmp<-c(rep(polyvec$Date[[v]],length(polyvec$LonVec[[v]])),NA)
  polynamefill<-c(polynamefill,polynamefilltmp)
  polydatefill<-c(polydatefill,polydatefilltmp)
}

p<-  latlntable %>%
  plot_ly( #this is for the lat/lon coord layer
    lat = ~lat,
    lon = ~lon,
    sizes = c(15, 100),
    size = ~optrad,
    opacity = 0.95,
    type = "scattermapbox",
    hovertext = ~paste(paste("Ingest Date:", date), paste("Name:",name), sep = "<br />"),
    marker = list(color = "red"), #"fuchsia"),
    mode = 'markers',
    name='coords') %>% 
  add_trace(
    name="bbox",
    mode="markers", 
    type="scattermapbox", #this is for the bounding box trace layer
    lat=llatall, 
    lon=llonall, 
    marker=list(
      color = "blue", 
      opacity = 0.4, 
      sizeref = 0.9, 
      size = 7, 
      sizemode = "area"
      ),
    fill = "toself",fillcolor="rgba(255, 0, 0, 0.24)",
    hovertext=~paste(paste("Ingest Date:", datefill), paste("Name:",namefill), sep = "<br />"),
    inherit = FALSE) %>%
  add_trace(
    name="poly",
    mode="markers", 
    type="scattermapbox",
    lat=polyllatall,
    lon=polyllonall,
    marker=list(
      color = "orange", 
      opacity = 0.4, 
      sizeref = 0.9, 
      size = 7, 
      sizemode = "area"
    ),
    fill = "toself",fillcolor="rgba(0, 255, 0, 0.24)",
    hovertext=~paste(paste("Ingest Date:", polydatefill), paste("Name:",polynamefill), sep = "<br />"),
    inherit = FALSE) %>%
  layout(
  mapbox=list( #map layout and config
    style = 'open-street-map', #style = "white-bg",#can switch in stamen terrain, using open street map currently
    zoom = 0.6,
    margin = list(l = 0, r = 0, b = 0, t = 0, pad = 0)
    ),
    paper_bgcolor="rgba(237, 241, 247, 0.14)",
    title = list(
      text="Fixed Coordinate Points in Terbine",
      yref="paper",
      font=list(family = "sans serif",color="black"),
      y=0.99,
      x=0.5
      ),
    font=list(family = "sans serif",size = 25, color="rgba(255, 255, 255, 1)"),
    showlegend=TRUE) %>%
  config(displaylogo = FALSE,
         modeBarButtonsToRemove = list(
           'sendDataToCloud',
           'toImage',
           'resetScale2d',
           'hoverClosestCartesian',
           'hoverCompareCartesian',
           'lasso2d',
           'select2d',
           'toggleSpikelines'
         )
  )

wid<- as_widget(p)
wid$sizingPolicy$padding<- 0

htmlwidgets::saveWidget(wid, "potestaticmapboxv1.4.html", selfcontained = TRUE, background = "black") #for widget
###########################

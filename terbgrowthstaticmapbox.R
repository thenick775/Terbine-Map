library(plotly)
library(readr)
library(dplyr)
library(lubridate)
latlntable<- read_csv("latlondatloc.csv")         #read coordinates file
bboxtable<- read_csv("latlonbboxwvecreduced.csv") #read bbox file
polytable<- read_csv("latlonpolywvecreduced.csv") #read bbox file

xiii<- mutate( bboxtable,LatVec = lapply(strsplit(bboxtable$LatVec, ",", TRUE), as.numeric))%>%#columns from string to numeric
mutate( LonVec = lapply(strsplit(bboxtable$LonVec, ",", TRUE), as.numeric))

xppp<- mutate( polytable,LatVec = lapply(strsplit(polytable$LatVec, ",", TRUE), as.numeric))%>%#columns from string to numeric
mutate( LonVec = lapply(strsplit(polytable$LonVec, ",", TRUE), as.numeric))

llatall<-c()
llonall<-c()
namefill<-c()
datefill<-c()
for (v in 1:length(xiii$LonVec)){ #accumulate bounding boxes in a vector
  tmplat<-c(xiii$LatVec[[v]],NA)
  tmplon<-c(xiii$LonVec[[v]],NA)
  llatall<-c(llatall,tmplat)
  llonall<-c(llonall,tmplon)
  namefilltmp<-c(rep(xiii$Name[[v]],4),NA)
  datefilltmp<-c(rep(xiii$Date[[v]],4),NA)
  namefill<-c(namefill,namefilltmp)
  datefill<-c(datefill,datefilltmp)
}

polyllatall<-c()
polyllonall<-c()
polynamefill<-c()
polydatefill<-c()
for (v in 1:length(xppp$LonVec)){ #accumulate bounding boxes in a vector
  polytmplat<-c(xppp$LatVec[[v]],NA)
  polytmplon<-c(xppp$LonVec[[v]],NA)
  polyllatall<-c(polyllatall,polytmplat)
  polyllonall<-c(polyllonall,polytmplon)
  polynamefilltmp<-c(rep(xppp$Name[[v]],length(xppp$LonVec[[v]])),NA)
  polydatefilltmp<-c(rep(xppp$Date[[v]],length(xppp$LonVec[[v]])),NA)
  polynamefill<-c(polynamefill,polynamefilltmp)
  polydatefill<-c(polydatefill,polydatefilltmp)
}

#remove problem poolygons (future use blacklist file)
polylatfin<-c(polyllatall[1:150])
polylonfin<-c(polyllonall[1:150])
polylatfin<-c(polylatfin,polyllatall[162:257])
polylonfin<-c(polylonfin,polyllonall[162:257])

polynamefillfin<-c(polynamefill[1:150])
polydatefillfin<-c(polydatefill[1:150])
polynamefillfin<-c(polynamefillfin,polynamefill[162:257])
polydatefillfin<-c(polydatefillfin,polydatefill[162:257])

#remove the few readings that broke the plot due to invalid coordinates
testlat<-c(llatall[1:405])
testlon<-c(llonall[1:405])
testlat<-c(testlat,llatall[410:1125])
testlon<-c(testlon,llonall[410:1125])
testlat<-c(testlat,llatall[1130:1625])
testlon<-c(testlon,llonall[1130:1625])

namefillnew<-c(namefill[1:405])
datefillnew<-c(datefill[1:405])
namefillnew<-c(namefillnew,namefill[410:1125])
datefillnew<-c(datefillnew,datefill[410:1125])
namefillnew<-c(namefillnew,namefill[1130:1625])
datefillnew<-c(datefillnew,datefill[1130:1625])

p <-  latlntable %>%
  plot_ly( #this is for the lat/lon coord layer
    lat = ~lat,
    lon = ~lon,
    sizes = c(13, 100),
    size = ~optrad,
    opacity = 0.95,
    type = "scattermapbox",
    hovertext = ~paste(paste("Ingest Date:", Date), paste("Name:",Name), sep = "<br />"),
    marker = list(color = "fuchsia"),
    mode = 'markers',name='coords') %>% 
  add_trace(
    name="bbox",
    mode="markers", 
    type="scattermapbox", #this is for the bounding box trace layer
    lat=testlat, 
    lon=testlon, 
    marker=list(
      color = "blue", 
      opacity = 0.4, 
      sizeref = 0.9, 
      size = 7, 
      sizemode = "area"
      ),
    fill = "toself",fillcolor="rgba(255, 0, 0, 0.24)",
    hovertext=~paste(paste("Ingest Date:", datefillnew), paste("Name:",namefillnew), sep = "<br />"),
    inherit = FALSE) %>%
  add_trace(
    name="poly",
    mode="markers", 
    type="scattermapbox",
    lat=polylatfin,#polyllatall[162:257],#good:1-150, c(14.6541777,14.5854939,14.5299998,14.5332401,14.6541777),
    lon=polylonfin,#polyllonall[162:257],#good:1-150, c(121.0346116,121.0747146,121.0151183,120.9805113,121.0344399),
    marker=list(
      color = "orange", 
      opacity = 0.4, 
      sizeref = 0.9, 
      size = 7, 
      sizemode = "area"
    ),
    fill = "toself",fillcolor="rgba(0, 255, 0, 0.24)",
    hovertext=~paste(paste("Ingest Date:", polydatefillfin), paste("Name:",polynamefillfin), sep = "<br />"),
    inherit = FALSE
  ) %>%
  layout(
  mapbox=list( #map layout and config
    style = "white-bg",#can switch in stamen terrain
    zoom = 0.6,
    margin = list(l = 0, r = 0, b = 0, t = 0, pad = 0),
    layers = list(list(
      below = 'traces',
      sourcetype = "raster",
      source = list("https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}")))),
    title = list(text="Fixed Coordinate Points in Terbine",y=1,x=0.5),
    font=list(family = "sans serif",size = 25),
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

p #for viewer
#htmlwidgets::saveWidget(as_widget(p), "potestaticmapboxv1.3.html") #for widget
###########################

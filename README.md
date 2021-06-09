CSE 512 UW Homeworks
=======

# FP-astro-plan
Team members:  
* Conor Sayres  
* Dino Bektesevic  
* Jessica Birky  
* David Wang

Project page: https://www.apo.nmsu.edu/CS/cse512/ 

Project video: https://www.youtube.com/watch?v=4mhJHX6-ywI&t=1s 


# SDSS-V:  visualizing a telescopes' nightly plan

## 1. Visualization Motivation
The Sloan Digital Sky Survey (SDSS), is a robotic telescope that scans the sky every night.  It seeks to map large areas of the sky over years-long baselines.  SDSS has broken up the sky into small patches called "fields".  Each field contains a collection of many faint targets (stars or galaxies) that are simultaneously measured in a single image. The night is discretized into 18 minute exposure chunks, one exposure per field.  The night plan is the sequence of fields the telescope visits throughout the night.  The goal of this project is to prototype a helpful visualization of an SDSS night plan to aid the observers collecting data on a nightly basis.

The "optimal" plan for each night is determined algorithmically each day.  When night operations are running smoothly, there is little reason to deviate from the plan.  However, operations do not always run smoothly: weather or technical problems can interrupt observations, and often the telescope operators need to mitigate the situation and change the plan on the fly.  We hope this tool provides a way for operators to quickly come up with alternate observing plans as conditions change throughout the night.  A good visualization will aid quick accurate decision making, especially when the potential space of field options is large.  The important factors for observing a field are "altitude" (how high in the sky the field is: higher altitude leads to better data due to less atmospheric distortion), and how far from the moon the field is (data quality suffers as fields near the moon due to its brightness!)

In this visualization we've picked a single night to visualize, we are using A3 as a chance to prototype a more polished and sophisticated version of this for the final project. 

## 2. Design rationale

### 2.1 Sky Plot

<img src="docs/gifs/sky_plot_demo.gif" width=650px>

> ### Field Interaction
> 
> Since users will want to compare fields, particularly their altitude over time, we made both the field squares in the sky plot and the points in the altitude plot interactive, with multiple selections allowed. Selecting a field highlights the edge in the sky plot in red, and makes the corresponding track in the altitude plot completely opaque, making these points immediately stand out. Points selected in the altitude plot will outline the sky plot as both are linked. The field currently being observed is always in the top layer: this made them easier to click.

We took advantage of altair’s projection functions to map our data onto the sky. By mapping azimuth to longitude and altitude to latitude, and projecting using a north pole centered azimuthal equidistant projection, we could produce a circular map of the sky equivalent to a 180 degree fisheye view. Coincidentally, this is the view the all-sky camera at the SDSS telescope sees the sky--for the final project, we may incorporate a feed of this camera and plot fields on top of the live view. We made the background very dark and plotted lighter elements on top. We found this both approximates the sky better, appears less cluttered, and is more visually appealing.

Fields planned for observation during the night are plotted as squares corresponding to the area on the sky that would be imaged by the telescope. The yellow field corresponds to the field currently being observed, and the luminous blue (the “opposite” of yellow in L*ab) corresponds to fields not currently being observed, but meeting criteria for observation. We distinguish fields not meeting criteria for observation at that time by coloring them in pale blue. As time progresses, the status of the fields will change, with the colors updating correspondingly. We use tooltips to display the ID of each field and its separation from the moon, which are the two features observers will likely want to reference.
 
The sizes of background stars correspond to their brightnesses. Astronomers measure this in magnitudes, with 0 being the brightest magnitude and brightness decreasing thereafter. We only plot stars down to 4.5 magnitude: any more and the plot becomes slow and cluttered. This also simulates what the sky looks like in a suburban setting, which may be more familiar to most viewers. The moon is also plotted as a dark grey circle corresponding to the rough size of the moon. A label pops up on mouseover to inform the viewer that this object is the moon since its identity might not be immediately obvious.

The sky plot updates to reflect the time selected in the time vs altitude plot - we found this offered more control, and was both more intuitive and informative, than using a slider.

### 2.2 Altitude vs Time Plot

<img src="docs/gifs/altitude_time_demo.gif" width=650px>

> ### Time Interaction
> 
> Mousing over the plot selects the closest time (x-axis) to the cursor. This updates the linked sky plot, which displays the sky at the time selected. Running the cursor horizontally through the bottom thus animates the sky plot to show the motion of the sky over the night. Text in the bottom left of the plot always displays the time selected and the ID of the field observed at that time which the user will often need to reference.

Since we wish to optimize the altitude of each field during observation, we also plot the altitude of each field over time in a scatterplot below the sky plot. The initial renderings of these points are transparent, since we will usually only want to compare a few at a time. Selecting a field (explained below) will cause the points corresponding to this field to become opaque. 

The colors match the field statuses in the sky plot: yellow for currently observing, bright blue for not observing but available, and pale blue for unavailable. Points representing fields currently being observed (one for each time), are also larger and filled in to facilitate easier interaction.

### 2.3 Field Completion and Priority

<img src="docs/gifs/completion_priority_demo.gif" width=650px>

> ### Selections
>
> Description

### 2.4 Calendar

<img src="docs/gifs/calendar_date_demo.gif" width=650px>

> ### Select Different Dates
>
> The user can explore 365 nights worth of simulated observing strategies using the calendar display in the upper left corner. Hovering over each date displays the value for the variable selected in the drop down menu above the calendar. The user can also change the date by clicking on the calendar, which will change the data displayed in the sky plot/altitude plot below to a different night.

<img src="docs/gifs/calendar_menu_demo.gif" width=650px>

> ### Select Color Encoding
>
> 

### 2.5 Cloud Cam Demo

<img src="docs/gifs/cloud_cam_demo.gif" width=400px>

> ### Video 
>
> Description

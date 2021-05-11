# cse512
CSE 512 UW Homeworks
=======

# A3-astroviz
Team members:  
* Conor Sayres  
* Dino Bektesevic  
* Jessica Birky  
* David Wang

Project page: https://cse512-21s.github.io/A3-astroviz/  

# SDSS-V:  visualizing a telescopes' nightly plan

## Visualization Motivation

The Sloan Digital Sky Survey (SDSS), is a robotic telescope that scans the sky every night.  It seeks to map large areas of the sky over years-long baselines.  SDSS has broken up the sky into small patches called "fields".  Each field contains a collection of many faint targets (stars or galaxies) that are simultaneously measured in a single image. The night is discretized into 18 minute exposure chunks, one exposure per field.  The night plan is the sequence of fields the telescope visits throughout the night.  The goal of this project is to prototype a helpful visualization of an SDSS night plan to aid the observers collecting data on a nightly basis.

The "optimal" plan for each night is determined algorithmically each day.  When night operations are running smoothly, there is little reason to deviate from the plan.  However, operations do not always run smoothly: weather or technical problems can interrupt observations, and often the telescope operators need to mitigate the situation and change the plan on the fly.  We hope this tool provides a way for operators to quickly come up with alternate observing plans as conditions change throughout the night.  A good visualization will aid quick accurate decision making, especially when the potential space of field options is large.  The important factors for observing a field are "altitude" (how high in the sky the field is: higher altitude leads to better data due to less atmospheric distortion), and how far from the moon the field is (data quality suffers as fields near the moon due to its brightness!)

In this visualization we've picked a single night to visualize, we are using A3 as a chance to prototype a more polished and sophisticated version of this for the final project. 

## Design rationale

<img src="docs/prtscr_viz.png" alt="A screenshot of the visualization showing the sky dome, top, and the time plot, bottom. On the sky dome, frames that are availible for observing are shown in darker blue, while frames that can not currently be observed are shown in lighter blue color. Yellow colored square denotes the frame that is currently being observed. The azimuth-time plot displays an entire nightly observation plan, in 18 minutes bins, where yellow colored cirlces represent planned optimal frame observations. Darker blue colored cirlces are selected frames of interest, also accented in red on the sky dome plot." width=400px>

### Sky Plot
We took advantage of altair’s projection functions to map our data onto the sky. By mapping azimuth to longitude and altitude to latitude, and projecting using a north pole centered azimuthal equidistant projection, we could produce a circular map of the sky equivalent to a 180 degree fisheye view. Coincidentally, this is the view the all-sky camera at the SDSS telescope sees the sky--for the final project, we may incorporate a feed of this camera and plot fields on top of the live view. We made the background very dark and plotted lighter elements on top. We found this both approximates the sky better, appears less cluttered, and is more visually appealing.

Fields planned for observation during the night are plotted as squares corresponding to the area on the sky that would be imaged by the telescope. The yellow field corresponds to the field currently being observed, and the luminous blue (the “opposite” of yellow in L*ab) corresponds to fields not currently being observed, but meeting criteria for observation. We distinguish fields not meeting criteria for observation at that time by coloring them in pale blue. As time progresses, the status of the fields will change, with the colors updating correspondingly. We use tooltips to display the ID of each field and its separation from the moon, which are the two features observers will likely want to reference. 

The sizes of background stars correspond to their brightnesses. Astronomers measure this in magnitudes, with 0 being the brightest magnitude and brightness decreasing thereafter. We only plot stars down to 4.5 magnitude: any more and the plot becomes slow and cluttered. This also simulates what the sky looks like in a suburban setting, which may be more familiar to most viewers. The moon is also plotted as a dark grey circle corresponding to the rough size of the moon. A label pops up on mouseover to inform the viewer that this object is the moon since its identity might not be immediately obvious.

The sky plot updates to reflect the time selected in the time vs altitude plot (see below)--we found this offered more control, and was both more intuitive and informative, than using a slider.

### Altitude vs Time Plot
Since we wish to optimize the altitude of each field during observation, we also plot the altitude of each field over time in a scatterplot below the sky plot. The initial renderings of these points are transparent, since we will usually only want to compare a few at a time. Selecting a field (explained below) will cause the points corresponding to this field to become opaque. 

The colors match the field statuses in the sky plot: yellow for currently observing, bright blue for not observing but available, and pale blue for unavailable. Points representing fields currently being observed (one for each time), are also larger and filled in to facilitate easier interaction. 

### Time Interaction
Mousing over the plot selects the closest time (x-axis) to the cursor. This updates the linked sky plot, which displays the sky at the time selected. Running the cursor horizontally through the bottom thus animates the sky plot to show the motion of the sky over the night. Text in the bottom left of the plot always displays the time selected and the ID of the field observed at that time which the user will often need to reference.

We originally used a slider to control time in both plots. However we found that mousing over the lower plot provided a greater space for interaction and linked the two plots more intuitively.

### Field Interaction
Since users will want to compare fields, particularly their altitude over time, we made both the field squares in the sky plot and the points in the altitude plot interactive, with multiple selections allowed. Selecting a field highlights the edge in the sky plot in red, and makes the corresponding track in the altitude plot completely opaque, making these points immediately stand out. Points selected in the altitude plot will outline the sky plot as both are linked. The field currently being observed is always in the top layer: this made them easier to click.

### Development process
For our prototype visualization this assignment, our design choices were largely motivated by scientific utility. The idea for creating a data visualization involving SDSS data was initiated by Conor, who works on developing instrumentation for the survey, and saw the need for developing a visualization tool to help future users of this survey plan nightly observing strategies. Because Dino, David, and Jessica were not as familiar with dataset and survey, we started our development process by first discussing the dataset with Jose Sanchez-Gallego and John Donor (two research scientist working on SDSS) to get a sense of what data we have and what the most important utilities from a user perspective would be. 

Deciding the scope for this project was the first major challenge for us, which took a few days of discussion. Initially we thought it would be useful to create a dynamic visualization product, which could load the data in real time, but realized this would likely take more effort to deal with a database server than it would to actually create the frontend visualization. 

Once we had settled on the constraints of a static visualization, Conor put together a simulated dataset, and we met over zoom on 5/3 to discuss plot ideas and choice of visualization tool. At his point we were kind of divided between using d3 and a python-based library such as altair. Because this process was a bit of a learning curve for everyone, and we each had kind of different visions for the project, we decided to split up the group where David and Jessica started working on implementing a visualization in python, and Dino and Conor started working on a d3 implementation. 

A few days later on 5/6 we met again over zoom and shared our progress/initial iterations of plots. At that point David had put together the most functional version of an interactive plot using altair, and so we decided to build off of that iteration for this assignment submission, and would continue thinking about using d3 for the more ambitious final project.
 
Creating the altair version of the visualization took about 12 hours, split roughly as follows:
* 3 hours to create the two plots separately, 
* about 3 hours to link the plots to update together using a slider, 
* an additional 3 hours to use mouseover in the altitude plot to select time and link that to the time displayed in the sky plot, plus linking field selection between the plots, 
* 3 hours to mess with color schemes, optimize the layering, sizes, colors, and opacity.
The most difficult (i.e frustrating) part was linking the time selection between the two plots. The error handling in altair often leaves little to no traceback as to what went wrong. Sometimes, certain elements just didn’t appear at all. After a few hours, I discovered that since the variables encoded by color in both plots were the same, the points wouldn’t appear in the lower plot unless the color scale was also the same. However, I found that altair is immensely powerful for putting advanced visualizations together quickly, evidenced by the fact that it only took 3 hours to create the two plots separately, and only about 12 hours to get the entire thing working.

I did find altair limited in several ways. I hoped to use lines to connect points in the altitude plot--however altair requires a 3rd variable such as color or shape to group series to create a multi series line chart. It’s also difficult to add custom backgrounds and encodings in altair, or to dynamically query data, and not possible to run scripts to process data and update the plots. For these reasons, we will likely use d3 for our final project.

In the end, we found that altair was much better for rapidly prototyping interactive plots. For the purposes of a prototype, we found that we were able to effectively display a lot of the essential utilities needed for observing in a night using pretty standard types of data encoding (position, color, size, shapes) by adapting templates from altair (radial and cartesian scatter plot). However, exploring how to use d3 has definitely given us a head start on the final project and think about additional things we could add to our interactive display given more flexibility. 


import pandas as pd
import altair as alt
import numpy as np


def get_data(data, moon_data=True):
    '''
    Takes the sdss field data, rounds floats, subsets to only observed fields, and calculates utcs times.
    '''
    field_cols = ['alt', 'az', 'moonSep', 'fieldID', 'fieldStatus', 'Observation Start Time', 'time_step_id', 'priority', 'completion', 'Scheduled']
    star_cols = ['alt', 'az', 'time_step_id', 'mag']
    moon_cols = ['moonAlt', 'moonAz', 'time_step_id', 'phase_icon']

    # Rename columms to make dataset smaller
    renamed_field_cols = ['alt', 'az', 'mS', 'fid', 'fS', 'st', 'tsid', 'p', 'c', 'sch']
    renamed_star_cols = ['alt', 'az', 'tsid', 'mag']
    renamed_moon_cols = ['mAlt', 'mAz', 'tsid', 'phase']

    # round columms
    for col in data.dtypes[data.dtypes == 'float64'].index:
        data[col] = round(data[col], 6)
        data['moonSep'] = round(data['moonSep'], 1)

    scheduled = data.loc[data['scheduled']==True]
    scheduled.sort_values('mjdExpStart', inplace=True)

    ####################
    #    Extract relevant field data into dataset
    ####################
    fields = data.query('objType == "sdss field"')
    timestamps = pd.to_datetime(fields['mjdExpStart'] + 2400000.5, unit='D', origin='julian') - pd.Timedelta(hours=6)
    datetimes = [dt.to_pydatetime().strftime("%Y-%m-%dT%H:%M:%S") for dt in timestamps]
    fields['Observation Start Time'] = datetimes
    fields = fields.loc[fields['alt'] > -.5] # could change to use 'Risen'

    ####################
    #    Extract relevant star data into dataset
    ####################
    stars = data.query('objType == "bright star"')
    stars = stars.loc[stars['alt'] > -.5] # could change to use 'Risen'

    # Round mangitudes to nearest 0.5
    stars = stars.query('magnitude < 4.5')
    stars['mag'] = round(stars['magnitude'], 0)

    ####################
    # Create different field statuses
    ####################
    fields['fieldStatus'] = 'Available'
    fields.loc[fields['scheduled'], 'fieldStatus'] = 'Scheduled Now'
    fields.loc[fields['alt'] < 40, 'fieldStatus'] = 'Unavailable'

    fields['Scheduled'] = False
    fields.loc[fields['fieldID'].isin(scheduled['fieldID']), 'Scheduled'] = True

    ####################
    # Assign observation numbers as time step id
    ####################
    ts = {mjd: ii for ii, mjd in enumerate(fields['mjdExpStart'].sort_values().unique())}
    fields['time_step_id'] = [ts[mjd] for mjd in fields['mjdExpStart']]
    stars['time_step_id'] = [ts[mjd] for mjd in stars['mjdExpStart']]

    ###################
    # Rename columns
    ###################
    fields.rename(columns={old:new for old, new in zip(field_cols, renamed_field_cols)}, inplace=True)
    stars.rename(columns={old:new for old, new in zip(star_cols, renamed_star_cols)}, inplace=True)

    # round columms
    for col in data.dtypes[data.dtypes == 'float64'].index:
        data[col] = round(data[col], )
        data['moonSep'] = round(data['moonSep'], 1)

    ####################
    #    Extract relevant moon data into dataset
    ####################
    if moon_data:
        moon = fields[['mjdExpStart', 'moonAz', 'moonAlt', 'moonPhase']].drop_duplicates()
        moon = moon.loc[moon['moonAlt'] > -.5]
        moon['time_step_id'] = [ts[mjd] for mjd in moon['mjdExpStart']]

        # Get moon phase emoji
        avg_moon_phase = np.nanmean(moon['moonPhase'])
        phase_dict = {'🌑': [0,.1],
                      '🌒': [.1,.3],
                      '🌓': [.3,.7],
                      '🌔': [.7,.9],
                      '🌕': [.9,1.01]}
        phase_icon = []
        for i in range(len(phase_dict)):
            rng  = list(phase_dict.values())[i]
            char = list(phase_dict.keys())[i]
            if rng[0] <= avg_moon_phase < rng[1]:
                phase_icon.append(char)

        moon['phase_icon'] = [phase_icon[0] for i in range(len(moon))]

        moon.rename(columns={old:new for old, new in zip(moon_cols, renamed_moon_cols)}, inplace=True)
        return fields[renamed_field_cols], stars[renamed_star_cols], moon[renamed_moon_cols]

    return fields, stars

####################
#    Plot priorities as histogram with selection
####################
def make_p_interact(field_data, p_selection, height=150, width=600):
    '''histogram of priorities that is brush-linked the plots'''
    pri = alt.Chart(
        field_data
    ).mark_bar(
        size=50,
        color="#226082"
    ).encode(
        x=alt.X('p:O', title='Field Priority'),
        y=alt.Y('count()', title='# of Fields')
    ).add_selection(
        p_selection
    ).properties(
        height=height,
        width=width,
    )
    return pri

####################
#    Plot examples of different completions with selection
####################
def make_c_interact(field_data, c_selection, height=30, width=600):
    '''legend that is also brush-linked to the plots'''
    comp = alt.layer(
        # completion chart/legend
        alt.Chart(
            data
        ).mark_square(
            size=150,
            fill="blue"
        ).encode(
            x=alt.X('c', bin=alt.Bin(extent=[0, 100], step=10), title="Field Completion")
        ),
        # Field Priority chart/legent
        alt.Chart(
            data
        ).mark_square(
            size=60,
            fillOpacity=0,
            stroke="orange"
        ).encode(
            x=alt.X('c', bin=alt.Bin(extent=[0, 100], step=10), title="Field Completion"),
            strokeWidth=alt.Size('max(c)', legend=None, bin=alt.Bin(extent=[0, 100], step=20))
        )
    ).add_selection(
        c_selection
    ).properties(
        height=height,
        width=width)

    return comp

####################
#    Left-hand-side Altitude-Time plot
####################
def make_alts_plot(field_data, select_field, select_time, select_c, select_p, field_scale):
    '''
    Plot the altitude of fields over time.
    '''
    ####################
    #     Plot time against altitude (Base plot)
    ####################
    base = alt.Chart().mark_point().encode(
        x=alt.X('st:T', title='Local Time'),
        y=alt.Y('alt:Q', scale=alt.Scale(domain=(0,90)), title='Altitude(°)'),
        color=alt.Color('fS:N', sort='descending', scale=field_scale, legend=alt.Legend(title="Field Status")),
            opacity=alt.condition(select_field, alt.value(1), alt.value(0))
    ).add_selection(
        select_time
    ).transform_filter(
        'datum.fS != "Scheduled Now"'
    ).transform_filter(
        {'or': ['datum.sch', select_field]}
    ).add_selection(
        select_field
    )

    ####################
    #     Plot time against altitude for the currently field observed so it's always on top
    ####################
    observing_field_alts1 = alt.Chart().mark_point(filled=True).encode(
        x=alt.X('st:T', title='Local Time'),
        y=alt.Y('alt:Q', title='Altitude(°)'),
        color=alt.Color('fS:N', sort='descending', scale=field_scale, legend=alt.Legend(title='Field Status')),
        opacity=alt.condition(select_field, alt.value(1), alt.value(0.55)),
        size=alt.condition(select_field, alt.value(200), alt.value(200))
    ).transform_filter(
        'datum.fS == "Scheduled Now"'
    ).add_selection(
        select_field
    )

    ####################
    #    Plot fields including those not scheduled for observation
    ####################
    observing_field_alts = alt.Chart(
        field_data
    ).mark_square(
        opacity=0.25,
        size=30,
        stroke='red',
        strokeWidth=2
    ).encode(
        x=alt.X('st:T', title='Local Time'),
        y=alt.Y('alt:Q', title='Altitude(°)'),
        color=alt.Color('fS', sort='descending', scale=field_scale),
        tooltip=[
            alt.Tooltip('mS', title="Moon separation: "),
            alt.Tooltip('fid', title="Field ID"),
            alt.Tooltip('c', title="Field Completion"),
            alt.Tooltip("p", title="Field Priority")],
        opacity=alt.condition(select_c & select_p , alt.value(1), alt.value(0)),
        strokeOpacity=alt.condition(select_field, alt.value(1), alt.value(0))
    ).transform_filter(
        select_time
    )
    ####################
    #    Plot fields schedule for observation as yellow pluses
    ####################
    observing_field_crosses = alt.Chart().mark_point(
        shape='cross',
        fill='yellow',
        size=60,
        fillOpacity=1,
        strokeWidth=0
    ).encode(
        x=alt.X('st:T', title='Local Time'),
        y=alt.Y('alt:Q', title='Altitude(°)')
    ).transform_filter(
        'datum.fS == "Scheduled Now"'
    )

    ####################
    #    Layer all altitude plot elements together
    ####################
    alts = alt.layer(
        # add interactive line for mouseover
        alt.Chart().mark_rule(color='#C0C0C0').encode(
            x=alt.X('st:T', title='Local Time')
        ).transform_filter(select_time),
        base,
        observing_field_alts,
        observing_field_crosses,
        data=field_data,
    ).properties(
        width=600,
        height=300
    )

    return alts


def make_viz(field_data, star_data, moon_data, select_field, select_time, field_scale):
    '''
    Create the sky mapping part of the visualization, with fields, stars, and the moon.
    '''
    ####################
    #    Create selection objects for completion and priority
    ####################
    select_c = alt.selection_interval(init={'c': [60, 100]})
    select_p = alt.selection_interval(init={'p': [3, 5]})

    ####################
    #    Create plots that serve as legends for completion and priority
    ####################
    c_legend = make_c_interact(field_data, select_c)
    p_legend = make_p_interact(field_data, select_p)

    ####################
    #    data for NSEW labels
    ####################
    directions = pd.DataFrame({"lat": [-3, -3, -3, -3],
                               "long": [0, 90, 180, 270],
                               "text": ["N", "E", "S", "W"]})
    ####################
    #    Plot NSEW labels to plot
    ####################
    dir_labels = alt.Chart(
        directions
    ).mark_text(
        fontSize=16,
        color="#C0C0C0"
    ).encode(
        longitude="long",
        latitude="lat",
        text="text")

    ####################
    #    Data for altitude labels
    ####################
    alt_df = pd.DataFrame({"lat": [2, 30, 60, 90, 60, 30, 2],
                           "long": [0, 0, 0, 0, 180, 180, 180],
                           "text": ["0°", "30°", "60°", "90°", "60°", "30°", "0°"]})

    ####################
    #    Plot altitude labels
    ####################
    alt_labels = alt.Chart(
        alt_df
    ).mark_text(
        color='white'
    ).encode(
        longitude="long",
        latitude="lat",
        text="text")

    ####################
    #    Plot moon
    ####################
    moon_base = alt.Chart().mark_text(size=26).encode(
        latitude='mAlt',
        longitude='mAz',
        text='phase'
    ).transform_filter(
        select_time
    )

    ####################
    #    Mouseover label for the moon
    ####################
    moon_selection = alt.selection_single(on='mouseover')
    moon_text = alt.Chart().mark_text(
        stroke='white',
        dy=12,
        text='moon'
    ).encode(
        latitude='mAlt',
        longitude='mAz',
        opacity=alt.condition(moon_selection, alt.value(1), alt.value(0))
    ).transform_filter(
        select_time
    ).add_selection(
        moon_selection
    )

    moon = alt.layer(
        moon_base,
        moon_text,
        data=moon_data
    )

    ####################
    #    Plot bright stars
    ####################
    stars = alt.Chart(
        star_data
    ).mark_point(
        filled=True,
        color='#ffffff'
    ).encode(
        latitude='alt',
        longitude='az',
        size=alt.Size('mag', sort='descending', scale=alt.Scale(type='pow', range=(2,50)), legend=alt.Legend(title="Stellar Magnitude"))
    ).add_selection(
        select_time
    ).transform_filter(
        select_time
    )

    ####################
    #     Tooltips shared amongst the plots
    ####################
    tooltips = [
        alt.Tooltip('mS', title="Moon separation: "),
        alt.Tooltip('fid', title="Field ID"),
        alt.Tooltip('c', title="Field Completion"),
        alt.Tooltip("p", title="Field Priority")
    ]

    ####################
    #     Plot fields not scheduled on sky map
    ####################
    fields_not_scheduled = alt.Chart(
        field_data
    ).mark_square(
        opacity=0.75,
        size=100
    ).encode(
        latitude='alt',
        longitude='az',
        color=alt.Color('fS', sort='descending', scale=field_scale),
        tooltip=tooltips,
        opacity=alt.condition(select_c & select_p , alt.value(1), alt.value(0))
    ).transform_filter(
        select_time
    ).transform_filter(
        '! datum.sch'
    )

    ####################
    #    Plot scheduled fields on sky map
    ####################
    fields_scheduled = alt.Chart(
        field_data
    ).mark_square(
        opacity=0.75,
        size=100,
        stroke='red',
        strokeWidth=2
    ).encode(
        latitude='alt',
        longitude='az',
        color=alt.Color('fS', sort='descending', scale=field_scale),
        tooltip=tooltips,
        opacity=alt.condition('datum.sch', alt.value(1), alt.value(0)),
        strokeOpacity=alt.condition(select_field, alt.value(1), alt.value(0))
    ).transform_filter(
        select_time
    ).add_selection(
        select_field
    )

    ####################
    #    Plot yellow + over fields scheduled to be observed tonight on sky map
    ####################
    scheduled_fields_mark = alt.Chart(
        field_data
    ).mark_point(
        shape='cross',
        fill='yellow',
        size=50,
        fillOpacity=1,
        strokeWidth=0
    ).encode(
        latitude='alt',
        longitude='az'
    ).transform_filter(
        select_time
    ).transform_filter(
        'datum.sch'
    )

    ####################
    #    Plot completion overlay on sky map
    ####################
    c = alt.Chart(
        field_data
    ).mark_square(
        stroke='orange',
        fillOpacity=0
    ).encode(
        latitude='alt',
        longitude='az',
        tooltip=tooltips,
        strokeWidth=alt.Size('c'),  # thickness of stroke indicates completion
        opacity=alt.condition(select_c & select_p , alt.value(1), alt.value(0))
    ).transform_filter(
        select_time
    ).transform_filter(
        'datum.fS == "Available"'  # Only plot for available fields
    ).transform_filter(
        '! datum.sch')  # Don't plot of fields already scheduled

    ####################
    #    Plot field currently observed so it's on top/higher opacity on the sky map
    ####################
    field_scheduled_now = alt.Chart(
        field_data
    ).mark_square(
        opacity=1,
        size=80
    ).encode(
        latitude='alt',
        longitude='az',
        color=alt.Color('fS', sort='descending', scale=field_scale),
        tooltip=tooltips,
    ).transform_filter(
        select_time
    ).transform_filter(
        'datum.fS == "Scheduled Now"'
    )

    ####################
    #     Add red border to selected fields
    ####################
    selected_field = alt.Chart(
        field_data
    ).mark_square(
        opacity=1,
        size=90,
        filled=False,
        color='red'
    ).encode(
        latitude='alt',
        longitude='az'
    ).transform_filter(
        select_time
    ).transform_filter(
        select_field
    )

    ####################
    #     Compose all field related elements together
    ####################
    fields = alt.layer(
        # fields_scheduled
        fields_scheduled,
        # fields not scheduled
        fields_not_scheduled,
        # field scheduled now
        field_scheduled_now,
        # + for scheduled fields
        scheduled_fields_mark,
        # plot completion
        c,
        # field selection borders
        selected_field,
    ).add_selection(
        select_field
    )

    ####################
    #    add text to display datetime (upper left on the page)
    ####################
    time = alt.Chart(
        field_data
    ).mark_text(
        align='left',
        dx=0,
        dy=0,
        baseline='bottom',
        fontSize=25,
        color="#C0C0C0",
        fontWeight=300
    ).encode(
        text=alt.Text('st:T', format="%Y-%m-%dT%H:%M:%S")
    ).transform_filter(select_time)

    ####################
    #    add text to display field Scheduled Now (upper middle on page)
    ####################
    field_text = alt.Chart(
        field_data
    ).mark_text(
        align='left',
        dx=50,
        dy=0,
        baseline='bottom',
        fontSize=25,
        color="#C0C0C0",
        fontWeight=500
    ).encode(
        text='fid'
    ).transform_calculate(
        fid = '"Scheduled fid: " + datum.fid'
    ).transform_filter(
        select_time
    ).transform_filter(
        'datum.fS == "Scheduled Now"'
    )

    ####################
    #    Make altitude plot
    ####################
    alts = make_alts_plot(data, select_field, select_time, select_c, select_p, field_scale)

    ####################
    #    Create sky map visualization (right side circular plot)
    ####################
    sky_map = ((time | field_text) & (c_legend & p_legend &  alts)) | alt.layer(  # LAYOUT ARRANGED HERE
        # use the sphere of the Earth as the base layer
        alt.Chart({'sphere': True}).mark_geoshape(
            color=alt.RadialGradient(
                gradient='radial',
                stops=[alt.GradientStop(color='#07161f', offset=0),
                       alt.GradientStop(color='#0e2836', offset=1)],
            )
        ),
        # add a graticule for geographic reference lines
        alt.Chart({'graticule': True}).mark_geoshape(
            stroke='#515151', strokeWidth=1
        ),
        # star layer
        stars,
        # moon layer
        moon,
        # field layer
        fields,
        # NSEW direction labels
        dir_labels,
        # altitude lables
        alt_labels,
    ).properties(
        width=800,
        height=800,
    ).project(
        type='azimuthalEquidistant', clipAngle=90, rotate=[0,-90, 180]
    )


    return sky_map


def get_interactive_elements():
    '''
    Create the time and field selection objects and the field status color scheme.
    '''
    ####################
    #    Create interaction object for by mouseover on time
    ####################
    select_time = alt.selection_single(
        on='mouseover',   # select on mouseover events
        nearest=True,     # select data point nearest the cursor
        empty='none',     # empty selection includes no data points
        fields=['tsid'],
        init={'tsid': 0}
    )

    ####################
    # Create field interaction object
    ####################
    select_field = alt.selection_multi(on='click', fields=['fid'], empty='none')

    ####################
    #    Set up color scheme for field status
    ####################
    field_scale = alt.Scale(domain=('Scheduled Now', 'Available', 'Unavailable'),
                            range=["yellow", "blue", "#6E7DDB"])

    return select_field, select_time, field_scale


if __name__ == "__main__":
    import warnings
    warnings.simplefilter(action='ignore')

    ####################
    #    Read data and preprocess
    ####################
    df = pd.read_csv('mjd-59305-sdss-simple-expanded-priority.csv', index_col=0)
    data, star_data, moon_pos = get_data(df, moon_data=True)

    ####################
    #    Create interactive selection elements and scales
    ####################
    select_field, select_time, field_scale = get_interactive_elements()

    ####################
    #    Make visualization
    ####################
    visual = make_viz(data, star_data, moon_pos, select_field, select_time, field_scale)

    ####################
    #    Configure plot
    ####################
    chart = (visual).configure(background="#0e2836"
    ).configure_axis(
        labelFontSize=20,
        titleFontSize=20,
        labelFontWeight=200,
    ).configure_axisLeft(
        labelColor="#C0C0C0",
        titleColor="#C0C0C0",
        titleFontSize=20,
        labelFontSize=14,
    ).configure_axisBottom(
        labelColor="#C0C0C0",
        titleColor="#C0C0C0",
        titleFontSize=20,
        labelFontSize=14
    ).configure_title(
        fontSize=24
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        grid=False
    ).configure_legend(
        labelColor="#C0C0C0",
        titleColor="#C0C0C0"
    ).configure_concat(
        columns=2,
        spacing=40
    )

    ####################
    #    Save plot
    ####################
    saveName = "altair_with_moon_final"
    chart.save(f"{saveName}.html")
    chart.save(f"{saveName}.json")

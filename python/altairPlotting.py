import pandas as pd
import altair as alt
import numpy as np

def airmass(altitude, precise=False):
    z = 90 - altitude
    if precise:
        return 1 / (np.cos(z) + 0.025 * np.exp(-1 * np.cos(z)))
    return 1 / (np.cos(z))

def get_data(data, moon_data=False):
    '''
    Takes the sdss field data, rounds floats, subsets to only observed fields, and calculates utcs times.
    '''
    field_cols = ['Altitude(°)', 'az', 'moonSep', 'fieldID', 'objType', 'fieldStatus', 'Observation Start Time', 'time_step_id', 'priority', 'completion', 'Scheduled']
    star_cols = ['Altitude(°)', 'az', 'time_step_id', 'Stellar Magnitude']
    moon_cols = ['moonAlt', 'moonAz', 'time_step_id', 'fieldID']
    # round columms
    for col in data.dtypes[data.dtypes == 'float64'].index:
        data[col] = round(data[col], 6)
    data['moonSep'] = round(data['moonSep'], 1)

    scheduled = data.loc[data['scheduled']==True]
    scheduled.sort_values('mjdExpStart', inplace=True)

    # fields = data[data['fieldID'].isin(scheduled['fieldID'])]
    fields = data.query('objType == "sdss field"')
    fields['Observation Start Time'] = pd.to_datetime(fields['mjdExpStart'] + 2400000.5, unit='D', origin='julian') - pd.Timedelta(hours=6)
    fields = fields.loc[fields['alt'] > -.5] # could change to use 'Risen'

    stars = data.query('objType == "bright star"')
    stars = stars.loc[stars['alt'] > -.5] # could change to use 'Risen'

    # Create different field statuses
    fields['fieldStatus'] = 'Available'
    fields.loc[fields['scheduled'], 'fieldStatus'] = 'Scheduled Now'
    fields.loc[fields['alt'] < 40, 'fieldStatus'] = 'Unavailable'
    
    fields['Scheduled'] = False
    fields.loc[fields['fieldID'].isin(scheduled['fieldID']), 'Scheduled'] = True
    
    fields['Altitude(°)'] = fields['alt']

    # Assign observation numbers as time step id
    ts = {mjd: ii for ii, mjd in enumerate(fields['mjdExpStart'].sort_values().unique())}
    fields['time_step_id'] = [ts[mjd] for mjd in fields['mjdExpStart']]
    stars['time_step_id'] = [ts[mjd] for mjd in stars['mjdExpStart']]

    # Round mangitudes to nearest 0.5
    stars = stars.query('magnitude < 4.5')
    stars['Stellar Magnitude'] = round(stars['magnitude'], 0)
    stars['Altitude(°)'] = stars['alt']
    
    # Get moon data
    if moon_data:
        moon = fields[['mjdExpStart', 'moonAz', 'moonAlt']].drop_duplicates()
        moon = moon.loc[moon['moonAlt'] > -.5]
        moon['time_step_id'] = [ts[mjd] for mjd in moon['mjdExpStart']]
        moon['fieldID'] = 'moon'
        
        return fields[field_cols], stars[star_cols], moon[moon_cols]
    
    return fields, stars

def get_moon_data(field_data):
    '''
    Get moon positions and phases over the course of the night
    '''
    moon_pos = field_data[['mjdExpStart', 'moonAz', 'moonAlt', 'moonPhase']].drop_duplicates()
    moon_pos = moon_pos.loc[moon_pos['moonAlt'] > -.5]
    return moon_pos

def make_alts_plot(field_data, select_field, select_time, field_scale):
    '''
    Plot the altitude of fields over time.
    '''
    # Plot time against altitude
    base = alt.Chart().mark_point().encode(
        x='Observation Start Time:T',
        y='Altitude(°):Q',
        color=alt.Color('fieldStatus:N', sort='descending', scale=field_scale, legend=alt.Legend(title="Field Status")),
        opacity=alt.condition(select_field, alt.value(1), alt.value(0.21))
    ).add_selection(
        select_time
    ).transform_filter(
        'datum.fieldStatus != "Scheduled Now"'
    )

    # Plot time against altitude for the currently field observed so it's always on top
    observing_field_alts = alt.Chart().mark_point(filled=True).encode(
        x='Observation Start Time:T',
        y='Altitude(°):Q',
        color=alt.Color('fieldStatus:N', sort='descending', scale=field_scale),
        opacity=alt.condition(select_field, alt.value(1), alt.value(0.55)),
        size=alt.condition(select_field, alt.value(200), alt.value(200))
    ).transform_filter(
        'datum.fieldStatus == "Scheduled Now"'
    ).add_selection(
        select_field
    )

    # layer all altitude plot elements together
    alts = alt.layer(
        base,
        observing_field_alts,
        # add interactive line for mouseover
        alt.Chart().mark_rule().encode(
            x='Observation Start Time:T'
        ).transform_filter(select_time),
        # add text to display datetime
        alt.Chart().mark_text(align='left', dx=-375, dy=75, baseline='bottom', fontSize=14, fontWeight=300).encode(
            text=alt.Text('Observation Start Time:T', format="%Y-%m-%dT%H:%M:%S")
        ).transform_filter(select_time),
        # add text to display field currently observing
        alt.Chart().mark_text(align='left', dx=-375, dy=90, baseline='bottom', fontSize=14, fontWeight=500).encode(
            text='fieldID'
        ).transform_calculate(
            fieldID = '"Obseving fieldID: " + datum.fieldID'
        ).transform_filter(select_time)
        .transform_filter(
            'datum.fieldStatus == "Scheduled Now"'
        ),

        data=field_data
    ).properties(
        width=800,
        height=200
    )

    return alts

def make_sky_map(field_data, star_data, moon_data, select_field, select_time, field_scale):
    '''
    Create the sky mapping part of the visualization, with fields, stars, and the moon.
    '''
    # NSEW labels
    directions = pd.DataFrame({"lat": [-3, -3, -3, -3], "long": [0, 90, 180, 270], "text": ["N", "E", "S", "W"]})
    dir_labels = alt.Chart(directions).mark_text(fontSize=16).encode(
        longitude="long",
        latitude="lat",
        text="text")

    # Altitude labels
    alt_df = pd.DataFrame({"lat": [2, 30, 60, 90, 60, 30, 2], "long": [0, 0, 0, 0, 180, 180, 180], "text": ["0°", "30°", "60°", "90°", "60°", "30°", "0°"]})
    alt_labels = alt.Chart(alt_df).mark_text(color='white').encode(
        longitude="long",
        latitude="lat",
        text="text")

    moon_base = alt.Chart().mark_text(size=26, text='🌗').encode(
        latitude='moonAlt',
        longitude='moonAz'
    ).transform_filter(
        select_time
    )

    # Mouseover label
    moon_selection = alt.selection_single(on='mouseover')
    moon_text = alt.Chart().mark_text(stroke='white', dy=12).encode(
        latitude='moonAlt',
        longitude='moonAz',
        text='fieldID',
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

    # Plot bright stars
    # https://github.com/altair-viz/altair/issues/2258 - white is not actually white?
    stars = alt.Chart(star_data).mark_point(filled=True, color='#ffffff').encode(
        latitude='Altitude(°)',
        longitude='az',
        size=alt.Size('Stellar Magnitude', sort='descending', scale=alt.Scale(type='pow', range=(2,50)))
    ).add_selection(
        select_time
    ).transform_filter(
        select_time
    )


    # Plot fields
    fields = alt.Chart(field_data).mark_square(opacity=0.75, size=80).encode(
        latitude='Altitude(°)',
        longitude='az',
        color=alt.Color('fieldStatus', sort='descending', scale=field_scale),
        tooltip=['moonSep', 'fieldID']
    ).transform_filter(
        select_time
    ).add_selection(
        select_field
    )

    # Plot field currently observed so it's on top/higher opacity
    observing_field_skymap = alt.Chart(field_data).mark_square(opacity=1, size=80).encode(
        latitude='Altitude(°)',
        longitude='az',
        color=alt.Color('fieldStatus', sort='descending', scale=field_scale),
        tooltip=['moonSep', 'fieldID']
    ).transform_filter(
        select_time
    ).transform_filter(
        'datum.fieldStatus == "Scheduled Now"'
    )

    # Add red border to selected fields
    selected_field = alt.Chart(field_data).mark_square(opacity=1, size=90, filled=False, color='red').encode(
        latitude='Altitude(°)',
        longitude='az'
    ).transform_filter(
        select_time
    ).transform_filter(
        select_field
    )

    # Create sky map visualization
    sky_map = alt.layer(
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
        # fields not being observed
        fields,
        # field currently observed
        observing_field_skymap,
        # field selection borders
        selected_field,
        # NSEW direction labels
        dir_labels,
        # altitude lables
        alt_labels,
        title="Sky with SDSS fields, looking up while facing south"
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
    # Interaction by mouseover on time
    select_time = alt.selection_single(
        on='mouseover',  # select on mouseover events
        nearest=True,    # select data point nearest the cursor
        empty='none',     # empty selection includes no data points
        fields=['time_step_id'],
        init={'time_step_id': 0}
    )

    # Interaction on fields
    # https://github.com/vega/vega-lite/issues/5553 - jeez 
    select_field = alt.selection_multi(on='click', fields=['fieldID'], empty='none')

    # Set up color scheme for field status
    field_scale = alt.Scale(domain=('Scheduled Now', 'Available', 'Unavailable'),
                            range=["#ffda60", '#a7b7bf', '#506e7f'])
    return select_field, select_time, field_scale

if __name__ == "__main__":
    import warnings
    warnings.simplefilter(action='ignore')
    for mjd in range(59390, 59391):
        print(mjd)
        # Read data and preprocess
        df = pd.read_csv(f'../data/full_data/mjd-{mjd}-sdss-simple-expanded-priority.csv', index_col=0)
        data, star_data, moon_pos = get_data(df, moon_data=True)
        # moon_pos = pd.read_csv('../data/moon-positions-mjd-59418.csv')

        # Create interactive selection elements and scales
        select_field, select_time, field_scale = get_interactive_elements()

        # Make sky plot
        sky = make_sky_map(data, star_data, moon_pos, select_field, select_time, field_scale)

        # Make time vs altitude plot
        altitudes = make_alts_plot(data, select_field, select_time, field_scale)

        # Configure plot
        chart = (sky & altitudes).configure(background="white"
        ).configure_legend(
            labelFontSize=14,
            titleFontSize=16,
            symbolSize=150
        ).configure_axis(
            labelFontSize=14,
            titleFontSize=16,
            labelFontWeight=500
        ).configure_title(
            fontSize=24
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False
        )

        # Save as html
        # chart.save(f"../data/viz_jsons/altair_{mjd}.html")
        chart.save(f"altair_{mjd}.html")

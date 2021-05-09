import pandas as pd
import altair as alt
import numpy as np

def airmass(altitude, precise=False):
    z = 90 - altitude
    if precise:
        return 1 / (np.cos(z) + 0.025 * np.exp(-1 * np.cos(z)))
    return 1 / (np.cos(z))

def get_data(data):
    '''
    Takes the sdss field data, rounds floats, subsets to only observed fields, and calculates utcs times.
    '''
    # round columms
    for col in data.dtypes[data.dtypes == 'float64'].index:
        data[col] = round(data[col], 6)
    data['moonSep'] = round(data['moonSep'], 1)
        
    scheduled = data.loc[data['scheduled']==True]
    scheduled.sort_values('mjdExpStart', inplace=True)
    
    fields = data[data['fieldID'].isin(scheduled['fieldID'])]
    # fields = data.query('objType == "sdss field"')
    fields['Observation Start Time'] = pd.to_datetime(fields['mjdExpStart'] + 2400000.5, unit='D', origin='julian') - pd.Timedelta(hours=6)
    fields = fields.loc[fields['alt'] > -.5] # could change to use 'Risen'
    
    stars = data.query('objType == "bright star"')
    stars = stars.loc[stars['alt'] > -.5] # could change to use 'Risen'
    
    fields['fieldStatus'] = ['Observing' if x else 'Available' for x in fields['scheduled']]
    fields.loc[fields['alt'] < 40, 'fieldStatus'] = 'Unavailable'
    
    # Assign observation numbers as time step id
    ts = {mjd: ii for ii, mjd in enumerate(fields['mjdExpStart'].sort_values().unique())}
    fields['time_step_id'] = [ts[mjd] for mjd in fields['mjdExpStart']]
    stars['time_step_id'] = [ts[mjd] for mjd in stars['mjdExpStart']]
    
    # Round mangitudes to nearest 0.5
    stars['Magnitude'] = round(stars['magnitude'] * 2, 0) / 2
    
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
        y='alt:Q',
        color=alt.Color('fieldStatus:N', sort='descending', scale=field_scale),
        opacity=alt.condition(select_field, alt.value(1), alt.value(0.1))
    ).add_selection(
        select_time
    ).add_selection(
        select_field
    ).transform_filter(
        'datum.fieldStatus != "Observing"'
    )

    # Plot time against altitude for the currently field observed so it's always on top
    observing_field_alts = alt.Chart().mark_point(filled=True).encode(
        x='Observation Start Time:T',
        y='alt:Q',
        color=alt.Color('fieldStatus:N', sort='descending', scale=field_scale),
        opacity=alt.condition(select_field, alt.value(1), alt.value(0.5)),
        size=alt.condition(select_field, alt.value(200), alt.value(50))
    ).transform_filter(
        'datum.fieldStatus == "Observing"'
    )

    # layer all altitude plot elements together
    alts = alt.layer(
        base,
        observing_field_alts,
        # add interactive line for mouseover
        alt.Chart().mark_rule(color='#777777').encode(
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
        'datum.fieldStatus == "Observing"'
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

    # Plot moon position
    moon = alt.Chart(moon_data).mark_point(filled=True, size=400, color='#A0A0A0').encode(
        latitude='moonAlt',
        longitude='moonAz'
    ).transform_filter(
        select_time
    )

    # Plot bright stars
    stars = alt.Chart(star_data).mark_point(filled=True, color='#FFFFFF').encode(
        latitude='alt',
        longitude='az',
        size=alt.Size('Magnitude', sort='descending', scale=alt.Scale(range=(5,50)))
    ).add_selection(
        select_time
    ).transform_filter(
        select_time
    )


    # Plot fields
    fields = alt.Chart(field_data).mark_square(opacity=0.75, size=80).encode(
        latitude='alt',
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
        latitude='alt',
        longitude='az',
        color=alt.Color('fieldStatus', sort='descending', scale=field_scale),
        tooltip=['moonSep', 'fieldID']
    ).transform_filter(
        select_time
    ).transform_filter(
        'datum.fieldStatus == "Observing"'
    )

    # Add red border to selected fields
    selected_field = alt.Chart(field_data).mark_square(opacity=1, size=90, filled=False, color='red').encode(
        latitude='alt',
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
            fill='#1A1A1A'
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
        height=600
    ).project(
        type='azimuthalEquidistant', scale=178, translate=[400, 300], clipAngle=90, rotate=[0,-90, 180]
    )

    return sky_map
    
def get_interactive_elements():
    '''
    Create the time and field selection objects and the field status color scheme.
    '''
    # Interaction by mouseover on time
    select_time = alt.selection_single(
    #     encodings=['x'], # limit selection to x-axis value
        on='mouseover',  # select on mouseover events
        nearest=True,    # select data point nearest the cursor
        empty='none',     # empty selection includes no data points
        fields=['time_step_id'],
        init={'time_step_id': 0}
    )

    # Interaction on fields
    select_field = alt.selection_multi(on='click', fields=['fieldID'], empty='none')

    # Set up color scheme for field status

    # color scheme for field status
    yellow = 'yellow' # '#E3E028' # "#6E7DDB"
    field_scale = alt.Scale(domain=('Observing', 'Available', 'Unavailable'),
                          range=[yellow, "blue", '#6E7DDB'])
    return select_field, select_time, field_scale

if __name__ == "__main__":
    import warnings
    warnings.simplefilter(action='ignore')
    
    # Read data and preprocess
    df = pd.read_csv('../data/mjd-59418-sdss-simple-expanded.csv', index_col=0)
    data, star_data = get_data(df)
    moon_pos = pd.read_csv('../data/moon-positions-mjd-59418.csv')

    # Create interactive selection elements and scales
    select_field, select_time, field_scale = get_interactive_elements()

    # Make sky plot
    sky = make_sky_map(data, star_data, moon_pos, select_field, select_time, field_scale)
    
    # Make time vs altitude plot
    altitudes = make_alts_plot(data, select_field, select_time, field_scale)

    # Configure plot
    chart = (sky & altitudes).configure(background="#CACACA"
        ).configure_legend(
            labelFontSize=14, 
            titleFontSize=16, 
            symbolSize=150
        ).configure_axis(
            labelFontSize=14, 
            titleFontSize=16, 
            labelFontWeight=500
        ).configure_title(fontSize=24)

    # Save as html
    chart.save("altair_polished.html")
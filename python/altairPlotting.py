import pandas as pd
import altair as alt
import numpy as np

def airmass(altitude, precise=False):
    z = 90 - altitude
    if precise:
        return 1 / (np.cos(z) + 0.025 * np.exp(-1 * np.cos(z)))
    return 1 / (np.cos(z))

def clean_data(data):
    '''
    Takes the sdss field data, rounds floats, subsets to only observed fields, and calculates utcs times.
    '''
    for col in data.dtypes[data.dtypes == 'float64'].index:
        data[col] = round(data[col], 6)
        
    scheduled = data.loc[data['scheduled']==True]
    # Different scheduling algorithm
    # scheduled = data.loc[data.groupby('fieldID').alt.idxmax()].sort_values('alt', ascending=True).drop_duplicates(['mjdExpStart'], keep='first')
    scheduled.sort_values('mjdExpStart', inplace=True)
    
    data = data[data['fieldID'].isin(scheduled['fieldID'])]
    data['start'] = pd.to_datetime(data['mjdExpStart'] + 2400000.5, unit='D', origin='julian')
    
    return data

def get_moon_data(field_data):
    '''
    Get moon positions and phases over the course of the night
    '''
    moon_pos = field_data[['mjdExpStart', 'moonAz', 'moonAlt', 'moonPhase']].drop_duplicates()
    moon_pos = moon_pos.loc[moon_pos['moonAlt'] > -.5]
    return moon_pos

def make_sky_plot(field_data, moon_data):
    '''
    Use altair to make an interactive plot showing the locations of fields ove the course of the night
    '''
    label_df = pd.DataFrame({"lat": [0, 0, 0, 0], "long": [0, 90, 180, 270], "text": ["N", "E", "S", "W"]})
    labels = alt.Chart(label_df).mark_text().encode(
            longitude="long",
            latitude="lat",
            text="text")
        
    start = field_data['mjdExpStart'].min()
    stop = field_data['mjdExpStart'].max()
    tstep = 0.0125

    pink_blue = alt.Scale(domain=(True, False),
                          range=["salmon", "steelblue"])

    slider = alt.binding_range(min=start, max=stop, step=tstep)


    select_time = alt.selection_single(name="select", fields=['mjdExpStart'],
                                       bind=slider, init={'mjdExpStart': start})

    moon = alt.Chart(moon_data).mark_point(filled=True, size=400, color='grey').encode(
        latitude='moonAlt',
        longitude='moonAz',
        tooltip='moonPhase'
    ).transform_filter(
        select_time
    )

    fields = alt.Chart(field_data).mark_square(opacity=1, size=150).encode(
        latitude='alt',
        longitude='az',
        color=alt.Color('scheduled', scale=pink_blue),
        tooltip=['moonSep', 'fieldID']
    ).add_selection(
        select_time
    ).transform_filter(
        select_time
    )

    sky_map = alt.layer(
        # use the sphere of the Earth as the base layer
        alt.Chart({'sphere': True}).mark_geoshape(
            fill='#e6f3ff'
        ),
        # add a graticule for geographic reference lines
        alt.Chart({'graticule': True}).mark_geoshape(
            stroke='#ffffff', strokeWidth=1
        ),
        fields,
        moon,
        labels,
        title="Sky with SDSS fields, looking up while facing south"
    ).configure_title(
        fontSize=24
    ).properties(
        width=1000,
        height=800
    )

    return sky_map.project(
        type='azimuthalEquidistant', scale=250, translate=[500, 400], clipAngle=90, rotate=[0,-90, 180]
    ).configure_view(stroke=None)

if __name__ == "__main__":
    df = pd.read_csv('../data/mjd-59418-sdss-simple.csv', index_col=0)

    data = clean_data(df)
    moon_pos = get_moon_data(data)
    
    chart = make_sky_plot(data, moon_pos)
    chart.save('altair.html')
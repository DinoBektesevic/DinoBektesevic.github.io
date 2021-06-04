import pandas as pd
import altair as alt
import numpy as np
import json
import os
import tqdm

from .altairPlotting import get_data


if __name__ == "__main__":
    
    import warnings
    warnings.simplefilter(action='ignore')

    for mjd in tqdm.tqdm(range(59305, 59670)):
        # Create json save directory
        save_dir=f'json_data_v2/{mjd}/'
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
            
        # Read data and preprocess
        file = f"simpleExpandedPriorityV2/mjd-{mjd}-sdss-simple-expanded-priority.csv"
        df = pd.read_csv(file, index_col=0)
        data, star_data, moon_data = get_data(df, moon_data=True)
        
        # Save star json
        star_json = star_data.to_json(orient='records')
        with open(save_dir + "stars.json", "w") as outfile: 
            json.dump(star_json, outfile)
            
        # Save field json
        field_json = data.to_json(orient='records')
        with open(save_dir + "fields.json", "w") as outfile: 
            json.dump(field_json, outfile)
            
        # Save moon json
        moon_json = moon_data.to_json(orient='records')
        with open(save_dir + "moon.json", "w") as outfile: 
            json.dump(moon_json, outfile)
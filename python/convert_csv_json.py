import pandas as pd
import os

from altairPlotting import get_data


DATA_IN_DIR="../../full_data/"
DATA_OUT_DIR="../../data/"


if __name__ == "__main__":
    if not os.path.exists(DATA_OUT_DIR):
        os.mkdir(DATA_OUT_DIR)

    for mjd in range(59305, 59670):
        import warnings
        warnings.simplefilter(action='ignore')

        save_path = os.path.join(DATA_OUT_DIR, str(mjd))
        if not os.path.exists(save_path):
            os.mkdir(save_path)

        # Read data and preprocess
        file = os.path.join(DATA_IN_DIR, f"mjd-{mjd}-sdss-simple-expanded-priority.csv")
        df = pd.read_csv(file, index_col=0)
        data = get_data(df, moon_data=True)

        for name, datum in zip(("fields.json", "stars.json",  "moon.json"), data):
            outPath = os.path.join(save_path, name)
            datum.to_json(outPath, orient='records', double_precision=2, date_unit="s")

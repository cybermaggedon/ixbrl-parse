
import pandas as pd

def values_to_df(values):

    data = []

    for n, v in values.items():
        data.append([
            n.localname, v.to_value().get_value(), v.unit
        ])

    return pd.DataFrame(
        data,
        columns = ["fact", "value", "unit"]
    )


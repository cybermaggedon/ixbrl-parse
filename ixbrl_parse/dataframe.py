
import pandas as pd

def values_to_df(values):

    data = []

    for n, v in values.items():
        data.append([
            n.localname, v.to_value().get_value(), v.unit
        ])

    return pd.DataFrame(
        data,
        columns = ["name", "value", "unit"]
    )

def instance_to_df(inst):

    columns = ["name", "value", "unit", "entity", "scheme", "start", "end",
               "instant"]
    columnset = set(columns)

    data = []

    for c in inst.contexts.values():

        for v in c.values.values():

            row = {
                "name": v.name.localname,
                "value": str(v.to_value().get_value()),
                "unit": v.to_value().get_unit(),
            }

            if c.entity:
                row["entity"] = c.entity.id
                row["scheme"] = c.entity.scheme

            if c.period:
                row["start"] = c.period.start
                row["end"] = c.period.end

            if c.instant:
                row["instant"] = c.instant.instant

            for dim in c.dimensions:

                d = dim.dimension.localname
                v = dim.value.localname

                if d not in columnset:
                    columns.append(d)
                    columnset.add(d)

                row[d] = v

            data.append(row)

    return pd.DataFrame(data, columns=columns)

    

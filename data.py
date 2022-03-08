def spore_id_from_clickdata(clickData):
    try:
        return clickData["points"][0]["customdata"][0]
    except TypeError:
        return None

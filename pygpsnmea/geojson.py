"""
Module to output GeoJSON
"""


import json


class GeoJsonParser():
    """
    Simple parser to generate a dictionary that can be used with json.dump(s)

    Attributes:
        main(dict): main dictionary to store all the points and linestrings
    """

    def __init__(self):
        self.main = {"type": "FeatureCollection", "features": []}

    @staticmethod
    def create_feature_point(lon, lat, properties):
        """
        create a single point on the map

        Args:
            lat(float): latitude
            lon(float): longitude
            properties(dict): dictionary of info about this point

        Returns:
            fpoint(dict): dictionary for a GeoJSON point
        """
        fpoint = {"type": "Feature", "geometry": {"type": "Point",
                                                  "coordinates": [lon, lat]},
                  "properties": properties}
        return fpoint

    @staticmethod
    def create_feature_linestring(coords, properties):
        """
        create a line made up of multiple co-ordinates

        Args:
            coords(list): list of lists each containing 2 elements latitude
                          and longitude
            properties(dict): dictionary of info about this linestring

        Returns:
            flinestring(dict): dictionary for a GeoJSON line string
        """
        flinestring = {"type": "Feature", "geometry": {"type": "LineString",
                                                       "coordinates": coords},
                       "properties": properties}
        return flinestring

    def add_map_point(self, properties, lastlon, lastlat):
        """
        add a point to the GEOJSON

        Args:
            properties(dict): dictionary of info relating to the this point
            lastlon(float): the longitude
            lastlat(float): the latitude
        """
        shippoint = self.create_feature_point(lastlon, lastlat, properties)
        self.main["features"].append(shippoint)

    def add_map_linestring(self, coords, properties):
        """
        add a linestring to the GEOJSON

       Args:
            coords(list): list of lists each containing 2 elements latitude
                          and longitude
            properties(dict): dictionary of info about this linestring
        """
        linestr = self.create_feature_linestring(coords, properties)
        self.main["features"].append(linestr)

    def save_to_file(self, outputfilepath):
        """
        save the GeoJSON to a file

        Args:
            outputfilepath(str or path like object): where to save to
        """
        with open(outputfilepath, 'w') as geojsonfile:
            json.dump(self.main, geojsonfile)

    def get_json_string(self):
        """
        get the self.main JSON as a string

        Returns:
            geojson(str): the JSON representation of self.main as a string
        """
        geojson = json.dumps(self.main)
        return geojson

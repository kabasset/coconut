from astropy import units as u
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

from coconut import _version
from coconut.ctree import CTree
from coconut.gmapping import GMapping

_geocoder = Nominatim(user_agent=_version.__title__)

defaults = {
    "means_ranges": {
        "feet": 2 * u.km,
        "bike": 10 * u.km,
        "car": 200 * u.km,
        "train": 500 * u.km,
        "plane": None,
    },
    "means_intensities": {
        "feet": 0,
        "bike": 0,
        "car": 100,
        "train": 1,
        "plane": 1000,
    },
}


def name_to_lonlat(name):
    loc = _geocoder.geocode(name)
    return loc.longitude, loc.latitude  # type: ignore


def endpoints_to_distance(departure, arrival):
    return geodesic(name_to_lonlat(departure), name_to_lonlat(arrival)).km * u.km


def distance_to_means(distance, means_ranges):
    means_ranges = [means_ranges.items()]
    sorted(means_ranges, key=lambda mr: mr[1])
    for m, r in means_ranges:
        if r is not None and distance < r:
            return m
    return None


def eval_travel_footprint(
    travels: GMapping,
    means_intensities: dict = defaults["means_intensities"],
    means_ranges: dict = defaults["means_ranges"],
):

    # Endpoints to distance
    travels.bind(
        "distance",
        lambda: [endpoints_to_distance(t["departure"], t["arrival"]) for t in travels],
    )

    # Transportation means from distance
    travels.bind(
        "transportation_means",
        lambda: [
            distance_to_means(t["distance"], means_ranges) or travels.na
            for t in travels
        ],
    )

    # Transportation intensity from transportation means
    travels.bind(
        "transportation_intensity",
        lambda: [means_intensities[m] for m in travels["transportation_means"]],
    )

    # Travel footprint from distance and transportation intensity
    travels["travel_footprint"] = (
        travels["transportation_intensity"] * travels["distance"]
    )

    return CTree({"travel_footprint": sum(travels["travel_footprint"])})

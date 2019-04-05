import pydicom

"""\
Defines AddressAnonymizer, responsible for anonymizing addresses
"""


class AddressAnonymizer:
    """\
    Anonymizes addresses.
    """

    def __init__(self, randomizer):
        """\
        Create a new AddressAnonymizer.

        Parameters
        ----------
        randomizer : dicognito.randomizer.Randomizer
            Provides a source of randomness.
        """
        self.randomizer = randomizer

        address_tag = pydicom.datadict.tag_for_keyword("PatientAddress")
        region_tag = pydicom.datadict.tag_for_keyword("RegionOfResidence")
        country_tag = pydicom.datadict.tag_for_keyword("CountryOfResidence")

        self._value_factories = {
            address_tag: self.get_street_address,
            region_tag: self.get_region,
            country_tag: self.get_country,
        }

    def __call__(self, dataset, data_element):
        """\
        Potentially anonymize a single DataElement, replacing its
        value with something that obscures the patient's identity.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if it has a value
            and if its keyword is one of PatientAddress, RegionOfResidence,
            or CountryOfResidences.

        Returns
        -------
        True if the element was anonymized, or False if not.
        """
        value_factory = self._value_factories.get(data_element.tag, None)
        if not value_factory:
            return False
        if not data_element.value:
            return True

        data_element.value = value_factory(data_element.value)
        return True

    def get_street_address(self, original_value):
        (street_number_index, street_index) = self.randomizer.get_ints_from_ranges(
            original_value, 1000, len(self._streets)
        )
        street_number = street_number_index + 1
        return str(street_number) + " " + self._streets[street_index]

    def get_region(self, original_value):
        (city_index,) = self.randomizer.get_ints_from_ranges(original_value, len(self._cities))
        return self._cities[city_index]

    def get_country(self, original_value):
        (country_index,) = self.randomizer.get_ints_from_ranges(original_value, len(self._countries))
        return self._countries[country_index]

    # from https://www.randomlists.com/random-street-names?qty=100&dup=false, mostly
    _streets = [
        "JACKSON STREET",
        "ROUTE 41",
        "HILLCREST AVENUE",
        "5TH STREET",
        "RIDGE AVENUE",
        "CREEKSIDE DRIVE",
        "ORCHARD LANE",
        "MECHANIC STREET",
        "3RD STREET NORTH",
        "CANTERBURY COURT",
        "ASHLEY COURT",
        "CYPRESS COURT",
        "SCHOOL STREET",
        "FRANKLIN STREET",
        "RIVER STREET",
        "COBBLESTONE COURT",
        "DELAWARE AVENUE",
        "5TH STREET WEST",
        "4TH STREET NORTH",
        "WILLOW LANE",
        "MYRTLE STREET",
        "CHESTNUT STREET",
        "COURT STREET",
        "FAIRVIEW ROAD",
        "WINDING WAY",
        "IVY LANE",
        "8TH STREET",
        "HARRISON AVENUE",
        "AMHERST STREET",
        "HUDSON STREET",
        "FRONT STREET SOUTH",
        "RAILROAD STREET",
        "HAWTHORNE AVENUE",
        "GRANT STREET",
        "TANGLEWOOD DRIVE",
        "DOGWOOD DRIVE",
        "EDGEWOOD DRIVE",
        "FAWN COURT",
        "2ND STREET EAST",
        "SUMMIT STREET",
        "LAUREL DRIVE",
        "ANN STREET",
        "ELMWOOD AVENUE",
        "CROSS STREET",
        "WINDSOR COURT",
        "RIVER ROAD",
        "VIRGINIA AVENUE",
        "FOREST AVENUE",
        "HEATHER LANE",
        "1ST STREET",
        "2ND STREET NORTH",
        "MYRTLE AVENUE",
        "WOODLAND ROAD",
        "8TH AVENUE",
        "BROOKSIDE DRIVE",
        "SMITH STREET",
        "MAPLE LANE",
        "STATE STREET",
        "HAWTHORNE LANE",
        "QUEEN STREET",
        "OVERLOOK CIRCLE",
        "4TH AVENUE",
        "JEFFERSON STREET",
        "HILLTOP ROAD",
        "INVERNESS DRIVE",
        "MAGNOLIA COURT",
        "DOGWOOD LANE",
        "HENRY STREET",
        "SPRING STREET",
        "FRANKLIN COURT",
        "LOCUST STREET",
        "YORK STREET",
        "RIVERSIDE DRIVE",
        "CEMETERY ROAD",
        "MAIN STREET",
        "HIGHLAND DRIVE",
        "PINE STREET",
        "LOIS LANE",
        "CANTERBURY DRIVE",
        "MAIN STREET EAST",
        "HARRISON STREET",
        "CLINTON STREET",
        "MADISON AVENUE",
        "2ND STREET WEST",
        "SUMMIT AVENUE",
        "WOODLAND AVENUE",
        "CAMBRIDGE COURT",
        "SHADY LANE",
        "GEORGE STREET",
        "LAUREL STREET",
        "BRIARWOOD COURT",
        "IVY COURT",
        "LAFAYETTE AVENUE",
        "YORK ROAD",
        "VALLEY VIEW ROAD",
        "CREEK ROAD",
        "SYCAMORE LANE",
        "PEARL STREET",
        "11TH STREET",
        "ROUTE 1",
    ]

    # from https://www.randomlists.com/random-world-cities?qty=50&dup=false
    _cities = [
        "MADRID",
        "BENGALURU",
        "AHMEDABAD",
        "LOS ANGELES",
        "BAKU",
        "ALGIERS",
        "SHIRAZ",
        "DONGGUAN",
        "QUITO",
        "TORONTO",
        "WUHAN",
        "HONG KONG",
        "MELBOURNE",
        "MAPUTO",
        "XI'AN",
        "RECIFE",
        "SANTA CRUZ DE LA SIERRA",
        "SHANGHAI",
        "MONTERREY",
        "HAVANA",
        "TAIPEI",
        "ABIDJAN",
        "KARACHI",
        "TASHKENT",
        "MUMBAI",
        "SHIJIAZHUANG",
        "JAKARTA",
        "NANJING",
        "HYDERABAD",
        "XIAMEN",
        "FAISALABAD",
        "QUANZHOU",
        "BOGOTA",
        "KUALA LUMPUR",
        "FOSHAN",
        "BAGHDAD",
        "ROSTOV-ON-DON",
        "KAOHSIUNG",
        "PHOENIX",
        "SYDNEY",
        "PESHAWAR",
        "ADDIS ABABA",
        "RIO DE JANEIRO",
        "BARCELONA",
        "SAPPORO",
        "MONTEVIDEO",
        "ASTANA",
        "AHVAZ",
        "TEHRAN",
        "HEFEI",
    ]

    # from https://www.randomlists.com/random-country?qty=40&dup=false
    _countries = [
        "UKRAINE",
        "DJIBOUTI",
        "COLOMBIA",
        "ALGERIA",
        "ERITREA",
        "BELIZE",
        "UNITED STATES OF AMERICA",
        "POLAND",
        "TOKELAU",
        "JORDAN",
        "RUSSIAN FEDERATION",
        "BRITISH INDIAN OCEAN TERRITORY",
        "SURINAME",
        "NORTHERN MARIANA ISLANDS",
        "FRENCH SOUTHERN TERRITORIES",
        "JERSEY",
        "ANGUILLA",
        "UZBEKISTAN",
        "CHINA",
        "ISRAEL",
        "MALI",
        "SAINT VINCENT AND THE GRENADINES",
        "SYRIAN ARAB REPUBLIC",
        "IRAQ",
        "SOMALIA",
        "ESTONIA",
        "KIRIBATI",
        "NORFOLK ISLAND",
        "COSTA RICA",
        "KYRGYZSTAN",
        "LAO PEOPLE'S DEMOCRATIC REPUBLIC",
        "ISLE OF MAN",
        "BOTSWANA",
        "CANADA",
        "FALKLAND ISLANDS (MALVINAS)",
        "WALLIS AND FUTUNA",
        "AFGHANISTAN",
        "CHAD",
        "SRI LANKA",
        "LATVIA",
    ]

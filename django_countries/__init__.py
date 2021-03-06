from itertools import islice
from operator import itemgetter

from django_countries.conf import settings
try:
    from django.utils.encoding import force_text
except ImportError:  # Django 1.4
    from django.utils.encoding import force_unicode as force_text


class Countries(object):
    """
    An object containing a list of ISO3166-1 countries.

    Iterating this object will return the countries as tuples (of the country
    code and name), sorted by name.
    """

    @property
    def countries(self):
        """
        Return the countries list, modified by any overriding settings.
        The result is cached so future lookups are less work intensive.
        """
        # Local import so that countries aren't loaded into memory until first
        # used.
        from django_countries.data import COUNTRIES

        if not hasattr(self, '_countries'):
            if settings.COUNTRIES_ONLY:
                self._countries = list(settings.COUNTRIES_ONLY.items())
            else:
                self._countries = []
                overrides = settings.COUNTRIES_OVERRIDE
                for code, name in COUNTRIES.items():
                    if code in overrides:
                        name = overrides[code]
                    if name is not None:
                        self._countries.append((code, name))
                for key in set(overrides) - set(COUNTRIES):
                    self._countries.append((key, overrides[key]))

        return self._countries

    @countries.deleter
    def countries(self):
        """
        Reset the countries cache in case for some crazy reason the settings
        change. But surely no one is crazy enough to do that, right?
        """
        if hasattr(self, '_countries'):
            del self._countries

    def __iter__(self):
        """
        Return an iterator of countries, sorted by name.

        Each country record consists of a tuple of the two letter ISO3166-1
        country code and short name.

        The sorting happens based on the thread's current translation.
        """
        countries = [(code, force_text(name)) for code, name in self.countries]
        return iter(sorted(countries, key=itemgetter(1)))

    def name(self, code):
        """
        Return the name of a country, based on the code.

        If no match is found, returns an empty string.
        """
        return dict(self.countries).get(code, '')

    def __len__(self):
        """
        len() used by several third party applications to calculate the length
        of choices this will solve bug related to generating fixtures.
        """
        return len(self.countries)

    def __contains__(self, code):
        """
        Check to see if the countries contains the given code.
        """
        for part in self.countries:
            if code == part[0]:
                return True
        return False

    def __getitem__(self, index):
        """
        Some applications expect to be able to access members of the field
        choices by index.
        """
        try:
            return next(islice(self.__iter__(), index, index+1))
        except TypeError:
            return list(islice(self.__iter__(), index.start, index.stop,
                               index.step))

countries = Countries()

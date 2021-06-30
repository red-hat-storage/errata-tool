from __future__ import print_function
import sys
import warnings
from datetime import date
import errata_tool
from errata_tool import ErrataConnector
from errata_tool.product import Product
from errata_tool.product_version import ProductVersion
from errata_tool.user import User


class NoReleaseFoundError(Exception):
    pass


class MultipleReleasesFoundError(Exception):
    pass


class ReleaseCreationError(Exception):
    pass


class Release(ErrataConnector):
    def _setattr(self):
        self.attributes = self.data['attributes']
        self.relationships = self.data['relationships']
        self.id = self.data['id']
        self.program_manager = \
            self.relationships['program_manager']['login_name'] if \
            self.relationships.get('program_manager') else None
        self.product = self.relationships['product']['short_name'] if \
            self.relationships.get('product') else None
        self.type = self.attributes['type']
        self.url = self._url + '/release/show/%d' % self.id
        # For displaying in scripts/logs:
        self.edit_url = self._url + '/release/edit/%d' % self.id

    def __init__(self, name=None, id=None, data=None):
        if not name and not id:
            raise ValueError('missing release "id" or "name" kwarg')
        self.id = id
        self.name = name
        # For backwards compatibility, we support querying releases
        # with encoded "+" characters. We'll remove this in a future
        # python-errata-tool release.
        if name and '%2B' in name:
            msg = 'use "+" in Release name %s instead of url-encoded "%%2B"'
            with warnings.catch_warnings():
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(msg % self.name, DeprecationWarning)
            self.name = _unquote_plus(name)
        self.data = data

        if self.data:
            self._setattr()
        else:
            self.refresh()

    def refresh(self):
        url = self._url + '/api/v1/releases'
        if self.id is not None:
            params = {'filter[id]': self.id}
        elif self.name is not None:
            params = {'filter[name]': self.name}
        result = self._get(url, params=params)
        if len(result['data']) < 1:
            raise NoReleaseFoundError()
        if len(result['data']) > 1:
            # it's possible to accidentally have identically named releases,
            # see engineering RT 461783
            raise MultipleReleasesFoundError()
        self.data = result['data'][0]
        self._setattr()

    def __getattr__(self, name):
        if self.data is None:
            self.refresh()

        if name in self.data:
            result = self.data[name]
        elif name in self.attributes:
            result = self.attributes[name]
        else:
            result = self.relationships[name]
        return result

    def render(self):
        return {
            'product': str(self.product),
            'supports_component_acl': self.supports_component_acl,
            'program_manager': str(self.program_manager) if
            self.program_manager else None,
            'enabled': self.enabled,
            'active': self.is_active,
            'type': str(self.type),
            'allow_pkg_dupes': self.allow_pkg_dupes,
            'internal_target_release': str(self.internal_target_release) if
            self.internal_target_release else None,
            'zstream_target_release': str(self.zstream_target_release) if
            self.zstream_target_release else None,
            'name': str(self.name),
            'description': str(self.description),
            'product_versions': [
                str(product_version['name'])
                for product_version in self.product_versions
            ],
            'blocker_flags': [str(flag) for flag in self.blocker_flags],
            'ship_date': str(self.ship_date) if self.ship_date else None,
        }

    def advisories(self):
        """Find all advisories for this release.

        :returns: a list of dicts, one per advisory.
                  For example:
                  [{
                      "id": 32972,
                      "advisory_name": "RHSA-2018:0546",
                      "product": "Red Hat Ceph Storage",
                      "release": "rhceph-3.0",
                      "synopsis": "Important: ceph security update",
                      "release_date": None,
                      "qe_owner": "someone@redhat.com",
                      "qe_group": "RHC (Ceph) QE",
                      "status": "SHIPPED_LIVE",
                      "status_time": "March 15, 2018 18:29"
                  }]

        """
        url = '/release/%d/advisories.json' % self.id
        return self._get(url)

    @classmethod
    def create(klass, name, product, product_versions, type, program_manager,
               default_brew_tag, blocker_flags, ship_date=None):
        """Create a new release in the ET.

        See https://bugzilla.redhat.com/1401608 for background.

        Note this method enforces certain conventions:
        * Always disables PDC for a release
        * Always creates the releases as "enabled"
        * Always allows multiple advisories per package
        * Description is always the combination of the product's own
          description (for example "Red Hat Ceph Storage") with the number
          from the latter part of the release's name. So a new "rhceph-3.0"
          release will have a description "Red Hat Ceph Storage 3.0".

        :param name: short name for this release, eg "rhceph-3.0"
        :param product: short name, eg. "RHCEPH".
        :param product_versions: list of names, eg. ["RHEL-7-CEPH-3"]
        :param type: "Zstream" or "QuarterlyUpdate"
        :param program_manager: for example "anharris" (Drew Harris, Ceph PgM)
        :param default_brew_tag: for example "ceph-3.0-rhel-7-candidate"
        :param blocker_flags: for example, "ceph-3.0"
        :param ship_date: date formatted as strftime("%Y-%b-%d"). For example,
                          "2017-Nov-17". If ommitted, the ship_date will
                          be set to today's date. (This can always be updated
                          later to match the ship date value in Product
                          Pages.)
        """
        product = errata_tool.Product(product)

        (_, number) = name.split('-', 1)
        description = '%s %s' % (product.description, number)

        program_manager = User(program_manager)

        product_version_ids = set([])
        for pv_name in product_versions:
            pv = ProductVersion(pv_name)
            product_version_ids.add(pv.id)

        if ship_date is None:
            today = date.today()
            ship_date = today.strftime("%Y-%b-%d")

        et = ErrataConnector()
        url = et._url + '/release/create'
        payload = {
            'type': type,
            'release[allow_blocker]': 0,
            'release[allow_exception]': 0,
            'release[allow_pkg_dupes]': 1,
            'release[allow_shadow]': 0,
            'release[blocker_flags]': blocker_flags,
            'release[default_brew_tag]': default_brew_tag,
            'release[description]': description,
            'release[enable_batching]': 0,
            'release[enabled]': 1,
            'release[is_deferred]': 0,
            'release[name]': name,
            'release[product_id]': product.id,
            'release[product_version_ids][]': product_version_ids,
            'release[program_manager_id]': program_manager.id,
            'release[ship_date]': ship_date,
            'release[type]': type,
        }
        result = et._post(url, data=payload)
        if (sys.version_info > (3, 0)):
            body = result.text
        else:
            # Found during live testing:
            # UnicodeEncodeError: 'ascii' codec can't encode character u'\xe1'
            # in position 44306: ordinal not in range(128)
            # Not sure why there was a non-ascii character in the ET's HTTP
            # response, but this fixes it.
            body = result.text.encode('utf-8')
        if result.status_code != 200:
            # help with debugging:
            print(body)
        result.raise_for_status()
        # We can get a 200 HTTP status_code here even when the POST failed to
        # create the release in the ET database. (This happens, for example, if
        # there are no Approved Components defined in Bugzilla for the release
        # flag, and the ET hits Bugzilla's XMLRPC::FaultException.)
        if 'field_errors' in body:
            print(body)
            raise ReleaseCreationError('see field_errors <div>')
        return klass(name=name)


def _unquote_plus(string):
    """This method is similar to urllib.parse.unquote_plus(), but it *only*
    unquotes the "%2B" characters to "+".
    """
    return string.replace('%2B', '+')

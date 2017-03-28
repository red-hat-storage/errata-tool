import copy

from errata_tool import ErrataException, ErrataConnector, security  # NOQA

#
# Change this if you change the structure of the tables we assemble
# here.  This is added to export() and checked on import().
#
_product_table_version = 3


class ProductList(ErrataConnector):

    def __init__(self, **kwargs):
        self._releases = {}
        self._products = {}
        self._versions = {}
        self._product_ids = {}

        #
        # Because this is a lot of data to pull, allow
        # users to pass in save/restore functions so they
        # can cache it locally.
        #
        # This literally takes 3-5 minutes on a fast connection.
        #
        self.__save = None
        self.__load = None

        if 'save' in kwargs and callable(kwargs['save']):
            self.__save = kwargs['save']

        if 'load' in kwargs and callable(kwargs['load']):
            self.__load = kwargs['load']
            if self.restore(self.__load()):
                return

        if 'fetch' not in kwargs or kwargs['fetch'] is not False:
            # print 'Loading it the slow way'
            self.fetch_products()
            self.fetch_all_versions()
            self.fetch_releases()
            self.coallate_data()
            if self.__save is not None:
                self.__save(self.export())

    def __str__(self):
        return str(self._products)

    def save(self):
        if self.__save is not None:
            self.__save(self.export)

    def export(self):
        export_info = {}
        export_info['name'] = 'errata_tool_products'
        export_info['version'] = _product_table_version
        export_info['products'] = copy.deepcopy(self._products)
        export_info['product_ids'] = copy.deepcopy(self._product_ids)
        export_info['releases'] = copy.deepcopy(self._releases)
        export_info['versions'] = copy.deepcopy(self._versions)

        return export_info

    def restore(self, import_info):
        if import_info is None:
            return False
        if type(import_info) is not dict:
            raise ValueError('import_info is not a dict')
        if 'name' not in import_info or 'version' not in import_info or \
                'products' not in import_info or 'releases' not in import_info:
            raise ValueError('Malformed import_info')

        if import_info['version'] != _product_table_version:
            return False

        # Don't use references to existing tables
        self._products = copy.deepcopy(import_info['products'])
        self._product_ids = copy.deepcopy(import_info['product_ids'])
        self._releases = copy.deepcopy(import_info['releases'])

        return True

    #
    # Fetch product information
    #
    def fetch_releases(self):
        page = 1
        releases = {}
        while True:
            ret = self._get('/api/v1/releases?page[number]=' + str(page))
            if ret is None:
                break
            if 'data' not in ret:
                raise ErrataException('Malformed response from server')
            if len(ret['data']) == 0:
                break

            for r in ret['data']:
                attrs = r['attributes']
                if r['type'] != 'releases' or not attrs['enabled']:
                    continue

                # Ignore this specific release.
                if r['id'] == 21:
                    continue

                info = {}
                ident = int(r['id'])
                info['id'] = ident
                info['product'] = None
                info['name'] = attrs['name']
                info['description'] = attrs['description']
                info['async'] = attrs['is_async']
                info['bz_flags'] = []

                if 'blocker_flags' in attrs:
                    for f in attrs['blocker_flags']:
                        if '_ack' in f:
                            continue
                        if f in info['bz_flags']:
                            continue
                        info['bz_flags'].append(f)

                info['brew_tags'] = {}
                for t in r['relationships']['brew_tags']:
                    info['brew_tags'][int(t['id'])] = t['name']

                info['versions'] = {}
                for t in r['relationships']['product_versions']:
                    info['versions'][int(t['id'])] = t['name']

                releases[ident] = info
            page = page + 1
        self._releases = releases

    def fetch_products(self):
        ret = self._get('/products.json')

        self._products = {}

        for p in ret:
            try:
                product = p['product']
            except KeyError:
                continue
            if int(product['isactive']) == 0:
                continue
            info = {}
            ident = int(product['id'])
            info['id'] = ident
            info['name'] = str(product['name'])
            info['short_name'] = str(product['short_name'])
            if str(product['short_name']) in self._products:
                raise ValueError('Duplicate product:' +
                                 str(product['short_name']))
            info['versions'] = {}
            info['releases'] = {}
            self._products[ident] = info
            self._product_ids[str(product['short_name'])] = ident

    def fetch_versions(self, prod):
        if type(prod) is str:
            prod = self._product_ids[prod]

        versions = {}
        ret = self._get('/products/' + str(prod) + '/product_versions.json')
        for v in ret:
            version = v['product_version']
            if int(version['enabled']) == 0:
                continue

            info = {}
            ident = int(version['id'])
            if ident in self._versions:
                if version['name'] != self._versions[ident]:
                    raise Exception('Duplicate version ID: ' + str(ident))
                # Duplicate version - probably already fetched versions
                # for this product - don't update.
                return

            info['name'] = version['name']
            info['brew_tag'] = version['default_brew_tag']
            info['description'] = version['description']
            info['id'] = ident
            info['releases'] = {}
            info['product'] = prod

            # Store global version
            self._versions[ident] = info

            # Store product version information
            versions[ident] = version['name']
        self._products[prod]['versions'] = versions

    def fetch_all_versions(self):
        for p in self._products:
            n = self._products[p]['short_name']
            self.fetch_versions(n)

    def coallate_data(self):
        #
        # Link up products and releases
        #
        for v in self._versions:
            ver = self._versions[v]
            ver['releases'] = {}
            for r in self._releases:
                rel = self._releases[r]
                for rv in rel['versions']:
                    if v == rv:
                        # Append release ID on product...
                        rel['product'] = ver['product']
                        prod = self._products[ver['product']]
                        ver['releases'][r] = rel['name']
                        prod['releases'][r] = rel['name']

    def _prune_releases(self, releases, **kwargs):
        if releases is None or len(releases) is 0:
            return None
        if 'async' not in kwargs or kwargs['async'] is True:
            return releases
        ret = []
        for r in releases:
            if self._releases[r]['async'] is True:
                continue
            ret.append(r)
        return ret

    def get_release_ids_by_version(self, product, version):
        prod = self.__getitem__(product)
        if type(version) is int:
            ret = [rel_id for rel_id in prod['versions'][version]['releases']]
        elif type(version) is not str:
            raise ValueError('Product must be an ID or string')
        else:
            for v in prod['versions']:
                if prod['versions'][v]['name'] == version:
                    ret = prod['versions'][v]['releases']
                    break
        return ret

    def get_release_ids_by_flag(self, product, flag):
        prod = self.__getitem__(product)
        if type(flag) is not str:
            raise ValueError('Flag must be a string')
        ret = []
        for r in prod['releases']:
            rel = self._releases[r]
            for f in rel['bz_flags']:
                if flag == f:
                    ret.append(r)
        return ret

    def get_release_ids_by_name(self, product, name):
        prod = self.__getitem__(product)
        if type(name) is not str:
            raise ValueError('Name must be a string')
        ret = []
        for r in prod['releases']:
            rel = self._releases[r]
            if rel['name'] == name:
                ret.append(r)
        return ret

    def get_release_ids_by_tag(self, product, tag):
        prod = self.__getitem__(product)
        if type(tag) is not str and type(tag) is not int:
            raise ValueError('Tag must be a string or int')
        ret = []
        for r in prod['releases']:
            rel = self._releases[r]
            for t in rel['brew_tags']:
                if type(tag) is int and t == tag:
                    ret.append(r)
                elif type(tag) is str and rel['brew_tags'][t] == tag:
                    ret.append(r)
        return ret

    def get_version_info(self, version):
        if type(version) is int:
            return self._versions[version]
        elif type(version) is str:
            for v in self._versions:
                if self._versions[v]['name'] == version:
                    return self._versions[v]
            raise KeyError('Version not found')
        raise ValueError('Version must be an int or string')

    #
    # Return array of releases by ID
    #
    def get_release_ids(self, product, **kwargs):
        ret = None

        if 'version' in kwargs:
            ret = self.get_release_ids_by_version(product, kwargs['version'])
        elif 'flag' in kwargs:
            ret = self.get_release_ids_by_flag(product, kwargs['flag'])
        elif 'name' in kwargs:
            ret = self.get_release_ids_by_name(product, kwargs['name'])
        elif 'tag' in kwargs:
            ret = self.get_release_ids_by_tag(product, kwargs['tag'])
        else:
            prod = self.__getitem__(product)
            ret = [rel_id for rel_id in prod['releases']]
        return self._prune_releases(ret, **kwargs)

    #
    # Return detailed release information
    #
    def get_release_info(self, release):
        if type(release) is int:
            return self._releases[release]
        elif type(release) is str:
            for r in self._releases:
                if self._releases[r]['name'] == release:
                    return self._releases[r]
            # XXX if two releases with same name?
            return None
        else:
            raise ValueError('Release must be an int or string')

    def __getitem__(self, prod):
        if type(prod) is int:
            if prod not in self._products:
                raise ValueError('No such product: ' + str(prod))
            return self._products[prod]

        if type(prod) is str and prod in self._product_ids:
            return self._products[self._product_ids[prod]]

        raise ValueError('No such product: ' + str(prod))

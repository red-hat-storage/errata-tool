from errata_tool import ErrataConnector
from errata_tool import Erratum


class BatchSearch(ErrataConnector):

    def list(self):
        self._data = self._get('/api/v1/batches')

        return self._parse_data(self._data)

    def search(self, batch_id_or_name):
        """Fetch batch data from Errata Tool API and create batch objects"""

        args = {}
        if batch_id_or_name is None or batch_id_or_name == '':
            return None
        else:
            try:
                args['id'] = int(batch_id_or_name)
            except ValueError:
                args['name'] = batch_id_or_name

            self._data = self.get_filter('/api/v1/batches', 'filter', **args)

        ret_data = self._parse_data(self._data)
        if len(ret_data) == 1:
            return ret_data[0]

        return ret_data

    def _parse_data(self, data_blob):

        ret_data = []

        if data_blob and 'data' in data_blob:

            batch_list = data_blob['data']

            for entry in batch_list:
                batch_id = entry['id']
                ret_data.append(Batch(batch_id, entry))
        return ret_data


class Batch(ErrataConnector):
    """Encapsulate ET Details for a specific batch"""

    def __init__(self, batch_name_or_id, entry=None):
        """Find batch details by batch name or batch_id

        :param batch_name_or_id: batch name or batch_id from ET
        """
        self._fetch(batch_name_or_id, entry=entry)

    def _fetch(self, batch_name_or_id, entry=None):
        """Fetch batch data from Errata Tool API and store to properties"""

        args = {}
        if entry is None and batch_name_or_id is not None:
            try:
                args['id'] = int(batch_name_or_id)
            except ValueError:
                args['name'] = batch_name_or_id

            data = self.get_filter('/api/v1/batches', 'filter', **args)
            entry = data['data'][0]

        self._batch = {}
        self._data = entry

        if self._data:
            self._batch_id = entry['id']
            self._batch_name = entry['attributes']['name']
            self._batch_description = entry['attributes']['description']
            self._release_date = entry['attributes']['release_date']
            self._release_name = entry['relationships']['release']['name']
            errata_list = entry['relationships']['errata']
            self._errata_ids = [e['id'] for e in errata_list]

    @property
    def batch_id(self):
        """batch id for this batch"""
        return self._batch_id

    @property
    def batch_name(self):
        """batch name for this batch"""
        return self._batch_name

    @property
    def batch_description(self):
        """batch description for this batch"""
        return self._batch_description

    @property
    def data(self):
        return self._data

    @property
    def errata_ids(self):
        """List of all Errata IDs for this batch

        :return: list of Errata ids
        """
        return self._errata_ids

    @property
    def errata(self):
        """List of all Erratas for a given batch_id

        :return: list of Errata objects
        """
        if self._all_errata is None:
            self._all_errata = {}

        for errata_id in self._errata_ids:
            errata = Erratum(errata_id=errata_id)
            self._all_errata.append(errata)

        return self._all_errata

    def __getattr__(self, name):
        return self._data.get(name)

    def __repr__(self):

        return 'batch(%s)' % self._batch_id

    def __str__(self):
        """Convert batch object to string representation

        :return: batch info string
        """
        output = "Batch: {0} [{1}]\n".format(self.batch_name, self.batch_id)
        output += "Description: {0}\n".format(self.batch_description)
        output += "Release Date: {0}\n".format(self.release_date)
        output += "ET Release: {0}\n".format(self.release)
        output += "Errata IDs: {0}\n".format(str(self.errata_ids))

        return output

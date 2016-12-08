from errata_tool import ErrataException
import requests
from requests_kerberos import HTTPKerberosAuth
from jsonpath_rw import parse


class ErrataConnector:
    _url = "https://errata.devel.redhat.com"
    _auth = HTTPKerberosAuth()
    ssl_verify = True  # Shared

    # Simple wrappers to avoid copying around when auth changes.
    def _post(self, url, **kwargs):
        if kwargs is not None:
            if 'data' in kwargs:
                return requests.post(url,
                                     auth=self._auth,
                                     data=kwargs['data'],
                                     verify=self.ssl_verify)
            elif 'json' in kwargs:
                return requests.post(url,
                                     auth=self._auth,
                                     json=kwargs['json'],
                                     verify=self.ssl_verify)
        return requests.post(url, auth=self._auth, verify=self.ssl_verify)

    def _get(self, url, **kwargs):
        ret_data = None
        ret_json = None
        if kwargs is not None:
            if 'data' in kwargs:
                ret_data = requests.get(url,
                                        auth=self._auth,
                                        data=kwargs['data'],
                                        verify=self.ssl_verify)
            elif 'json' in kwargs:
                ret_data = requests.get(url,
                                        auth=self._auth,
                                        json=kwargs['json'],
                                        verify=self.ssl_verify)

        if ret_data is None:
            ret_data = requests.get(url, auth=self._auth,
                                    verify=self.ssl_verify)

        if ret_json is None and ret_data is not None:
            if ret_data.status_code == 200:
                ret_json = ret_data.json()
            elif ret_data.status_code in [401]:
                raise ErrataException(
                    'Pigeon crap. Did it forget to run kinit?')
            elif ret_data.status_code in [403]:
                raise ErrataException(
                    'You need Errata access for this operation!')
            elif ret_data.status_code in [500]:
                raise LookupError('No matching errata')

            else:
                print "Result not handled:", ret_data
                print "While fetching:", url
                raise ErrataException(str(ret_data))

        return ret_json

    def _put(self, url, **kwargs):
        if kwargs is not None:
            if 'data' in kwargs:
                return requests.put(url,
                                    auth=self._auth,
                                    data=kwargs['data'],
                                    verify=self.ssl_verify)
            elif 'json' in kwargs:
                return requests.put(url,
                                    auth=self._auth,
                                    json=kwargs['json'],
                                    verify=self.ssl_verify)
        return requests.put(url, auth=self._auth, verify=self.ssl_verify)

    def _processResponse(self, r):
        if r.status_code in [200, 201, 202, 203, 204]:
            return  # all good

        # If subclassed as an Erratum and we have an ID, add it
        # to the error message
        err_msg = ''
        try:
            if type(self.errata_id) is int and self.errata_id > 0:
                err_msg += 'Erratum ' + str(self.errata_id) + ': '
        except AttributeError:
            pass

        # Generate a really big message if e.g. bug is in a different
        # erratum
        if r.status_code in [400, 422]:
            rj = r.json()
            if rj is None:
                raise Exception(err_msg + 'No Json returned')
            if 'error' in rj:
                # err_msg += '; '.join(rj['error'])
                err_msg += str(rj['error'])
            else:
                # TODO: drop jsonpath
                pe = parse('errors[*]')
                for match in pe.find(rj):
                    # This grabs the index since the json returns a dict
                    for k in match.value:
                        err_msg += k + ": "
                        petmp = parse('errors.' + k + '[*]')
                        for m in petmp.find(rj):
                            if type(m.value) is str or \
                               type(m.value) is unicode:
                                err_msg += m.value + "\n"
                            elif type(m.value) is int:
                                err_msg += str(m.value) + "\n"
                            else:
                                for n in m.value:
                                    err_msg += str(n) + "\n"
            raise ErrataException(err_msg)

        if r.status_code in [401]:
            # lhh - this is not a typo, and the syntax is correct, I assure you.
            raise ErrataException('Pigeon crap. Did it forget to run kinit?')

        if r.status_code in [500]:
            err_msg += "Broke errata tool!"
            print r.json()
            raise ErrataException(err_msg)

        if r.status_code in [404]:
            err_msg += 'Bug in your code - wrong method for this api? '
            err_msg += 'Wrong location?'
            print r.json()
            raise ErrataException(err_msg)

        raise ErrataException(err_msg + "Unhandled HTTP status code: " +
                              str(r.status_code))

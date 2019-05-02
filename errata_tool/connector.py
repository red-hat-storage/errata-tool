from __future__ import print_function
from errata_tool import ErrataException
import requests
from requests_kerberos import HTTPKerberosAuth, DISABLED
from jsonpath_rw import parse
import re
import time
import six
import kerberos


class ErrataConnector(object):
    # Staging is https://errata.stage.engineering.redhat.com
    _url = "https://errata.devel.redhat.com"
    _auth = HTTPKerberosAuth(mutual_authentication=DISABLED)
    _username = None
    ssl_verify = True  # Shared
    debug = False

    # Timings are only recorded if debug is set to True
    timings = {'GET': {}, 'POST': {}, 'PUT': {}}

    def _set_username(self, **kwargs):
        if self._username is not None:
            return
        try:
            (ret, ctx) = kerberos.authGSSClientInit('krbtgt@REDHAT.COM')
            assert (ret == kerberos.AUTH_GSS_COMPLETE)
            ret = kerberos.authGSSClientInquireCred(ctx)
            assert (ret == kerberos.AUTH_GSS_COMPLETE)
            # XXX What if you have >1 ticket?
            ret = kerberos.authGSSClientUserName(ctx)
            if '@' in ret:
                self._username = ret.split('@')[0]
            else:
                self._username = ret
        except AssertionError:
            raise ErrataException('Pigeon crap. Did it forget to run kinit?')

    # Shortcut
    def canonical_url(self, u):
        if u[:8] != 'https://' and u[:1] == '/':
            return self._url + u
        return u

    # Simple wrappers to avoid copying around when auth changes.
    def _record(self, call, url, t):
        #
        # Debugging needs to be turned on prior to calling any APIs
        # if you want to time errata calls. e.g.:
        #    erratum.ErrataConnector.debug = True
        #
        if not self.debug:
            return

        url = str(url)
        info = None

        # Unlikely, but possible
        if url in self.timings[call]:
            info = self.timings[call][url]
        else:
            #
            # Errata API calls are differentiated by a bugzilla #,
            # a build, or an erratum.  Normalize calls to match
            # URLs except for those specific differences.
            #
            api = url[8:]
            same = set(re.split(r'[/]|(\.json)', api))
            same = same - set(['', None])
            newurl = None
            for u in self.timings[call]:
                rapi = set(re.split(r'[/]|(\.json)', u[8:]))
                rapi = rapi - set(['', None])
                if len(rapi) != len(same):
                    continue
                delta = same ^ rapi
                if len(delta) != 2:
                    continue

                # Oops, the exception that proves the rule
                # about API locations above
                if delta == set(['tps_jobs', 'builds']):
                    continue
                info = self.timings[call][u]
                if '***' not in delta:
                    for i in delta:
                        if i in rapi:
                            url = u
                            newurl = u.replace(str(i), '***')
                            break
                else:
                    url = u
                    break
                if newurl is not None:
                    break
            if newurl is not None:
                del self.timings[call][url]
                self.timings[call][newurl] = info
                url = newurl

        if info is None:
            info = {'max': t, 'count': 0, 'min': t, 'mean': t, 'total': 0}

        info['count'] = info['count'] + 1

        if t < info['min']:
            info['min'] = t
        if t > info['max']:
            info['max'] = t

        info['total'] = info['total'] + t
        info['mean'] = info['total'] / info['count']

        self.timings[call][url] = info

    def _post(self, u, **kwargs):
        self._set_username()
        url = self.canonical_url(u)
        start = time.time()
        ret = None
        if kwargs is not None:
            if 'data' in kwargs:
                ret = requests.post(url,
                                    auth=self._auth,
                                    data=kwargs['data'],
                                    verify=self.ssl_verify)
            elif 'json' in kwargs:
                ret = requests.post(url,
                                    auth=self._auth,
                                    json=kwargs['json'],
                                    verify=self.ssl_verify)
        if ret is None:
            ret = requests.post(url, auth=self._auth, verify=self.ssl_verify)

        self._record('POST', url, time.time() - start)
        return ret

    def _get(self, u, **kwargs):
        """_get is convience method that retrives content from server

        Recognized kwargs
            'data' for requests data object to send with get call
            'json' for requests json object to send with get call
            'raw' bool (defaulting to False) for returning response object

        by default the return value is the response.json() object from Requests
        """
        self._set_username()
        url = self.canonical_url(u)
        ret_data = None
        ret_json = None
        start = time.time()
        return_json_decoded_data = True

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
            if 'raw' in kwargs:
                return_json_decoded_data = not kwargs['raw']

        if ret_data is None:
            ret_data = requests.get(url, auth=self._auth,
                                    verify=self.ssl_verify)

        self._record('GET', url, time.time() - start)

        if ret_json is None and ret_data is not None:
            if ret_data.status_code == 200:
                if return_json_decoded_data:
                    ret_json = ret_data.json()
                else:
                    return ret_data

            elif ret_data.status_code in [401]:
                raise ErrataException(
                    'Pigeon crap. Did it forget to run kinit?')
            elif ret_data.status_code in [403]:
                raise ErrataException(
                    'You need Errata access for this operation!')
            else:
                print("Result not handled: " + str(ret_data.text))
                print("While fetching: " + url)
                raise ErrataException(str(ret_data))

        return ret_json

    def _put(self, u, **kwargs):
        self._set_username()
        url = self.canonical_url(u)
        start = time.time()
        ret = None
        if kwargs is not None:
            if 'data' in kwargs:
                ret = requests.put(url,
                                   auth=self._auth,
                                   data=kwargs['data'],
                                   verify=self.ssl_verify)
            elif 'json' in kwargs:
                ret = requests.put(url,
                                   auth=self._auth,
                                   json=kwargs['json'],
                                   verify=self.ssl_verify)

        if ret is None:
            ret = requests.put(url, auth=self._auth, verify=self.ssl_verify)
        self._record('PUT', url, time.time() - start)
        return ret

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
                            if isinstance(m.value, six.string_types):
                                err_msg += m.value + "\n"
                            elif type(m.value) is int:
                                err_msg += str(m.value) + "\n"
                            else:
                                for n in m.value:
                                    err_msg += str(n) + "\n"
            raise ErrataException(err_msg)

        if r.status_code in [401]:
            # lhh - this is not a typo, and the syntax is correct,
            # I assure you.
            raise ErrataException('Pigeon crap. Did it forget to run kinit?')

        if r.status_code in [500]:
            json = r.json()
            # If we have a specific "error" string from the ET, raise that:
            if 'error' in json:
                raise ErrataException(json['error'])
            # Otherwise, fall back to just raising whatever data we got back.
            raise ErrataException(json)

        if r.status_code in [404]:
            err_msg += 'Bug in your code - wrong method for this api? '
            err_msg += 'Wrong location?'
            print(r.json())
            raise ErrataException(err_msg)

        raise ErrataException(err_msg + "Unhandled HTTP status code: " +
                              str(r.status_code))

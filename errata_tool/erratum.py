from __future__ import print_function
import datetime
import os
import re
import requests_kerberos
import six
import textwrap
import time

from errata_tool import ErrataException, ErrataConnector, security, User


class Erratum(ErrataConnector):

    def fmt(self, s):
        # The textwrap library doesn't parse newlines, so you'll want to
        # split on them first, then format each line, then join it all back
        # up.
        lines = s.split('\n')

        page = []
        for l in lines:
            b = textwrap.TextWrapper(width=75, replace_whitespace=True,
                                     break_long_words=False,
                                     break_on_hyphens=False)
            page.append(b.fill(l))
        return '\n'.join(page)

    def _do_init(self):
        self.errata_id = 0
        self._original_bugs = []
        self._cve_bugs = []
        self._original_state = 'NEW_FILES'
        self._original_json = {}

        self._product = None            # Set when you call new
        self._release = None            # Set when you call new
        self._new = False               # set when you call create
        self._update = False            # Set to true if you update any fields
        self._format = True             # Format fields on update (new adv.)
        self._buildschanged = False     # Set to true if you changed builds

        # These should be updated with the 'update()' method, and are provided
        # primarily for debugging/printing by user apps
        self.errata_type = None
        self.text_only = False
        self.text_only_cpe = None
        self.publish_date_override = None
        self.publish_date = None
        self.creation_date = None
        self.ship_date = None           # Set if SHIPPED_LIVE
        self.age = 0                    # Erratum age in days
        self.package_owner_email = None
        self.manager_email = None
        self.manager_id = 0
        self.product_id = 0
        self.release_id = 0
        self.qe_email = ''
        self.qe_group = ''
        self.synopsis = None
        self.topic = None
        self.description = None
        self.solution = None
        self.security_impact = None
        self.cve_names = None
        self.errata_bugs = []
        self.errata_builds = {}
        self.current_flags = []
        self.missing_prod_listings = []
        self.batch_id = None

    def update(self, **kwargs):
        if 'errata_type' in kwargs:
            self.errata_type = kwargs['errata_type']
            self._update = True
        if 'security_impact' in kwargs:
            self.security_impact = kwargs['security_impact']
            self._update = True
        if 'text_only' in kwargs:
            self.text_only = kwargs['text_only']
            self._update = True
        if 'text_only_cpe' in kwargs:
            self.text_only_cpe = kwargs['text_only_cpe']
            self._update = True
        if 'date' in kwargs:
            try:
                datetime.datetime.strptime(kwargs['date'], '%Y-%b-%d')
            except ValueError:
                raise ValueError(
                    'Date must be of the form: YYYY-MON-DD; 2015-Mar-11')
            self.publish_date_override = kwargs['date']
            self._update = True
        if 'owner_email' in kwargs:
            self.package_owner_email = kwargs['owner_email']
            self._update = True
        if 'manager_email' in kwargs:
            self.manager_email = kwargs['manager_email']
            self._update = True
        if 'manager_id' in kwargs:
            self.manager_id = kwargs['manager_id']
            self._update = True
        if 'qe_email' in kwargs:
            self.qe_email = kwargs['qe_email']
            self._update = True
        if 'qe_group' in kwargs:
            self.qe_group = kwargs['qe_group']
            self._update = True
        if 'synopsis' in kwargs:
            self.synopsis = kwargs['synopsis']
            self._update = True
        if 'cve_names' in kwargs:
            self.cve_names = kwargs['cve_names']
            self._update = True
        if 'topic' in kwargs:
            self.topic = self.fmt(kwargs['topic'])
            self._update = True
        if 'description' in kwargs:
            self.description = self.fmt(kwargs['description'])
            self._update = True
        if 'solution' in kwargs:
            self.solution = self.fmt(kwargs['solution'])
            self._update = True

    def __init__(self, **kwargs):

        self.ssl_verify = security.security_settings.ssl_verify()

        # Blank erratum e.g. if create is required
        self._do_init()
        if 'errata_id' in kwargs:
            self._fetch(kwargs['errata_id'])
            return

        if 'bug_id' in kwargs:
            self._fetch_by_bug(kwargs['bug_id'])
            return

        if 'product' not in kwargs:
            raise ErrataException('Creating errata requires a product')
        if 'release' not in kwargs:
            raise ErrataException('Creating errata requires a release')
        if 'format' in kwargs:
            self._format = kwargs['format']

        self._new = True
        self.errata_name = '(unassigned)'
        self.errata_state = 'NEW_FILES'
        self._product = kwargs['product']
        self._release = kwargs['release']
        self.update(**kwargs)
        if 'solution' not in kwargs:
            self.solution = self.fmt("Before applying this update, \
make sure all previously released errata relevant to your system \
have been applied.\n\
\n\
For details on how to apply this update, refer to:\n\
\n\
https://access.redhat.com/articles/11258")

        # errata tool defaults
        if 'errata_type' in kwargs:
            self.errata_type = kwargs['errata_type']
        else:
            self.errata_type = 'RHBA'

    # Pull down the state of the erratum and store it.
    def _fetch(self, errata_id):
        self._new = False
        self._update = False
        self._buildschanged = False
        self.errata_builds = {}
        self.current_flags = []

        try:
            # TODO: remove call to /advisory/X.json once new API
            # supports all the information
            endpoint_list = [
                '/advisory/' + str(errata_id) + '.json',
                '/api/v1/erratum/' + str(errata_id),
            ]
            # Want to ditch advisory_old eventually
            advisory_old = None
            advisory = None
            erratum = None
            for endpoint in endpoint_list:
                r = self._get(endpoint)
                if r is None:
                    continue
                if advisory is None and 'erratum' in endpoint:
                    advisory = r
                    continue
                # Fallthrough
                if advisory_old is None:
                    advisory_old = r
            if advisory is None:
                print('do not have requested data bailing')
                return None

            # Short circuit to get the advisory
            for key in advisory['errata']:
                erratum = advisory['errata'][key]
                self.errata_type = key.upper()
                break

            self.errata_id = erratum['id']
            # NEW_FILES QE etc.
            self.errata_state = erratum['status']
            self._original_state = self.errata_state
            self._original_json = erratum

            # Check if the erratum is under embargo
            self.embargoed = False
            self.release_date = erratum['release_date']
            if self.release_date is not None:
                cur = datetime.datetime.utcnow()
                cur = str(cur).split()[0]
                if self.release_date > cur:
                    self.embargoed = True

            # Target Ship date
            d = erratum['publish_date_override']
            if d is not None:
                pd = time.strptime(str(d), '%Y-%m-%dT%H:%M:%SZ')
                self.publish_date_override = time.strftime('%Y-%b-%d', pd)

            # Target Ship date (immutable; e.g. from batch)
            d = erratum['publish_date']
            if d is not None:
                pd = time.strptime(str(d), '%Y-%m-%dT%H:%M:%SZ')
                self.publish_date = time.strftime('%Y-%b-%d', pd)

            # Actual ship date (if in SHIPPED_LIVE)
            if self.errata_state in ('SHIPPED_LIVE'):
                d = erratum['actual_ship_date']
                # Could be None. e.g. advisory 43686
                if d:
                    d = time.strptime(str(d), '%Y-%m-%dT%H:%M:%SZ')
                    self.ship_date = time.strftime('%Y-%b-%d', d)

            # File date
            d = erratum['created_at']
            d = time.strptime(str(d), '%Y-%m-%dT%H:%M:%SZ')
            self.creation_date = time.strftime('%Y-%b-%d', d)

            d = time.strftime('%Y-%b-%d', time.gmtime())
            if self.ship_date is not None:
                d = self.ship_date

            filed = datetime.datetime.strptime(self.creation_date, '%Y-%b-%d')
            ship = datetime.datetime.strptime(d, '%Y-%b-%d')
            age = ship - filed
            self.age = age.days

            # Baseline flags.
            if self.errata_state in ('QE'):
                if 'sign_requested' in erratum and \
                   erratum['sign_requested'] == 0:
                    self.addFlags('request_sigs')
                if 'rhnqa' in erratum and erratum['rhnqa'] == 0:
                    self.addFlags('needs_distqa')

            if 'doc_complete' in erratum and erratum['doc_complete'] == 0:
                self.addFlags('needs_docs')

            if self.errata_state == 'NEW_FILES':
                self.addFlags('needs_devel')

            # Note: new errata return values will have other bits.
            self.errata_name = erratum['fulladvisory']

            # Grab immutable fields
            self._product = advisory_old['product']['short_name']
            self._release = advisory_old['release']['name']

            # A maybe-empty list, containing eg. "rpm" or "docker"
            self.content_types = erratum['content_types']

            # store product and release IDs
            self.product_id = advisory_old['product']['id']
            self.release_id = advisory_old['release']['id']

            self.package_owner_email = advisory_old['people']['package_owner']
            self.reporter = advisory_old['people']['reporter']
            self.qe_email = advisory_old['people']['assigned_to']
            self.qe_group = advisory_old['people']['qe_group']

            # XXX Errata tool doesn't report manager?
            # https://bugzilla.redhat.com/show_bug.cgi?id=1664884
            # self.manager_email = ???
            self.manager_id = erratum.get('manager_id')

            # Grab mutable errata content
            self.text_only = erratum['text_only']
            self.synopsis = erratum['synopsis']
            content = advisory['content']['content']
            self.text_only_cpe = content['text_only_cpe']
            self.topic = content['topic']
            self.description = content['description']
            self.solution = content['solution']
            self.errata_bugs = [int(b['bug']['id']) for b
                                in advisory['bugs']['bugs']]
            self.cve_names = content['cve']
            if self.cve_names == '':
                self.cve_names = None
            self._original_bugs = list(self.errata_bugs)

            self._cache_bug_info(self._original_bugs)

            # Try to check to see if we need devel assistance, qe assistance or
            # rel prep assistance
            if self.errata_state == 'QE':
                self._check_tps()
                self._check_bugs()
                self._check_need_rel_prep()

            # Check for security review
            if 'rhsa' in advisory['errata']:
                sa = advisory['errata']['rhsa']['security_approved']
                self.security_impact = advisory['errata']['rhsa']['security_impact']  # NOQA

                if sa is None:
                    self.addFlags('request_security')
                elif sa is False:
                    self.addFlags('needs_security')

            check_signatures = self.errata_state != 'NEW_FILES'
            self._get_build_list(check_signatures)
            self.batch_id = erratum.get('batch_id')

            return

        except RuntimeError:
            # Requests seems to loop infinitely if this happens...
            raise ErrataException('Pigeon crap. Did it forget to run kinit?')
        except IndexError:
            # errata_id not found
            raise ErrataException('Errata ID field not found in response')
        except Exception:
            # Todo: better handling
            raise

    def _check_signature_for_build(self, build):
        signed = False

        url = os.path.join('/api/v1/build/', build)
        nvr_json = self._get(url)

        if u'rpms_signed' in nvr_json:
            if nvr_json[u'rpms_signed']:
                signed = True

        return signed

    def _cache_bug_info(self, bug_id_list):
        # Omitted: RHOS shale's use of bz_cache here.
        pass

    def metadataCdnRepos(self, enable=[], disable=[]):
        """Get or set the CDN repos for this advisory.

        Note: This method applies only for advisories containing Docker images.

        When called with no arguments, this method returns all available CDN
        repos for advisory metadata. Otherwise you may enable or disable repos
        here.

        :param enable: (optional) A list of CDN repos to enable.
                       Example: ["rhel-7-server-rhceph-3-mon-rpms__x86_64"]
        :param disable: (optional) A list of CDN repos to disable.
        :returns: a list of dicts about each available repo, and whether they
                  are enabled or disabled.
        """
        return self._cdn_repos('metadata_cdn_repos', enable, disable)

    def textOnlyRepos(self, enable=[], disable=[]):
        """Get or set the text-only repos for this advisory.

        Note: This method applies only for text-only advisories.

        When called with no arguments, this method returns all available CDN
        repos for the advisory text. Otherwise you may enable or disable repos
        here.

        :param enable: (optional) A list of CDN repos to enable.
                       Example: ["rhel-7-server-rhceph-3-mon-rpms__x86_64"]
        :param disable: (optional) A list of CDN repos to disable.
        :returns: a list of dicts about each available repo, and whether they
                  are enabled or disabled.
        """
        return self._cdn_repos('text_only_repos', enable, disable)

    def _cdn_repos(self, endpoint, enable=[], disable=[]):
        """Get or set the repos for this advisory.

        Use this for setting repos on text-only or docker advisories.

        :param endpoint: The erratum API endpoint to request.
                         Example: "metadata_cdn_repos" or "text_only_repos".
        :param enable: (optional) A list of CDN repos to enable.
                       Example: ["rhel-7-server-rhceph-3-mon-rpms__x86_64"]
        :param disable: (optional) A list of CDN repos to disable.
        :returns: a list of dicts about each available repo, and whether they
                  are enabled or disabled.
        """
        if endpoint not in ('metadata_cdn_repos', 'text_only_repos'):
            raise ValueError('unsupported endpoint %s', endpoint)
        url = '/api/v1/erratum/%d/%s' % (self.errata_id, endpoint)
        if not enable and not disable:
            return self._get(url)
        payload = [{'enabled': True, 'repo': repo} for repo in enable]
        payload += [{'enabled': False, 'repo': repo} for repo in disable]
        result = self._put(url, json=payload)
        # XXX we should fix error handling and return values in _put() to work
        # like _get() currently does.
        result.raise_for_status()
        return result.json()

    def _check_tps(self):
        # Check for TPS failure (QE state only)
        url = '/advisory/%i/tps_jobs.json' % self.errata_id
        r = self._get(url)
        distqa_tps = 0
        distqa_passing = 0
        for tps in r:
            if tps['rhnqa'] is True:
                distqa_tps = distqa_tps + 1
            if tps['state'] == 'BAD' or \
               'failed to generate' in tps['state']:
                self.addFlags('tps_errors')
                continue
            if tps['state'] in ('BUSY', 'NOT_STARTED'):
                self.addFlags('tps_wait')
                continue
            if tps['rhnqa'] is True:
                distqa_passing = distqa_passing + 1

        # Assume testing is done... ;)
        if distqa_tps > 0 and distqa_passing != distqa_tps:
            self.addFlags('needs_distqa')
            self.need_rel_prep = False
        else:
            self.need_rel_prep = True

    def _check_bugs(self):
        pass

    def _check_need_rel_prep(self):
        # Omitted: RHOS shale's "need_rel_prep" here, uses bz_cache.
        pass

    def externalTests(self, test_type=None):
        """Get active external test results for this advisory.

        :param test_type: str, like "rpmdiff" or "covscan"
        :returns: a possibly-empty list of dicts, one per result.
        """
        response = self.get_filter('/api/v1/external_tests', 'filter',
                                   active='true', errata_id=self.errata_id,
                                   test_type=test_type, paginated=True)
        return response['data']

    def _get_build_list(self, check_signatures=False):
        # Grab build list; store on a per-key basis
        # REFERENCE

        # Item 5.2.10.3. GET /advisory/{id}/builds.json
        # Then try to check to see if they are signed or not
        # Item 5.2.2.1. GET /api/v1/build/{id_or_nvr}
        url = "/advisory/%i/builds.json" % self.errata_id
        product_versions = self._get(url)
        have_all_sigs = True
        for product_version in product_versions:
            builds = []
            for pv_builds in product_versions[product_version]:
                for nvr, mappings in six.iteritems(pv_builds):
                    builds.append(nvr)
                    if not mappings:
                        self.missing_prod_listings.append(nvr)
                    if have_all_sigs and check_signatures:

                        if not self._check_signature_for_build(nvr):
                            self.addFlags('needs_sigs')
                            have_all_sigs = False

            self.errata_builds[product_version] = builds
        if have_all_sigs:
            self.removeFlags(['request_sigs', 'needs_sigs'])

    def _fetch_by_bug(self, bug_id):
        # print("fetch_by_bug")
        try:
            url = "/bugs/%i/advisories.json" % bug_id
            rj = self._get(url)

            stored = False
            for e in rj:
                if not stored:
                    stored = True
                    self._fetch(e['id'])
                else:
                    print('Warning: Ignoring additional erratum ' +
                          str(e['id']) + ' for bug ', str(bug_id))

        except RuntimeError:
            # Requests seems to loop infinitely if this happens...
            raise ErrataException('Pigeon crap. Did it forget to run kinit?')
        except IndexError:
            # errata_id not found
            raise ErrataException('Errata ID field not found in response')
        except LookupError:
            # Errata not found
            pass
        except Exception:
            # Todo: better handling
            raise

    def refresh(self):
        if self.errata_id != 0:
            self._fetch(self.errata_id)

    def reloadBuilds(self,
                     no_rpm_listing_only=False,
                     no_current_files_only=False):
        val = {
            'no_rpm_listing_only': int(no_rpm_listing_only),
            'no_current_files_only': int(no_current_files_only),
        }
        url = '/api/v1/erratum/%d/reload_builds' % self.errata_id
        r = self._post(url, data=val)
        self._processResponse(r)
        return r.json()

    def setState(self, state):
        if self._new:
            raise ErrataException('Cannot simultaneously create and change ' +
                                  'an erratum\'s state')
        if self.errata_id == 0:
            raise ErrataException('Cannot change state for uninitialized ' +
                                  'erratum')
        if self.errata_state.upper() == 'NEW_FILES':
            if state.upper() == 'QE':
                self.errata_state = 'QE'
        elif self.errata_state.upper() == 'QE':
            if state.upper() == 'NEW_FILES':
                self.errata_state = 'NEW_FILES'
            if state.upper() == 'REL_PREP':
                self.errata_state = 'REL_PREP'
        elif self.errata_state.upper() == 'REL_PREP':
            if state.upper() == 'NEW_FILES':
                self.errata_state = 'NEW_FILES'
            if state.upper() == 'QE':
                self.errata_state = 'QE'
        else:
            raise ErrataException('Cannot change state from ' +
                                  self.errata_state.upper() + " to " +
                                  state.upper())

    def _addBug(self, b):
        if not isinstance(b, int):
            b = int(b)
        if self.errata_bugs is None:
            self.errata_bugs = []
            self.errata_bugs.append(b)
            return
        if b not in self.errata_bugs:
            self.errata_bugs.append(b)

    def addBugs(self, buglist):
        if isinstance(buglist, int):
            self._addBug(buglist)
            return
        for b in buglist:
            self._addBug(b)

    def _removeBug(self, b):
        if not isinstance(b, int):
            b = int(b)
        if b in self.errata_bugs:
            self.errata_bugs.remove(b)

    def removeBugs(self, buglist):
        if isinstance(buglist, int):
            self._removeBug(buglist)
            return
        for b in buglist:
            self._removeBug(b)

    # Omitted: RHOS shale's syncBugs()
    def syncBugs(self):
        raise NotImplementedError('RHOS-only method')

    # Omitted: RHOS shale's findMissingBuilds()
    def findMissingBuilds(self):
        raise NotImplementedError('RHOS-only method')

    def changeDocsReviewer(self, login_name):
        val = {'login_name': login_name}
        url = '/api/v1/erratum/%d/change_docs_reviewer' % self.errata_id
        r = self._post(url, data=val)
        self._processResponse(r)

    def addCC(self, email):
        """Add someone to the CC list for this advisory. """
        # rhbz#1572000 will add an official API for this.
        val = {'id': self.errata_id, 'email': email}
        url = '/carbon_copies/add_to_cc_list'
        r = self._post(url, data=val)
        self._processResponse(r)

    #
    # Flag list could be replaced with a set at some
    # point.
    #
    # Some flags are tracked and managed here in
    # errata-tool, but users can add their own as well.
    #
    def addFlags(self, flags):
        if not isinstance(flags, list):
            flags = [flags]
        # Two loops intentionally. First one is for
        # input validation.
        for f in flags:
            if not isinstance(f, str):
                raise ValueError('flag ' + str(f) + ' is not a string')
        for f in flags:
            if f not in self.current_flags:
                self.current_flags.append(f)

    def removeFlags(self, flags):
        if not isinstance(flags, list):
            flags = [flags]
        # Two loops intentionally. First one is for
        # input validation.
        for f in flags:
            if not isinstance(f, str):
                raise ValueError('flag ' + str(f) + ' is not a string')
        for f in flags:
            if f in self.current_flags:
                self.current_flags.remove(f)

    # Adding and removing builds can't be done atomically.  Wondering whether
    def addBuildsDirect(self, buildlist, release, **kwargs):
        if 'file_types' not in kwargs:
            file_types = None
        else:
            file_types = kwargs['file_types']

        blist = []
        if isinstance(buildlist, six.string_types):
            blist.append(buildlist)
        else:
            blist = buildlist

        # Adding builds

        # List of dicts.
        pdata = []
        for b in blist:
            # Avoid double-add
            if release in self.errata_builds and \
               b in self.errata_builds[release]:
                continue
            val = {}
            if file_types is not None and b in file_types:
                val['file_types'] = file_types[b]
            val['build'] = b
            val['product_version'] = release
            pdata.append(val)
        url = "/api/v1/erratum/%i/add_builds" % self.errata_id
        r = self._post(url, json=pdata)
        self._processResponse(r)
        self._buildschanged = True
        return

    def addBuilds(self, buildlist, **kwargs):
        """Add Build(s) to erratum"""
        if self._new:
            raise ErrataException('Cannot add builds to unfiled erratum')

        release = None

        if 'release' in kwargs:
            release = kwargs['release']
            del kwargs['release']

        if release is None and len(self.errata_builds.keys()) == 1:
            release = list(self.errata_builds.keys())[0]

        if release is None:
            raise ErrataException('Need to specify a release')

        return self.addBuildsDirect(buildlist, release, **kwargs)

    def setFileInfo(self, file_info):
        # XXX API broken??

        if not isinstance(file_info, dict):
            raise ValueError('file_info is not a dict')
        if len(file_info) < 1:
            return

        # Get:

        url = '/api/v1/erratum/%i/filemeta' % self.errata_id
        r = self._get(url)

        info = []
        files = [k for k in file_info]
        for f in r:
            # print(f['file']['path'] + f['file']['id'])
            fn = os.path.basename(f['file']['path'])
            if fn in files:
                info.append({'file': f['file']['id'],
                             'title': file_info[fn]['title']})

        # print(info)
        # Set:

        # url += '?put_rank=true'
        r = self._put(url, data=info)
        self._processResponse(r)

    def removeBuilds(self, buildlist):
        """Remove build(s) from advisory"""
        if not isinstance(buildlist, (str, list)):
            raise IndexError

        # Removing builds
        # REFERENCE

        if isinstance(buildlist, six.string_types):
            builds = []
            if len(buildlist.strip()) == 0:
                raise IndexError
            builds.append(buildlist.strip())
        else:
            builds = buildlist

        if len(builds) == 0:
            raise IndexError

        for b in builds:
            val = {}
            val['nvr'] = b
            url = "/api/v1/erratum/%i/remove_build" % self.errata_id
            r = self._post(url, data=val)
            self._processResponse(r)
        self._buildschanged = True

    def _write(self):
        pdata = {}

        # See below for APIs used when talking to the errata tool.
        if self._new:
            if self.package_owner_email is None:
                raise ErrataException("Can't create erratum without " +
                                      "package owner email")
            if self.manager_email is None:
                if self.manager_id:
                    manager = User(self.manager_id)
                    self.manager_email = manager.email_address
                else:
                    raise ErrataException("Can't create erratum without " +
                                          "manager email or manager id")
            if self._product is None:
                raise ErrataException("Can't create erratum with no " +
                                      "product specified")
            if self._release is None:
                raise ErrataException("Can't create erratum with no " +
                                      "release specified")
            if self.errata_type is None:
                self.errata_type = 'RHBA'

            if self.errata_type == 'RHSA':
                val = 'None'
                if self.security_impact is not None:
                    val = self.security_impact
                pdata['advisory[security_impact]'] = val

            pdata['product'] = self._product
            pdata['release'] = self._release
            pdata['advisory[package_owner_email]'] = self.package_owner_email
            pdata['advisory[manager_email]'] = self.manager_email

        if self.qe_email is not None and self.qe_email != '':
            pdata['advisory[assigned_to_email]'] = self.qe_email
        if self.qe_group is not None and self.qe_group != '':
            pdata['advisory[quality_responsibility_name]'] = self.qe_group

        if self.synopsis is None:
            raise ErrataException("Can't write erratum without synopsis")
        if self.topic is None:
            raise ErrataException("Can't write erratum without topic")
        if self.description is None:
            raise ErrataException("Can't write erratum without description")
        if self.solution is None:
            raise ErrataException("Can't write erratum without a solution")

        if self.errata_bugs is None:
            raise ErrataException("Can't write erratum without a list of " +
                                  "bugs")

        # Default from errata tool
        pdata['advisory[errata_type]'] = self.errata_type

        # POST/PUT a 1 or 0 value for this text_only boolean
        pdata['advisory[text_only]'] = int(self.text_only)

        if self.text_only_cpe:
            pdata['advisory[text_only_cpe]'] = self.text_only_cpe

        if self.publish_date_override:
            pdata['advisory[publish_date_override]'] = \
                self.publish_date_override

        # ET automagically handles the severity for the synopsis in RHSA's
        # but will still see it as a docs change if we write the same one
        # back again, so remove it.
        if self.errata_type == 'RHSA':
            severity = r'^(Low|Moderate|Important|Critical): '
            self.synopsis = re.sub(severity, "", self.synopsis)
            pdata['advisory[cve]'] = self.cve_names
        pdata['advisory[synopsis]'] = self.synopsis
        pdata['advisory[topic]'] = self.topic
        pdata['advisory[description]'] = self.description
        pdata['advisory[solution]'] = self.solution

        # XXX Delete all bugs is a special case
        last_bug = None
        if len(self.errata_bugs) == 0 and len(self._original_bugs) > 0:
            last_bug = self._original_bugs[0]
            self.errata_bugs = [last_bug]

        # Add back any Vulnerability bugs
        allbugs = list(set(self.errata_bugs) | set(self._cve_bugs))
        idsfixed = ' '.join(str(i) for i in allbugs)
        pdata['advisory[idsfixed]'] = idsfixed

        # Sync newly added bug states
        newbugs = list(set(allbugs) - set(self._original_bugs))
        if len(newbugs):
            # url = '/api/v1/bug/refresh'
            # print(allbugs)
            # r = self._post(url, data=newbugs)
            # self._processResponse(r)
            # ^ XXX broken
            #
            # XXX Sync bug states by force using UI
            # Note: UI limits syncs to 100 bugs per run, so split
            # up into chunks
            syncs = [newbugs[x:x + 100] for x in range(0, len(newbugs), 100)]
            bug_list = {}
            for s in syncs:
                bug_list['issue_list'] = ' '.join(str(i) for i in s)
                url = "/bugs/sync_bug_list"
                r = self._post(url, data=bug_list)
                # XXX should we process return code?

        # Push it
        if self._new:
            # REFERENCE

            # New is 'POST'
            url = "/api/v1/erratum"
            r = self._post(url, data=pdata)
            self._processResponse(r)
            rj = r.json()
            json_errata_type = self.errata_type.lower()
            self.errata_id = rj['errata'][json_errata_type]['errata_id']
            # XXX return JSON returns full advisory name but not
            # typical advisory name - e.g. RHSA-2015:19999-01, but not
            # RHSA-2015:19999, but it's close enough
            self.errata_name = rj['errata'][json_errata_type]['fulladvisory']
        else:
            # REFERENCE

            # Update is 'PUT'
            url = "/api/v1/erratum/%i" % self.errata_id
            r = self._put(url, data=pdata)
        self._processResponse(r)

        # XXX WOW VERY HACK
        # If deleting last bug...
        if last_bug is not None:
            # This doesn't work to remove the last bug, nor does setting
            # idsfixed to empty-string
            # url = "/api/v1/erratum/%i/remove_bug" % self.errata_id
            # pdata = {'bug': str(last_bug)}

            # Solution: Use hacks to pretend we're using the remove-bugs
            # web UI :(
            url = '/bugs/remove_bugs_from_errata/%i' % self.errata_id
            pdata = {}
            pdata['bug[' + str(last_bug) + ']'] = 1

            # Handle weird interaction we get in this particular case
            try:
                r = self._post(url, data=pdata)
            except requests_kerberos.exceptions.MutualAuthenticationError:
                pass
            self._processResponse(r)

    def _putStatus(self):
        # REFERENCE

        # State change is 'POST'
        pdata = {}
        pdata['new_state'] = self.errata_state
        url = "/api/v1/erratum/%i" % self.errata_id
        url += "/change_state"
        r = self._post(url, data=pdata)
        self._processResponse(r)

    def commit(self):
        ret = False
        # Commit changes
        if self._new:
            self._write()
            self.refresh()
            # self.syncBugs() # RHOS shale only
            return

        # XXX Not atomic, but we should refresh on commit
        if self._buildschanged:
            ret = True

        try:
            # Special case:
            # If new state is 'NEW_FILES', set it before anything else
            if (self._original_state != self.errata_state and
                    self.errata_state.upper() == 'NEW_FILES'):
                self._putStatus()
                ret = True

            # Update buglist if it changed
            # Errata tool is very slow - don't PUT if it hasn't changed
            allbugs = list(set(self.errata_bugs) | set(self._cve_bugs))
            if sorted(self._original_bugs) != sorted(allbugs) \
               or self._update:
                self._write()
                # self.syncBugs() # RHOS shale only
                ret = True

            # Perhaps someone did addbugs + setState('QE')
            if (self._original_state != self.errata_state and
                    self.errata_state.upper() != 'NEW_FILES'):
                self._putStatus()
                ret = True
        except ErrataException:
            raise

        if ret:
            self.refresh()
        return ret

    def push(self, target='stage'):
        """Push an advisory to "stage", "live", or both.

        :param target: A string "stage" or "live". Defaults to "stage". You
                       can also pass a list here, ['stage', 'live'] to do both
                       in one operation.
        :returns: a list describing the Errata Tool's newly triggered push
                  tasks. Each push task includes an "id". You can query the
                  status of this push ID at
                  /api/v1/erratum/{id}/push/{push_id} .
        """
        # Accept 'stage', 'live', or a set of specific options
        if self.errata_id == 0:
            return False

        # Basic mode: 'stage' or 'live'
        url = '/api/v1/erratum/' + str(self.errata_id) + '/push'
        if isinstance(target, str):
            if target != 'stage' and target != 'live':
                raise ValueError('Wrong value for target: expected ' +
                                 '\'stage\', \'live\', or a list')

            r = self._post(url + '?defaults=' + str(target))
            self._processResponse(r)
            return r.json()

        # Advanced mode: see ET documentation.
        if not isinstance(target, list):
            raise ValueError('Wrong value for target: expected ' +
                             '\'stage\', \'live\', or a list')
        r = self._post(url, data=target)
        self._processResponse(r)
        return r.json()

    def dump(self):
        print(self)
        print("Package Owner Email: " + self.package_owner_email)
        print("Manager Email: " + self.manager_email)
        print("QE: " + self.qe_email + " " + self.qe_group)
        print("Type: " + self.errata_type)
        if self.creation_date is not None:
            print("Created: " + self.creation_date)
        if self.errata_state == 'SHIPPED_LIVE':
            print("Shipped: " + self.ship_date)
        print("Age: " + str(self.age) + " days")
        if len(self.current_flags) > 0:
            print("Flags: " + ' '.join(self.current_flags))
        print("Synopsis: " + self.synopsis)
        if self.publish_date_override is not None:
            print('')
            print("Ship Target: {0}".format(self.publish_date_override))
        if self.publish_date is not None:
            print('')
            print("Ship Target: {0}".format(self.publish_date))
        if self.batch_id is not None:
            print('')
            print("Batch: {0}".format(self.batch_id))
            print("Ship Target: {0}".format(self.publish_date))
        print('')
        print("Topic")
        print("=====")
        print(self.topic)
        print('')
        print("Description")
        print("===========")
        print(self.description)
        print('')
        print("Solution")
        print("========")
        print(self.solution)

    def url(self):
        return super(Erratum, self).canonical_url("/advisory/" +
                                                  str(self.errata_id))

    def get_erratum_data(self):
        """Return the server's JSON data for this advisory.

        This returns the JSON response from the Errata Tool's
        REST API /advisory/<errata_id>.json and /api/v1/erratum/<errata_id>
        endpoints. Use this when debugging interactions with the Errata Tool
        or when passing this data on to other non-Python tools.

        :returns: a dict that is simply the parsed JSON from the server.
        """
        return dict(self._original_json)  # shallow copy

    def __lt__(self, other):
        return self.errata_id < other.errata_id

    def __gt__(self, other):
        return self.errata_id > other.errata_id

    def __eq__(self, other):
        return self.errata_id == other.errata_id

    def __le__(self, other):
        return self.errata_id <= other.errata_id

    def __ge__(self, other):
        return self.errata_id >= other.errata_id

    def __ne__(self, other):
        return self.errata_id != other.errata_id

    def __str__(self):
        s = "\n  builds: \n"
        for k in self.errata_builds:
            s = s + "    " + k + "\n"
            for b in sorted(self.errata_builds[k], key=lambda x: x.lower()):
                s = s + "      " + b + "\n"
        if len(self.current_flags) > 0:
            s = "\n  Flags:       " + ' '.join(self.current_flags) + s
        if len(self._cve_bugs) > 0:
            s = "\n  Impact:      " + str(self.security_impact) + s
            s = "\n  CVE bugs:    " + str(self._cve_bugs) + s
        if self.cve_names is not None:
            s = "\n  CVEs:        " + str(self.cve_names) + s

        pdate = self.publish_date_override
        if pdate is None and self.publish_date is not None:
            pdate = self.publish_date
        if self.batch_id is not None and self.publish_date is not None:
            pdate = self.publish_date

        return self.errata_name + ": " + self.synopsis + \
            "\n  package owner: " + self.package_owner_email + \
            "  qe: " + self.qe_email + \
            " qe_group: " + self.qe_group + \
            "\n  url:   " + \
            self.url() + \
            "\n  state: " + self.errata_state + \
            "\n  created:     " + str(self.creation_date) + \
            "\n  ship target: " + str(pdate) + \
            "\n  batch_id:    " + str(self.batch_id) + \
            "\n  ship date:   " + str(self.ship_date) + \
            "\n  age:         " + str(self.age) + " days" \
            "\n  bugs:        " + str(self.errata_bugs) + \
            s

    def __int__(self):
        return self.errata_id

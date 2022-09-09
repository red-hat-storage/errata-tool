%global pkgname errata-tool

Name:           python-%{pkgname}
Version:        1.28.1
Release:        1%{?dist}
Summary:        Modern Python API to Red Hat's Errata Tool
Group:          Development/Languages

License:        MIT
URL:            https://github.com/red-hat-storage/errata-tool

Source0:        %{pkgname}-%{version}.tar.gz

BuildArch:      noarch
%if 0%{?el7}
BuildRequires:  pytest
BuildRequires:  PyYAML
BuildRequires:  python2-devel
BuildRequires:  python-jsonpath-rw
BuildRequires:  python-requests-gssapi
BuildRequires:  python-setuptools
BuildRequires:  python-six
%else
BuildRequires:  python3-devel
BuildRequires:  python3-jsonpath-rw
BuildRequires:  python3-pytest
BuildRequires:  python3-pyyaml
BuildRequires:  python3-requests-gssapi
BuildRequires:  python3-setuptools
BuildRequires:  python3-six
%endif

%description
Modern Python API to Red Hat's Errata Tool


%if 0%{?el7}
Requires:  PyYAML
Requires:  python-requests-gssapi
Requires:  python-jsonpath-rw
Requires:  python-six
%else
%package -n python3-%{pkgname}
Summary:    %{summary}
Requires:   python3 >= 3.5
Requires:   python3-requests-gssapi
Requires:   python3-jsonpath-rw
Requires:   python3-pyyaml
Requires:   python3-six

%description -n python3-%{pkgname}
Modern Python API to Red Hat's Errata Tool
%endif


%prep
%setup -q -n %{pkgname}-%{version}

%if 0%{?with_python3}
cp -a . %{py3dir}
%endif

%build
%if 0%{?el7}
%{__python2} setup.py build
%else
%{py3_build}
%endif

%install
%if 0%{?el7}
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%else
%py3_install
%endif

%check
export PYTHONPATH=$(pwd)
%if 0%{?el7}
py.test-%{python2_version} -v errata_tool/tests
%else
py.test-%{python3_version} -v errata_tool/tests
%endif

%if 0%{?el7}
%files
%{!?_licensedir:%global license %%doc}
%doc README.rst
%license LICENSE
%{python2_sitelib}/*
%else
%files -n python3-%{pkgname}
%doc README.rst
%license LICENSE
%{python3_sitelib}/*
%endif

# Will go to python3 subpkg when enabled, otherwise to python2
%{_bindir}/errata-tool

%changelog
* Wed Aug 31 2016 Ken Dreyer <kdreyer@redhat.com> - 1.0.0-1
- Initial package

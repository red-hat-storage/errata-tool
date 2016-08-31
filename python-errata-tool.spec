%if 0%{?fedora}
%global with_python3 1
%global _docdir_fmt %{name}
%endif

%global pkgname errata-tool

Name:           python-%{pkgname}
Version:        1.1.0
Release:        1%{?dist}
Summary:        Modern Python API to Red Hat's Errata Tool
Group:          Development/Languages

License:        MIT
URL:            https://github.com/ktdreyer/errata-tool

Source0:        %{pkgname}-%{version}.tar.gz

BuildArch:      noarch
%if 0%{?with_python3}
Requires:  python3-requests
BuildRequires:  python3-devel
BuildRequires:  python3-pytest
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
%else # python 2
Requires:  python-requests
BuildRequires:  pytest
BuildRequires:  python2-devel
BuildRequires:  python-requests
BuildRequires:  python-setuptools
%endif

%description
Modern Python API to Red Hat's Errata Tool

%prep
%setup -q -n %{pkgname}-%{version}

%build

%if 0%{?with_python3}
%{__python3} setup.py build
%else
%{__python2} setup.py build
%endif # with_python3

%install
%if 0%{?with_python3}
%{__python3} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%else
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%endif

%check
export PYTHONPATH=$(pwd)

%if 0%{?with_python3}
py.test-%{python3_version} -v errata_tool/tests
%else
py.test-%{python_version} -v errata_tool/tests
%endif

%files
%{!?_licensedir:%global license %%doc}
%doc README.rst
%license LICENSE
%if 0%{?with_python3}
%{python3_sitelib}/*
%else
%{python2_sitelib}/*
%endif # with_python3


%changelog
* Wed Aug 31 2016 Ken Dreyer <kdreyer@redhat.com> - 1.0.0-1
- Initial package

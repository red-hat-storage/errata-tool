%if 0%{?fedora}
%global with_python3 1
%global _docdir_fmt %{name}
%endif

%global pkgname errata-tool

Name:           python-%{pkgname}
Version:        1.8.2
Release:        1%{?dist}
Summary:        Modern Python API to Red Hat's Errata Tool
Group:          Development/Languages

License:        MIT
URL:            https://github.com/red-hat-storage/errata-tool

Source0:        %{pkgname}-%{version}.tar.gz

BuildArch:      noarch
%if 0%{?with_python3}
BuildRequires:  python3-devel
BuildRequires:  python3-jsonpath-rw
BuildRequires:  python3-pytest
BuildRequires:  python3-requests-kerberos
BuildRequires:  python3-setuptools
BuildRequires:  python3-six
%endif
Requires:  python-requests-kerberos
Requires:  python-jsonpath-rw
Requires:  python-six
BuildRequires:  pytest
BuildRequires:  python2-devel
BuildRequires:  python-jsonpath-rw
BuildRequires:  python-requests-kerberos
BuildRequires:  python-setuptools
BuildRequires:  python-six

%description
Modern Python API to Red Hat's Errata Tool


%if 0%{?with_python3}
%package -n python3-%{pkgname}
Summary:    %{summary}
Requires:   python3 >= 3.5
Requires:   python3-requests-kerberos
Requires:   python3-jsonpath-rw
Requires:   python3-six

%description -n python3-%{pkgname}
Modern Python API to Red Hat's Errata Tool
%endif # with_python3


%prep
%setup -q -n %{pkgname}-%{version}

%if 0%{?with_python3}
cp -a . %{py3dir}
%endif # with_python3

%build
%{__python2} setup.py build

%if 0%{?with_python3}
%{py3_build}
%endif # with_python3

%install
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%if 0%{?with_python3}
%py3_install
%endif # with_python3

%check
export PYTHONPATH=$(pwd)
py.test-%{python_version} -v errata_tool/tests

%if 0%{?with_python3}
pushd %{py3dir}
py.test-%{python3_version} -v errata_tool/tests
popd
%endif # with_python3

%files
%{!?_licensedir:%global license %%doc}
%doc README.rst
%license LICENSE
%{python2_sitelib}/*

%if 0%{?with_python3}
%files -n python3-%{pkgname}
%doc README.rst
%license LICENSE
%{python3_sitelib}/*
%endif # with_python3


%changelog
* Wed Aug 31 2016 Ken Dreyer <kdreyer@redhat.com> - 1.0.0-1
- Initial package

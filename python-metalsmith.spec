%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global sname metalsmith

%global common_summary Bare metal provisioner using Ironic
%global common_desc Simple Python library and CLI tool to provision bare metal machines using OpenStack Ironic.
%global common_desc_tests Tests for metalsmith.

Name: python-%{sname}
Version: XXX
Release: XXX
Summary: %{common_summary}
License: ASL 2.0
URL: https://metalsmith.readthedocs.io/

Source0: http://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz

BuildArch: noarch

%description
%{common_desc}

%package -n python2-%{sname}
Summary: %{common_summary}
%{?python_provide:%python_provide python2-%{sname}}

BuildRequires: python2-devel
BuildRequires: python2-pbr
BuildRequires: python2-setuptools
BuildRequires: git
# Required for running unit tests
BuildRequires: python2-ironicclient
BuildRequires: python2-mock
BuildRequires: python2-openstacksdk
BuildRequires: python2-six
BuildRequires: python2-testtools

Requires: python2-ironicclient
Requires: python2-openstacksdk
Requires: python2-pbr
Requires: python2-six

Requires(pre): shadow-utils

%description -n python2-%{sname}
%{common_desc}

%package -n python2-%{sname}-tests
Summary: metalsmith tests
Requires: python2-%{sname} = %{version}-%{release}

%description -n python2-%{sname}-tests
%{common_desc_tests}

%if 0%{?with_python3}

%package -n python3-%{sname}
Summary: %{common_summary}

%{?python_provide:%python_provide python3-%{sname}}
BuildRequires: python3-devel
BuildRequires: python3-pbr
BuildRequires: python3-setuptools
# Required for running unit tests
BuildRequires: python3-ironicclient
BuildRequires: python3-mock
BuildRequires: python3-openstacksdk
BuildRequires: python3-six
BuildRequires: python3-testtools

Requires: python3-ironicclient
Requires: python3-openstacksdk
Requires: python3-pbr
Requires: python3-six

%description -n python3-%{sname}
%{common_desc}

%package -n python3-%{sname}-tests
Summary: metalsmith tests
Requires: python3-%{sname} = %{version}-%{release}

%description -n python3-%{sname}-tests
%{common_desc_tests}

%endif # with_python3

%package -n python-%{sname}-doc
Summary: %{common_summary} - documentation

BuildRequires: python2-sphinx
BuildRequires: python2-sphinxcontrib-apidoc
BuildRequires: openstack-macros

%description -n python-%{sname}-doc
%{common_summary}

This package contains documentation.

%prep
%autosetup -n %{sname}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup

%build
%py2_build
%if 0%{?with_python3}
%py3_build
%endif # with_python3

# generate html docs
%{__python2} setup.py build_sphinx -b html
# remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}

%install
%if 0%{?with_python3}
%py3_install
# remove python3 binary for now
rm %{buildroot}/%{_bindir}/metalsmith
%endif # with_python3

%py2_install

%check
%{__python2} -m unittest discover metalsmith.test

%if 0%{?with_python3}
%{__python3} -m unittest discover metalsmith.test
%endif # with_python3

%files -n python2-%{sname}
%license LICENSE
%{_bindir}/metalsmith
%{python2_sitelib}/%{sname}
%{python2_sitelib}/%{sname}-*.egg-info
%exclude %{python2_sitelib}/%{sname}/test

%files -n python2-%{sname}-tests
%license LICENSE
%{python2_sitelib}/%{sname}/test

%if 0%{?with_python3}

%files python3-%{sname}
%license LICENSE
%{python3_sitelib}/%{sname}
%{python3_sitelib}/%{sname}-*.egg-info
%exclude %{python3_sitelib}/%{sname}/test

%files -n python3-%{sname}-tests
%license LICENSE
%{python3_sitelib}/%{sname}/test

%endif # with_python3

%files -n python-%{sname}-doc
%license LICENSE
%doc doc/build/html README.rst

%changelog
* Wed May 23 2018 Dmitry Tantsur <divius.inside@gmail.com> 0.3.0-1
- Initial package.

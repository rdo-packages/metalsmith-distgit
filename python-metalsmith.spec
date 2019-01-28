# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1
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

%package -n python%{pyver}-%{sname}
Summary: %{common_summary}
%{?python_provide:%python_provide python%{pyver}-%{sname}}
%if %{pyver} == 3
Obsoletes: python2-%{sname} < %{version}-%{release}
%endif

BuildRequires: git
BuildRequires: openstack-macros
BuildRequires: python%{pyver}-devel
BuildRequires: python%{pyver}-pbr
BuildRequires: python%{pyver}-setuptools
# Required for running unit tests
BuildRequires: python%{pyver}-mock
BuildRequires: python%{pyver}-openstacksdk
BuildRequires: python%{pyver}-six
BuildRequires: python%{pyver}-stestr
BuildRequires: python%{pyver}-testtools

Requires: genisoimage
Requires: python%{pyver}-openstacksdk >= 0.22.0
Requires: python%{pyver}-pbr >= 2.0.0
Requires: python%{pyver}-six >= 1.10.0

Requires(pre): shadow-utils

%description -n python%{pyver}-%{sname}
%{common_desc}

%package -n python%{pyver}-%{sname}-tests
Summary: metalsmith tests
Requires: python%{pyver}-%{sname} = %{version}-%{release}
Requires: python%{pyver}-mock
Requires: python%{pyver}-testtools

%description -n python%{pyver}-%{sname}-tests
%{common_desc_tests}

%if 0%{?with_doc}
%package -n python-%{sname}-doc
Summary: %{common_summary} - documentation

BuildRequires: python%{pyver}-sphinx
BuildRequires: python%{pyver}-sphinxcontrib-apidoc

%description -n python-%{sname}-doc
%{common_summary}

This package contains documentation.
%endif

%package -n ansible-role-%{sname}-deployment
Summary: %{common_summary} - ansible role

# The ansible role uses CLI which is currently provided by the Python 2
# package. Change this when the CLI is provided by the Python 3 package.
Requires: python%{pyver}-%{sname} = %{version}-%{release}
# Handle python2 exception
%if %{pyver} == 2
Requires: ansible >= 2.3
%else
Requires: ansible-python3 >= 2.3
%endif

%description -n ansible-role-%{sname}-deployment
%{common_summary}

This package contains the metalsmith_deployment role to use metalsmith
in ansible playbooks.

%prep
%autosetup -n %{sname}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup

%build
%{pyver_build}

%if 0%{?with_doc}
# generate html docs
sphinx-build-%{pyver} -b html doc/source doc/build/html
# remove the sphinx-build-%{pyver} leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{pyver_install}

# Create a versioned binary for backwards compatibility until everything is pure py3
ln -s metalsmith %{buildroot}%{_bindir}/metalsmith-%{pyver}

%check
stestr-%{pyver} run

%files -n python%{pyver}-%{sname}
%license LICENSE
%{_bindir}/metalsmith
%{_bindir}/metalsmith-%{pyver}
%{pyver_sitelib}/%{sname}
%{pyver_sitelib}/%{sname}-*.egg-info
%exclude %{pyver_sitelib}/%{sname}/test

%files -n python%{pyver}-%{sname}-tests
%license LICENSE
%{pyver_sitelib}/%{sname}/test

%if 0%{?with_doc}
%files -n python-%{sname}-doc
%license LICENSE
%doc doc/build/html README.rst
%endif

%files -n ansible-role-%{sname}-deployment
%license LICENSE
%doc roles/metalsmith_deployment/README.rst
%{_datadir}/ansible/roles/metalsmith_deployment
%exclude %{_datadir}/ansible/roles/metalsmith_deployment/README.rst

%changelog
# REMOVEME: error caused by commit http://git.openstack.org/cgit/openstack/metalsmith/commit/?id=a57d58493502c1038d2f6cbf162538a206c63f64

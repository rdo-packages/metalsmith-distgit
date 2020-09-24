%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1
%global sname metalsmith

%global common_summary Bare metal provisioner using Ironic
%global common_desc Simple Python library and CLI tool to \
provision bare metal machines using OpenStack Ironic.
%global common_desc_tests Tests for metalsmith.

Name: python-%{sname}
Version: XXX
Release: XXX
Summary: %{common_summary}
License: ASL 2.0
URL: https://docs.openstack.org/metalsmith/latest/

Source0: http://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz

BuildArch: noarch

%description
%{common_desc}

%package -n python3-%{sname}
Summary: %{common_summary}
%{?python_provide:%python_provide python3-%{sname}}
Obsoletes: python2-%{sname} < %{version}-%{release}

BuildRequires: git
BuildRequires: openstack-macros
BuildRequires: python3-devel
BuildRequires: python3-pbr
BuildRequires: python3-setuptools
# Required for running unit tests
BuildRequires: python3-mock
BuildRequires: python3-openstacksdk
BuildRequires: python3-prettytable
BuildRequires: python3-stestr
BuildRequires: python3-testtools
BuildRequires: python3-requests
BuildRequires: ansible >= 2.6

Requires: python3-openstacksdk >= 0.29.0
Requires: python3-pbr >= 2.0.0
Requires: python3-prettytable >= 0.7.2
Requires: python3-requests >= 2.18.4


Requires(pre): shadow-utils

%description -n python3-%{sname}
%{common_desc}

%package -n python3-%{sname}-tests
Summary: metalsmith tests
Requires: python3-%{sname} = %{version}-%{release}
Requires: python3-mock
Requires: python3-testtools
Requires: ansible >= 2.6

%description -n python3-%{sname}-tests
%{common_desc_tests}

%if 0%{?with_doc}
%package -n python-%{sname}-doc
Summary: %{common_summary} - documentation

BuildRequires: python3-sphinx
BuildRequires: python3-openstackdocstheme
BuildRequires: python3-sphinxcontrib-apidoc
BuildRequires: python3-sphinxcontrib-rsvgconverter

%description -n python-%{sname}-doc
%{common_summary}

This package contains documentation.
%endif

%package -n ansible-role-%{sname}-deployment
Summary: %{common_summary} - ansible role

# The ansible role uses CLI which is currently provided by the Python 2
# package. Change this when the CLI is provided by the Python 3 package.
Requires: python3-%{sname} = %{version}-%{release}
Requires: python3dist(ansible) >= 2.9
Requires: ansible-role-openstack-operations

%description -n ansible-role-%{sname}-deployment
%{common_summary}

This package contains the metalsmith_deployment role to use metalsmith
in ansible playbooks.

%prep
%autosetup -n %{sname}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup

# remove shebangs and fix permissions
if [ -f metalsmith_ansible/ansible_plugins/modules/metalsmith_instances.py ]; then
  sed -i '1{/^#!/d}' metalsmith_ansible/ansible_plugins/modules/metalsmith_instances.py
  chmod u=rw,go=r metalsmith_ansible/ansible_plugins/modules/metalsmith_instances.py
fi


%build
%{py3_build}

%if 0%{?with_doc}
# generate html docs
sphinx-build-3 -b html doc/source doc/build/html
# remove the sphinx-build-3 leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{py3_install}

if [ ! -d %{buildroot}%{_datadir}/ansible/plugins ]; then
  mkdir -p %{buildroot}%{_datadir}/ansible/plugins
fi

# Create a versioned binary for backwards compatibility until everything is pure py3
ln -s metalsmith %{buildroot}%{_bindir}/metalsmith-3

%check
PYTHON=%{__python3} stestr-3 run

%files -n python3-%{sname}
%license LICENSE
%{_bindir}/metalsmith
%{_bindir}/metalsmith-3
%{python3_sitelib}/%{sname}
%{python3_sitelib}/%{sname}-*.egg-info
%exclude %{python3_sitelib}/%{sname}/test

%files -n python3-%{sname}-tests
%license LICENSE
%{python3_sitelib}/%{sname}/test

%if 0%{?with_doc}
%files -n python-%{sname}-doc
%license LICENSE
%doc doc/build/html README.rst
%endif

%files -n ansible-role-%{sname}-deployment
%license LICENSE
%doc README.rst
%{_datadir}/ansible/roles/metalsmith_deployment
%{_datadir}/ansible/plugins
%exclude %{_datadir}/ansible/roles/metalsmith_deployment/README.rst

%changelog

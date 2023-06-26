%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some runtime reqs from automatic generator
%global excluded_reqs ansible
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order ansible

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
License: Apache-2.0
URL: https://docs.openstack.org/metalsmith/latest/

Source0: http://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        http://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch: noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
BuildRequires: openstack-macros
%endif

%description
%{common_desc}

%package -n python3-%{sname}
Summary: %{common_summary}
Obsoletes: python2-%{sname} < %{version}-%{release}

BuildRequires: git-core
BuildRequires: openstack-macros
BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
BuildRequires: (python3dist(ansible) >= 2.6 or ansible-core >= 2.11)
BuildRequires: python3-sphinxcontrib-rsvgconverter

Requires(pre): shadow-utils

%description -n python3-%{sname}
%{common_desc}

%package -n python3-%{sname}-tests
Summary: metalsmith tests
Requires: python3-%{sname} = %{version}-%{release}
Requires: python3-mock
Requires: python3-testtools
Requires: (python3dist(ansible) >= 2.6 or ansible-core >= 2.11)

%description -n python3-%{sname}-tests
%{common_desc_tests}

%if 0%{?with_doc}
%package -n python-%{sname}-doc
Summary: %{common_summary} - documentation

%description -n python-%{sname}-doc
%{common_summary}

This package contains documentation.
%endif

%package -n ansible-role-%{sname}-deployment
Summary: %{common_summary} - ansible role

# The ansible role uses CLI which is currently provided by the Python 2
# package. Change this when the CLI is provided by the Python 3 package.
Requires: python3-%{sname} = %{version}-%{release}
Requires: (python3dist(ansible) >= 2.9 or ansible-core >= 2.11)
Requires: ansible-collections-openstack

%description -n ansible-role-%{sname}-deployment
%{common_summary}

This package contains the metalsmith_deployment role to use metalsmith
in ansible playbooks.

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{sname}-%{upstream_version} -S git


# remove shebangs and fix permissions
if [ -f metalsmith_ansible/ansible_plugins/modules/metalsmith_instances.py ]; then
  sed -i '1{/^#!/d}' metalsmith_ansible/ansible_plugins/modules/metalsmith_instances.py
  chmod u=rw,go=r metalsmith_ansible/ansible_plugins/modules/metalsmith_instances.py
fi


sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs};do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
# Exclude some bad-known runtime reqs
for pkg in %{excluded_reqs};do
  sed -i /^${pkg}.*/d doc/requirements.txt
done

%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%if 0%{?with_doc}
# generate html docs
%tox -e docs
# remove the sphinx-build-3 leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%pyproject_install

if [ ! -d %{buildroot}%{_datadir}/ansible/plugins ]; then
  mkdir -p %{buildroot}%{_datadir}/ansible/plugins
fi

# Create a versioned binary for backwards compatibility until everything is pure py3
ln -s metalsmith %{buildroot}%{_bindir}/metalsmith-3

%check
%tox -e %{default_toxenv}

%files -n python3-%{sname}
%license LICENSE
%{_bindir}/metalsmith
%{_bindir}/metalsmith-3
%{python3_sitelib}/%{sname}
%{python3_sitelib}/%{sname}-*.dist-info
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

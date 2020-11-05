# Copyright (c) 2020 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/

Name:           orthos2
Version:        0.1
Release:        0
Summary:        Machine administration
Url:            https://github.com/openSUSE/orthos2

Group:          Productivity/Networking/Boot/Servers
%{?systemd_ordering}

License:        GPL-2.0-or-later
Source:         orthos2-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  systemd-rpm-macros
# For /etc/nginx{,/conf.d} creation
BuildRequires:  nginx
BuildRequires:  python3-setuptools
BuildRequires:  python3-devel
%if 0%{?suse_version}
BuildRequires:  python-rpm-macros
%endif

# Finds python dependencies based on egg info generated by setup.py
# Theoretically distro independent and should work this way, but has
# quite some pitfalls. Only works after SLE 15 SP2, due to build service
# restrictions (be careful, there they messed it up and
# python_enable_dependency_generator macro is defined, but does not do
# anything. This check still also needs to explicitly check for SLE 15 SP2...
%if 0%{?sle_version} <= 150200
%undefine python_enable_dependency_generator
%undefine python_disable_dependency_generator
%endif
%{?python_enable_dependency_generator}
%if ! (%{defined python_enable_dependency_generator} || %{defined python_disable_dependency_generator})
Requires:  python3-django >= 3.1
Requires:  python3-django-extensions
Requires:  python3-django-auth-ldap
Requires:  python3-paramiko
Requires:  python3-djangorestframework
Requires:  python3-validators
Requires:  python3-netaddr
%endif
Requires:  nginx
Requires:  uwsgi
Requires:  uwsgi-python3
Requires:  /sbin/service

Provides: orthos2-%{version}-%{release}

%description
Orthos is the machine administration tool of the development network at SUSE. It is used for following tasks:

    getting the state of the machine
    overview about the hardware
    overview about the installed software (installations)
    reservation of the machines
    generating the DHCP configuration (via Cobbler)
    reboot the machines remotely
    managing remote (serial) consoles

%package client
Summary:        Command line client for orthos2
Requires:       python3-base
Requires:       python3-pytz

%description client
Command line client that provides a shell like command
line interface based on readline.

%prep
%setup

%build
%py3_build


%install
%py3_install


#systemd
%if 0%{?suse_version}
mkdir -p %{buildroot}%{_sbindir}
ln -sf service %{buildroot}%{_sbindir}/rcorthos2_taskmanager
ln -sf service %{buildroot}%{_sbindir}/rcorthos2
%endif
mkdir -p /%{buildroot}/srv/www/orthos2
# This should go into setup.py - but copying tons of non *.py files recursively
# is cumbersome...
cp -r orthos2/frontend/static /%{buildroot}/%{python3_sitelib}/orthos2/frontend
# ToDo: Try to separate the html templates somewhere else
cp -r templates/* /%{buildroot}/%{python3_sitelib}/orthos2
ln -sr %{buildroot}%{python3_sitelib}/orthos2 %{buildroot}/usr/lib/orthos2/orthos2
install -d /home/orthos/.ssh

%pre
getent group orthos >/dev/null || groupadd -r orthos
getent passwd orthos >/dev/null || \
    useradd -r -g orthos -d /home/orthos -s /sbin/nologin \
    -c "Useful comment about the purpose of this account" orthos
%service_add_pre orthos2.service orthos2_taskmanager.service orthos2.socket

%post
%tmpfiles_create %{_tmpfilesdir}/%{name}.conf
%service_add_post orthos2.service orthos2_taskmanager.service orthos2.socket


%preun
%service_del_preun  orthos2.service orthos2_taskmanager.service orthos2.socket

%postun
%service_del_postun  orthos2.service orthos2_taskmanager.service orthos2.socket


%files
%{python3_sitelib}/orthos2-*
%_unitdir/orthos2_taskmanager.service
%_unitdir/orthos2.service
%_unitdir/orthos2.socket
%if 0%{?suse_version}
%{_sbindir}/rcorthos2_taskmanager
%{_sbindir}/rcorthos2
%endif
%{_tmpfilesdir}/orthos2.conf
%dir %{python3_sitelib}/orthos2/
%{python3_sitelib}/orthos2/*
%dir %{_sysconfdir}/orthos2
%config %{_sysconfdir}/orthos2/orthos2.ini
%config %{_sysconfdir}/orthos2/settings
%config(noreplace) %{_sysconfdir}/nginx/conf.d/orthos2_nginx.conf
%dir /usr/share/orthos2
%dir /usr/lib/orthos2
/usr/share/orthos2/*
/usr/lib/orthos2/*
%attr(755,orthos,orthos) %dir /srv/www/orthos2
%ghost %dir /run/%{name}
%attr(755,orthos,orthos) %dir /var/log/orthos2
%attr(775,orthos,orthos) %dir /var/lib/orthos2
%attr(755,orthos,orthos) %dir /home/orthos
%attr(700,orthos,orthos) %dir /home/orthos/.ssh

%files client
%attr(755, root, root) /usr/bin/orthos2

%changelog
* Tue Sep 15 00:26:20 UTC 2020 - Thomas Renninger <trenn@suse.de>
- First submissions

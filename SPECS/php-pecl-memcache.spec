%if 0%{?scl:1}
%scl_package php-pecl-memcache
%endif

%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%{!?pecl_phpdir: %{expand: %%global pecl_phpdir  %(%{__pecl} config-get php_dir  2> /dev/null || echo undefined)}}
%{?!pecl_xmldir: %{expand: %%global pecl_xmldir %{pecl_phpdir}/.pkgxml}}

%define php_extdir %(%{_bindir}/php-config --extension-dir 2>/dev/null || echo %{_libdir}/php4)
#%{!?php_extdir: %{expand: %%global php_extdir %(%{_bindir}/php-config --extension-dir)}}
%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)


%global pecl_name memcache

Summary: Extension to work with the Memcached caching daemon
Name: %{?scl_prefix}php-pecl-memcache
Version: 3.0.8
Release: 2.ius%{?dist}
License: PHP
Group: Development/Languages
Vendor: IUS Community Project
URL: http://pecl.php.net/package/%{pecl_name}

Source: http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
Source2: xml2changelog

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: %{?scl_prefix}php-devel, %{?scl_prefix}php-cli, %{?scl_prefix}php-pear, zlib-devel
Provides: %{?scl_prefix}php-pecl(%{pecl_name}) = %{version}-%{release}
Requires(post): %{__pecl}
Requires(postun): %{__pecl}

%if %{?php_zend_api}0
Requires: %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires: %{?scl_prefix}php(api) = %{php_core_api}
%else
Requires: %{?scl_prefix}php-api = %{php_apiver}
%endif

%description
Memcached is a caching daemon designed especially for
dynamic web applications to decrease database load by
storing objects in memory.

This extension allows you to work with memcached through
handy OO and procedural interfaces.

Memcache can be used as a PHP session handler.

%prep 
%setup -c -n %{name}-%{version} -q
%{_bindir}/php -n %{SOURCE2} package.xml >CHANGELOG


%build
cd %{pecl_name}-%{version}
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
%{__make} %{?_smp_mflags}


%install
cd %{pecl_name}-%{version}
%{__rm} -rf %{buildroot}
%{__make} install INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
%{__mkdir_p} %{buildroot}%{_sysconfdir}/php.d
%{__cat} > %{buildroot}%{_sysconfdir}/php.d/%{pecl_name}.ini << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so

; Options for the %{pecl_name} module

; Whether to transparently failover to other servers on errors
;memcache.allow_failover=1
; Defines how many servers to try when setting and getting data.
;memcache.max_failover_attempts=20
; Data will be transferred in chunks of this size
;memcache.chunk_size=8192
; The default TCP port number to use when connecting to the memcached server 
;memcache.default_port=11211
; Hash function {crc32, fnv}
;memcache.hash_function=crc32
; Hash strategy {standard, consistent}
;memcache.hash_strategy=standard

; Options to use the memcache session handler

; Use memcache as a session handler
;session.save_handler=memcache
; Defines a comma separated of server urls to use for session storage
;session.save_path="tcp://localhost:11211?persistent=1&weight=1&timeout=1&retry_interval=15"
EOF

# Install XML package description
# use 'name' rather than 'pecl_name' to avoid conflict with pear extensions
%{__mkdir_p} %{buildroot}%{pecl_xmldir}
%{__install} -m 644 ../package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml


%clean
%{__rm} -rf %{buildroot}


%post
%{__pecl} install --nodeps --soft --force --register-only --nobuild %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ]; then
%{__pecl} uninstall --nodeps --ignore-errors --register-only %{pecl_name} >/dev/null || :
fi


%files
%defattr(-, root, root, -)
%doc CHANGELOG %{pecl_name}-%{version}/CREDITS %{pecl_name}-%{version}/README %{pecl_name}-%{version}/example.php
%config(noreplace) %{_sysconfdir}/php.d/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{pecl_name}.xml


%changelog
* Wed Jan 29 2014 Mark McKinstry <mmckinst@nexcess.net> - 3.0.8-2.ius
- convert to SCL style RPM
- give it the path to php-config

* Mon Apr 08 2013 Ben Harper <ben.harper@rackspace.com> - 0:3.0.8-1.ius
- Latest sources from upstream. Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=3.0.8

* Thu Nov 01 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.7-2.ius
- Rebuilding against internal 6.3.z

* Mon Sep 24 2012 Ben Harper <ben.harper@rackspace.com> - 0:3.0.7.ius
- Latest sources from upstream. Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=3.0.7

* Tue Aug 21 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.6-5.ius
- Rebuilding against php54-5.4.6-2.ius as it is now using bundled PCRE.

* Fri May 11 2012 Dustin Henry Offutt <dustin.offutt@rackspace.com> - 0:3.0.6-4.ius
- Building for PHP54

* Fri Aug 19 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.6-3.ius
- Rebuilding

* Fri Aug 12 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.6-2.ius
- Rebuilding with EL6 support

* Mon Apr 11 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.6-1.ius
- Latest sources from upstream. Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=3.0.6

* Fri Feb 11 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.5-1.ius
- Latest sources from upstream. Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=3.0.5
- Changed basever from 2.2 to 3

* Thu Feb 03 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:2.2.6-2.ius
- Removed Obsoletes: php53*

* Thu Dec 16 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:2.2.6-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=2.2.6
- Rename package as php53u-pecl-memcache. Resolves LP#691755
- Rebuild against php53u-5.3.4
- BuildRequires: php53u-cli 

* Mon Jul 27 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:2.2.5-2.ius
- Rebuild for php 5.3.3

* Tue Jun 22 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:2.2.5-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=2.2.5

* Fri Oct 16 2009 BJ Dierkes <wdierkes@rackspace.com> - 0.2.2.3-5.ius
- Repackaging for php53

* Wed Oct 14 2009 BJ Dierkes <wdierkes@rackspace.com> - 0:2.2.3-4.ius
- Repackaging for IUS
- Renaming to php52-pecl-memcache
- Removing Epoch version

* Mon Sep 28 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:2.2.3-3.3.rs
- Rebuilding against new php.

* Mon Sep 14 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:2.2.3-3.2.rs
- Upping Epoch version due to conflicts with EPEL pecl packages.

* Thu Jul 02 2009 BJ Dierkes <wdierkes@rackspace.com> - 2.2.3-3.1.rs
- Rebuild against php-5.2.10
 
* Thu May 07 2009 BJ Dierkes <wdierkes@rackspace.com> - 2.2.3-3.rs
- Rebuild against latest PHP.
    
* Fri Jan 23 2009 BJ Dierkes <wdierkes@rackspace.com> - 2.2.3-2.rs
- Fixing post/postun scripts to properly register with pecl.  Resolves
  Rackspace Bug [#1096].
- Adding php_ver_tag for different major PHP versions.
- Adding Vendor tag.

* Tue Jan 06 2009 BJ Dierkes <wdierkes@rackspace.com> - 2.2.3-1.1.rs
- Rebuild

* Sat Feb  9 2008 Remi Collet <Fedora@FamilleCollet.com> 2.2.3-1
- new version

* Thu Jan 10 2008 Remi Collet <Fedora@FamilleCollet.com> 2.2.2-1
- new version

* Thu Nov 01 2007 Remi Collet <Fedora@FamilleCollet.com> 2.2.1-1
- new version

* Sat Sep 22 2007 Remi Collet <Fedora@FamilleCollet.com> 2.2.0-1
- new version
- add new INI directives (hash_strategy + hash_function) to config
- add BR on php-devel >= 4.3.11 

* Mon Aug 20 2007 Remi Collet <Fedora@FamilleCollet.com> 2.1.2-1
- initial RPM


Name:		imsettings
Version:	0.108.0
Release:	3.4%{?dist}
License:	LGPLv2+
URL:		http://code.google.com/p/imsettings/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	desktop-file-utils
BuildRequires:	intltool gettext
BuildRequires:	libtool automake autoconf
BuildRequires:	dbus-devel >= 0.23, dbus-glib-devel >= 0.74, glib2 >= 2.16
BuildRequires:	libgxim-devel >= 0.3.1, libnotify-devel
%if !0%{?rhel}
BuildRequires:	xfconf-devel
%endif
BuildRequires:	GConf2-devel
BuildRequires:	libX11-devel
Source0:	http://imsettings.googlecode.com/files/%{name}-%{version}.tar.bz2
# workaround for KDE, it will be removed when we have a correct fix
Source1: 	imsettings-kde.sh
Patch0:		imsettings-constraint-of-language.patch
Patch1:		imsettings-disable-xim.patch
Patch2:		imsettings-none.conf-gtk-xim-default.patch
Patch3:		imsettings-fix-lxde-fail.patch
Patch4:		imsettings-no-restart-with-exit0.patch
Patch5:		imsettings-translation-updates.patch
Patch6:		imsettings-fix-race-on-popen.patch
Patch7:		imsettings-translation-updates2.patch

Summary:	Delivery framework for general Input Method configuration
Group:		Applications/System
Requires:	xorg-x11-xinit >= 1.0.2-22.fc8
Requires:	imsettings-libs = %{version}-%{release}
Requires(pre):	GConf2
Requires(post):	/bin/dbus-send %{_sbindir}/alternatives GConf2
Requires(preun):	GConf2
Requires(postun):	/bin/dbus-send %{_sbindir}/alternatives

%description
IMSettings is a framework that delivers Input Method
settings and applies the changes so they take effect
immediately without any need to restart applications
or the desktop.

This package contains the core DBus services and some utilities.

%package	libs
Summary:	Libraries for imsettings
Group:		Development/Libraries

%description	libs
IMSettings is a framework that delivers Input Method
settings and applies the changes so they take effect
immediately without any need to restart applications
or the desktop.

This package contains the shared library for imsettings.

%package	devel
Summary:	Development files for imsettings
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	pkgconfig
Requires:	glib2-devel >= 2.16.0
Requires:	dbus-glib-devel >= 0.74

%description	devel
IMSettings is a framework that delivers Input Method
settings and applies the changes so they take effect
immediately without any need to restart applications
or the desktop.

This package contains the development files to make any
applications with imsettings.

%if !0%{?rhel}
%package	xfce
Summary:	Xfce support on imsettings
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	im-chooser
Requires:	xfce4-settings >= 4.5.99.1-2

%description	xfce
IMSettings is a framework that delivers Input Method
settings and applies the changes so they take effect
immediately without any need to restart applications
or the desktop.

This package contains a plugin to get this working on Xfce.  

%package	lxde
Summary:	LXDE support on imsettings
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	lxde-settings-daemon

%description	lxde
IMSettings is a framework that delivers Input Method
settings and applies the changes so they take effect
immediately without any need to restart applications
or the desktop.

This package contains a helper program to get this working on LXDE.
%endif

%prep
%setup -q
%patch0 -p1 -b .0-lang
%patch1 -p1 -b .1-xim
%patch2 -p1 -b .2-xim
%patch3 -p0 -b .3-lxde
%patch4 -p0 -b .4-no-restart
%patch5 -p0 -b .5-translations
%patch6 -p0 -b .6-popen
%patch7 -p2 -b .7-translations2
autoreconf -Im4macros -f

%build
%configure	\
	--with-xinputsh=50-xinput.sh \
	--disable-static \
	--disable-schemas-install

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# change the file attributes
chmod 0755 $RPM_BUILD_ROOT%{_libexecdir}/xinputinfo.sh
chmod 0755 $RPM_BUILD_ROOT%{_sysconfdir}/X11/xinit/xinitrc.d/50-xinput.sh

# clean up the unnecessary files
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/xfce4/mcs-plugins/*.la
%if 0%{?rhel}
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/imsettings-xfce-helper.desktop
rm -f $RPM_BUILD_ROOT%{_bindir}/imsettings-xfce-helper
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/imsettings-lxde-helper.desktop
rm -f $RPM_BUILD_ROOT%{_bindir}/imsettings-lxde-helper
%endif

# still not stable
rm -f $RPM_BUILD_ROOT%{_datadir}/dbus-1/services/qt-im-settings-daemon.service
rm -f $RPM_BUILD_ROOT%{_libexecdir}/qt-im-settings-daemon

# workaround for KDE
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/kde/env
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/kde/env/

# disable running applet by default
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/imsettings-applet.desktop

#desktop-file-install						\
#	--delete-original					\
#	--dir=$RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart	\
#	$RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/imsettings-applet.desktop

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT


%pre
if [ "$1" -gt 1 ]; then
	export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
	if [ -f %{_sysconfdir}/gconf/schemas/imsettings-applet.schemas ]; then
		gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/imsettings-applet.schemas > /dev/null || :
	fi
fi

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/imsettings-applet.schemas > /dev/null || :
alternatives --install %{_sysconfdir}/X11/xinit/xinputrc xinputrc %{_sysconfdir}/X11/xinit/xinput.d/none.conf 10
alternatives --install %{_sysconfdir}/X11/xinit/xinputrc xinputrc %{_sysconfdir}/X11/xinit/xinput.d/xim.conf 30
dbus-send --system --type=method_call --dest=org.freedesktop.DBus / org.freedesktop.DBus.ReloadConfig > /dev/null 2>&1 || :

%preun
if [ "$1" -eq 0 ]; then
	export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
	gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/imsettings-applet.schemas > /dev/null || :
fi

%postun
if [ "$1" = 0 ]; then
	alternatives --remove xinputrc %{_sysconfdir}/X11/xinit/xinput.d/none.conf
	alternatives --remove xinputrc %{_sysconfdir}/X11/xinit/xinput.d/xim.conf
	dbus-send --system --type=method_call --dest=org.freedesktop.DBus / org.freedesktop.DBus.ReloadConfig > /dev/null 2>&1 || :
fi

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files	-f %{name}.lang
%defattr(-, root, root, -)
%doc AUTHORS COPYING ChangeLog NEWS README
%{_bindir}/imsettings-applet
%{_bindir}/imsettings-info
%{_bindir}/imsettings-list
%{_bindir}/imsettings-reload
%{_bindir}/imsettings-restart
%{_bindir}/imsettings-start
%{_bindir}/imsettings-stop
%{_bindir}/imsettings-xim
%{_libexecdir}/gconf-im-settings-daemon
%{_libexecdir}/im-settings-daemon
%{_libexecdir}/xinputinfo.sh
%{_datadir}/dbus-1/services/*.service
%{_datadir}/pixmaps/*.png
%{_sysconfdir}/X11/xinit/xinitrc.d/50-xinput.sh
%{_sysconfdir}/X11/xinit/xinput.d
%{_sysconfdir}/xdg/autostart/imsettings-start.desktop
%{_sysconfdir}/gconf/schemas/imsettings-applet.schemas
%{_sysconfdir}/kde/env/*.sh

%files	libs
%defattr(-, root, root, -)
%doc AUTHORS COPYING ChangeLog NEWS README
%{_libdir}/libimsettings.so.*
%{_libdir}/libimsettings-xim.so.*

%files	devel
%defattr(-, root, root, -)
%doc AUTHORS COPYING ChangeLog NEWS README
%{_includedir}/imsettings
%{_libdir}/libimsettings.so
%{_libdir}/libimsettings-xim.so
%{_libdir}/pkgconfig/imsettings.pc

%if !0%{?rhel}
%files	xfce
%defattr(-, root, root, -)
%doc AUTHORS COPYING ChangeLog NEWS README
%{_bindir}/imsettings-xfce-helper
%{_sysconfdir}/xdg/autostart/imsettings-xfce-helper.desktop

%files	lxde
%defattr(-, root, root, -)
%doc AUTHORS COPYING ChangeLog NEWS README
%{_bindir}/imsettings-lxde-helper
%{_sysconfdir}/xdg/autostart/imsettings-lxde-helper.desktop
%endif


%changelog
* Mon Jul 26 2010 Akira TAGOH <tagoh@redhat.com> - 0.108.0-3.4
- more translations update. (#589212)

* Fri Jun 25 2010 Akira TAGOH <tagoh@redhat.com> - 0.108.0-3.3
- Fix a segfault. (#607506)

* Fri May 21 2010 Bill Nottingham <notting@redhat.com> - 0.108.0-3.2
- don't use gconf macros (#593964)

* Wed May 19 2010 Akira TAGOH <tagoh@redhat.com> - 0.108.0-3.1
- Translation updates. (#589212)

* Tue May 18 2010 Akira TAGOH <tagoh@redhat.com> - 0.108.0-3
- Don't restart the IM process when the exit status is 0.

* Thu Apr 15 2010 Akira TAGOH <tagoh@redhat.com> - 0.108.0-2
- Fix issue the invocation of IM always fails in the internal status. (#582448)
- Add imsettings-lxde subpackage.

* Tue Mar 23 2010 Akira TAGOH <tagoh@redhat.com> - 0.108.0-1
- New upstream release.
- Fix the abort issue. (#570462)
- clean up the unnecessary patches.

* Tue Feb 16 2010 Akira TAGOH <tagoh@redhat.com> - 0.107.4-8
- Fix a segfault issue when /bin/sh points to non-bash shell. (#553680)

* Tue Feb  9 2010 Akira TAGOH <tagoh@redhat.com> - 0.107.4-7
- Add -lX11 to avoid DSO issue.

* Fri Feb  5 2010 Akira TAGOH <tagoh@redhat.com> - 0.107.4-6
- Fix an abort issue on GConf backend. (#543005)

* Mon Jan  4 2010 Akira TAGOH <tagoh@redhat.com> - 0.107.4-5
- Fix an abort issue. (#530357)

* Tue Nov 24 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.4-4
- Fix a segfault issue on XFCE desktop. (#540062)

* Mon Nov  2 2009 Jens Petersen <petersen@redhat.com> - 0.107.4-3
- none.conf: default GTK to xim if available like qt does to fix
  current missing X locale compose for gtk and X (#505100)

* Fri Oct 16 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.4-2
- Run IM for Maithili by default. (#529144)

* Mon Sep 28 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.4-1
- New upstream release.
  - Update the translations.
  - Remove the unnecessary patches:
    - imsettings-unref-notify.patch
    - imsettings-unref-later.patch
    - imsettings-update-info.patch
    - imsettings-close-fd.patch

* Thu Sep 17 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.3-5
- Fix taking too much CPU issue.

* Tue Sep 15 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.3-4
- Update the IM information as needed if the configuration file is written
  in the script. (#523349)

* Fri Sep 11 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.3-3
- Fix keeping IM process running as the defunct process. (#522689)

* Tue Sep  8 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.3-2
- Fix aborting after dbus session closed. (#520976)

* Tue Sep  1 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.3-1
- New upstream release.
  - Fix taking CPU load after switching IM.
  - Fix getting stuck after starting some IM.

* Mon Aug 31 2009 Akira TAGOH <tagoh@redhat.com>
- Add a conditional build to disable xfce module for RHEL.

* Thu Aug 27 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.2-1
- New upstream release.
  - Stop IM process properly with the DBus disconnect signal. (#518970)
  - Update the translation. (#517679)

* Fri Aug 14 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.1-2
- export the certain environment variables.

* Fri Aug 14 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.1-1
- New upstream release.
  - Fix memory leaks.

* Wed Aug 12 2009 Akira TAGOH <tagoh@redhat.com> - 0.107.0-1
- New upstream release.
  - Pop up an error if failed to invoke IM. (#497946)
  - Fix the duplicate recommendation message issue. (#514852)

* Thu Jul 27 2009 Akira TAGOH <tagoh@redhat.com> - 0.106.2-5
- Support immodule only configuration file.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.106.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 23 2009 Akira TAGOH <tagoh@redhat.com> - 0.106.2-3
- Support immodule only configuration file.

* Mon Apr 13 2009 Akira TAGOH <tagoh@redhat.com> - 0.106.2-2
- Disable applet by default.

* Tue Apr  7 2009 Akira TAGOH <tagoh@redhat.com> - 0.106.2-1
- New upstream release.
  - Fix a freeze issue on X applications with switching IM (#488877)
  - Fix a segfault issue with switching IM (#488899)
  - Fix not creating .xinputrc with disabiling IM first time (#490587)
  - Invoke IM for certain locales. (#493406)

* Wed Mar 18 2009 Akira TAGOH <tagoh@redhat.com> - 0.106.1-2
- Fix XIM-related issues.
- Fix a parser error during reading Compose data. (#484142)
- Get rid of more debugging messages.

* Tue Mar 10 2009 Akira TAGOH <tagoh@redhat.com> - 0.106.1-1
- New upstream release.
  - Fix a double-free issue. (#485595)
  - Workaround to get the accelerator keys working on X apps. (#488713)
  - Get rid of debugging messages (#489119)

* Mon Feb 23 2009 Akira TAGOH <tagoh@redhat.com> - 0.106.0-1
- New upstream release.
  - Fix a parser error for Compose data. (#484142)
  - Allow a lowername or .conf name for IM name. (#471833)
  - Add Xfconf support. (#478669)
- Remove unnecessary autostart files anymore. (#475907)

* Tue Oct 28 2008 Akira TAGOH <tagoh@redhat.com> - 0.105.1-3
- imsettings-fix-registertriggerkeys.patch: Fix to send
  XIM_REGISTER_TRIGGERKEYS anyway. (#468833)

* Mon Oct 27 2008 Akira TAGOH <tagoh@redhat.com> - 0.105.1-2
- imsettings-fix-unpredictable-session-order.patch: Run imsettings-applet with
  --disable-xsettings for GNOME/XFCE. (#466206)

* Thu Oct 23 2008 Akira TAGOH <tagoh@redhat.com> - 0.105.1-1
- New upstream release.
  - Fix another freeze issue. (#452849)
- imsettings-r210.patch: removed.

* Tue Oct 21 2008 Akira TAGOH <tagoh@redhat.com> - 0.105.0-4
- Read %%{_sysconfdir}/X11/xinput.d/none.conf for non-CJKI locales to make
  consistency in the status on im-chooser. so it would /disables/ IM regardless
  of what the kind of locales you use and what the kind of IM you installed.
  NOTE: if you can't input any characters with GTK+ application, you may
  implicitly use the different buiit-in immodule. you can modify none.conf to
  get the right thing then.
- imsettings-r210.patch: backport to allow starting none without warnings.

* Fri Oct 17 2008 Than Ngo <than@redhat.com> 0.105.0-3
- readd the workaround for KDE

* Tue Oct 14 2008 Than Ngo <than@redhat.com> 0.105.0-2
- get rid of workaround for KDE

* Tue Oct 14 2008 Akira TAGOH <tagoh@redhat.com> - 0.105.0-1
- New upstream release.
  - Have a workaround for the race condition issue. (#452849)
  - Fix a freeze issue with ibus. (#465431)
  - Fix a freeze issue on Desktops not supporting XSETTINGS.

* Wed Oct 01 2008 Than Ngo <than@redhat.com> 0.104.1-3
- add workaround for KDE

* Mon Sep 29 2008 Akira TAGOH <tagoh@redhat.com> - 0.104.1-2
- Fix a gconf error in %%pre. (#464453)

* Thu Sep 25 2008 Akira TAGOH <tagoh@redhat.com> - 0.104.1-1
- New upstream release.
  - Fix a segfault issue. (#462899)
  - Suppress the unnecessary notification. (#463797)
  - Add .schemas file missing. real fix of #460703.

* Wed Sep 17 2008 Akira TAGOH <tagoh@redhat.com> - 0.104.0-1
- New upstream release.
  - Fix deadkey issue under XIM. (#457901)
  - Correct .desktop file for imsettings-applet (#460695)
  - Hide a status icon by default. (#460703)

* Fri Aug 29 2008 Akira TAGOH <tagoh@redhat.com> - 0.103.0-1
- New upstream release.
  - im-xsettings-daemon doesn't run automatically. (#459443)
- Enable XIM support again. (#457635)
- BR: libgxim-devel and libnotify-devel

* Tue Jul 29 2008 Akira TAGOH <tagoh@redhat.com> - 0.102.0-1
- New upstream release.
  - Fix no recommendation updated. (#455363)
  - Work on WMs not own/bring up XSETTINGS manager. (#455228)

* Tue Jul  8 2008 Akira TAGOH <tagoh@redhat.com> - 0.101.3-2
- rebuild.

* Thu Jul  3 2008 Akira TAGOH <tagoh@redhat.com> - 0.101.3-1
- New upstream release.
  - Use the system-wide xinputrc if .xinputrc is a dangling
    symlink. (#453358)

* Thu Jun 26 2008 Akira TAGOH <tagoh@redhat.com> - 0.101.2-3
- Disable XIM support so far. (#452849, #452870)

* Wed Jun 18 2008 Akira TAGOH <tagoh@redhat.com> - 0.101.2-2
- Backport patch from upstream to solve issues.
  - always saying IM is running when no .xinputrc.
  - workaround for a delay of that IM is ready for XIM.

* Tue Jun 17 2008 Akira TAGOH <tagoh@redhat.com> - 0.101.2-1
- New upstream release.
  - Fix a typo in the help message. (#451739)
  - Fix a invalid memory access. (#451753)

* Mon Jun 16 2008 Akira TAGOH <tagoh@redhat.com> - 0.101.1-2
- Add Reqruies: glib2-devel, dbus-glib-devel to -devel.

* Thu Jun 12 2008 Akira TAGOH <tagoh@redhat.com> - 0.101.1-1
- New upstream release.
- Add Requires pkgconfig to -devel.

* Wed Jun 11 2008 Akira TAGOH <tagoh@redhat.com> - 0.101.0-1
- New upstream release.
- Add Requires alternatives for %%post and %%postun.
- Improve summary.
- Remove imsettings-reload from %%post and %%postun. these are
  no longer needed.

* Wed Jun  4 2008 Akira TAGOH <tagoh@redhat.com> - 0.100.0-1
- Initial package.


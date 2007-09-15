%define docver  2.4
%define dirver  2.4

%define lib_major	%{dirver}
%define lib_name_orig	libpython
%define lib_name	%mklibname python %{lib_major}

Summary:	An interpreted, interactive object-oriented programming language
Name:		python2.4
Version:	2.4.4
Release:	%mkrel 5
License:	Modified CNRI Open Source License
Group:		Development/Python

Source:		http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.bz2
Source1:	http://www.python.org/ftp/python/doc/%{docver}/html-%{docver}.tar.bz2
Source2:	python-2.4-base.list
Source3:	exclude.py
Source4:	python-mode-1.0.tar.bz2

# Don't include /usr/local/* in search path
Patch3:		Python-2.3-no-local-incpath.patch.bz2

# Support */lib64 convention on x86_64, sparc64, etc.
Patch4:		Python-2.4.4-lib64.patch

# Do handle <asm-XXX/*.h> headers in h2py.py
# FIXME: incomplete for proper bi-arch support as #if/#else/#endif
# clauses generally should have been handled
Patch5:		Python-2.2.2-biarch-headers.patch.bz2

# detect and link with gdbm_compat for dbm module
Patch6:		Python-2.4.1-gdbm.patch.bz2

Patch7:     python-2.4.3-fix-buffer_overflow_with_glibc2.3.5.diff
Patch8:     python-2.4.4-parallel.patch
URL:		http://www.python.org/
Icon:		python-logo.xpm
Conflicts:	tkinter < %{version}
Requires:	%{lib_name} = %{version}
Requires:	%{name}-base = %{version}
BuildRequires:	XFree86-devel 
BuildRequires:	blt
BuildRequires:	db2-devel, db4-devel
BuildRequires:	emacs-bin
BuildRequires:	expat-devel
BuildRequires:	gdbm-devel 
BuildRequires:	gmp-devel
BuildRequires:	ncurses-devel 
BuildRequires:	openssl-devel 
BuildRequires:	readline-devel 
BuildRequires:	termcap-devel
BuildRequires:	tcl tcl-devel
BuildRequires:	tk tk-devel
BuildRequires:	tcl tk tix
BuildRequires:	tix
BuildRequires:	autoconf2.5
BuildRequires:  bzip2-devel
Provides:       python = %{version}-%{release}
Buildroot:	%{_tmppath}/%{name}-%{version}

%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that
need a programmable interface. This package contains most of the
standard Python modules, as well as modules for interfacing to the
Tix widget set for Tk and RPM.

Note that documentation for Python is provided in the python-docs
package.

%package -n	%{lib_name}
Summary:	Shared libraries for Python %{version}
Group:		System/Libraries
Requires(post):		/sbin/ldconfig
Requires(postun):	/sbin/ldconfig

%description -n	%{lib_name}
This packages contains Python shared object library.  Python is an
interpreted, interactive, object-oriented programming language often
compared to Tcl, Perl, Scheme or Java.

%package -n	%{lib_name}-devel
Summary:	The libraries and header files needed for Python development
Group:		Development/Python
Icon:		python-devel-logo.xpm
Requires:	%{name} = %version
Requires:	%{lib_name} = %{version}
Obsoletes:	%{name}-devel
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{lib_name_orig}-devel = %{version}-%{release}
Provides:	python-devel = %{version}-%{release}

%description -n	%{lib_name}-devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install %{lib_name}-devel if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%package	docs
Summary:	Documentation for the Python programming language
Icon:		python-docs-logo.xpm
Requires:	python = %version
Group:		Development/Python

%description	docs
The python-docs package contains documentation on the Python
programming language and interpreter.  The documentation is provided
in ASCII text files and in LaTeX source files.

Install the python-docs package if you'd like to use the documentation
for the Python language.

%package -n	tkinter2.4
Summary:	A graphical user interface for the Python scripting language
Group:		Development/Python
Icon:		python-tkinter-logo.xpm
Requires:	%{name} = %version
Requires:   tcl tk

%description -n	tkinter2.4
The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.

%package	base
Summary:	Python base files
Group:		Development/Python
Requires:	%{lib_name} = %{version}

%description	base
This packages contains the Python part that is used by the base packages
of a Mandriva Linux distribution.

%prep
%setup -q -n Python-%{version}
# local include
%patch3 -p1 
# lib64
%patch4 -p1
# biarch header
%patch5 -p1
# gdbm 
%patch6 -p1 
# fix some crash du to a buffer overflow
%patch7 -p0
# allow parallel usage with main python
%patch8 -p1
autoconf

mkdir html
bzcat %{SOURCE1} | tar x  -C html

find . -type f -print0 | xargs -0 perl -p -i -e 's@/usr/local/bin/python@/usr/bin/python@'

tar --strip-components=1 -xjf %{SOURCE4} -C Misc   

%build
rm -f Modules/Setup.local
cat > Modules/Setup.local << EOF
linuxaudiodev linuxaudiodev.c
EOF

OPT="$RPM_OPT_FLAGS -g"
export OPT
%configure2_5x \
    --with-threads \
    --with-cycle-gc \
    --with-cxx=g++ \
    --without-libdb \
    --enable-ipv6 \
    --enable-shared

# fix build
perl -pi -e 's/^(LDFLAGS=.*)/$1 -lstdc++/' Makefile
# (misc) if the home is nfs mounted, rmdir fails due to delay
export TMP="/tmp" TMPDIR="/tmp"
%make

%check
# (misc) if the home is nfs mounted, rmdir fails
export TMP="/tmp" TMPDIR="/tmp"
# all tests must pass
# (misc) test_minidom is not working for the moment
# tested on 2.4.1 (mdk), on ubuntu, on debian, on freebsd and gentoo
# should be reenabled for 2.4.3
TESTOPTS="-l -x test_linuxaudiodev -x test_nis -x test_minidom -x test_socket"
%ifarch x86_64
TESTOPTS="$TESTOPTS  -x test_pwd"
%endif
make test TESTOPTS="$TESTOPTS"

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_prefix}

# fix Makefile to get rid of reference to distcc
perl -pi -e "/^CC=/ and s/distcc/gcc/" Makefile

# set the install path
echo '[install_scripts]' >setup.cfg
echo 'install_dir='"%{buildroot}/usr/bin" >>setup.cfg

# python is not GNU and does not know fsstd
mkdir -p %{buildroot}%{_mandir}
%makeinstall_std

# remove unversioned binary
rm -f %{buildroot}%{_bindir}/python
mv %{buildroot}%{_bindir}/pydoc %{buildroot}%{_bindir}/pydoc2.4
mv %{buildroot}%{_bindir}/idle %{buildroot}%{_bindir}/idle2.4

(cd %{buildroot}%{_libdir}; ln -sf libpython%{lib_major}.so.* libpython%{lib_major}.so)

# Provide a libpython%{dirver}.so symlink in /usr/lib/puthon*/config, so that
# the shared library could be found when -L/usr/lib/python*/config is specified
(cd %{buildroot}%{_libdir}/python%{dirver}/config; ln -sf ../../libpython%{lib_major}.so .)

# emacs, I use it, I want it
mkdir -p %{buildroot}%{_datadir}/emacs/site-lisp
install -m 644 Misc/python-mode.el %{buildroot}%{_datadir}/emacs/site-lisp/python2.4-mode.el
emacs -batch -f batch-byte-compile %{buildroot}%{_datadir}/emacs/site-lisp/python2.4-mode.el

install -d %{buildroot}%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
(setq auto-mode-alist (cons '("\\\\.py$" . python-mode) auto-mode-alist))
(autoload 'python-mode "python-mode" "Mode for python files." t)
EOF

# smtpd proxy
mv -f %{buildroot}%{_bindir}/smtpd.py %{buildroot}%{_libdir}/python%{dirver}/

# modulator
cat << EOF > %{buildroot}%{_bindir}/modulator2.4
#!/bin/bash
exec %{_libdir}/python%{dirver}/site-packages/modulator/modulator.py
EOF
cp -r Tools/modulator %{buildroot}%{_libdir}/python%{dirver}/site-packages/

# pynche
cat << EOF > %{buildroot}%{_bindir}/pynche2.4
#!/bin/bash
exec %{_libdir}/python%{dirver}/site-packages/pynche/pynche
EOF
rm -f Tools/pynche/*.pyw
cp -r Tools/pynche %{buildroot}%{_libdir}/python%{dirver}/site-packages/

chmod 755 %{buildroot}%{_bindir}/{idle,modulator,pynche}2.4

ln -f Tools/modulator/README Tools/modulator/README.modulator
ln -f Tools/pynche/README Tools/pynche/README.pynche

rm -f modules-list.full
for n in %{buildroot}%{_libdir}/python%{dirver}/*; do
  [ -d $n ] || echo $n
done >> modules-list.full

for mod in %{buildroot}%{_libdir}/python%{dirver}/lib-dynload/* ; do
  [ `basename $mod` = _tkinter.so ] || echo $mod
done >> modules-list.full
sed -e "s|%{buildroot}||g" < modules-list.full > modules-list


mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-tkinter.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=IDLE
Comment=IDE for Python
Exec=%{_bindir}/idle2.4
Icon=development_environment_section
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Development-DevelopmentEnvironments;Development;IDE;
EOF


cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}-docs.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=Python documentation
Comment=Python complete reference
Exec=%{_bindir}/www-browser %_defaultdocdir/%{name}-docs-%{version}/index.html
Icon=documentation_section
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Documentation;
EOF

rm -f include.list main.list
sed 's@%%{_libdir}@%{_libdir}@' < %{SOURCE2} > include.list
cat >> modules-list << EOF
%{_bindir}/python2.4
%{_bindir}/pydoc2.4
%{_mandir}/man1/python*
%{_libdir}/python*/bsddb/
%{_libdir}/python*/curses/
%{_libdir}/python*/distutils/
%{_libdir}/python*/encodings/*
%{_libdir}/python*/lib-old/
%{_libdir}/python*/logging/
%{_libdir}/python*/xml/
%{_libdir}/python*/compiler/
%{_libdir}/python*/email/
%{_libdir}/python*/hotshot/
%{_libdir}/python*/site-packages/README
%{_libdir}/python*/plat-linux2/
%{_datadir}/emacs/site-lisp/python2.4-mode.el*
EOF

LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}%{_bindir}/python2.4 %{SOURCE3} %{buildroot} include.list modules-list > main.list

# fix non real scripts
chmod 644 %{buildroot}%{_libdir}/python*/test/test_{binascii,grp,htmlparser}.py*
# fix python library not stripped
chmod u+w %{buildroot}%{_libdir}/libpython2.4.so.1.0


mkdir -p %{buildroot}%{_sysconfdir}/profile.d/

cat > %{buildroot}%{_sysconfdir}/profile.d/python2.4.sh << EOF
#!/bin/sh
if [ -f \$HOME/.python2.4rc.py ] ; then
	export PYTHONSTARTUP=\$HOME/.python2.4rc.py
else
	export PYTHONSTARTUP=/etc/python2.4rc.py
fi
	
EOF

cat > %{buildroot}/%{_sysconfdir}/profile.d/python2.4.csh << EOF
if ( -f \${HOME}/.python2.4rc.py ) then
	setenv PYTHONSTARTUP \${HOME}/.python2.4rc.py
else
	setenv PYTHONSTARTUP /etc/python2.4rc.py
endif

EOF

cat >  %{buildroot}%{_sysconfdir}/python2.4rc.py << EOF
try:
    # this add completion to python interpreter
    import readline
    import rlcompleter
    # see readline man page for this
    readline.parse_and_bind("set show-all-if-ambiguous on")
    readline.parse_and_bind("tab: complete")
except:
    pass
# you can place a file .python2.4rc.py in your home to overrides this one
# but then, this file will not be sourced
EOF

chmod ugo+rx %{buildroot}%{_sysconfdir}/profile.d/*

cat > README.mdv << EOF
Python interpreter support readline completion by default.
This is only used with the interpreter. In order to remove it,
you can :
1) unset PYTHONSTARTUP when you login
2) create a empty file $HOME/.pythonrc.py
3) change /etc/pythonrc.py
EOF

%multiarch_includes %{buildroot}/usr/include/python*/pyconfig.h

%clean
rm -rf %{buildroot}
rm -f modules-list main.list

%files -f main.list
%defattr(-,root,root)
%doc README.mdv
%dir %{_libdir}/python*/lib-dynload
%dir %{_libdir}/python*/site-packages
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/%{name}.el
%{_sysconfdir}/profile.d/python2.4.*
%config(noreplace) %{_sysconfdir}/python2.4rc.py

%files -n %{lib_name}
%defattr(-,root,root)
%{_libdir}/libpython*.so.1*

%files -n %{lib_name}-devel
%defattr(-,root,root)
%{_libdir}/libpython*.so
%dir %{_includedir}/python*
%multiarch %multiarch_includedir/python*/pyconfig.h
%{_includedir}/python*/*
%{_libdir}/python*/config/
%{_libdir}/python*/test/


%files docs
%defattr(-,root,root)
%doc html/*/*
%{_datadir}/applications/mandriva-%{name}-docs.desktop

%files -n tkinter2.4
%defattr(-,root,root)
%dir %{_libdir}/python*/lib-tk
%{_libdir}/python*/lib-tk/*.py*
%{_libdir}/python*/lib-dynload/_tkinter.so
%{_libdir}/python*/idlelib
%{_libdir}/python*/site-packages/modulator
%{_libdir}/python*/site-packages/pynche
%{_bindir}/idle2.4
%{_bindir}/pynche2.4
%{_bindir}/modulator2.4
%{_datadir}/applications/mandriva-tkinter.desktop

%files base -f include.list
%defattr(-,root,root)
%dir %{_libdir}/python*

%post -n %{lib_name} -p /sbin/ldconfig
%postun -n %{lib_name} -p /sbin/ldconfig

%post -n tkinter2.4
%update_menus

%postun -n tkinter2.4
%clean_menus


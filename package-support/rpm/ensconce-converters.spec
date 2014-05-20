# NOTE: On CentOS 5.x you must have the buildsys-macros package installed in order
# for these conditionals to work correctly.
%if 0%{?rhel}
%if 0%{?el5}
# Define a new basename for python (also is assumed to be prefix for the python packages)
%define __python_pkgname python26
%define __python_exe python2.6
# Override the global %{__python} macro to point to our own python version
%define __python %{_bindir}/%{__python_exe}
# Specify the distribute package to use
%define setuptools_package python26-distribute
%else
# We are assuming EL6 (<EL5 is not supported)
%define __python_exe python
%define __python_pkgname python
%define setuptools_package python-setuptools
%endif
%else
# We are assuming fedora
%define __python_exe python
%define __python_pkgname python
%define setuptools_package python-setuptools
%endif


# This is the "package name" that we use in naming the /etc, /var/run, /var/log, subdirs.
%define PACKAGE ensconce-converters

# This is the directory where we will install a Python virtual environment.
%define venvdir /opt/%{PACKAGE}/env

# This is the top-level directory for the application.  (It matches the directory
# of the virtual environment in this case.)
%define packagedir /opt/%{PACKAGE}

# This is the directory (in /etc/) where we will keep configuration files.
%define configdir %{_sysconfdir}/ensconce-converters

# some systems dont have initrddir defined -- it seems that CentOS may be one of them (?)
%{?_initrddir:%define _initrddir /etc/rc.d/init.d}


### Abstract ###

Name:           ensconce-converters
Version:        %{version}
Release:        %{release}
Epoch:          %{epoch}
Summary:        Conversion utilities for Ensconce GPG/YAML export files.
Group:          Applications/System

### Requirements ###

# It is critical to disable the automagical requirements gathering!  Without this
# rpmbuild will look at all the binary files we're bundling (like python) and add these
# as requirements.  (This breaks things.)
AutoReqProv:		0

# These are the requirements for installing the RPM.
Requires:	      %{__python_pkgname} >= 2.6
Requires:			  gnupg

### Source ###

# This probably needs to be GPL due to included keepassdb library license.
License:        	GPL

# This needs to match the actual file that will be dropped in
Source:  %{name}-%{version}.tar.gz

### Build Configuration ###

# This is the conventional uniquely named build-root that Fedora recommends.
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# This is a binary build, since we are putting a bunch of compiled stuff into the virtual environment.
# (But let the host choose the architecture, please.)
# BuildArch:      i386

# On Fedora we will just assert that the python-* packages are installed.
BuildRequires:  %{__python_pkgname}-devel, %{setuptools_package}, %{__python_pkgname}-virtualenv

%description
ensconce-converters is a set of utilities to converts the Ensconce GPG YAML export to various
formats, such as Keepass 1.x DB file (KDB).

# -------------------------------------------------------------------
# Preparation
# -------------------------------------------------------------------
# The %setup macro is basically a "tar zxvf" shortcut; this is convention for RPMs
#
%prep
%setup -q

# -------------------------------------------------------------------
# Build
# -------------------------------------------------------------------
# The build step actually builds the project; this is a little less relevant for Python, though
# we'll skip the build in the %%install section (by passing --skip-build to python setup.py install)
#
%build

# We do this with the virtualenv python now.
#%{__python} setup.py build

# -------------------------------------------------------------------
# Install
# -------------------------------------------------------------------
# This %%install scriptlet is the code that installs the build package into the temporary location.  This is NOT code that
# runs when installing the RPM on a target system; this is only relevant for the build process.
#
%install
%{__rm} -rf %{buildroot}


# Create all the needed directories:
%{__mkdir} -p %{buildroot}%{_bindir}
%{__mkdir} -p %{buildroot}%{packagedir}

#%{__mkdir} -p %{buildroot}%{configdir}
#%{__mkdir} -p %{buildroot}%{_localstatedir}/lib/%{PACKAGE}
#%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{PACKAGE}
#%{__mkdir} -p %{buildroot}%{_localstatedir}/tmp/%{PACKAGE}

#touch %{buildroot}%{_localstatedir}/log/%{PACKAGE}/application.log
#touch %{buildroot}%{_localstatedir}/log/%{PACKAGE}/startup.log

#%{__mkdir} -p %{buildroot}%{_localstatedir}/run/%{PACKAGE}

# Copy in the pavement.py since we use this for utility scripts later.
%{__mv} pavement.py %{buildroot}%{packagedir}

# Create a virtual environment for this application
%{__python} -m virtualenv --distribute %{buildroot}%{venvdir}

# Remove the lib64 symlink that was added by virtualenv and replace with a non-absolute-path symlink
# (This only applies to builds on x86_64 arch.)

if [ -h "%{buildroot}%{venvdir}/lib64" ]
then
    rm %{buildroot}%{venvdir}/lib64
    ln -s lib %{buildroot}%{venvdir}/lib64
fi

# Define a new macro to refer to our virtualenv python
%define __venv_python %{buildroot}%{venvdir}/bin/%{__python_exe}

# This was moved from the %%build phase, since it appears to work better (or "at all")
# with the venv python.  We probably don't need to have this be a separate command, anymore.
%{__venv_python} setup.py build

# Use our newly installed virtualenv python to install the package (and dependencies)
# Note: this part will probably require that the user has an HTTP connection (to fetch deps).
%{__venv_python} setup.py install --skip-build

# Fix the incorrect absolute path that will exist in files in venv bin directory.
# (virtualenv sticks absolute paths in shebang headers and in the contents of the activate_this.py)
for file in %{buildroot}%{venvdir}/bin/*
do
	if [ "`basename $file`" != "python" ] && [ "`basename $file`" != "%{__python}" ]
	then
		%{__sed} -i -e "s|%{buildroot}%{venvdir}|%{venvdir}|" $file
	fi
done

# Do the same thing in the EGG-INFO/scripts dirs.
for file in %{buildroot}%{venvdir}/lib/python*/site-packages/*/EGG-INFO/scripts/*
do
	%{__sed} -i -e "s|%{buildroot}%{venvdir}|%{venvdir}|" $file
done


# And the setuptools.pth file
#%{__sed} -i -e "s|%{buildroot}%{venvdir}|%{venvdir}|"  %{buildroot}%{venvdir}/lib/python*/site-packages/setuptools.pth

# Recompile the pyc files, using our final %{venvdir} as the root (rather than the current build dir)
%{__venv_python} -c 'from compileall import *; compile_dir("%{buildroot}%{venvdir}", maxlevels=20, ddir="%{venvdir}", force=True)'

# Remove all installed dependency_links.txt files, since these may contain URLs we don't want to leak.
find %{buildroot}%{venvdir} -name "dependency_links.txt" -exec rm {} \;

# Install non-Python files into the right places
#%{__install} %{SOURCE1} %{buildroot}%{_initrddir}/ensconce-converters
#%{__install} %{SOURCE2} %{buildroot}%{configdir}
#%{__install} %{SOURCE3} %{buildroot}%{configdir}
#%{__install} %{SOURCE4} %{buildroot}%{configdir}
#%{__install} %{SOURCE5} %{buildroot}%{packagedir}

# Symlink any script.
# (Note that we're deliberately creating a broken symlink at this point.)
ln -s %{venvdir}/bin/ensconce2keepass %{buildroot}%{_bindir}/ensconce2keepass


# -------------------------------------------------------------------
# Cleanup Routine
# -------------------------------------------------------------------
%clean
rm -rf %{buildroot}

# -------------------------------------------------------------------
# The files that should be included in RPM
# -------------------------------------------------------------------
#
# The %files section needs to list all of the files, with their final
# resulting absolute paths (not the path to the temporary location where
# they were put by %%install).

%files
# By default chown everything root:root
%defattr(-,root,root,-)

# the /etc/ensconce-converters/*.cfg files are config files & should not be overwritten
#%config(noreplace) %{configdir}/settings.cfg
#%config(noreplace) %{configdir}/logging.cfg

# Include the entire contents of %{packagedir}
%{packagedir}/

# And our symlink in _bindir
%{_bindir}/


%changelog
* Tue Feb 09 2013 HL 0.1.0-1
- Initial Version

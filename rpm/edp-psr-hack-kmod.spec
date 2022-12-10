%global buildforkernels akmod
%global debug_package %{nil}

%global _name edp-psr-hack

Name:           %{_name}-kmod
Version:        1.0
Release:        2%{?dist}
Summary:        Kernel module for force enabling PSR on internal eDP displays

License:        GPLv2+
URL:            https://github.com/chenxiaolong/edp-psr-hack
Source0:        https://github.com/chenxiaolong/edp-psr-hack/archive/v%{version}.tar.gz

BuildRequires:  kmodtool

%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
edp-psr-hack is a hacky kernel module to force enable PSR (panel self refresh)
for the laptop's eDP display when the only reason it's disabled is because the
reported PSR setup time from DPCD exceeds the vblank time minus one line.

This package contains the kernel module for kernel %{kversion}.


%package common
Summary:        Common files for the edp-psr-hack kernel module
BuildArch:      noarch

%description common
This package contains the common files (license, documentation, etc.) for the
edp-psr-hack kernel module as well as a config to load the module by default on
boot.


%prep
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c

for kernel_version in %{?kernel_versions}; do
  cp -a %{_name}-%{version} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    make V=1 %{?_smp_mflags} \
        -C ${kernel_version##*___} \
        M=${PWD}/_kmod_build_${kernel_version%%___*} \
        modules
done


%install
for kernel_version in %{?kernel_versions}; do
    install -D -m 755 _kmod_build_${kernel_version%%___*}/%{_name}.ko \
        %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/%{_name}.ko
done

# Load the module by default
install -d -m 755 %{buildroot}%{_modulesloaddir}
echo %{_name} > %{buildroot}%{_modulesloaddir}/%{_name}.conf

%{?akmod_install}


%files common
%license %{_name}-%{version}/LICENSE
%doc %{_name}-%{version}/README.md
%_modulesloaddir/%{_name}.conf


%changelog
* Fri Dec 9 2022 Andrew Gunnerson <accounts+fedora@chiller3.com> - 1.0-2
- Fix directory structure for Github-generated tarballs
- Mark LICENSE as license instead of documentation

* Fri Dec 9 2022 Andrew Gunnerson <accounts+fedora@chiller3.com> - 1.0-1
- Initial release

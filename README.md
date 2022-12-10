# edp-psr-hack

edp-psr-hack is a hacky kernel module to force enable PSR (panel self refresh) for the laptop's eDP display when the only reason it's disabled is because the reported PSR setup time from DPCD exceeds the vblank time minus one line.

When PSR is disabled, the system cannot enter the lowest C10 power state when idle. On a Lenovo P1 Gen 3, this is the difference between the system idling at 9.8W vs. 5.5W.

This module is inspired by encomHat's blog post at https://encomhat.com/2022/09/linux-laptop-intel-gpu/. However, instead of patching the kernel at build time, this module patches the return value of `drm_dp_psr_setup_time` at runtime to always report 0us. As of kernel 6.0.11, the only place that function is called is in the i915 driver where it decides whether or not to disable PSR.

## Supported laptops

To determine whether your laptop is supported, boot with the `drm.debug=0x1ff log_buf_len=32M` kernel options and check `dmesg | grep PSR` for:

```
i915 0000:00:02.0: [drm:intel_psr_init_dpcd [i915]] eDP panel supports PSR version 1
i915 0000:00:02.0: [drm:intel_dp_initial_fastset_check [i915]] Forcing full modeset to compute PSR state
i915 0000:00:02.0: [drm:intel_dp_compute_config [i915]] PSR condition failed: PSR setup time (330 us) too long
```

If that last line doesn't show up, then this module isn't applicable to your system because PSR was disabled for a different reason.

## Did it work?

After the module is installed and the system is rebooted, if things are working, then `dmesg | grep edp-psr-hack` should show messages like:

```
edp-psr-hack: [drm_dp_psr_setup_time@000000009e7497bf] Registered hook
edp-psr-hack: [drm_dp_psr_setup_time] Changed return value from 330 to 0
```

`/sys/kernel/debug/dri/0/i915_edp_psr_status` should report that PSR is enabled:

```
Sink support: yes [0x01]
PSR mode: PSR1 enabled
Source PSR ctl: enabled [0x81f00e29]
Source PSR status: IDLE [0x04010002]
Busy frontbuffer bits: 0x00000000
```

In `powertop`, the `Idle stats` tab should show the system entering the C10 power state.

## License

GPLv2+

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/kprobes.h>
#include <drm/display/drm_dp_helper.h>

#define HOOK_FUNC "drm_dp_psr_setup_time"
#define LOG_PREFIX "edp-psr-hack: "

static int ret_handler(struct kretprobe_instance *ri, struct pt_regs *regs)
{
    const unsigned long ret_old = regs_return_value(regs);
    const unsigned long ret_new = 0;

    regs_set_return_value(regs, ret_new);

    pr_info(LOG_PREFIX "[%s] Changed return value from %lu to %lu\n",
            HOOK_FUNC, ret_old, ret_new);

    return 0;
}
NOKPROBE_SYMBOL(ret_handler);

static struct kretprobe krp = {
    .kp = {
        .symbol_name = HOOK_FUNC,
    },
    .handler = ret_handler,
    .maxactive = 1,
};

static int __init kretprobe_init(void)
{
    int ret;

    // Hack to force a hard dependency on drm_display_helper
    {
        const u8 dummy[EDP_PSR_RECEIVER_CAP_SIZE] = {};
        drm_dp_psr_setup_time(dummy);
    }

    ret = register_kretprobe(&krp);
    if (ret < 0) {
        pr_err(LOG_PREFIX "Failed to hook %s: %d\n", krp.kp.symbol_name, ret);
        return ret;
    }

    pr_info(LOG_PREFIX "[%s@%p] Registered hook\n",
            krp.kp.symbol_name, krp.kp.addr);

    return 0;
}

static void __exit kretprobe_exit(void)
{
    unregister_kretprobe(&krp);
    pr_info(LOG_PREFIX "[%s@%p] Unregistered hook\n",
            krp.kp.symbol_name, krp.kp.addr);

    pr_info(LOG_PREFIX "[%s@%p] Missed probing %d instances\n",
            krp.kp.symbol_name, krp.kp.addr, krp.nmissed);
}

module_init(kretprobe_init)
module_exit(kretprobe_exit)

MODULE_SOFTDEP("post: i915");
MODULE_LICENSE("GPL");

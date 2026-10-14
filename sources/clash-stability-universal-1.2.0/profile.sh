# Sourced into both maintainer scripts at build time. No user settings changed.
# Exact OS/device plus jailbreak file fingerprints; never guess a profile.
select_profile() {
    model=$(/var/jb/usr/sbin/sysctl -n hw.machine) || return 1
    build=$(/var/jb/usr/sbin/sysctl -n kern.osversion) || return 1
    case "$model:$build" in
        iPad14,6:20B82)
            profile=ios16
            payload_sha=d9dbc5299c92274bc6160ef1666678843d06ee24bf783a6344d97e4ec01a634f
            hook_sha=b4e9e7d352e53bf7e91ce8c56f985612f2606b993e1ef3a02a3b4e4f765285c5
            dyld_sha=4c5df2d35feb85398d71dbdc62a8ccb5dc479af1993cac8bb555998677317f25
            ;;
        iPad7,2:21H461)
            profile=ios17
            payload_sha=af5aa166f22195bcc362375cdd3bed3803c16c216c22db3c017557665d47a44e
            hook_sha=d9eea18e2e1f8d038f65753f8300331052a7a558f50ba81987bfd84a157b66f5
            dyld_sha=7376f20cffb173ac297f030a4c6cce168b3215d00fbc8bb6d031a2b21ac2d5ad
            ;;
        *) echo 'Unsupported device/build; refusing installation. 不支持此设备/构建，拒绝安装。' >&2; return 1 ;;
    esac
    printf '%s  %s\n%s  %s\n' "$hook_sha" /var/jb/basebin/systemhook.dylib \
        "$dyld_sha" /var/jb/basebin/gen/dyld | /var/jb/usr/bin/sha256sum -c - || return 1
}

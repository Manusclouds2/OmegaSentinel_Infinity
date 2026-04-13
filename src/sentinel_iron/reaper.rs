#[cfg(target_family = "unix")]
mod unix_impl {
    use nix::sys::signal::{self, Signal};
    use nix::unistd::Pid;

    pub fn atomic_reap(target_pid: i32) {
        let pid = Pid::from_raw(target_pid);

        // Send SIGKILL - cannot be caught or ignored by the malware
        match signal::kill(pid, Signal::SIGKILL) {
            Ok(_) => println!("[+] Malicious Process {} Reaped successfully.", target_pid),
            Err(e) => eprintln!("[!] Error reaping process: {}", e),
        }
    }
}

#[cfg(not(target_family = "unix"))]
mod stub_impl {
    pub fn atomic_reap(target_pid: i32) {
        println!("[!] atomic_reap is not supported on this platform (target_pid={})", target_pid);
    }
}

pub fn atomic_reap(target_pid: i32) {
    #[cfg(target_family = "unix")]
    {
        unix_impl::atomic_reap(target_pid);
    }
    #[cfg(not(target_family = "unix"))]
    {
        stub_impl::atomic_reap(target_pid);
    }
}

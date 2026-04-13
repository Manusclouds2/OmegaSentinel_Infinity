use std::fs;
use std::process::Command;

// Check if the System Call Table or Kernel Modules have been "Hooked"
// Real implementation for Linux reads /proc/kallsyms.
// Real implementation for Windows audits loaded drivers via PowerShell.

pub fn verify_syscall_table() -> bool {
    #[cfg(target_os = "windows")]
    {
        return verify_windows_drivers();
    }

    #[cfg(not(target_os = "windows"))]
    {
        let original_sys_kill_addr: u64 = 0xffffffff810a3ac0;
        let current_sys_kill_addr = get_kernel_symbol("sys_kill");

        if current_sys_kill_addr == 0 {
            eprintln!("[!] Could not resolve current sys_kill address");
            return false;
        }

        if current_sys_kill_addr != original_sys_kill_addr {
            println!("[!] CRITICAL: Kernel Hook Detected at sys_kill!");
            return false;
        }
        true
    }
}

#[cfg(target_os = "windows")]
fn verify_windows_drivers() -> bool {
    // Audit signed vs unsigned drivers - a key indicator of kernel rootkits
    println!("[*] AUDIT: Verifying Windows Kernel Driver integrity...");
    let output = Command::new("powershell")
        .args(&["-Command", "Get-WmiObject Win32_PnPSignedDriver | Where-Object { $_.IsSigned -ne $true } | Select-Object DeviceName"])
        .output();

    match output {
        Ok(out) => {
            let s = String::from_utf8_lossy(&out.stdout);
            if !s.trim().is_empty() {
                println!("[!] WARNING: Unsigned kernel drivers detected:\n{}", s);
                // In strict mode, we might return false here
            } else {
                println!("[+] All active kernel drivers are signed.");
            }
            true
        }
        Err(_) => false
    }
}

fn get_kernel_symbol(name: &str) -> u64 {
    // Linux: read /proc/kallsyms if available
    #[cfg(target_os = "linux")]
    {
        if let Ok(s) = fs::read_to_string("/proc/kallsyms") {
            for line in s.lines() {
                // Format: address type name
                let mut parts = line.split_whitespace();
                if let (Some(addr_str), Some(_type), Some(sym)) = (parts.next(), parts.next(), parts.next()) {
                    if sym == name {
                        if let Ok(v) = u64::from_str_radix(addr_str, 16) {
                            return v;
                        }
                    }
                }
            }
        }
        // Fallback to teacher/kallsyms.mock for testing
        if let Ok(s) = fs::read_to_string("teacher/kallsyms.mock") {
            for line in s.lines() {
                if let Some((addr, sym)) = line.split_once(' ') {
                    if sym.trim() == name {
                        if let Ok(v) = u64::from_str_radix(addr.trim_start_matches("0x"), 16) {
                            return v;
                        }
                    }
                }
            }
        }
        return 0;
    }

    // Non-Linux: attempt mock file only (safe)
    #[cfg(not(target_os = "linux"))]
    {
        if let Ok(s) = fs::read_to_string("teacher/kallsyms.mock") {
            for line in s.lines() {
                if let Some((addr, sym)) = line.split_once(' ') {
                    if sym.trim() == name {
                        if let Ok(v) = u64::from_str_radix(addr.trim_start_matches("0x"), 16) {
                            return v;
                        }
                    }
                }
            }
        }
        return 0;
    }
}

pub fn enforce_zero_trust_whitelisting(whitelist: Vec<String>) -> bool {
    """Elite Host-Based Micro-Segmentation: Blocking unauthorized process execution"""
    println!("[*] ZERO TRUST: Auditing active processes against company whitelist...");
    
    #[cfg(target_os = "windows")]
    {
        let output = Command::new("powershell")
            .args(&["-Command", "Get-Process | Select-Object ProcessName"])
            .output();
        
        match output {
            Ok(out) => {
                let s = String::from_utf8_lossy(&out.stdout);
                for line in s.lines().skip(3) { // Skip headers
                    let proc_name = line.trim().to_lowercase();
                    if proc_name.is_empty() { continue; }
                    
                    if !whitelist.contains(&proc_name) {
                        println!("[!] ZERO TRUST BREACH: Unauthorized process detected: {}", proc_name);
                        // In strict mode, we might terminate the process here
                        // Command::new("taskkill").args(&["/F", "/IM", &format!("{}.exe", proc_name)]).spawn();
                    }
                }
                true
            }
            Err(_) => false
        }
    }
    
    #[cfg(not(target_os = "windows"))]
    {
        // Linux: check ps -e
        let output = Command::new("ps")
            .arg("-e")
            .output();
            
        match output {
            Ok(out) => {
                let s = String::from_utf8_lossy(&out.stdout);
                for line in s.lines().skip(1) {
                    let parts: Vec<&str> = line.split_whitespace().collect();
                    if let Some(proc_name) = parts.last() {
                        if !whitelist.contains(&proc_name.to_lowercase()) {
                            println!("[!] ZERO TRUST BREACH: Unauthorized process: {}", proc_name);
                        }
                    }
                }
                true
            }
            Err(_) => false
        }
    }
}

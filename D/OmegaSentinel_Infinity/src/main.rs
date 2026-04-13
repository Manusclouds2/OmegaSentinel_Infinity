// teacher/src/main.rs

mod sentinel_hw_shield;
mod sentinel_ebpf;
mod sentinel_iron;
mod converted;
mod abstraction;

use std::env;
use sentinel_hw_shield::verify_boot_integrity;
use sentinel_ebpf::start_ebpf;

#[tokio::main]
async fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        println!("Usage: teacher <command>\nCommands:\n  verify   - run hardware boot integrity check\n  ebpf     - start (mocked) eBPF firewall\n  monitor  - verify syscall table\n  block    - block attacker (mock)\n  reaper   - atomic reap process\n  recover  - trigger self heal\n  converted - run all converted Python stubs");
        return;
    }

    match args[1].as_str() {
        "verify" => {
            match verify_boot_integrity() {
                Ok(_) => println!("[+] verify: OK"),
                Err(e) => eprintln!("[!] verify failed: {}", e),
            }
        }
        "ebpf" => {
            if let Err(e) = start_ebpf() {
                eprintln!("[!] eBPF start failed: {}", e);
            }
        }
        "monitor" => {
            if sentinel_iron::monitor::verify_syscall_table() {
                println!("[+] Syscall table OK.");
            } else {
                eprintln!("[!] Syscall table compromised.");
            }
        }
        "block" => {
            abstraction::block_attacker();
        }
        "reaper" => {
            if args.len() < 3 {
                eprintln!("Usage: teacher reaper <pid>");
            } else if let Ok(pid) = args[2].parse::<i32>() {
                sentinel_iron::reaper::atomic_reap(pid);
            } else {
                eprintln!("Invalid pid: {}", args[2]);
            }
        }
        "recover" => {
            if args.len() < 4 {
                eprintln!("Usage: teacher recover <target_path> <backup_path>");
            } else {
                if let Err(e) = sentinel_iron::recovery::trigger_self_heal(&args[2], &args[3]) {
                    eprintln!("[!] Recovery failed: {}", e);
                }
            }
        }
        "converted" => {
            // Run all converted Python stubs
            if let Err(e) = converted::run_all() {
                eprintln!("[!] converted run failed: {}", e);
            }
        }
        _ => {
            eprintln!("Unknown command: {}", args[1]);
        }
    }
}

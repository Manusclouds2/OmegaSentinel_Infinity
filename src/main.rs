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
        println!("Usage: teacher <command>\nCommands:\n  verify   - run hardware boot integrity check\n  ebpf     - start (mocked) eBPF firewall\n  monitor  - verify syscall table\n  seal     - seal data to TPM PCRs\n  unseal   - unseal data from TPM PCRs\n  reaper   - atomic reap process\n  recover  - trigger self heal\n  converted - run all converted Python stubs");
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
        "seal" => {
            if args.len() < 3 {
                eprintln!("Usage: teacher seal <data>");
            } else {
                match sentinel_hw_shield::seal_master_key_to_pcr_policy(args[2].as_bytes()) {
                    Ok(blob) => println!("[+] Data Sealed to PCR 0, 4, 7: {:?}", blob),
                    Err(e) => eprintln!("[!] Seal failed: {}", e),
                }
            }
        }
        "unseal" => {
            if args.len() < 3 {
                eprintln!("Usage: teacher unseal <hex_blob> <pcr_index>");
            } else {
                let pcr = args[3].parse::<u32>().unwrap_or(7);
                let blob = hex::decode(&args[2]).unwrap_or_default();
                match sentinel_hw_shield::unseal_data_from_pcr(&blob, pcr) {
                    Ok(data) => println!("[+] Data Unsealed: {}", String::from_utf8_lossy(&data)),
                    Err(e) => eprintln!("[!] Unseal failed: {}", e),
                }
            }
        }
        _ => {
            eprintln!("Unknown command: {}", args[1]);
        }
    }
}

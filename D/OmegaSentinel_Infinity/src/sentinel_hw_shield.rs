// teacher/src/sentinel_hw_shield.rs

use std::process::Command;
use std::fs;
use std::path::Path;

/// verify_boot_integrity
///
/// Provides two implementations:
/// - real TPM-backed (enabled with `--features real_hw`) using tss-esapi (user-provided snippet)
/// - mocked, safe default that reads teacher/pcr0.hex
pub fn verify_boot_integrity() -> Result<(), Box<dyn std::error::Error>> {
    verify_impl()
}

#[cfg(not(feature = "real_hw"))]
fn verify_impl() -> Result<(), Box<dyn std::error::Error>> {
    // Expected BIOS hash (from the user's snippet)
    let expected_hash = "f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2";

    // Attempt to read a pre-populated PCR value from teacher/pcr0.hex for testing.
    let pcr_file = Path::new("teacher/pcr0.hex");

    let measured = if pcr_file.exists() {
        let s = fs::read_to_string(pcr_file)?;
        s.trim().to_string()
    } else {
        // Mocked value: for safety, default to an empty string so it will not match.
        String::new()
    };

    if measured != expected_hash {
        println!("[!] ALERT: BIOS TAMPERING DETECTED!");
        // EMERGENCY: Force system halt to prevent further execution. This is a destructive
        // operation; here we only attempt a shutdown command on Unix-like systems.
        #[cfg(target_family = "unix")]
        {
            let _ = Command::new("shutdown").arg("-h").arg("now").spawn();
        }
        #[cfg(target_family = "windows")]
        {
            let _ = Command::new("shutdown").arg("/s").arg("/t").arg("0").spawn();
        }

        return Err("boot integrity check failed".into());
    }

    println!("[+] Hardware Integrity Verified.");
    Ok(())
}

#[cfg(feature = "real_hw")]
fn verify_impl() -> Result<(), Box<dyn std::error::Error>> {
    // Real TPM-backed implementation. This block is only compiled when the
    // `real_hw` feature is enabled. It uses the user's provided pattern and
    // requires the tss-esapi crate and appropriate platform support.

    // The following mirrors the user's snippet. Replace or extend as needed
    // based on the exact tss-esapi version and environment.
    use tss_esapi::{Context, TctiNameConf};
    use tss_esapi::structures::PcrSelectionList;

    // Connect to the hardware TPM 2.0
    let mut context = Context::new(TctiNameConf::Device(Default::default()))?;

    // Read PCR0 (The BIOS/Firmware measurement)
    let (_pcr_update, pcr_values) = context.pcr_read(PcrSelectionList::from_pcr(0))?;

    // Convert read PCR value(s) to hex. Implementation details may vary by tss-esapi version.
    let pcr_hex = if let Some((_sel, digest)) = pcr_values.into_iter().next() {
        hex::encode(digest.value())
    } else {
        String::new()
    };

    let expected_hash = "f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2";

    if pcr_hex != expected_hash {
        println!("[!] ALERT: BIOS TAMPERING DETECTED!");
        // EMERGENCY: Force system halt to prevent "Bricking"
        #[cfg(target_family = "unix")]
        {
            let _ = Command::new("shutdown").arg("-h").arg("now").spawn();
        }
        #[cfg(target_family = "windows")]
        {
            let _ = Command::new("shutdown").arg("/s").arg("/t").arg("0").spawn();
        }
        return Err("boot integrity check failed".into());
    }

    println!("[+] Hardware Integrity Verified.");
    Ok(())
}

/*
Original suggested code (from user) is retained in prior commits as a reference.
*/

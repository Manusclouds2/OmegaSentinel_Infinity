use std::error::Error;

mod advanced_malware_detector;
mod app;
mod app_backup_simulated;
mod app_real;
mod autoresponder;
mod auto_recovery_system;
mod check_password;
mod cross_platform_defender;
mod defender_integration;
mod elite_autoresponder;
mod email_scanner;
mod enterprise_firewall;
mod file_monitor;
mod firewall_manager;
mod hardware_root_of_trust;
mod measured_boot_verification;
mod network_monitor;
mod post_quantum_crypto;
mod process_monitor;
mod ransomware_detector;
mod rbac;
mod reset_password;
mod security_services;
mod server;
mod system_file_scanner;
mod universal_responder;
mod unix_defender;
mod update_password;

pub fn run_all() -> Result<(), Box<dyn Error>> {
    // Call each module's run() stub
    advanced_malware_detector::run()?;
    app::run()?;
    app_backup_simulated::run()?;
    app_real::run()?;
    autoresponder::run()?;
    auto_recovery_system::run()?;
    check_password::run()?;
    cross_platform_defender::run()?;
    defender_integration::run()?;
    elite_autoresponder::run()?;
    email_scanner::run()?;
    enterprise_firewall::run()?;
    file_monitor::run()?;
    firewall_manager::run()?;
    hardware_root_of_trust::run()?;
    measured_boot_verification::run()?;
    network_monitor::run()?;
    post_quantum_crypto::run()?;
    process_monitor::run()?;
    ransomware_detector::run()?;
    rbac::run()?;
    reset_password::run()?;
    security_services::run()?;
    server::run()?;
    system_file_scanner::run()?;
    universal_responder::run()?;
    unix_defender::run()?;
    update_password::run()?;
    println!("[+] All converted modules ran (stubs).");
    Ok(())
}

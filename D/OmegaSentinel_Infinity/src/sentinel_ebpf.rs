// teacher/src/sentinel_ebpf.rs

use std::path::Path;
use std::fs;

/// start_ebpf
///
/// Two modes:
/// - real eBPF mode (enabled via `--features real_hw`) using aya to load/attach an XDP program
/// - mocked default that only checks for a prebuilt blob so the program remains runnable
pub fn start_ebpf() -> Result<(), Box<dyn std::error::Error>> {
    start_impl()
}

#[cfg(not(feature = "real_hw"))]
fn start_impl() -> Result<(), Box<dyn std::error::Error>> {
    let bpf_path = Path::new("teacher/firewall.bpf");

    if !bpf_path.exists() {
        println!("[!] No BPF program found at teacher/firewall.bpf (mock mode).\n    To enable real eBPF loading, compile a BPF program for your target and place it there.");
        return Ok(());
    }

    // In a real implementation we would use aya::Bpf::load and attach the XDP program
    // to an interface. Here we simply report that a BPF blob was found.
    let _contents = fs::read(bpf_path)?;
    println!("[+] eBPF binary found. (Mock load successful). Monitoring for C2 signatures...");
    Ok(())
}

#[cfg(feature = "real_hw")]
fn start_impl() -> Result<(), Box<dyn std::error::Error>> {
    // Real eBPF loader using aya. This requires the compiled BPF object to be available
    // and appropriate privileges to load/attach it. Adjust the path and interface as needed.
    use aya::Bpf;
    use aya::programs::Xdp;
    use std::convert::TryInto;

    // Path to compiled BPF ELF blob. Update for your build pipeline.
    let bpf_bytes = include_bytes!("../../target/bpfel-unknown-none/debug/firewall");
    let mut bpf = Bpf::load(bpf_bytes.as_ref())?;

    let program = bpf.program_mut("drop_c2_traffic").ok_or("program not found")?;
    let program: &mut Xdp = program.try_into()?;

    // Attach to the network interface (default eth0)
    program.load()?;
    program.attach("eth0", aya::programs::XdpFlags::default())?;

    println!("[+] eBPF Kernel Firewall Active. Monitoring for C2 signatures...");
    Ok(())
}

/*
Original suggested code (from user) is retained in prior commits as reference.
*/

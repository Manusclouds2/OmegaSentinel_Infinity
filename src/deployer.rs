use std::error::Error;
use std::process::{Command, Stdio};
use std::env;
use std::path::Path;
use std::fs;

fn is_command_available(cmd: &str) -> bool {
    // Try common version flags, fall back to spawn to check existence on PATH
    let tries = vec!["--version", "-v", "-V"];
    for flag in &tries {
        if Command::new(cmd).arg(flag).stdout(Stdio::null()).stderr(Stdio::null()).status().is_ok() {
            return true;
        }
    }
    // Try without args
    match Command::new(cmd).stdout(Stdio::null()).stderr(Stdio::null()).status() {
        Ok(_) => true,
        Err(e) => {
            // If the error is NotFound, the command is not available
            e.kind() != std::io::ErrorKind::NotFound
        }
    }
}

fn check_tools(required: &[(&str, &str)]) -> Vec<(String, bool, String)> {
    // Returns tuples of (tool, available, hint)
    let mut out = Vec::new();
    for (tool, hint) in required {
        let ok = is_command_available(tool);
        out.push((tool.to_string(), ok, hint.to_string()));
    }
    out
}

fn run_cmd(mut cmd: Command) -> Result<(), Box<dyn Error>> {
    println!("Running: {:?}", cmd);
    let status = cmd.status()?;
    if !status.success() {
        return Err(format!("command failed: {:?}", status).into());
    }
    Ok(())
}

fn install_cross() -> Result<(), Box<dyn Error>> {
    println!("[+] Installing cross (cargo install cross)");
    run_cmd(Command::new("cargo").arg("install").arg("cross"))
}

fn build_target(target: &str, use_cross: bool) -> Result<(), Box<dyn Error>> {
    let mut cmd = if use_cross {
        let mut c = Command::new("cross");
        c.arg("build").arg("--release").arg("--target").arg(target);
        c
    } else {
        let mut c = Command::new("cargo");
        c.arg("build").arg("--release").arg("--target").arg(target);
        c
    };
    run_cmd(cmd)
}

fn package_binary(crate_name: &str, target: &str) -> Result<(), Box<dyn Error>> {
    // Determine binary name and path
    let bin_name = if target.contains("windows") { format!("{}.exe", crate_name) } else { crate_name.to_string() };
    let rel_path = format!("target/{}/release/{}", target, bin_name);
    let path = Path::new(&rel_path);
    if !path.exists() {
        return Err(format!("built binary not found: {}", rel_path).into());
    }

    let out_dir = Path::new("dist").join(target);
    fs::create_dir_all(&out_dir)?;
    let dest = out_dir.join(&bin_name);
    fs::copy(path, &dest)?;

    // Create a zip archive if zip is available, otherwise leave the binary
    let zip_path = out_dir.join(format!("{}-{}.zip", crate_name, target));

    #[cfg(target_family = "unix")]
    {
        // try zip
        if Command::new("zip").arg("-v").stdout(Stdio::null()).status().is_ok() {
            run_cmd(Command::new("zip").arg("-j").arg(zip_path.to_str().unwrap()).arg(dest.to_str().unwrap()))?;
        }
    }

    #[cfg(target_family = "windows")]
    {
        // Use PowerShell Compress-Archive
        let ps = format!("Compress-Archive -Path '{0}' -DestinationPath '{1}' -Force", dest.display(), zip_path.display());
        run_cmd(Command::new("powershell").arg("-Command").arg(ps))?;
    }

    println!("Packaged {} -> {}", dest.display(), zip_path.display());
    // Optional signing step
    if env::var("SIGN_PFX").is_ok() || env::var("SIGN_KEY").is_ok() {
        if let Err(e) = sign_binary(&dest) {
            eprintln!("[!] Signing failed: {}", e);
        }
    }

    // Optionally embed an install password into an encrypted file inside the package directory.
    if let Ok(pw) = env::var("EMBED_PASSWORD") {
        let pw_path = out_dir.join("INSTALL_PASSWORD.txt");
        std::fs::write(&pw_path, pw.as_bytes())?;

        // Try openssl first
        if is_command_available("openssl") {
            let enc_path = out_dir.join("INSTALL_PASSWORD.txt.enc");
            let status = Command::new("openssl")
                .arg("enc")
                .arg("-aes-256-cbc")
                .arg("-pbkdf2")
                .arg("-salt")
                .arg("-in")
                .arg(pw_path.to_str().unwrap())
                .arg("-out")
                .arg(enc_path.to_str().unwrap())
                .arg("-pass")
                .arg(format!("pass:{}", pw))
                .status()?;
            if status.success() {
                println!("[+] Created encrypted password file: {}", enc_path.display());
                let _ = std::fs::remove_file(&pw_path);
            } else {
                eprintln!("[!] OpenSSL failed to create encrypted password file");
            }
        } else if is_command_available("7z") {
            // Create an encrypted zip containing only the password file
            let zip_enc = out_dir.join("password_protected.zip");
            let status = Command::new("7z")
                .arg("a")
                .arg("-tzip")
                .arg(zip_enc.to_str().unwrap())
                .arg(pw_path.to_str().unwrap())
                .arg(format!("-p{}", pw))
                .arg("-mem=AES256")
                .status()?;
            if status.success() {
                println!("[+] Created encrypted zip with password file: {}", zip_enc.display());
                let _ = std::fs::remove_file(&pw_path);
            } else {
                eprintln!("[!] 7z failed to create encrypted archive for password file");
            }
        } else {
            eprintln!("[!] No encryption tool (openssl or 7z) available to encrypt the install password. Leaving plaintext in package.");
        }
    }

    Ok(())
}

fn sign_binary(path: &Path) -> Result<(), Box<dyn Error>> {
    // Windows: use signtool if SIGN_PFX provided
    if cfg!(target_family = "windows") {
        if let Ok(pfx) = env::var("SIGN_PFX") {
            let pass = env::var("SIGN_PFX_PASS").unwrap_or_default();
            // signtool sign /f cert.pfx /p <pass> /fd SHA256 <file>
            if Command::new("signtool").arg("sign").arg("/f").arg(&pfx).arg("/p").arg(&pass).arg("/fd").arg("SHA256").arg(path).status().is_ok() {
                println!("[+] signtool signed {}", path.display());
                return Ok(());
            } else {
                return Err("signtool failed".into());
            }
        }
    }

    // Unix: try sbsign if SIGN_KEY and SIGN_CERT provided
    if cfg!(target_family = "unix") {
        if let (Ok(key), Ok(cert)) = (env::var("SIGN_KEY"), env::var("SIGN_CERT")) {
            // sbsign --key PK.key --cert PK.crt --output signed.efi original.efi
            let signed = path.with_extension("signed");
            if Command::new("sbsign").arg("--key").arg(&key).arg("--cert").arg(&cert).arg("--output").arg(&signed).arg(path).status().is_ok() {
                println!("[+] sbsign produced {}", signed.display());
                return Ok(());
            } else {
                return Err("sbsign failed".into());
            }
        }
    }

    Err("no signing method matched or required env vars missing".into())
}

fn create_uefi_image(crate_name: &str, target: &str) -> Result<(), Box<dyn Error>> {
    // Place the built binary as EFI/BOOT/BOOTX64.EFI inside a temp dir and create an ISO
    let bin_name = if target.contains("windows") { format!("{}.exe", crate_name) } else { crate_name.to_string() };
    let rel_path = format!("target/{}/release/{}", target, bin_name);
    let path = Path::new(&rel_path);
    if !path.exists() {
        return Err(format!("built binary not found: {}", rel_path).into());
    }

    let work = Path::new("target").join("uefi_image").join(target);
    let efi_dir = work.join("EFI").join("BOOT");
    fs::create_dir_all(&efi_dir)?;

    // target filename for EFI must be BOOTX64.EFI for x86_64
    let efi_name = if env::var("UEFI_FILENAME").is_ok() { env::var("UEFI_FILENAME").unwrap() } else { "BOOTX64.EFI".to_string() };
    let dest_efi = efi_dir.join(&efi_name);
    fs::copy(path, &dest_efi)?;

    // Optionally sign the EFI binary with sbsign
    if env::var("SIGN_KEY").is_ok() && env::var("SIGN_CERT").is_ok() {
        if let Err(e) = sign_binary(&dest_efi) {
            eprintln!("[!] EFI signing failed: {}", e);
        }
    }

    let out_dir = Path::new("dist").join(target);
    fs::create_dir_all(&out_dir)?;
    let iso_path = out_dir.join(format!("{}-{}-uefi.iso", crate_name, target));

    // Try platform-specific ISO builders
    if cfg!(target_family = "windows") {
        // Try oscdimg if available
        if Command::new("oscdimg").arg("/v").stdout(Stdio::null()).status().is_ok() {
            run_cmd(Command::new("oscdimg").arg("-n").arg("-m").arg(work.to_str().unwrap()).arg(iso_path.to_str().unwrap()))?;
            println!("[+] Created UEFI ISO {}", iso_path.display());
            return Ok(());
        }
    } else {
        // Unix: try genisoimage or mkisofs
        if Command::new("genisoimage").arg("-version").stdout(Stdio::null()).status().is_ok() {
            run_cmd(Command::new("genisoimage").arg("-o").arg(iso_path.to_str().unwrap()).arg("-b").arg("EFI/BOOT/BOOTX64.EFI").arg(work.to_str().unwrap()))?;
            println!("[+] Created UEFI ISO {}", iso_path.display());
            return Ok(());
        }
        if Command::new("mkisofs").arg("-version").stdout(Stdio::null()).status().is_ok() {
            run_cmd(Command::new("mkisofs").arg("-o").arg(iso_path.to_str().unwrap()).arg("-b").arg("EFI/BOOT/BOOTX64.EFI").arg(work.to_str().unwrap()))?;
            println!("[+] Created UEFI ISO {}", iso_path.display());
            return Ok(());
        }
    }

    Err("no ISO creation tool found (oscdimg/genisoimage/mkisofs)".into())
}

fn detect_host() -> (String, String) {
    (env::consts::OS.to_string(), env::consts::ARCH.to_string())
}

fn detect_removable_drive() -> Option<String> {
    // Try platform-specific heuristics to find a removable drive path
    #[cfg(target_os = "windows")]
    {
        // Use PowerShell to query Win32_LogicalDisk DriveType 2
        if let Ok(output) = Command::new("powershell").arg("-Command").arg("(Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object {$_.DriveType -eq 2} | Select-Object -First 1).DeviceID").output() {
            if output.status.success() {
                if let Ok(s) = String::from_utf8(output.stdout) {
                    let drive = s.trim().to_string();
                    if !drive.is_empty() { return Some(drive); }
                }
            }
        }
        None
    }

    #[cfg(target_os = "linux")]
    {
        // check common mount points
        let candidates = vec!["/run/media", "/media", "/mnt"];
        for c in candidates {
            if let Ok(entries) = fs::read_dir(c) {
                for e in entries.flatten() {
                    let p = e.path();
                    if p.is_dir() {
                        return Some(p.to_string_lossy().to_string());
                    }
                }
            }
        }
        None
    }

    #[cfg(target_os = "macos")]
    {
        if let Ok(entries) = fs::read_dir("/Volumes") {
            for e in entries.flatten() {
                let p = e.path();
                if p.is_dir() && p != Path::new("/Volumes/Macintosh HD") {
                    return Some(p.to_string_lossy().to_string());
                }
            }
        }
        None
    }

    #[cfg(not(any(target_os = "windows", target_os = "linux", target_os = "macos")))]
    {
        None
    }
}

fn attempt_package_install(tool: &str, assume_yes: bool) -> Result<(), Box<dyn Error>> {
    // Map tools to package manager commands per platform
    let os = env::consts::OS;
    let mut cmds: Vec<Command> = Vec::new();

    match os {
        "windows" => {
            // use choco
            let mut c = Command::new("choco");
            c.arg("install").arg(tool).arg("-y");
            cmds.push(c);
        }
        "linux" => {
            // try apt, yum, or pacman depending on availability
            if is_command_available("apt-get") {
                let mut c = Command::new("sudo"); c.arg("apt-get").arg("install").arg("-y").arg(tool); cmds.push(c);
            } else if is_command_available("yum") {
                let mut c = Command::new("sudo"); c.arg("yum").arg("install").arg("-y").arg(tool); cmds.push(c);
            } else if is_command_available("pacman") {
                let mut c = Command::new("sudo"); c.arg("pacman").arg("-S").arg("--noconfirm").arg(tool); cmds.push(c);
            }
        }
        "macos" => {
            if is_command_available("brew") {
                let mut c = Command::new("brew"); c.arg("install").arg(tool); cmds.push(c);
            }
        }
        _ => {}
    }

    if cmds.is_empty() {
        return Err(format!("No package manager command available to install {} on {}", tool, os).into());
    }

    for mut cmd in cmds {
        println!("About to run: {:?}", cmd);
        if !assume_yes {
            println!("Run this command? set env AUTO_INSTALL=1 or pass 'yes' to prepare-toolchain to auto-run.");
            return Err("user approval required".into());
        }
        run_cmd(cmd)?;
    }
    Ok(())
}

fn print_usage(program: &str) {
    eprintln!("Usage: {} [check-tools|prepare-toolchain|build-all|build <target>|package <target>|deploy <target>|create-uefi-image <target>|help]", program);
}

fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = env::args().collect();
    let program = args.get(0).map(|s| s.as_str()).unwrap_or("deployer");

    if args.len() < 2 {
        print_usage(program);
        return Ok(());
    }

    let (host_os, host_arch) = detect_host();
    println!("Host: {} {}", host_os, host_arch);

    // List of common targets to attempt
    let targets = vec![
        "x86_64-unknown-linux-gnu",
        "x86_64-unknown-linux-musl",
        "aarch64-unknown-linux-gnu",
        "aarch64-unknown-linux-musl",
        "x86_64-pc-windows-msvc",
        "aarch64-apple-darwin",
    ];

    let crate_name = "teacher";
    let use_cross = env::var("USE_CROSS").unwrap_or_default() == "1";

    match args[1].as_str() {
        "help" => print_usage(program),
        "check-tools" => {
            let required = vec![
                ("rustup", "Install from https://rustup.rs/"),
                ("cargo", "Install from https://rustup.rs/ (cargo comes with rustup)"),
                ("zip", "Install zip (apt/yum/choco)") ,
                ("genisoimage", "Install genisoimage or mkisofs for ISO creation"),
                ("mkisofs", "Install mkisofs or genisoimage for ISO creation"),
                ("oscdimg", "Windows: install Windows ADK to get oscdimg"),
                ("signtool", "Windows: install Windows SDK / ADK for signtool"),
                ("sbsign", "Install sbsigntools for EFI signing"),
                ("cross", "cargo install cross (optional, for cross-compilation)")
            ];
            let results = check_tools(&required);
            println!("Tool check results:");
            for (tool, ok, hint) in results {
                println!("  {:<12} : {} {}", tool, if ok {"OK"} else {"MISSING"}, if ok {""} else {format!(" - hint: {}", hint) });
            }
        }
        "prepare-toolchain" => {
            // Install rustup targets for the common deployment targets used by the deployer.
            // Optionally accepts additional targets as subsequent args.
            let mut to_install = vec![
                "x86_64-unknown-linux-gnu",
                "x86_64-unknown-linux-musl",
                "aarch64-unknown-linux-gnu",
                "aarch64-unknown-linux-musl",
                "x86_64-pc-windows-msvc",
                "aarch64-apple-darwin",
            ];
            // append any user-specified targets
            if args.len() > 2 {
                to_install = args[2..].to_vec();
            }

            for t in &to_install {
                println!("[+] Adding rustup target: {}", t);
                if let Err(e) = run_cmd(Command::new("rustup").arg("target").arg("add").arg(t)) {
                    eprintln!("[!] Failed to add target {}: {}", t, e);
                }
            }
            // Optionally install cross if requested via env var INSTALL_CROSS=1 or arg 'with-cross'
            let want_cross = env::var("INSTALL_CROSS").unwrap_or_default() == "1" || args.iter().any(|a| a == "with-cross");
            if want_cross {
                if let Err(e) = install_cross() {
                    eprintln!("[!] Failed to install cross: {}", e);
                }
            } else {
                println!("\n[+] If you need to cross-compile from this host, consider installing 'cross':\n    cargo install cross\n    or see https://github.com/rust-embedded/cross for setup details.");
            }
            // Optionally auto-install missing helper tools when user passes 'auto' or sets AUTO_INSTALL=1
            let auto = env::var("AUTO_INSTALL").unwrap_or_default() == "1" || args.iter().any(|a| a == "auto");
            if auto {
                let required = vec!["zip", "genisoimage", "sbsign", "oscdimg", "signtool", "cross"];
                for t in required {
                    if !is_command_available(t) {
                        println!("[+] Attempting to auto-install {}", t);
                        if let Err(e) = attempt_package_install(t, true) {
                            eprintln!("[!] Auto-install failed for {}: {}", t, e);
                        }
                    }
                }
            }
        }
        "build-all" => {
            for t in &targets {
                println!("\n=== Building target: {} ===", t);
                if let Err(e) = build_target(t, use_cross) {
                    eprintln!("[!] build failed for {}: {}", t, e);
                } else if let Err(e) = package_binary(crate_name, t) {
                    eprintln!("[!] packaging failed for {}: {}", t, e);
                }
            }
        }
        "build" => {
            if args.len() < 3 { print_usage(program); return Ok(()); }
            let t = &args[2];
            build_target(t, use_cross)?;
        }
        "package" => {
            if args.len() < 3 { print_usage(program); return Ok(()); }
            let t = &args[2];
            package_binary(crate_name, t)?;
        }
        "deploy" => {
            if args.len() < 3 { print_usage(program); return Ok(()); }
            let t = &args[2];
            // Build, package, and optionally attempt a simple deploy step (copy to usb path)
            build_target(t, use_cross)?;
            package_binary(crate_name, t)?;
            println!("[+] Build and package complete for {}", t);
            println!("Note: Actual deployment (installing to remote machine) is not automated by this script.\nYou can copy the dist/{}/ directory to your target media.", t);

            // Optionally create a UEFI image if requested
            let want_uefi = env::var("CREATE_UEFI_IMAGE").unwrap_or_default() == "1" || args.iter().any(|a| a == "uefi");
            if want_uefi {
                if let Err(e) = create_uefi_image(crate_name, t) {
                    eprintln!("[!] UEFI image creation failed: {}", e);
                }
            }
        }
        "create-uefi-image" => {
            if args.len() < 3 { print_usage(program); return Ok(()); }
            let t = &args[2];
            create_uefi_image(crate_name, t)?;
        }
        "copy-to-usb" => {
            if args.len() < 3 { print_usage(program); return Ok(()); }
            let t = &args[2];
            let dest = if args.len() > 3 { Some(args[3].clone()) } else { None };
            let dist_path = Path::new("dist").join(t);
            if !dist_path.exists() {
                return Err(format!("dist for target {} not found. Build/package first.", t).into());
            }
            let target_dest = if let Some(d) = dest {
                d
            } else {
                if let Some(drive) = detect_removable_drive() {
                    drive
                } else {
                    return Err("No removable drive detected; provide destination path".into());
                }
            };

            println!("Copying {} -> {}", dist_path.display(), target_dest);
            // Perform recursive copy
            if cfg!(target_os = "windows") {
                run_cmd(Command::new("powershell").arg("-Command").arg(format!("Copy-Item -Path '{}' -Destination '{}' -Recurse -Force", dist_path.display(), target_dest)))?;
            } else {
                run_cmd(Command::new("cp").arg("-r").arg(dist_path.to_str().unwrap()).arg(&target_dest))?;
            }
            println!("[+] Copy to USB completed.");
        }
        _ => print_usage(program),
    }

    Ok(())
}

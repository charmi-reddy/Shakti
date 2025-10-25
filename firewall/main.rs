use std::net::{TcpListener, TcpStream};
use std::io::{BufRead, BufReader, Write};
use std::process::Command;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use regex::Regex;

fn block_mac(mac: &str) -> Result<(), String> {
    let command = format!(
        "nft add rule inet filter input ether saddr {} drop",
        mac.to_lowercase()
    );
    let status = Command::new("sh")
        .arg("-c")
        .arg(&command)
        .status()
        .map_err(|e| format!("Failed to run command: {}", e))?;

    if status.success() {
        Ok(())
    } else {
        Err("Firewall command failed".to_string())
    }
}

fn is_valid_mac(mac: &str) -> bool {
    let re = Regex::new(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$").unwrap();
    re.is_match(mac)
}

fn handle_client(mut stream: TcpStream) {
    let peer = stream.peer_addr().unwrap_or_else(|_| "unknown".parse().unwrap());
    let reader = BufReader::new(stream.try_clone().unwrap());

    for line in reader.lines() {
        let mac = line.unwrap_or_default().trim().to_string();
        if mac.is_empty() {
            continue;
        }

        let response = if is_valid_mac(&mac) {
            match block_mac(&mac) {
                Ok(_) => format!("Blocked MAC: {}\n", mac),
                Err(e) => format!("Error blocking MAC {}: {}\n", mac, e),
            }
        } else {
            format!("Invalid MAC address format: {}\n", mac)
        };

        if let Err(e) = stream.write_all(response.as_bytes()) {
            eprintln!("Failed to send response to {}: {}", peer, e);
            break;
        }
    }
}

fn main() -> std::io::Result<()> {
    let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();

    // Handle Ctrl+C for graceful shutdown
    ctrlc::set_handler(move || {
        r.store(false, Ordering::SeqCst);
        println!("\nReceived Ctrl+C, shutting down firewall server.");
    }).expect("Error setting Ctrl+C handler");

    let listener = TcpListener::bind("127.0.0.1:9000")?;
    println!("Firewall server running on 127.0.0.1:9000");

    for stream in listener.incoming() {
        if !running.load(Ordering::SeqCst) {
            break;
        }
        match stream {
            Ok(stream) => {
                std::thread::spawn(|| handle_client(stream));
            }
            Err(e) => eprintln!("Connection failed: {}", e),
        }
    }
    println!("Firewall server stopped.");
    Ok(())
}

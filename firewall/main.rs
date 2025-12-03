use std::net::{TcpListener, TcpStream};
use std::io::{BufRead, BufReader, Write};
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicBool, Ordering};
use std::collections::HashSet;
use std::fs;
use regex::Regex;
use serde::{Deserialize, Serialize};
use chrono::Local;
use lazy_static::lazy_static;
// Configuration
const HOST: &str = "127.0.0.1";
const PORT: u16 = 9000;
const BLOCK_LOG_FILE: &str = "logs/blocked_macs.json";

lazy_static! {
    static ref MAC_REGEX: Regex = 
        Regex::new(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$").unwrap();
}

#[derive(Debug, Serialize, Deserialize)]
struct BlocklistData {
    blocked_macs: Vec<String>,
    last_updated: String,
    total_blocked: usize,
}

struct FirewallServer {
    blocked_macs: Arc<Mutex<HashSet<String>>>,
}

impl FirewallServer {
    fn new() -> Self {
        Self {
            blocked_macs: Arc::new(Mutex::new(HashSet::new())),
        }
    }

    /// Load previously blocked MACs from file
    fn load_blocklist(&self) -> Result<(), String> {
        let mut macs = self.blocked_macs.lock().unwrap();
        
        match fs::read_to_string(BLOCK_LOG_FILE) {
            Ok(contents) => {
                match serde_json::from_str::<BlocklistData>(&contents) {
                    Ok(data) => {
                        *macs = data.blocked_macs.into_iter().collect();
                        println!("📋 Loaded {} previously blocked MACs", macs.len());
                        Ok(())
                    }
                    Err(e) => {
                        println!("📋 Error parsing blocklist: {}", e);
                        Ok(())
                    }
                }
            }
            Err(_) => {
                println!("📋 No previous blocklist found, starting fresh");
                Ok(())
            }
        }
    }

    /// Save blocked MACs to file
    fn save_blocklist(&self) -> Result<(), String> {
        // Create logs directory if it doesn't exist
        fs::create_dir_all("logs")
            .map_err(|e| format!("Failed to create logs directory: {}", e))?;

        let macs = self.blocked_macs.lock().unwrap();
        let data = BlocklistData {
            blocked_macs: macs.iter().cloned().collect(),
            last_updated: Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
            total_blocked: macs.len(),
        };

        let json = serde_json::to_string_pretty(&data)
            .map_err(|e| format!("Failed to serialize data: {}", e))?;

        fs::write(BLOCK_LOG_FILE, json)
            .map_err(|e| format!("Failed to write blocklist: {}", e))?;

        Ok(())
    }

    /// Validate MAC address format
    fn is_valid_mac(&self, mac: &str) -> bool {
        MAC_REGEX.is_match(mac)
    }

    /// Block a MAC address
    fn block_mac(&self, mac: &str) -> Result<String, String> {
        let mac_lower = mac.to_lowercase();
        let mut macs = self.blocked_macs.lock().unwrap();

        if macs.contains(&mac_lower) {
            return Ok(format!(
                "MAC {} already blocked (total: {})",
                mac,
                macs.len()
            ));
        }

        // Add to blocklist
        macs.insert(mac_lower.clone());
        drop(macs); // Release lock before saving

        // Save to persistent storage
        self.save_blocklist()?;

        // Execute nftables command for actual blocking
        let command = format!(
            "nft add rule inet filter input ether saddr {} drop",
            mac_lower
        );
        
        let status = std::process::Command::new("sh")
            .arg("-c")
            .arg(&command)
            .status();

        match status {
            Ok(s) if s.success() => {
                println!("✅ Added {} to blocklist (nftables rule created)", mac);
                Ok(format!(
                    "Successfully added {} to blocklist (total: {})",
                    mac,
                    self.blocked_macs.lock().unwrap().len()
                ))
            }
            Ok(_) => {
                println!("⚠  Added {} to blocklist (nftables command failed)", mac);
                Ok(format!(
                    "Added {} to blocklist, but nftables rule failed",
                    mac
                ))
            }
            Err(e) => {
                println!("⚠  Added {} to blocklist (nftables error: {})", mac, e);
                Ok(format!(
                    "Added {} to blocklist, but nftables unavailable",
                    mac
                ))
            }
        }
    }

    /// Unblock a MAC address
    fn unblock_mac(&self, mac: &str) -> Result<String, String> {
        let mac_lower = mac.to_lowercase();
        let mut macs = self.blocked_macs.lock().unwrap();

        if !macs.contains(&mac_lower) {
            return Err(format!("MAC {} not in blocklist", mac));
        }

        macs.remove(&mac_lower);
        drop(macs); // Release lock before saving

        // Save to persistent storage
        self.save_blocklist()?;

        // Remove nftables rule
        let command = format!(
            "nft delete rule inet filter input ether saddr {} drop",
            mac_lower
        );
        
        let _ = std::process::Command::new("sh")
            .arg("-c")
            .arg(&command)
            .status();

        println!("♻  Removed {} from blocklist", mac);
        Ok(format!("Removed {} from blocklist", mac))
    }

    /// Check if MAC is blocked
    fn is_blocked(&self, mac: &str) -> bool {
        let mac_lower = mac.to_lowercase();
        let macs = self.blocked_macs.lock().unwrap();
        macs.contains(&mac_lower)
    }

    /// Get list of all blocked MACs
    fn get_blocklist(&self) -> Vec<String> {
        let macs = self.blocked_macs.lock().unwrap();
        macs.iter().cloned().collect()
    }

    /// Handle client connection and commands
    fn handle_client(&self, mut stream: TcpStream) {
        let peer = stream
            .peer_addr()
            .map(|a| a.to_string())
            .unwrap_or_else(|_| "unknown".to_string());
        
        println!("🔗 New connection from {}", peer);

        let reader = BufReader::new(match stream.try_clone() {
            Ok(s) => s,
            Err(_) => return,
        });

        for line in reader.lines() {
            let data = match line {
                Ok(l) => l.trim().to_string(),
                Err(_) => break,
            };

            if data.is_empty() {
                continue;
            }

            // Parse command
            let parts: Vec<&str> = data.split_whitespace().collect();
            let command = parts.get(0).map(|s| s.to_uppercase()).unwrap_or_default();
            let mac = parts.get(1).unwrap_or(&data.as_str()).to_string();

            let response = match command.as_str() {
                "UNBLOCK" => {
                    if !self.is_valid_mac(&mac) {
                        println!("⚠  Invalid MAC address format: {}", mac);
                        format!("Invalid MAC address format: {}\n", mac)
                    } else {
                        match self.unblock_mac(&mac) {
                            Ok(msg) => {
                                println!("♻  {}", msg);
                                format!("{}\n", msg)
                            }
                            Err(msg) => {
                                println!("⚠  {}", msg);
                                format!("{}\n", msg)
                            }
                        }
                    }
                }
                "LIST" => {
                    let macs = self.get_blocklist();
                    println!("📋 Sent blocklist: {} MACs", macs.len());
                    format!("Blocked MACs ({}): {}\n", macs.len(), macs.join(", "))
                }
                "CHECK" => {
                    if !self.is_valid_mac(&mac) {
                        format!("Invalid MAC address format: {}\n", mac)
                    } else {
                        let blocked = self.is_blocked(&mac);
                        format!(
                            "MAC {}: {}\n",
                            mac,
                            if blocked { "BLOCKED" } else { "NOT BLOCKED" }
                        )
                    }
                }
                _ => {
                    // Default: Block MAC
                    let mac_to_block = data.trim();
                    println!("🚫 Block request for MAC: {}", mac_to_block);

                    if !self.is_valid_mac(mac_to_block) {
                        println!("⚠  Invalid MAC address format: {}", mac_to_block);
                        format!("Invalid MAC address format: {}\n", mac_to_block)
                    } else {
                        match self.block_mac(mac_to_block) {
                            Ok(msg) => {
                                println!("✅ {}", msg);
                                format!("Blocked MAC: {}\n", mac_to_block)
                            }
                            Err(msg) => {
                                println!("❌ Failed to block {}: {}", mac_to_block, msg);
                                format!("Failed to block {}: {}\n", mac_to_block, msg)
                            }
                        }
                    }
                }
            };

            if let Err(e) = stream.write_all(response.as_bytes()) {
                eprintln!("Failed to send response to {}: {}", peer, e);
                break;
            }
        }
    }
}

fn main() -> std::io::Result<()> {
    println!("======================================================================");
    println!("🔥 Shakti Firewall Server (Rust Edition)");
    println!("======================================================================");
    println!("🌐 Listening on {}:{}", HOST, PORT);
    println!();
    println!("📝 Commands:");
    println!("   <MAC>          - Block MAC address");
    println!("   UNBLOCK <MAC>  - Unblock MAC address");
    println!("   LIST           - Show all blocked MACs");
    println!("   CHECK <MAC>    - Check if MAC is blocked");
    println!();
    println!("ℹ  Note: This maintains a persistent blocklist in logs/blocked_macs.json");
    println!("   Integrates with nftables for actual kernel-level blocking");
    println!();
    println!("Press Ctrl+C to stop");
    println!("======================================================================");
    println!();

    // Create firewall server
    let server = Arc::new(FirewallServer::new());

    // Load existing blocklist
    if let Err(e) = server.load_blocklist() {
        eprintln!("Warning: Failed to load blocklist: {}", e);
    }

    // Set up graceful shutdown
    let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();
    let server_shutdown = server.clone();

    ctrlc::set_handler(move || {
        r.store(false, Ordering::SeqCst);
        println!("\n🛑 Shutting down firewall server...");
        let macs = server_shutdown.blocked_macs.lock().unwrap();
        println!("📊 Final stats: {} MACs blocked", macs.len());
        drop(macs);
        if let Err(e) = server_shutdown.save_blocklist() {
            eprintln!("Warning: Failed to save blocklist: {}", e);
        }
        println!("✅ Server stopped");
        std::process::exit(0);
    })
    .expect("Error setting Ctrl+C handler");

    // Start TCP listener
    let listener = TcpListener::bind(format!("{}:{}", HOST, PORT))?;
    println!("✅ Server started successfully");

    for stream in listener.incoming() {
        if !running.load(Ordering::SeqCst) {
            break;
        }

        match stream {
            Ok(stream) => {
                let server = server.clone();
                std::thread::spawn(move || {
                    server.handle_client(stream);
                });
            }
            Err(e) => eprintln!("Connection failed: {}", e),
        }
    }

    Ok(())
}

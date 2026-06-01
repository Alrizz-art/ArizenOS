use tokio::signal;
use tracing::{info, warn};

mod config;
mod health;
mod ipc;
mod process_manager;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter("arizen_daemon=debug,info")
        .init();

    info!("ArizenOS Daemon v{} starting", env!("CARGO_PKG_VERSION"));

    let cfg = config::Config::load().await?;
    info!("Config loaded from {}", cfg.config_path.display());

    let pm         = process_manager::ProcessManager::new(cfg.clone()).await?;
    let ipc_server = ipc::IpcServer::new(cfg.clone(), pm.clone()).await?;

    tokio::select! {
        res = ipc_server.serve() => {
            if let Err(e) = res { warn!("IPC server error: {e}"); }
        }
        _ = signal::ctrl_c() => {
            info!("Shutdown signal received");
        }
    }

    info!("Daemon shutting down gracefully");
    pm.shutdown_all().await;
    Ok(())
}

//! LM Studio HTTP client (Rust side — used by runtime/daemon and Tauri backend).
//! Mirrors lm_studio.py for the Rust layer. Both target the same OpenAI-compatible API.

use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;

const DEFAULT_URL: &str = "http://localhost:1234";

#[derive(Debug, Clone)]
pub struct LMStudioClient {
    base_url: String,
    client:   Client,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ChatMessage {
    pub role:    String,
    pub content: String,
}

#[derive(Debug, Serialize)]
struct ChatRequest<'a> {
    model:       &'a str,
    messages:    &'a [ChatMessage],
    temperature: f32,
    max_tokens:  u32,
    stream:      bool,
}

#[derive(Debug, Deserialize)]
pub struct ModelList {
    pub data: Vec<ModelInfo>,
}

#[derive(Debug, Deserialize)]
pub struct ModelInfo {
    pub id: String,
}

impl LMStudioClient {
    pub fn new(base_url: Option<&str>) -> Self {
        let client = Client::builder()
            .timeout(Duration::from_secs(120))
            .build()
            .expect("failed to build reqwest client");

        Self {
            base_url: base_url.unwrap_or(DEFAULT_URL).trim_end_matches('/').to_string(),
            client,
        }
    }

    /// Returns true if LM Studio is reachable.
    pub async fn health_check(&self) -> bool {
        self.client
            .get(format!("{}/v1/models", self.base_url))
            .timeout(Duration::from_secs(3))
            .send()
            .await
            .map(|r| r.status().is_success())
            .unwrap_or(false)
    }

    /// List loaded model IDs.
    pub async fn list_models(&self) -> anyhow::Result<Vec<String>> {
        let resp: ModelList = self
            .client
            .get(format!("{}/v1/models", self.base_url))
            .send()
            .await?
            .json()
            .await?;
        Ok(resp.data.into_iter().map(|m| m.id).collect())
    }
}

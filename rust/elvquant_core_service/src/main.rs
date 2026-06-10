use std::collections::BTreeMap;
use std::env;
use std::net::SocketAddr;
use std::sync::{Arc, RwLock};

use axum::extract::{Path, State};
use axum::http::{HeaderMap, StatusCode};
use axum::routing::{get, post};
use axum::{Json, Router};
use elvquant_core_math::{max_drawdown, total_return};
use elvquant_core_types::{ArtifactRef, EquityPoint, RunSummary, StructuredReport, WorkflowDescriptor};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone)]
struct AppState {
    service_token: String,
    runs: Arc<RwLock<BTreeMap<String, OwnerRun>>>,
}

#[derive(Clone)]
struct OwnerRun {
    owner_user_id: String,
    report: StructuredReport,
}

#[derive(Deserialize)]
struct RunCreateRequest {
    #[serde(rename = "workflowId")]
    workflow_id: String,
}

#[derive(Serialize)]
struct HealthResponse {
    ok: bool,
    version: &'static str,
}

#[derive(Serialize)]
struct WorkflowsResponse {
    workflows: Vec<WorkflowDescriptor>,
}

#[derive(Serialize)]
struct RunsResponse {
    runs: Vec<RunSummary>,
}

#[derive(Serialize)]
struct RunCreateResponse {
    #[serde(rename = "runId")]
    run_id: String,
    status: String,
}

#[tokio::main]
async fn main() {
    let host = env::args().skip_while(|arg| arg != "--host").nth(1).unwrap_or("127.0.0.1".to_string());
    let port = env::args().skip_while(|arg| arg != "--port").nth(1).unwrap_or("8010".to_string());
    let addr: SocketAddr = format!("{host}:{port}").parse().expect("valid socket address");
    let state = AppState {
        service_token: env::var("ELVQUANT_API_SERVICE_TOKEN").unwrap_or_else(|_| "dev-token".to_string()),
        runs: Arc::new(RwLock::new(BTreeMap::new())),
    };
    let app = router(state);
    let listener = tokio::net::TcpListener::bind(addr).await.expect("bind listener");
    axum::serve(listener, app).await.expect("serve app");
}

fn router(state: AppState) -> Router {
    Router::new()
        .route("/health", get(health))
        .route("/workflows", get(workflows))
        .route("/runs", get(list_runs).post(create_run))
        .route("/runs/{run_id}", get(get_run))
        .with_state(state)
}

async fn health() -> Json<HealthResponse> {
    Json(HealthResponse { ok: true, version: "0.1.0" })
}

async fn workflows(State(state): State<AppState>, headers: HeaderMap) -> Result<Json<WorkflowsResponse>, StatusCode> {
    authorize(&state, &headers)?;
    Ok(Json(WorkflowsResponse { workflows: workflow_catalog() }))
}

async fn list_runs(State(state): State<AppState>, headers: HeaderMap) -> Result<Json<RunsResponse>, StatusCode> {
    let owner = authorize(&state, &headers)?;
    let runs = state.runs.read().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    let summaries = runs
        .values()
        .filter(|record| record.owner_user_id == owner)
        .map(|record| RunSummary {
            run_id: record.report.run_id.clone(),
            workflow: record.report.workflow.clone(),
            status: record.report.status.clone(),
            metrics: record.report.metrics.clone(),
        })
        .collect();
    Ok(Json(RunsResponse { runs: summaries }))
}

async fn create_run(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(request): Json<RunCreateRequest>,
) -> Result<Json<RunCreateResponse>, StatusCode> {
    let owner = authorize(&state, &headers)?;
    if request.workflow_id != "synthetic_demo" {
        return Err(StatusCode::BAD_REQUEST);
    }
    let report = synthetic_demo_report();
    let response = RunCreateResponse { run_id: report.run_id.clone(), status: report.status.clone() };
    state
        .runs
        .write()
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
        .insert(report.run_id.clone(), OwnerRun { owner_user_id: owner, report });
    Ok(Json(response))
}

async fn get_run(
    State(state): State<AppState>,
    headers: HeaderMap,
    Path(run_id): Path<String>,
) -> Result<Json<StructuredReport>, StatusCode> {
    let owner = authorize(&state, &headers)?;
    let runs = state.runs.read().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    let record = runs.get(&run_id).ok_or(StatusCode::NOT_FOUND)?;
    if record.owner_user_id != owner {
        return Err(StatusCode::NOT_FOUND);
    }
    Ok(Json(record.report.clone()))
}

fn authorize(state: &AppState, headers: &HeaderMap) -> Result<String, StatusCode> {
    let token = headers
        .get("X-Service-Token")
        .and_then(|value| value.to_str().ok())
        .ok_or(StatusCode::UNAUTHORIZED)?;
    if token != state.service_token {
        return Err(StatusCode::UNAUTHORIZED);
    }
    headers
        .get("X-Owner-User-Id")
        .and_then(|value| value.to_str().ok())
        .map(|value| value.to_string())
        .ok_or(StatusCode::UNAUTHORIZED)
}

fn workflow_catalog() -> Vec<WorkflowDescriptor> {
    vec![WorkflowDescriptor {
        id: "synthetic_demo".to_string(),
        label: "Synthetic demo".to_string(),
        description: "Deterministic synthetic backtest served by Rust.".to_string(),
        requires_data: false,
    }]
}

fn synthetic_demo_report() -> StructuredReport {
    let run_id = format!("rust-synthetic-{}", Uuid::new_v4());
    let curve = vec![
        EquityPoint { as_of: "2026-01-01T00:00:00+00:00".to_string(), cash: 10000.0, positions: BTreeMap::new(), equity: 10000.0, cumulative_cost: 0.0 },
        EquityPoint { as_of: "2026-01-02T00:00:00+00:00".to_string(), cash: 100.0, positions: BTreeMap::from([("AAA".to_string(), 33.0), ("BBB".to_string(), 30.0)]), equity: 10060.0, cumulative_cost: 0.0 },
        EquityPoint { as_of: "2026-01-03T00:00:00+00:00".to_string(), cash: 100.0, positions: BTreeMap::from([("AAA".to_string(), 33.0), ("BBB".to_string(), 30.0)]), equity: 10120.0, cumulative_cost: 0.0 },
    ];
    let values: Vec<f64> = curve.iter().map(|point| point.equity).collect();
    let mut metadata = BTreeMap::new();
    metadata.insert("git_commit".to_string(), "rust-service-dev".to_string());
    metadata.insert("config_hash".to_string(), "rust-synthetic".to_string());
    metadata.insert("data_version".to_string(), "synthetic-v1".to_string());
    metadata.insert("seed".to_string(), "deterministic".to_string());
    metadata.insert("start".to_string(), "2026-01-01T00:00:00+00:00".to_string());
    metadata.insert("end".to_string(), "2026-01-03T00:00:00+00:00".to_string());
    StructuredReport {
        run_id,
        workflow: "synthetic_demo".to_string(),
        status: "completed".to_string(),
        metadata,
        config_summary: BTreeMap::from([("workflow".to_string(), "synthetic_demo".to_string())]),
        metrics: BTreeMap::from([
            ("net_value".to_string(), values[values.len() - 1] / values[0]),
            ("total_return".to_string(), total_return(&values).unwrap()),
            ("max_drawdown".to_string(), max_drawdown(&values).unwrap()),
        ]),
        final_positions: curve.last().map(|point| point.positions.clone()).unwrap_or_default(),
        equity_curve: curve,
        artifacts: vec![ArtifactRef { kind: "json".to_string(), path_or_url: "inline".to_string(), content_type: "application/json".to_string() }],
        warnings: vec!["Rust service foundation covers synthetic_demo only".to_string()],
    }
}

use std::collections::BTreeMap;

use serde::Deserialize;
use serde::Serialize;

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct ArtifactRef {
    pub kind: String,
    pub path_or_url: String,
    pub content_type: String,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct EquityPoint {
    pub as_of: String,
    pub cash: f64,
    pub positions: BTreeMap<String, f64>,
    pub equity: f64,
    pub cumulative_cost: f64,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct StructuredReport {
    pub run_id: String,
    pub workflow: String,
    pub status: String,
    pub metadata: BTreeMap<String, String>,
    pub config_summary: BTreeMap<String, String>,
    pub metrics: BTreeMap<String, f64>,
    pub equity_curve: Vec<EquityPoint>,
    pub final_positions: BTreeMap<String, f64>,
    pub artifacts: Vec<ArtifactRef>,
    pub warnings: Vec<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct WorkflowDescriptor {
    pub id: String,
    pub label: String,
    pub description: String,
    #[serde(rename = "requiresData")]
    pub requires_data: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct RunSummary {
    #[serde(rename = "runId")]
    pub run_id: String,
    pub workflow: String,
    pub status: String,
    pub metrics: BTreeMap<String, f64>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn serializes_python_compatible_field_names() {
        let summary = RunSummary {
            run_id: "run-1".to_string(),
            workflow: "synthetic_demo".to_string(),
            status: "completed".to_string(),
            metrics: BTreeMap::new(),
        };

        let payload = serde_json::to_value(summary).expect("summary serializes");
        assert_eq!(payload["runId"], "run-1");
    }
}

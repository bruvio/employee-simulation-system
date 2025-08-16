#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union

from logger import LOGGER


class MarkdownReportBuilder:
    """
    Markdown report builder with Mermaid diagram support for GEL scenario.

    Generates narrative reports with coherent storylines about population structure, inequality, high-performer rewards,
    and recommended actions.
    """

    def __init__(self, output_dir: Union[str, Path] = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = LOGGER

    def build_gel_report(
        self, analysis_payload: Dict[str, Any], manifest: Dict[str, Any], output_file: str = "report.md"
    ) -> Path:
        """
        Build comprehensive GEL scenario report with Mermaid diagrams.

        Args:
            analysis_payload: Complete analysis results from orchestrator
            manifest: Run manifest with metadata and KPIs
            output_file: Output filename

        Returns:
            Path to generated report file
        """
        self.logger.info("Building GEL scenario Markdown report")

        report_path = self.output_dir / output_file

        with open(report_path, "w", encoding="utf-8") as f:
            # Write report sections
            f.write(self._generate_header(manifest))
            f.write(self._generate_overview_and_inputs(manifest, analysis_payload))
            f.write(self._generate_data_flow_diagram())
            f.write(self._generate_population_stratification(analysis_payload))
            f.write(self._generate_inequality_and_risk(analysis_payload, manifest))
            f.write(self._generate_high_performer_recognition(analysis_payload, manifest))
            f.write(self._generate_manager_budget_diagram(manifest))
            f.write(self._generate_recommendations(analysis_payload, manifest))
            f.write(self._generate_appendix(manifest, analysis_payload))

        self.logger.info(f"Generated Markdown report: {report_path}")
        return report_path

    def _generate_header(self, manifest: Dict[str, Any]) -> str:
        """
        Generate report header and title.
        """
        org = manifest.get("org", "Unknown")
        timestamp = manifest.get("timestamp_utc", datetime.utcnow().isoformat())
        scenario = manifest.get("scenario", "GEL")

        return f"""# {org} Employee Analysis Report - {scenario} Scenario

**Generated:** {timestamp}
**Scenario:** {scenario}
**Organization:** {org}

---

"""

    def _generate_overview_and_inputs(self, manifest: Dict[str, Any], analysis_payload: Dict[str, Any]) -> str:
        """
        Generate overview and inputs section.
        """
        population = manifest.get("population", "Unknown")
        seed = manifest.get("random_seed", "Unknown")
        roles_config_hash = manifest.get("roles_config_sha256", "Unknown")
        coverage = analysis_payload.get("population_coverage", "100%")

        return f"""## 1. Overview & Inputs {{#overview}}

### Scenario Configuration
- **Scenario Type:** {manifest.get("scenario", "GEL")}
- **Analysis Date:** {manifest.get("timestamp_utc", "Unknown")}
- **Random Seed:** {seed}
- **Configuration Hash:** `{roles_config_hash[:16]}...`

### Population Overview
- **Total Population:** {population:,} employees
- **Analysis Coverage:** {coverage}
- **Currency:** {manifest.get("currency", "GBP")}

### Key Performance Indicators
- **Median Salary:** £{manifest.get("median_salary", 0):,.2f}
- **Below-Median Employees:** {manifest.get("below_median_pct", 0):.1f}%
- **Gender Pay Gap:** {manifest.get("gender_gap_pct", 0):.1f}%
- **Intervention Budget Available:** {manifest.get("intervention_budget_pct", 0.5):.1f}% of payroll

---

"""

    def _generate_data_flow_diagram(self) -> str:
        """
        Generate Mermaid data flow diagram.
        """
        return """## 2. Data Flow Overview {{#dataflow}}

The following diagram illustrates how data flows through the GEL scenario analysis:

```mermaid
flowchart LR
    A[Population Generation] --> B[Role Minimums Validation]
    B --> C[Simulation Engine]
    C --> D[Analysis Modules]
    D --> E[Policy Constraints]
    E --> F[Manager Budget Allocation]
    F --> G[Report Builder]
    G --> H[index.html]
    G --> I[report.md]

    subgraph "Analysis Modules"
        D1[Median Convergence]
        D2[Gender Gap Analysis]
        D3[High Performer Identification]
        D4[Intervention Modeling]
    end
    
    subgraph "Policy Constraints"
        E1[≤ 6 Direct Reports]
        E2[0.5% Budget Cap]
        E3[Role Minimum Compliance]
    end
```

---

"""

    def _generate_population_stratification(self, analysis_payload: Dict[str, Any]) -> str:
        """
        Generate population stratification section.
        """
        stratification = analysis_payload.get("population_stratification", {})

        content = """## 3. Population Stratification {{#stratification}}

### By Level and Role
"""

        # Add level distribution if available
        if "by_level" in stratification:
            content += "\n| Level | Count | Median Salary | Gender Split |\n"
            content += "|-------|-------|---------------|-------------|\n"

            for level, data in stratification["by_level"].items():
                count = data.get("count", 0)
                median = data.get("median_salary", 0)
                gender_split = data.get("gender_split", "N/A")
                content += f"| {level} | {count:,} | £{median:,.2f} | {gender_split} |\n"

        # Add manager distribution
        content += """
### Manager Distribution
"""

        manager_data = stratification.get("managers", {})
        if manager_data:
            total_managers = manager_data.get("total_managers", 0)
            avg_reports = manager_data.get("average_direct_reports", 0)
            max_reports = manager_data.get("max_direct_reports", 0)

            content += f"""
- **Total Managers:** {total_managers:,}
- **Average Direct Reports:** {avg_reports:.1f}
- **Maximum Direct Reports:** {max_reports}
- **Managers at Policy Limit (6):** {manager_data.get("at_policy_limit", 0)}
"""

        content += """
### Population Stratification Diagram

```mermaid
graph TD
    A[Total Population] --> B[Individual Contributors]
    A --> C[Managers]
    
    B --> B1[Junior Levels 1-2]
    B --> B2[Mid Levels 3-4]
    B --> B3[Senior Levels 5-6]
    
    C --> C1[Team Leads]
    C --> C2[Department Heads]
    C --> C3[Directors]
    
    style B1 fill:#e1f5fe
    style B2 fill:#b3e5fc
    style B3 fill:#81d4fa
    style C1 fill:#fff3e0
    style C2 fill:#ffe0b2
    style C3 fill:#ffcc02
```

---

"""
        return content

    def _generate_inequality_and_risk(self, analysis_payload: Dict[str, Any], manifest: Dict[str, Any]) -> str:
        """
        Generate inequality and risk analysis section.
        """
        inequality_data = analysis_payload.get("inequality_analysis", {})

        content = """## 4. Inequality & Risk Analysis {#inequality}

### Key Findings

"""

        # Below-median analysis
        below_median_pct = manifest.get("below_median_pct", 0)
        gender_gap_pct = manifest.get("gender_gap_pct", 0)

        content += f"""
- **Below-Median Population:** {below_median_pct:.1f}% of employees earn below their level median
- **Gender Pay Gap:** {gender_gap_pct:.1f}% overall gap requiring attention  
- **Risk Level:** {"High" if below_median_pct > 40 else "Medium" if below_median_pct > 25 else "Low"}

"""

        # Role minimum compliance
        role_compliance = inequality_data.get("role_minimum_compliance", {})
        if role_compliance:
            violations = role_compliance.get("violations", 0)
            total_checked = role_compliance.get("total_employees", 0)

            content += f"""### Role Minimum Compliance

- **Employees Below Role Minimums:** {violations}
- **Compliance Rate:** {((total_checked - violations) / max(total_checked, 1) * 100):.1f}%
"""

        # Gap estimates by segment
        content += """
### Gap Analysis by Segment

| Segment | Affected Employees | Average Gap | Total Cost to Close |
|---------|-------------------|-------------|-------------------|
"""

        segments = inequality_data.get("segments", {})
        for segment_name, segment_data in segments.items():
            affected = segment_data.get("affected_count", 0)
            avg_gap = segment_data.get("average_gap", 0)
            total_cost = segment_data.get("total_cost", 0)
            content += f"| {segment_name} | {affected} | £{avg_gap:,.2f} | £{total_cost:,.2f} |\n"

        content += """
---

"""
        return content

    def _generate_high_performer_recognition(self, analysis_payload: Dict[str, Any], manifest: Dict[str, Any]) -> str:
        """
        Generate high performer recognition section.
        """
        high_performers = analysis_payload.get("high_performers", {})
        budget_pct = manifest.get("intervention_budget_pct", 0.5)

        content = f"""## 5. High-Performer Recognition (within constraints) {{#highperformers}}

### Policy Framework
- **Budget Constraint:** {budget_pct}% of payroll per manager
- **Manager Limit:** Maximum 6 direct reports per manager
- **Priority:** Below-median high performers receive first consideration

"""

        # High performer statistics
        total_high_performers = high_performers.get("total_identified", 0)
        eligible_for_uplift = high_performers.get("eligible_for_uplift", 0)
        estimated_cost = high_performers.get("estimated_uplift_cost_pct", 0)

        content += f"""### Recognition Analysis

- **High Performers Identified:** {total_high_performers:,}
- **Eligible for Immediate Uplift:** {eligible_for_uplift:,}
- **Estimated Cost:** {estimated_cost:.2f}% of total payroll
- **Budget Utilization:** {(estimated_cost / budget_pct * 100):.1f}% of available budget

"""

        # Trade-offs within budget
        trade_offs = high_performers.get("trade_offs", [])
        if trade_offs:
            content += """### Budget Trade-offs

The following trade-offs were considered within the 0.5% budget constraint:

"""
            for i, trade_off in enumerate(trade_offs[:5], 1):  # Show top 5
                employee_id = trade_off.get("employee_id", f"EMP{i}")
                current_salary = trade_off.get("current_salary", 0)
                proposed_uplift = trade_off.get("proposed_uplift", 0)
                impact = trade_off.get("inequality_impact", "Unknown")

                content += f"""
**Option {i}:** Employee {employee_id}
- Current Salary: £{current_salary:,.2f}
- Proposed Uplift: £{proposed_uplift:,.2f}
- Inequality Impact: {impact}
"""

        content += """
---

"""
        return content

    def _generate_manager_budget_diagram(self, manifest: Dict[str, Any]) -> str:
        """
        Generate Mermaid diagram for manager budget allocation.
        """
        max_reports = manifest.get("max_direct_reports", 6)
        budget_pct = manifest.get("intervention_budget_pct", 0.5)

        return f"""## 6. Manager Budget Allocation Process {{#budgetallocation}}

The following diagram shows how budget allocation decisions are made for each manager:

```mermaid
flowchart TD
    M[Manager with ≤ {max_reports} directs] --> B{{"{budget_pct}% budget available?"}}
    
    B -->|Yes| P{{Identify priorities}}
    B -->|No| N1[No budget available]
    
    P --> P1{{"Below-median employees?"}}
    P --> P2{{"High performers?"}}
    
    P1 -->|Yes| HP1{{"Also high performer?"}}
    P1 -->|No| P3[Standard progression]
    
    P2 -->|Yes| HP2{{"Below median salary?"}}
    P2 -->|No| P4[Performance bonus only]
    
    HP1 -->|Yes| A1[Priority 1: Recommend Uplift]
    HP1 -->|No| A2[Priority 2: Monitor closely]
    
    HP2 -->|Yes| A1
    HP2 -->|No| A3[Priority 3: Recognition only]
    
    A1 --> R[Recalculate Inequality KPIs]
    A2 --> R
    A3 --> R
    
    R --> R1{{Within budget cap?}}
    
    R1 -->|Yes| OK[Accept recommendations]
    R1 -->|No| T[Trim recommendations to fit budget]
    
    T --> S[Stage remaining for next cycle]
    
    style A1 fill:#c8e6c9
    style OK fill:#4caf50
    style T fill:#fff3e0
    style N1 fill:#ffcdd2
```

---

"""

    def _generate_recommendations(self, analysis_payload: Dict[str, Any], manifest: Dict[str, Any]) -> str:
        """
        Generate targeted recommendations section.
        """
        recommendations = analysis_payload.get("recommendations", {})

        content = """## 7. Targeted Recommendations {{#recommendations}}

### Immediate Actions

"""

        immediate_actions = recommendations.get("immediate", [])
        for i, action in enumerate(immediate_actions, 1):
            employee_info = action.get("employee", "Unknown")
            current_salary = action.get("current_salary", 0)
            proposed_uplift = action.get("proposed_uplift", 0)
            expected_impact = action.get("expected_impact", "Unknown")

            content += f"""
**Action {i}:** {action.get('action_type', 'Salary Adjustment')}
- **Employee:** {employee_info}
- **Current Salary:** £{current_salary:,.2f}
- **Recommended Adjustment:** £{proposed_uplift:,.2f} ({(proposed_uplift/max(current_salary, 1)*100):+.1f}%)
- **Expected Impact:** {expected_impact}
"""

        # Medium-term strategies
        content += """
### Medium-Term Strategies (6-12 months)

"""
        medium_term = recommendations.get("medium_term", [])
        for strategy in medium_term:
            content += f"- **{strategy.get('title', 'Strategy')}:** {strategy.get('description', 'No description')}\n"
            if cost := strategy.get("estimated_cost"):
                content += f"  - *Estimated Cost:* £{cost:,.2f}\n"

        # Success metrics
        content += """
### Success Metrics

The following metrics should be tracked to measure the effectiveness of interventions:

"""

        metrics = recommendations.get("success_metrics", [])
        for metric in metrics:
            content += f"- **{metric.get('name', 'Metric')}:** {metric.get('description', 'No description')}\n"
            if target := metric.get("target_value"):
                content += f"  - *Target:* {target}\n"

        content += """
---

"""
        return content

    def _generate_appendix(self, manifest: Dict[str, Any], analysis_payload: Dict[str, Any]) -> str:
        """
        Generate appendix with assumptions and references.
        """
        config_hash = manifest.get("roles_config_sha256", "Unknown")

        return f"""## 8. Appendix {{#appendix}}

### Assumptions

- **Currency:** All amounts in {manifest.get("currency", "GBP")}
- **Budget Period:** Annual budget allocations
- **Manager Constraints:** Maximum 6 direct reports per manager
- **Budget Constraint:** {manifest.get("intervention_budget_pct", 0.5)}% of manager's team payroll for interventions
- **Role Minimums:** Enforced according to configuration version {manifest.get("config_version", 1)}

### Data Dictionary

| Term | Definition |
|------|------------|
| Below-median | Employees earning less than the median for their level and gender |
| High performer | Employees with performance ratings above 4.0/5.0 |
| Intervention budget | {manifest.get("intervention_budget_pct", 0.5)}% of payroll available for salary adjustments |
| Role minimum | Minimum acceptable salary for a specific job title |
| Gender pay gap | Percentage difference in median salaries between genders |

### Role Minima Reference

**Configuration Hash:** `{config_hash}`  
**Total Roles Configured:** {len(analysis_payload.get("role_config", {}).get("roles", []))}

Selected role minimums:
"""

        # Add sample of role minimums
        roles = analysis_payload.get("role_config", {}).get("roles", [])
        for role in roles[:10]:  # Show first 10 roles
            title = role.get("title", "Unknown")
            min_salary = min(role.get("min_salaries", [0]))
            if "content" not in locals():
                content = ""
            content += f"- **{title}:** £{min_salary:,.2f}\n"

        if len(roles) > 10:
            content += f"- *... and {len(roles) - 10} more roles*\n"

        content += f"""
### Reproducibility Notes

- **Random Seed:** {manifest.get("random_seed", "Unknown")}
- **Analysis Date:** {manifest.get("timestamp_utc", "Unknown")}
- **Configuration Hash:** `{config_hash}`
- **Population Size:** {manifest.get("population", 0):,} employees

To reproduce this analysis, use:
```bash
python employee_simulation_orchestrator.py \\
  --scenario GEL \\
  --org GEL \\
  --roles-config config/orgs/GEL/roles.yaml \\
  --report \\
  --random-seed {manifest.get("random_seed", 42)}
```

---

*Report generated by Employee Simulation Orchestrator - GEL Scenario*  
*Generated at: {datetime.utcnow().isoformat()}Z*
"""

        return content


def create_sample_analysis_payload() -> Dict[str, Any]:
    """
    Create sample analysis payload for testing.
    """
    return {
        "population_stratification": {
            "by_level": {
                "Level 1": {"count": 45, "median_salary": 32000, "gender_split": "55% F / 45% M"},
                "Level 2": {"count": 67, "median_salary": 58000, "gender_split": "48% F / 52% M"},
                "Level 3": {"count": 89, "median_salary": 78000, "gender_split": "43% F / 57% M"},
            },
            "managers": {
                "total_managers": 25,
                "average_direct_reports": 3.8,
                "max_direct_reports": 6,
                "at_policy_limit": 3,
            },
        },
        "inequality_analysis": {
            "role_minimum_compliance": {"violations": 8, "total_employees": 201},
            "segments": {
                "Below-median Female": {"affected_count": 23, "average_gap": 4500, "total_cost": 103500},
                "Below-median Male": {"affected_count": 15, "average_gap": 3200, "total_cost": 48000},
            },
        },
        "high_performers": {
            "total_identified": 34,
            "eligible_for_uplift": 18,
            "estimated_uplift_cost_pct": 0.45,
            "trade_offs": [
                {
                    "employee_id": "EMP_2341",
                    "current_salary": 67000,
                    "proposed_uplift": 5500,
                    "inequality_impact": "Reduces gender gap by 0.3%",
                }
            ],
        },
        "recommendations": {
            "immediate": [
                {
                    "action_type": "Salary Adjustment",
                    "employee": "Data Engineer (Level 3)",
                    "current_salary": 67000,
                    "proposed_uplift": 5500,
                    "expected_impact": "Brings to role minimum, reduces gap",
                }
            ],
            "medium_term": [
                {
                    "title": "Review Role Bands",
                    "description": "Analyze roles with multiple salary bands for optimization",
                    "estimated_cost": 25000,
                }
            ],
            "success_metrics": [
                {
                    "name": "Gender Pay Gap",
                    "description": "Overall percentage gap between genders",
                    "target_value": "< 5%",
                }
            ],
        },
        "role_config": {
            "roles": [
                {"title": "Data Engineer", "min_salaries": [73000]},
                {"title": "Platform Engineer", "min_salaries": [71500]},
                {"title": "QA Engineer - Python", "min_salaries": [53500]},
            ]
        },
    }


if __name__ == "__main__":
    # Test the report builder
    builder = MarkdownReportBuilder(output_dir="test_output")

    # Create sample data
    sample_manifest = {
        "scenario": "GEL",
        "org": "GEL",
        "timestamp_utc": "2025-08-14T10:00:00Z",
        "population": 201,
        "median_salary": 71500,
        "below_median_pct": 42.3,
        "gender_gap_pct": 6.8,
        "intervention_budget_pct": 0.5,
        "roles_config_sha256": "8689a92285a3a305d8f4c87c2a54f3b7e1d29c6f8b7a4e5d3c2b1a9f8e7d6c5b4",
        "random_seed": 42,
        "currency": "GBP",
        "config_version": 1,
    }

    sample_payload = create_sample_analysis_payload()

    # Generate report
    report_path = builder.build_gel_report(sample_payload, sample_manifest)
    print(f"Generated test report: {report_path}")

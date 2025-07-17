# Echo Resonance Custom Dashboards Guide

This guide provides instructions for setting up custom dashboards for the Echo Resonance project in Jira.

## Dashboard Overview

Four custom dashboards are recommended for the Echo Resonance project:

1. **Executive Overview Dashboard**
2. **Team Progress Dashboard**
3. **Technical Implementation Dashboard**
4. **Stella's DevOps-MCP Command Board** (specialized board for DevOps-MCP team)

## Setup Instructions

### 1. Executive Overview Dashboard

This dashboard provides high-level visibility into the project's progress for leadership.

#### Gadgets to Include:

1. **Project Information**
   - Type: Project Information
   - Configuration: Select ER project

2. **Epic Burndown Chart**
   - Type: Burndown Chart
   - Configuration: 
     - Project: ER
     - Report Type: Epic Burndown
     - Epics: Select All
     - Time Scale: Days

3. **Epic Progress Pie Chart**
   - Type: Pie Chart
   - Configuration:
     - Project: ER
     - Statistic Type: Issues by Status
     - Issue Type: Epic
     - Group By: Status

4. **Team Allocation**
   - Type: Two Dimensional Filter Statistics
   - Configuration:
     - Project: ER
     - X-Axis: Component (Team)
     - Y-Axis: Issue Type

5. **Timeline with Key Milestones**
   - Type: Roadmap
   - Configuration: 
     - Project: ER
     - Issues: Epics
     - Group By: Component

### 2. Team Progress Dashboard

This dashboard provides team-specific progress tracking.

#### Gadgets to Include:

1. **Team Workload**
   - Type: Heat Map
   - Configuration:
     - Project: ER
     - X-Axis: Component (Team)
     - Y-Axis: Epic
     - Value: Issue Count

2. **Component Completion Status**
   - Type: Status Board
   - Configuration:
     - Project: ER
     - Group By: Component (Team)
     - Issues: All

3. **Cross-Team Dependencies Visualization**
   - Type: Issue Statistics
   - Configuration:
     - Project: ER
     - Group By: Component (Team)
     - Issues: All with Links

4. **Resource Allocation by Team**
   - Type: Two Dimensional Filter Statistics
   - Configuration:
     - Project: ER
     - X-Axis: Component (Team)
     - Y-Axis: Priority

5. **Filter Results - In Progress By Team**
   - Type: Filter Results
   - Configuration:
     - Project: ER
     - JQL: project = ER AND status = "In Progress" ORDER BY component

### 3. Technical Implementation Dashboard

This dashboard provides technical details and metrics for implementation teams.

#### Gadgets to Include:

1. **Component Completion Tracker**
   - Type: Status Board
   - Configuration:
     - Project: ER
     - Issues: All
     - Group By: Category Component

2. **Epic Dependencies Visualization**
   - Type: Issue Statistics
   - Configuration:
     - Project: ER
     - Group By: Epic
     - Issues: All with Links

3. **Technical Debt Tracker**
   - Type: Pie Chart
   - Configuration:
     - Project: ER
     - Statistic Type: Issues by Label
     - Issues: All with Label "technical-debt"

4. **Performance Metrics Table**
   - Type: Filter Results
   - Configuration:
     - Project: ER
     - JQL: project = ER AND labels in (performance, metrics)

5. **Integration Points Status**
   - Type: Status Board
   - Configuration:
     - Project: ER
     - Issues: All with Label "integration"
     - Group By: Status

## Creating a Dashboard in Jira

1. Navigate to Dashboards > Create Dashboard
2. Enter dashboard name (e.g., "ER - Executive Overview")
3. Add the gadgets as described above
4. Configure each gadget using the settings recommended
5. Arrange the gadgets in a logical layout
6. Save the dashboard and share with the appropriate teams

### 4. Stella's DevOps-MCP Command Board

This specialized dashboard is focused on DevOps-MCP team tasks led by Stella.

#### Gadgets to Include:

1. **DevOps-MCP Task List**
   - Type: Filter Results
   - Configuration:
     - Project: ER
     - JQL: project = ER AND component = "DevOps-MCP" ORDER BY status

2. **Redis + Redpanda Messaging Fabric Tracking**
   - Type: Issue Statistics
   - Configuration:
     - Project: ER
     - JQL: project = ER AND summary ~ "Redis" OR summary ~ "Redpanda" 
     - Group By: Status

3. **MCP Integration Status**
   - Type: Status Board
   - Configuration:
     - Project: ER
     - Issues: All with Component = "DevOps-MCP"
     - Group By: Status

4. **Team Velocity Chart**
   - Type: Velocity Chart
   - Configuration:
     - Project: ER
     - Team: DevOps-MCP
     - Time Period: Last 4 weeks

5. **Integration Points - DevOps-MCP**
   - Type: Two Dimensional Filter Statistics
   - Configuration:
     - Project: ER
     - X-Axis: Status
     - Y-Axis: Priority
     - Filter: component = "DevOps-MCP"

## Dashboard Links

After creation, the dashboards will be available at:

- Executive Overview: https://levelup2x.atlassian.net/jira/dashboards/[dashboard_id]
- Team Progress: https://levelup2x.atlassian.net/jira/dashboards/[dashboard_id]
- Technical Implementation: https://levelup2x.atlassian.net/jira/dashboards/[dashboard_id]
- Stella's DevOps-MCP Command Board: https://levelup2x.atlassian.net/jira/dashboards/[dashboard_id]

## Additional Dashboard Ideas

Other useful dashboards to consider:

1. **Timeline Visualization Dashboard**
   - Focus on project timeline and milestone tracking

2. **Risk Management Dashboard**
   - Track issues flagged as risks and their mitigation status

3. **Stakeholder Feedback Dashboard**
   - Track stakeholder feedback and related action items

4. **Performance Metrics Dashboard**
   - Focus exclusively on performance metrics across all components

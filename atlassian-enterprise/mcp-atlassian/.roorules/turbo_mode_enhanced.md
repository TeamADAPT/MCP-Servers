# Enhanced TURBO Mode Guidelines

## Overview
This document provides comprehensive guidelines for using Enhanced TURBO Mode (Continuous Execution Mode 2.0) for complex multi-phase deployments. This enhanced version includes integration with GitHub, Atlassian tools, improved clineplan structure, and comprehensive documentation standards.

## Activation Protocol

### Command Structure
To activate Enhanced TURBO Mode, use the following command pattern:
```
/new "Please implement [PLAN_NAME] in enhanced continuous execution mode. Continue working through all phases without stopping."
```

### Authorization Parameters
Always include the following authorization parameters:
```
I authorize autonomous execution through the entire deployment plan. Make necessary decisions to complete each phase. Only notify me for critical blockers requiring human intervention.
```

## GitHub Integration

### Repository Creation
- Repositories are automatically created using the project name or current working directory
- All repositories are created as private by default
- The GitHub CLI (`gh`) is used for all repository operations
- Do not attempt to re-authenticate as we maintain persistent authentication

### Branching Strategy
- Always use `main` as the default branch name
- Create feature branches for all development work
- Follow the branch naming convention: `${type}/${issueReference}-${description}`
- Valid branch types: feature, bugfix, hotfix, release, docs, chore

### Commit Standards
- Push changes frequently (at least hourly)
- Use the commit message template: `feat(${scope}): ${message}\n\n${description}\n\nResolves: ${issueReference}`
- Include detailed descriptions of changes
- Reference related issues in commit messages

### Pull Request Process
- Create pull requests for all feature branches
- Require at least one review before merging
- Ensure all status checks pass before merging
- Delete branches after merging

## Atlassian Integration

### Jira Project Management
- Create a Jira project at the start of each TURBO Mode execution
- Structure work using Epics, Stories, Tasks, and Sub-tasks
- Update issue status as work progresses
- Include name and department in all entries using custom fields
- Link related issues to track dependencies

### Confluence Documentation
- Create a Confluence space for each project
- Use standardized page templates for different document types
- Update documentation as the project progresses
- Attach relevant files to documentation pages
- Maintain version history for all documentation

### Required Documentation
1. **Project Overview**
   - High-level description of the project
   - Goals and objectives
   - Key stakeholders
   - Timeline and milestones

2. **Project Detail**
   - Steps completed
   - Next steps
   - Challenges and solutions
   - Suggested improvements
   - Files touched

3. **Architectural Diagrams**
   - System architecture
   - Component interactions
   - Data flow
   - Deployment architecture

4. **Technical Specifications**
   - Detailed technical requirements
   - API specifications
   - Data models
   - Performance requirements

5. **User Guides**
   - Installation instructions
   - Configuration guidelines
   - Usage examples
   - Troubleshooting tips

## Clineplan Structure

### Hierarchical Organization
- Organize work into Epics, Stories, Tasks, and Subtasks
- Ensure proper dependency tracking between tasks
- Include estimates for all tasks
- Define clear acceptance criteria

### Required Sections
1. **Project Overview**
   - Project name and description
   - Goals and objectives
   - Key stakeholders
   - Timeline and milestones

2. **Epics**
   - High-level work packages
   - Clear descriptions
   - Success criteria
   - Dependencies

3. **Stories**
   - User-focused requirements
   - Acceptance criteria
   - Dependencies
   - Estimates

4. **Tasks**
   - Specific implementation steps
   - Technical details
   - Dependencies
   - Estimates

5. **Subtasks**
   - Granular work items
   - Specific implementation details
   - Dependencies
   - Estimates

6. **Risks and Mitigations**
   - Potential risks
   - Impact assessment
   - Mitigation strategies
   - Contingency plans

7. **Success Criteria**
   - Measurable outcomes
   - Acceptance criteria
   - Validation methods
   - Stakeholder approval requirements

## Initial Planning Phase

### Requirements Gathering
- Conduct a thorough questionnaire at the beginning of each project
- Ensure all requirements are clearly defined
- Identify potential risks and mitigation strategies
- Define clear success criteria

### Project Setup
- Create GitHub repository
- Set up Jira project
- Create Confluence space
- Initialize documentation templates
- Configure monitoring and alerting

## Execution Guidelines

### Phase Transitions
- Proceed automatically to subsequent phases upon successful completion of current phase
- Create checkpoints at phase boundaries with summary of completed steps
- Log detailed completion status at each phase boundary
- Update Jira and Confluence with progress
- Push code changes to GitHub

### Decision Making
- Make autonomous decisions within the parameters defined in the plan
- Apply established standards and best practices when encountering ambiguity
- Use documented fallback positions for common decision points
- Document all significant decisions in execution logs and Confluence

### Progress Tracking
- Generate comprehensive logs of all executed steps
- Create progress reports at defined intervals (hourly for extended deployments)
- Update Jira issues with progress
- Maintain execution state that can be resumed in case of interruption
- Update plan checkboxes to reflect current execution state

## Error Handling

### Non-Critical Errors
- Attempt reasonable retries for transient errors (3 attempts with exponential backoff)
- Apply standard error resolution patterns when appropriate
- Log all errors and resolution attempts
- Continue execution if error does not prevent subsequent steps
- Document errors and resolutions in Confluence

### Critical Blockers
- Clearly identify truly blocking issues requiring human intervention
- Provide detailed context including:
  - Current step in the execution plan
  - Error details and significance
  - Attempted resolution steps
  - Specific guidance needed from human operator
- Continue execution of non-dependent tasks if possible
- Create Jira issues for critical blockers

## Completion Process

### Final Documentation
- Ensure all documentation is complete and up-to-date
- Generate comprehensive completion report
- Document lessons learned
- Identify areas for improvement
- Create follow-up action items in Jira

### Code Finalization
- Ensure all code is committed and pushed to GitHub
- Complete all pull requests
- Verify all tests pass
- Tag the final release

### Project Closure
- Update all Jira issues to reflect completion
- Finalize all Confluence documentation
- Generate final project report
- Conduct retrospective analysis
- Document follow-up actions

## Contact

For questions or assistance with Enhanced TURBO Mode, please contact the MemCommsOps team.

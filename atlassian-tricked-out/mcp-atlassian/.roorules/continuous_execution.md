# Continuous Execution Mode [TURBO MODE] Standards

## Overview
These standards govern Continuous Execution Mode for complex multi-phase deployments. When this mode is activated, Cline is authorized to work through entire deployment plans without stopping at phase boundaries.

## Activation Protocol

### Command Structure
To activate Continuous Execution Mode [TURBO MODE], use the following command pattern:
```
/new "Please implement [PLAN_NAME] in continuous execution mode. Continue working through all phases without stopping."
```

### Authorization Parameters
Always include the following authorization parameters:
```
I authorize autonomous execution through the entire deployment plan. Make necessary decisions to complete each phase. Only notify me for critical blockers requiring human intervention.
```

## Execution Guidelines

### Phase Transitions
- Proceed automatically to subsequent phases upon successful completion of current phase
- Create checkpoints at phase boundaries with summary of completed steps
- Log detailed completion status at each phase boundary
- Do not require explicit confirmation to proceed to next phase

### Decision Making
- Make autonomous decisions within the parameters defined in the plan
- Apply established standards and best practices when encountering ambiguity
- Use documented fallback positions for common decision points
- Document all significant decisions in execution logs

### Progress Tracking
- Generate comprehensive logs of all executed steps
- Create progress reports at defined intervals (hourly for extended deployments)
- Maintain execution state that can be resumed in case of interruption
- Update plan checkboxes to reflect current execution state

## Error Handling

### Non-Critical Errors
- Attempt reasonable retries for transient errors (3 attempts with exponential backoff)
- Apply standard error resolution patterns when appropriate
- Log all errors and resolution attempts
- Continue execution if error does not prevent subsequent steps

### Critical Blockers
- Clearly identify truly blocking issues requiring human intervention
- Provide detailed context including:
  - Current step in the execution plan
  - Error details and significance
  - Attempted resolution steps
  - Specific guidance needed from human operator
- Continue execution of non-dependent tasks if possible

### Recovery Procedures
- Maintain execution state to support resumption after interruptions
- Document precise point of interruption for manual restart
- Provide clear instructions for continuing execution
- Support partial execution of remaining phases

## Logging Standards

### Execution Logs
- Create timestamped logs of all executed commands
- Document start and completion of each phase
- Record all significant decision points
- Log output of critical verification steps
- Store logs in standardized location (/logs/[YOUR_DEPT]/execution_logs/)

### Progress Reports
- Generate structured progress reports at phase boundaries
- Include percentage completion of overall plan
- Summarize completed steps and upcoming work
- Document any deviations from the original plan
- Highlight any items requiring future attention

## Security Considerations

### Authentication Handling
- Securely manage credentials during extended execution periods
- Use shortest-lived credentials appropriate for the task
- Never log authentication information
- Implement secure credential rotation for long-running deployments

### Authorization Boundaries
- Respect defined authority limitations even in continuous mode
- Do not exceed authorized access levels
- Document all privileged operations
- Apply all standard security controls

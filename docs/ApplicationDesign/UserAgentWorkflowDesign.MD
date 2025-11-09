# User Agent Workflow Design

## 1. Purpose
The User Agent is a programmatic orchestrator (CLI, web application, or automation bot) that coordinates the end-to-end document generation workflow by invoking REST APIs across the three main services. This document defines the workflow state machine, error handling strategies, retry policies, and orchestration patterns that ensure reliable and predictable document generation.

## 2. Responsibilities
- Orchestrate sequential API calls to Content Intake Service, Gestalt Design Engine, and Document Formatter Service.
- Manage workflow state transitions and track progress through the pipeline.
- Handle transient failures with intelligent retry strategies.
- Manage partial failures (e.g., Word succeeds but PowerPoint fails).
- Provide status updates to end users and handle cancellation requests.
- Implement timeout handling and compensation actions on failures.

## 3. Workflow State Machine

### 3.1 Primary States
```
INITIALIZED → SUBMITTED → CONTENT_NORMALIZED → LAYOUT_QUEUED → LAYOUT_PROCESSING → 
LAYOUT_COMPLETE → RENDERING_QUEUED → RENDERING_PROCESSING → RENDERING_COMPLETE → DELIVERED

Failure states:
→ FAILED_CONTENT_VALIDATION
→ FAILED_LAYOUT_GENERATION
→ FAILED_RENDERING
→ CANCELLED
```

### 3.2 State Definitions
- **INITIALIZED**: User agent has received user input, preparing submission payload.
- **SUBMITTED**: Content Intake Service has accepted the session (`POST /v1/intake/sessions` succeeded).
- **CONTENT_NORMALIZED**: Content Intake Service has completed normalization; session status is `ready`.
- **LAYOUT_QUEUED**: Layout proposal request sent to Gestalt Design Engine; `proposal_id` received.
- **LAYOUT_PROCESSING**: Polling or waiting for layout completion; status is `processing`.
- **LAYOUT_COMPLETE**: Layout specification retrieved successfully; LSP available.
- **RENDERING_QUEUED**: Render job(s) submitted to Document Formatter Service; `render_job_id` received.
- **RENDERING_PROCESSING**: Polling or waiting for rendering completion; status is `processing`.
- **RENDERING_COMPLETE**: All requested formats rendered successfully; artifact IDs available.
- **DELIVERED**: User has been notified and artifacts are accessible.

### 3.3 Failure States
- **FAILED_CONTENT_VALIDATION**: Content Intake Service rejected payload (422); requires user correction.
- **FAILED_LAYOUT_GENERATION**: Gestalt Design Engine failed or timed out; may be retryable.
- **FAILED_RENDERING**: Document Formatter Service failed; may be retryable with same LSP.
- **CANCELLED**: User or system initiated cancellation; cleanup required.

## 4. Workflow Orchestration Patterns

### 4.1 Synchronous vs Asynchronous Operations
- **Synchronous**: Session creation, content normalization (if fast), immediate validation responses.
- **Asynchronous**: Layout generation, document rendering (always async for jobs >3 seconds).

### 4.2 Polling Strategy
For async operations, user agent polls status endpoints:
- **Initial delay**: 500ms after job submission
- **Polling interval**: 1 second for layout generation, 2 seconds for rendering
- **Maximum wait time**: 60 seconds for layout, 120 seconds for rendering
- **Exponential backoff**: Increase interval by 1.5x after each poll, cap at 5 seconds

### 4.3 Callback/Webhook Alternative (Future)
For production deployments, services may support webhook callbacks:
- User agent registers callback URL during job submission
- Services POST status updates to callback URL
- Reduces polling overhead and improves responsiveness

## 5. Error Classification and Retry Strategies

### 5.1 Error Categories

#### Retryable Errors (Transient Failures)
- **5xx Server Errors**: Internal server errors, service unavailable
- **429 Too Many Requests**: Rate limiting (with Retry-After header)
- **502 Bad Gateway**: Downstream service unavailable
- **503 Service Unavailable**: Temporary overload
- **504 Gateway Timeout**: Request timeout (may succeed on retry)
- **Network errors**: Connection refused, DNS failures, timeouts

**Retry Strategy**:
- Maximum retries: 3 attempts
- Exponential backoff: 1s, 2s, 4s delays
- Jitter: ±20% random variation to prevent thundering herd
- Idempotency: Use `Idempotency-Key` header for POST requests

#### Non-Retryable Errors (Permanent Failures)
- **400 Bad Request**: Malformed request (user agent bug)
- **401 Unauthorized**: Invalid or expired credentials
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist (invalid ID)
- **422 Unprocessable Entity**: Validation failure (requires user correction)
- **409 Conflict**: Resource conflict (duplicate submission)

**Action**: Log error, transition to appropriate failure state, notify user.

### 5.2 Idempotency Keys
All POST requests that create resources must include an `Idempotency-Key` header:
- Format: UUID v4
- Generated once per workflow execution
- Reused on retries to prevent duplicate resource creation
- Stored in workflow state for recovery scenarios

## 6. Partial Failure Handling

### 6.1 Multi-Format Generation
When generating both Word and PowerPoint from the same LSP:

**Scenario**: Word succeeds, PowerPoint fails
- **Action**: Mark Word artifact as `complete`, PowerPoint as `failed`
- **State**: Transition to `PARTIAL_COMPLETE` (new state)
- **User Notification**: Inform user that Word is available, PowerPoint failed
- **Recovery**: Allow user to retry PowerPoint generation using same LSP

**Scenario**: Both formats fail
- **Action**: Mark both as `failed`
- **State**: Transition to `FAILED_RENDERING`
- **Recovery**: Retry both render jobs (up to max retries)

### 6.2 Layout Generation Failure
If layout generation fails after content normalization:
- **State**: `FAILED_LAYOUT_GENERATION`
- **Recovery Options**:
  1. Retry with same CIP (if error was transient)
  2. Retry with `rule_only` mode (if AI was the failure point)
  3. Request user to modify content/intent and resubmit

## 7. Timeout Handling

### 7.1 Operation Timeouts
- **Content Normalization**: 30 seconds (synchronous expectation)
- **Layout Generation**: 60 seconds (async, but user agent waits)
- **Document Rendering**: 120 seconds per format (async job)

### 7.2 Timeout Actions
When timeout occurs:
1. Cancel the in-progress operation if cancellation endpoint exists
2. Mark operation as `timed_out`
3. Transition workflow to appropriate failure state
4. Notify user with timeout reason
5. Provide option to retry with longer timeout or simplified request

## 8. Cancellation Flow

### 8.1 User-Initiated Cancellation
1. User requests cancellation (e.g., Ctrl+C, cancel button)
2. User agent calls cancellation endpoints for in-progress operations:
   - `POST /v1/intake/sessions/{id}/cancel` (if in normalization)
   - `POST /v1/layout/proposals/{id}/cancel` (if layout generating)
   - `POST /v1/render/jobs/{id}/cancel` (if rendering)
3. Poll cancellation status until confirmed
4. Clean up local state
5. Transition to `CANCELLED` state

### 8.2 Cleanup Actions
On cancellation or failure:
- Delete session if no artifacts were generated
- Retain session if artifacts exist (for user retrieval)
- Release local resources (file handles, memory)
- Log cancellation reason and timing

## 9. Compensation Actions (Rollback)

### 9.1 When to Compensate
Compensation is required when:
- Workflow fails after resources were created (sessions, proposals, jobs)
- User explicitly cancels before completion
- System-initiated cancellation due to quota/timeout

### 9.2 Compensation Strategy
1. **Session Cleanup**: If no artifacts generated, delete session via `DELETE /v1/intake/sessions/{id}`
2. **Job Cleanup**: Cancel in-progress render jobs
3. **Artifact Cleanup**: Optionally delete partial artifacts (user preference)
4. **State Reset**: Clear local workflow state

### 9.3 Idempotent Cleanup
All cleanup operations must be idempotent:
- Deleting already-deleted resources returns success
- Cancelling already-completed jobs returns success
- No errors thrown for missing resources

## 10. Workflow Examples

### 10.1 Happy Path Sequence
```
1. User Agent: POST /v1/intake/sessions
   → Response: {session_id: "sess-123", status: "draft"}

2. User Agent: POST /v1/intake/sessions/sess-123/submit
   → Response: {status: "normalizing"}

3. User Agent: Poll GET /v1/intake/sessions/sess-123
   → Status: "ready" (content normalized)

4. User Agent: POST /v1/layout/proposals (with CIP)
   → Response: {proposal_id: "lsp-456", status: "queued"}

5. User Agent: Poll GET /v1/layout/proposals/lsp-456
   → Status: "complete" (after ~4 seconds)

6. User Agent: GET /v1/layout/proposals/lsp-456/spec
   → Response: LSP JSON

7. User Agent: POST /v1/render/presentations (with LSP)
   → Response: {render_job_id: "job-789", status: "queued"}

8. User Agent: Poll GET /v1/render/jobs/job-789
   → Status: "complete" (after ~3 seconds)

9. User Agent: GET /v1/artifacts/{artifact_id}
   → Response: Download URL or file

10. Workflow State: DELIVERED
```

### 10.2 Failure Recovery Sequence
```
1. User Agent: POST /v1/layout/proposals
   → Response: 503 Service Unavailable (retryable)

2. User Agent: Wait 1s (exponential backoff)
   → Retry POST /v1/layout/proposals (same Idempotency-Key)
   → Response: 202 Accepted, {proposal_id: "lsp-456"}

3. User Agent: Poll GET /v1/layout/proposals/lsp-456
   → Status: "processing" (continue polling)

4. User Agent: Poll GET /v1/layout/proposals/lsp-456 (after timeout)
   → Status: "failed", error: "AI timeout"

5. User Agent: Retry with rule_only mode
   → POST /v1/layout/proposals (with mode: "rule_only")
   → Response: {proposal_id: "lsp-457"}

6. Continue workflow with new proposal_id
```

### 10.3 Partial Failure Sequence
```
1. User Agent: POST /v1/render/documents (Word)
   → Response: {render_job_id: "job-word-123"}

2. User Agent: POST /v1/render/presentations (PowerPoint)
   → Response: {render_job_id: "job-ppt-456"}

3. User Agent: Poll both jobs
   → job-word-123: "complete"
   → job-ppt-456: "failed", error: "Image asset not found"

4. User Agent: State: PARTIAL_COMPLETE
   → Notify user: "Word document ready, PowerPoint failed"
   → Provide Word artifact download link
   → Offer retry option for PowerPoint (with same LSP)
```

## 11. State Persistence

### 11.1 Workflow State Storage
User agent must persist workflow state:
- **Session ID**: Primary identifier
- **Current State**: From state machine
- **Service IDs**: `proposal_id`, `render_job_id`(s), `artifact_id`(s)
- **Timestamps**: State transitions, last poll time
- **Error History**: Failed attempts, error messages
- **Idempotency Keys**: For retry scenarios

### 11.2 Recovery After Crash
If user agent crashes and restarts:
1. Load persisted workflow states
2. For each `IN_PROGRESS` state, poll current status from services
3. Resume workflow from last known good state
4. Handle any state inconsistencies (e.g., service completed but state not updated)

## 12. Monitoring and Observability

### 12.1 Metrics to Track
- Workflow completion rate (success vs failure)
- Average workflow duration (end-to-end)
- Retry frequency by error type
- Partial failure rate
- Timeout frequency
- Cancellation rate

### 12.2 Logging Requirements
- Log all state transitions with timestamps
- Log all API calls (request/response summaries)
- Log retry attempts with error details
- Log compensation actions
- Include correlation IDs in all logs for tracing

## 13. User Experience Considerations

### 13.1 Progress Feedback
- Provide real-time status updates (polling-based or webhooks)
- Show estimated time remaining (based on historical averages)
- Display current operation ("Generating layout...", "Rendering PowerPoint...")

### 13.2 Error Messages
- Translate technical error codes to user-friendly messages
- Provide actionable guidance ("Please check image file format")
- Offer retry options when appropriate
- Show partial results when available

### 13.3 Timeout Handling
- Warn user before timeout occurs ("This is taking longer than expected...")
- Offer option to extend timeout or simplify request
- Provide estimated completion time if available

## 14. Testing Considerations

### 14.1 Test Scenarios
- Happy path end-to-end
- Each failure state transition
- Retry logic with various error codes
- Partial failure scenarios
- Timeout scenarios
- Cancellation scenarios
- Recovery after crash

### 14.2 Mock Services
For testing user agent independently:
- Mock Content Intake Service with configurable delays/errors
- Mock Gestalt Design Engine with predictable responses
- Mock Document Formatter Service with various job states
- Simulate network failures and timeouts

## 15. Future Enhancements
- Webhook support for real-time status updates
- Parallel format generation optimization
- Workflow templates for common use cases
- Batch processing support (multiple documents in one workflow)
- Workflow visualization and debugging tools


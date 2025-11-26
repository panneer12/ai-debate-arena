# Next Session TODO List

## Phase 4: Demo Scenarios & Validation (Priority)

### 1. Demo Topics
Record 3 distinct debate scenarios to showcase system versatility:

- [ ] **Scenario A: "Universal Basic Income" (Economic Focus)**
  - **Agents:** Conservative, Progressive, Fact Checker
  - **Goal:** Demonstrate data-heavy argumentation and real-time fact-checking of GDP/inflation stats.

- [ ] **Scenario B: "Social Media Regulation" (Ethical/Legal Focus)**
  - **Agents:** Progressive, Devil's Advocate, Synthesizer
  - **Goal:** Show nuanced value clashes and synthesis finding common ground on "transparency".

- [ ] **Scenario C: "AI Safety Regulations" (Meta/Tech Focus)**
  - **Agents:** All available agents (Moderator, Conservative, Progressive, Fact Checker, Devil's Advocate)
  - **Goal:** Demonstrate complex multi-agent interaction, cross-examination, and handling of uncertainty.

### 2. Validation & Testing
- [ ] **Edge Case Testing**
  - Test empty/nonsense topics (Moderator rejection)
  - Test extremely long inputs (Token limit handling)
  - Test API failures (Graceful degradation)
  
- [ ] **Output Recording**
  - Save transcripts to `demo/examples/`
  - Capture screenshots of UI states
  - Record screen video of live debate flow.

### 3. Polish & Cleanup
- [ ] Remove any remaining debug prints
- [ ] Ensure consistent error logging
- [ ] Final UI tweaks (spacing, fonts, responsive layout)

---

## Phase 5: Deployment & Documentation (Follow-up)

### 4. Cloud Deployment
- [ ] **Docker Setup**
  - Verify `Dockerfile` builds locally
  - Optimize image size

- [ ] **Google Cloud Run**
  - Deploy container to Cloud Run
  - Configure environment variables (API Keys)
  - Verify public endpoint accessibility

### 5. Documentation
- [ ] **README.md**
  - Project overview and features
  - Installation and local run instructions
  - Deployment guide
  
- [ ] **API Documentation**
  - Document WebSocket events
  - Document REST endpoints (`/api/debate/start`, etc.)

### 6. Final Submission Prep
- [ ] Create 3-5 minute demo video
- [ ] Verify all tests pass (`pytest`)
- [ ] Clean up code repository

# Product Requirements Document (PRD)

## Maharashtra Citizen Certificate Application Portal

Scope confirmed

Initial legacy application

Version 1.0

## 1. Product Overview

### 1.1 Purpose

Build a citizen-facing Maharashtra Government-style certificate application portal that allows citizens to browse government certificate services, submit applications, upload supporting documents, simulate login and payment interactions, track application progress, and download generated certificates.

The application will simulate the complete citizen journey, including officer approval and certificate issuance, without requiring actual government integrations or administrative users.

This application will serve as the baseline legacy codebase for subsequent developer training sessions.

### 1.2 Product Objectives

- Provide a realistic citizen-facing government service portal.
- Support five certificate application types.
- Demonstrate a complete application lifecycle.
- Simulate authentication, payment and officer approval.
- Generate downloadable PDF certificates through the backend.
- Maintain application information and status in a persistent database.
- Package the complete application into a Docker container.

## 2. Technology Stack

| Layer             | Technology                    |
| ----------------- | ----------------------------- |
| Frontend          | HTML                          |
| Styling           | Tailwind CSS                  |
| Frontend logic    | Vanilla JavaScript            |
| Backend           | Python + FastAPI              |
| Database          | SQLite                        |
| PDF generation    | Python PDF generation library |
| API communication | REST APIs                     |
| Containerisation  | Docker                        |

### Architecture

The application will follow a simple monolithic architecture.

\#chatgpt-mermaid-\_r_18s\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_18s\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_18s\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_18s\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_18s\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_18s\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_18s\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_18s\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_18s\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_18s\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_18s\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_18s\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_18s\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_18s\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_18s\_ p{margin:0;}#chatgpt-mermaid-\_r_18s\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_18s\_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_18s\_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_18s\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_18s\_ .label text,#chatgpt-mermaid-\_r_18s\_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_18s\_ .node rect,#chatgpt-mermaid-\_r_18s\_ .node circle,#chatgpt-mermaid-\_r_18s\_ .node ellipse,#chatgpt-mermaid-\_r_18s\_ .node polygon,#chatgpt-mermaid-\_r_18s\_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_18s\_ .rough-node .label text,#chatgpt-mermaid-\_r_18s\_ .node .label text,#chatgpt-mermaid-\_r_18s\_ .image-shape .label,#chatgpt-mermaid-\_r_18s\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_18s\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_18s\_ .rough-node .label,#chatgpt-mermaid-\_r_18s\_ .node .label,#chatgpt-mermaid-\_r_18s\_ .image-shape .label,#chatgpt-mermaid-\_r_18s\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_18s\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_18s\_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_18s\_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_18s\_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-\_r_18s\_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-\_r_18s\_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_18s\_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_18s\_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_18s\_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-\_r_18s\_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-\_r_18s\_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_18s\_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_18s\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_18s\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_18s\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_18s\_ .icon-shape,#chatgpt-mermaid-\_r_18s\_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_18s\_ .icon-shape p,#chatgpt-mermaid-\_r_18s\_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-\_r_18s\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_18s\_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_18s\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_18s\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_18s\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_18s\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_18s\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_18s\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_18s\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_18s\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_18s\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_18s\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_18s\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_18s\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_18s\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_18s\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-\_r_18s\_ .node rect,#chatgpt-mermaid-\_r_18s\_ .node circle,#chatgpt-mermaid-\_r_18s\_ .node ellipse,#chatgpt-mermaid-\_r_18s\_ .node polygon,#chatgpt-mermaid-\_r_18s\_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_18s\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_18s\_ .mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_18s\_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_18s\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_18s\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Citizen BrowserHTML + Tailwind CSS + VanillaJSFastAPI REST APIApplication ServicesSQLite DatabaseDocument StoragePDF Certificate GeneratorGenerated Certificate PDFs

The frontend and backend will be packaged together in a single Docker container for the initial implementation.

## 3. Certificate Services

The portal must display the following five certificate services.

1\. Income Certificate

Allows citizens to apply for an income certificate by providing personal, family and income-related information.

2\. Caste Certificate

Allows citizens to submit caste-related information and supporting documents.

3\. Domicile Certificate

Allows citizens to apply for domicile certification using residential and personal information.

4\. Residence Certificate

Allows citizens to submit residential information and supporting address documents.

5\. Non-Creamy Layer Certificate

Allows eligible applicants to provide caste, family income and supporting information.

Each certificate service must have:

- Certificate name and description.
- Eligibility information (demonstration content).
- Required document checklist.
- Application initiation option.
- Indicative processing information.

Certificate requirements and eligibility descriptions will be sample content, not authoritative legal guidance.

## 4. Functional Requirements

### 4.1 Citizen Portal / Landing Page

The landing page should provide a simple government-service portal experience.

Requirements:

- Display portal branding and navigation.
- Display available certificate services.
- Provide certificate search or browsing.
- Display basic instructions for citizens.
- Provide Login / Register entry points.
- Provide an application tracking entry point.
- Display relevant announcements or informational content.

### 4.2 Mock Login and Registration

The application must demonstrate a login and registration experience without implementing actual authentication.

Requirements:

- Provide a login screen.
- Provide a registration screen.
- Accept sample citizen information.
- Simulate successful login and registration through frontend logic.
- Maintain a temporary citizen session in the browser.
- Allow the citizen to continue to certificate applications.

Technical boundary: No authentication APIs, password storage, JWT, OAuth or backend identity management.

### 4.3 Certificate Selection

Citizens must be able to browse the five available certificates.

Requirements:

- Display certificate cards.
- Show certificate descriptions.
- Show eligibility and document requirements.
- Provide an Apply Now action.
- Navigate to the corresponding application form.

### 4.4 Application Form

Each certificate must have an appropriate application form.

Common fields:

| Field            | Description          |
| ---------------- | -------------------- |
| Full Name        | Citizen's full name  |
| Date of Birth    | Citizen's birth date |
| Gender           | Selection field      |
| Mobile Number    | Contact number       |
| Email            | Email address        |
| Address          | Residential address  |
| District         | Maharashtra district |
| Taluka           | Taluka information   |
| PIN Code         | Postal code          |
| Certificate Type | Selected certificate |

Certificate-specific fields should be displayed dynamically depending on the selected service.

Examples:

- Income Certificate: occupation, annual family income and income source.
- Caste Certificate: caste, sub-caste and relevant family information.
- Domicile Certificate: place and duration of residence.
- Residence Certificate: current residential details.
- Non-Creamy Layer Certificate: caste category, family income and relevant parental details.

Requirements:

- Validate mandatory fields.
- Provide clear field-level validation messages.
- Allow citizens to review entered information.
- Save the submitted application through FastAPI.
- Generate a unique application reference number.

### 4.5 Document Upload

Citizens must be able to upload supporting documents.

Requirements:

- Display document requirements based on certificate type.
- Allow file selection and upload.
- Support PDF, JPG and PNG formats.
- Validate file extensions and file sizes.
- Associate uploaded documents with the relevant application.
- Store document references in SQLite and files in local persistent storage.

The initial version will not implement OCR or automated document verification.

### 4.6 Mock Payment

A simulated payment experience must be provided.

Requirements:

- Display an indicative application fee.
- Display a payment summary.
- Provide a mock payment interface.
- Simulate payment processing.
- Display successful payment confirmation.
- Generate a mock transaction reference.

No actual payment gateway, financial transaction or payment backend is required.

Payment simulation should be handled entirely through frontend JavaScript.

### 4.7 Application Submission

After completing the application and mock payment, the citizen can submit the application.

Requirements:

- Validate application details.
- Submit application information to FastAPI.
- Persist application data in SQLite.
- Associate uploaded documents with the application.
- Store mock payment confirmation details.
- Generate a unique application reference number.
- Display a submission confirmation page.

Initial application status:

SUBMITTED

### 4.8 Application Tracking

Citizens must be able to track their submitted applications.

Requirements:

- Provide an application tracking page.
- Accept an application reference number.
- Retrieve application information through FastAPI.
- Display certificate type and submission date.
- Display current application status.
- Display relevant status history.
- Show certificate download functionality after approval.

No government officer dashboard or manual status update interface will be implemented.

### 4.9 Mock Officer Approval Workflow

The application must simulate the government certificate approval process.

Workflow:

1. Application is submitted.
2. Backend stores the application with `SUBMITTED` status.
3. A simulated approval process starts.
4. After approximately 1–2 minutes, the backend transitions the application to `APPROVED`.
5. A mock officer approval/signing record is generated.
6. The backend initiates certificate PDF generation.
7. The citizen receives an on-screen notification.

Requirements:

- Approval must happen automatically.
- Approval processing must be backend-controlled.
- Refreshing the browser must not reset the approval process.
- Application status must persist in SQLite.
- Status history must record the transition.
- Approval simulation must be clearly identified as a demonstration.

### 4.10 Certificate PDF Generation and Download

Backend responsibility

Once an application is approved, FastAPI must generate a downloadable mock certificate PDF.

PDF contents:

- Maharashtra-style demonstration portal branding.
- Certificate title.
- Unique certificate number.
- Application reference number.
- Citizen name and details.
- Certificate-specific information.
- Issue date.
- Simulated officer name and designation.
- Mock officer signature.
- Mock government seal.
- Demonstration QR code.
- Visible disclaimer: `SAMPLE – NOT A VALID GOVERNMENT CERTIFICATE`.

Requirements:

- Generate PDF dynamically using saved application data.
- Store the generated PDF in local persistent storage.
- Associate the PDF reference with the application.
- Provide a backend download endpoint.
- Allow citizens to download the PDF from the tracking page.
- Prevent download before application approval.

The generated certificate is strictly for demonstration and training purposes.

### 4.11 Citizen Notifications

The portal must provide simple on-screen notifications.

Examples:

- Application submitted successfully.
- Payment simulation completed.
- Application approved.
- Certificate generated successfully.
- Certificate ready for download.

Notifications should appear as small toast messages without interrupting the citizen's workflow.

## 5. Application Lifecycle and Status Management

The application will use the following lifecycle:

\#chatgpt-mermaid-\_r_1a2\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_1a2\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_1a2\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_1a2\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_1a2\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_1a2\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_1a2\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_1a2\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_1a2\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_1a2\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_1a2\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_1a2\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_1a2\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_1a2\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_1a2\_ p{margin:0;}#chatgpt-mermaid-\_r_1a2\_ defs [id$="-barbEnd"]{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_1a2\_ g.stateGroup text{fill:rgb(31, 78, 148);stroke:none;font-size:10px;}#chatgpt-mermaid-\_r_1a2\_ g.stateGroup text{fill:rgb(237, 237, 237);stroke:none;font-size:10px;}#chatgpt-mermaid-\_r_1a2\_ g.stateGroup .state-title{font-weight:bolder;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_1a2\_ g.stateGroup rect{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_1a2\_ g.stateGroup line{stroke:rgb(175, 175, 175);stroke-width:1;}#chatgpt-mermaid-\_r_1a2\_ .transition{stroke:rgb(175, 175, 175);stroke-width:1;fill:none;}#chatgpt-mermaid-\_r_1a2\_ .stateGroup .composit{fill:transparent;border-bottom:1px;}#chatgpt-mermaid-\_r_1a2\_ .stateGroup .alt-composit{fill:#e0e0e0;border-bottom:1px;}#chatgpt-mermaid-\_r_1a2\_ .state-note{stroke:rgb(58, 132, 63);fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_1a2\_ .state-note text{fill:rgb(237, 237, 237);stroke:none;font-size:10px;}#chatgpt-mermaid-\_r_1a2\_ .stateLabel .box{stroke:none;stroke-width:0;fill:rgb(9, 23, 44);opacity:0.5;}#chatgpt-mermaid-\_r_1a2\_ .edgeLabel .label rect{fill:rgb(9, 23, 44);opacity:0.5;}#chatgpt-mermaid-\_r_1a2\_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_1a2\_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_1a2\_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_1a2\_ .edgeLabel .label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_1a2\_ .label div .edgeLabel{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_1a2\_ .stateLabel text{fill:rgb(237, 237, 237);font-size:10px;font-weight:bold;}#chatgpt-mermaid-\_r_1a2\_ .node circle.state-start{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_1a2\_ .node .fork-join{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_1a2\_ .node circle.state-end{fill:rgb(31, 78, 148);stroke:transparent;stroke-width:1.5;}#chatgpt-mermaid-\_r_1a2\_ .end-state-inner{fill:transparent;stroke-width:1.5;}#chatgpt-mermaid-\_r_1a2\_ .node rect{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_1a2\_ .node polygon{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_1a2\_ [id$="-barbEnd"]{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_1a2\_ .statediagram-cluster rect{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_1a2\_ .cluster-label,#chatgpt-mermaid-\_r_1a2\_ .nodeLabel{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_1a2\_ .statediagram-cluster rect.outer{rx:5px;ry:5px;}#chatgpt-mermaid-\_r_1a2\_ .statediagram-state .divider{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_1a2\_ .statediagram-state .title-state{rx:5px;ry:5px;}#chatgpt-mermaid-\_r_1a2\_ .statediagram-cluster.statediagram-cluster .inner{fill:transparent;}#chatgpt-mermaid-\_r_1a2\_ .statediagram-cluster.statediagram-cluster-alt .inner{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_1a2\_ .statediagram-cluster .inner{rx:0;ry:0;}#chatgpt-mermaid-\_r_1a2\_ .statediagram-state rect.basic{rx:5px;ry:5px;}#chatgpt-mermaid-\_r_1a2\_ .statediagram-state rect.divider{stroke-dasharray:10,10;fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_1a2\_ .note-edge{stroke-dasharray:5;}#chatgpt-mermaid-\_r_1a2\_ .statediagram-note rect{fill:rgb(48, 48, 48);stroke:rgb(58, 132, 63);stroke-width:1px;rx:0;ry:0;}#chatgpt-mermaid-\_r_1a2\_ .statediagram-note rect{fill:rgb(48, 48, 48);stroke:rgb(58, 132, 63);stroke-width:1px;rx:0;ry:0;}#chatgpt-mermaid-\_r_1a2\_ .statediagram-note text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_1a2\_ .statediagram-note .nodeLabel{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_1a2\_ .statediagram .edgeLabel{color:red;}#chatgpt-mermaid-\_r_1a2\_ [id$="-dependencyStart"],#chatgpt-mermaid-\_r_1a2\_ [id$="-dependencyEnd"]{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);stroke-width:1;}#chatgpt-mermaid-\_r_1a2\_ .statediagramTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].statediagram-cluster rect{fill:rgb(9, 23, 44);stroke:url(#chatgpt-mermaid-\_r_1a2\_-gradient);stroke-width:1;}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].statediagram-cluster rect.outer{rx:5px;ry:5px;filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_1a2\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_1a2\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_1a2\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_1a2\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_1a2\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_1a2\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_1a2\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_1a2\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}SubmittedApprovedCertificateGeneratedSimulated officer approvalPDF generationCitizen downloads PDF

| Status                | Meaning                                |
| --------------------- | -------------------------------------- |
| SUBMITTED             | Application successfully received      |
| APPROVED              | Simulated officer approval completed   |
| CERTIFICATE_GENERATED | PDF certificate successfully generated |

The status must be stored in the database, not maintained exclusively in frontend state.

## 6. Database Requirements

SQLite will be used as the application's persistent database.

Proposed initial entities:

| Entity                     | Purpose                                           |
| -------------------------- | ------------------------------------------------- |
| Applications               | Main application details                          |
| Application Documents      | Uploaded document metadata and file references    |
| Payment Records            | Mock payment transaction details                  |
| Application Status History | Tracks application status changes                 |
| Certificates               | Generated certificate metadata and PDF references |

Important database rules:

- Every application must have a unique reference number.
- Each application must belong to one certificate type.
- Documents must be associated with their respective application.
- Each application must maintain its current status.
- Status transitions must be recorded.
- Generated certificates must be linked to their applications.
- No citizen authentication table is required.

## 7. API Requirements

The following REST API endpoints are proposed.

| Method | Endpoint                                    | Purpose                      |
| ------ | ------------------------------------------- | ---------------------------- |
| GET    | `/api/certificates`                         | List available certificates  |
| GET    | `/api/certificates/{id}`                    | Get certificate information  |
| POST   | `/api/applications`                         | Submit an application        |
| POST   | `/api/applications/{id}/documents`          | Upload documents             |
| GET    | `/api/applications/{reference}`             | Retrieve application details |
| GET    | `/api/applications/{reference}/status`      | Retrieve current status      |
| GET    | `/api/applications/{reference}/certificate` | Download generated PDF       |

Payment simulation and login simulation will not have backend APIs.

The backend will initiate and manage the mock approval and PDF-generation workflow following application submission.

## 8. User Interface Requirements

The UI should resemble a conventional Maharashtra citizen-service portal.

Required screens:

| Screen                  | Main functionality                            |
| ----------------------- | --------------------------------------------- |
| Landing Page            | Portal introduction and certificate catalogue |
| Login Page              | Mock login                                    |
| Registration Page       | Mock registration                             |
| Certificate Details     | Information and document requirements         |
| Application Form        | Citizen information entry                     |
| Document Upload         | Supporting document selection                 |
| Payment Screen          | Mock payment                                  |
| Submission Confirmation | Reference number                              |
| Application Tracking    | Current status and history                    |
| Certificate Download    | PDF download                                  |

Design principles:

- Clean government-portal appearance.
- Responsive layouts.
- Simple navigation.
- Clear instructions and labels.
- Consistent form styling.
- Meaningful validation messages.
- Minimal animations and distractions.

## 9. Non-Functional Requirements

Performance

- Landing page should load quickly.
- API operations should return responses without unnecessary delays.
- PDF generation should complete promptly after approval.

Reliability

- Application data must persist across container restarts.
- Approval workflow must survive browser refreshes.
- File references must remain valid.

Security

- Validate uploaded file types and sizes.
- Prevent path traversal through uploaded filenames.
- Avoid exposing internal storage paths.
- Clearly mark all simulated transactions and approvals.

Maintainability

- Keep frontend, backend, database and document-generation responsibilities separated.
- Maintain readable API structures.
- Use environment-based configuration where appropriate.
- Keep the application straightforward to understand and modify.

Deployment

- Application must run inside Docker.
- SQLite and uploaded/generated files must use persistent Docker volumes or mounted storage.
- Provide a Dockerfile and README with startup instructions.

## 10. Explicitly Out of Scope

The following must not be developed in this initial version.

- Real user authentication.
- Real payment gateway integration.
- Government identity verification.
- Aadhaar or other external identity integrations.
- Real officer login or dashboard.
- Manual officer approval.
- Real digital signatures.
- Government certificate issuance.
- External government API integrations.
- OCR and intelligent document verification.
- Email/SMS/WhatsApp notifications.
- AI agents or automation.
- Microservices or distributed architecture.
- Cloud deployment infrastructure.
- Advanced analytics and reporting.

## 11. Acceptance Criteria

The application will be considered complete when the following conditions are met.

| ID    | Acceptance criteria                                                                                            |
| ----- | -------------------------------------------------------------------------------------------------------------- |
| AC-01 | Citizen can access the landing page and browse five certificate types.                                         |
| AC-02 | Citizen can complete mock login and registration.                                                              |
| AC-03 | Citizen can select a certificate and complete its application form.                                            |
| AC-04 | Citizen can upload supporting documents.                                                                       |
| AC-05 | Citizen can complete the mock payment flow.                                                                    |
| AC-06 | Application submission generates a unique reference number.                                                    |
| AC-07 | Application details are persisted in SQLite.                                                                   |
| AC-08 | Citizen can track an application using its reference number.                                                   |
| AC-09 | Application automatically transitions from SUBMITTED to APPROVED within approximately 1–2 minutes.             |
| AC-10 | Approval triggers backend PDF certificate generation.                                                          |
| AC-11 | Citizen receives an on-screen approval notification.                                                           |
| AC-12 | Citizen can download the generated certificate PDF.                                                            |
| AC-13 | Generated PDF contains citizen details, mock officer signature, seal and demonstration disclaimer.             |
| AC-14 | Application data and generated files survive Docker container restarts when persistent volumes are configured. |

## 12. Expected Deliverables

The development team should deliver:

1. Complete frontend application.
2. FastAPI backend.
3. SQLite database and schema.
4. Document upload and storage functionality.
5. Mock authentication and payment interactions.
6. Simulated approval workflow.
7. Backend PDF certificate generator.
8. Application tracking functionality.
9. Dockerfile and persistent storage configuration.
10. README containing setup and execution instructions.

## 13. Definition of Done

The final application must demonstrate one complete citizen journey:

## Citizen application demonstration

1. Citizen opens the portal and browses certificate services.
2. Citizen completes the mock login.
3. Citizen selects an Income Certificate.
4. Citizen fills the application and uploads documents.
5. Citizen completes the mock payment.
6. Citizen submits the application and receives a reference number.
7. Citizen tracks the application and initially sees SUBMITTED.
8. After 1–2 minutes, the application becomes APPROVED.
9. Citizen receives a notification that the certificate is ready.
10. Citizen downloads the generated PDF certificate.

Final outcome

Journey completed

One functional, persistent, containerised legacy application with a complete simulated citizen experience.

Product boundary: This is the baseline application only. Its purpose is to provide a realistic, understandable, conventional codebase that developers can subsequently inspect, test, modify and improve through the weekend development sessions. The reusable team plugin and development automation kit are separate future deliverables, not part of this PRD.
# Changelog

All notable changes to the **FolioPP** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-17

### Added
- Intial folder structure for the project.

- Implemented **Project Documentation** setup using VitePress.
- **Problem Statement** (`problem.md`): Defined the "Synthesis Deficit" in retail investing.
- **Planned Solution** (`solution.md`): Outlined the 6-layer agentic architecture.
- **Infrastructure Blueprint**: Added details for Ray, LangGraph, Qdrant, Neo4j, and Karpenter.
- **Architectural Diagram**: Visualized the Data-to-Presentation flow.

## [0.1.1] - 2026-03-18

### Added
- Landing page for the project. Templete taken from the [Cruip.](https://github.com/cruip/tailwind-landing-page-template)
- Added our features and the branding and logo for the project.

## [0.1.2] - 2026-03-19

### Added
- Implemented a professional workstation interface with reusable components.
- Custom windowing logic featuring collision-aware positioning and automatic 'Gravity/Vacuum' gap resolution.
- **Integrated AI Copilot**: Added a side-by-side market interrogation interface with tactical prompt cards and a multi-accessory input tray.
- Migrated the frontend to a scalable **`src/`** directory structure, isolating logic into **`charts/`**, **`signals/`**, and **`chat/`** domains.

## [0.2.0] - 2026-03-21

### Added
- Proper scalable backend structure.
- In the backend/providers folder, we have added the data providers for NSE India and yfinance that can be scalable to the other providers also. Also each provider has many models to the certain data.
- Added the standardized pipeline for data processing.
- In the frontend connceted using the fast-api currently no storage solution.

## [0.2.1] - 2026-03-23

### Added
- Financials Module: Implemented comprehensive financial statement tables (Income, Balance Sheet, Cash Flow) with real-time data integration.
- Data Visualization: Added **Plotly** charts for Expense Analysis, Profitability Trends, and Revenue Growth, featuring Indian market timelines (FY 2015-2026) and ₹ Cr valuation metrics.
- UI/UX Enhancements:
  - Smart Windowing: Enhanced the workstation to automatically resize and position new financial tables to fit available screen space without overlapping existing charts.
  - Data Density: Implemented "Compact Mode" for financial tables, reducing row height by 30% to display more historical data (12+ years) in a single view.
  - Visual Feedback: Added "Syncing..." loading states and "NSE/BSE Projected" data indicators for projected/simulated data.
- Research on the AI and trained a meta-llama-3.1-8b model for the financial domain.  
- **Currently the AI is not fully functional due to the lack of proper dataset and the computational power to train the model.**Its too much heavy to run in the local environment.

## [0.2.2] - 2026-03-25

### Added
- Trained and tested FolioGPT model it is becoming too heavy to run on the local environment so we are planning to use the Groq API for the AI.
- Implemented the Market Classifier module that will be used to classify the market news and extract features from it.
- Implemented the technical analysis tab that will be used to analyze the technical indicators of the stock.

## [0.2.3] - 2026-03-26

## Added
- Necessary modules required from the nse.
- Proper Test files to the incoming data.

## Modified
- Fixed the previous not working or NA data.

## [0.2.4] - 2026-03-27

### Added
- The context history and the backend to store the chat sessions.
- Added the portfolio Tab and stored in the backend.

## Modified 
- Improved the AI agent orchestrator and the tools with proper data fetching and analysis.
- Added the proper test files for the AI agent orchestrator and the tools.
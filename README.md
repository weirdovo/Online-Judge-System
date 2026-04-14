# Online Judge System

This project is a lightweight online judge backend built with FastAPI and SQLAlchemy. It was developed as a course project, but the implementation goes beyond a minimal assignment template and delivers a usable judging workflow for programming problems, user management, and administrative maintenance.

The system supports the full lifecycle of an online judge platform: user registration and login, problem publishing, code submission, asynchronous judging, result querying, access logging, language registration, and dataset import/export. It is designed as a REST-style backend with clear module boundaries and a database-backed state model.

## Project Overview

The core goal of this project is to provide a simple but complete OJ service for programming exercises. Users can create accounts, browse problems, submit source code, and retrieve judging results. Administrators can manage user roles, inspect access logs, register or update supported languages, reset the system state, and migrate platform data through JSON import/export interfaces.

The backend uses session-based authentication and role checks to separate regular user operations from privileged administration actions. A default `admin` account and a built-in `python` language entry are initialized automatically when the service starts.

## Main Capabilities

- User authentication with registration, login, logout, role updates, and ban control
- Problem management with structured statements, samples, constraints, test cases, and visibility settings for judging details
- Multi-language submission handling through dynamically registered language definitions
- Asynchronous judging with compile-and-run workflows, per-case scoring, and status reporting
- Support for common judge outcomes such as `AC`, `WA`, `CE`, `RE`, `TLE`, and `MLE`
- Submission history queries, result lookup, and detailed judge log access
- Administrative audit logs for submission detail access
- JSON-based system export and import for users, problems, and submissions

## Technical Design

The application is implemented with FastAPI as the web framework and SQLAlchemy as the ORM layer, using SQLite for persistence. Pydantic schemas are used for request validation, and Starlette's session middleware is used to maintain login state.

The judging pipeline writes submitted code into a temporary workspace, optionally compiles it according to the selected language definition, executes it against stored test cases, monitors time and memory usage, and records detailed per-case results in the database. This keeps the judge logic isolated from the API layer while allowing submissions to be processed asynchronously.

## Repository Structure

```text
.
├── app/          # FastAPI application, database models, judge logic, and API routers
├── tests/        # Automated API tests
├── spj_test/     # Additional special-judge related tests
├── report/       # Project report and supporting images
├── requirements.txt
└── README.md
```

## Summary

This repository presents a compact online judge system focused on backend engineering: structured problem storage, permission-aware APIs, extensible language support, asynchronous code judging, and operational tooling for administrators. It is intended as a practical demonstration of how a small OJ platform can be implemented with Python web technologies in a clean and modular way.

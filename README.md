# Concurrent Multi-Agent Evaluation System

## 🚀 Overview
This project implements a concurrent multi-agent workflow for evaluating executive candidates using structured + unstructured data.

## 🧠 Architecture

Parser → Parallel Agents → Synthesizer

- Requirement Parser
- Bio Agent
- Resume Agent
- Reference Agent
- Score Synthesizer

## ⚙️ Key Features

- Concurrent execution of independent agents
- Structured scoring system
- Deterministic orchestration
- Extensible agent framework

## 🏗️ Workflow

1. Parse job requirements
2. Run agents in parallel:
   - Bio analysis
   - Resume analysis
   - Reference analysis
3. Aggregate results
4. Generate final decision

## 🔥 Why this matters

Demonstrates:
- Agent orchestration patterns
- Parallel execution design
- Real-world enterprise use case (executive search)

## 🛠️ Run

```bash
python main.py


---

# 🎨 Step 2 — Visual (this makes interviews EASY)

Add this diagram to README:

```text id="diag001"
            +----------------------+
            | Requirement Parser   |
            +----------+-----------+
                       |
        -----------------------------------
        |               |                |
+-------------+  +-------------+  +-------------+
| Bio Agent   |  | Resume Agent|  | Ref Agent   |
+------+------+  +------+------+  +------+------+
        |               |                |
        ----------- Aggregation ----------
                       |
             +---------v---------+
             | Score Synthesizer |
             +-------------------+

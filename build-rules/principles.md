# Core Principles

> The non-negotiable rules that govern the entire architecture.

---

## 1. No Hidden Values

* No "magic numbers" in UI/layout/business rules (e.g., max width, padding, cache size, timeouts, limits).
* Any limit, threshold, sizing rule, toggle, feature availability, flow branching, and policy must exist as a **named key** in configuration.
* If a value must exist to boot, it belongs in **base configuration**, not code.

---

## 2. Stateless Code, State in Data

* Code must behave as **stateless transformers** wherever possible.
* State lives in **data files / stores**:

  * **Config** = rules, theme tokens, constraints, policies, flows.
  * **Memory** = "resume where I left off" (session/UI continuity).
  * **Runtime State** = in-memory store derived from inputs, config, and memory.

---

## 3. Determinism

* Same inputs + same config + same memory snapshot → same state output.
* Non-determinism (time, OS, network) is isolated behind the PAL (Platform Abstraction Layer).

---

## 4. Replaceability

* UI and backend must be separable.
* Communication occurs through a **Bridge Adapter** that can be in-process or IPC without changing contract.

---

## Non-Goals

* This is not "config as database". Domain data may live in DB/files; configuration governs behavior and constraints.
* Memory is best-effort continuity, not a source of truth for rules.

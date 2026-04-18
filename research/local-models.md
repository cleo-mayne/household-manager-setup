# Switching Cleo to Local Models: Feasibility Research

## 1. Executive Summary

**Viable as a hybrid, not as a pure swap — and it does not fix the OpenClaw problem.**

A Mac Studio M3 Ultra running GLM-4.6 or Qwen3-Coder-480B via MLX/Ollama can plausibly handle the easy 80% of Cleo's workload: morning briefs, inbox triage, Discord chit-chat, routine Todoist and Obsidian operations. The hard 10–20% — long agentic loops, vault-wide reasoning over thousands of notes, and the admin-vs-untrusted safety boundary — still degrades noticeably versus Claude Sonnet 4.6.

Critically, **local models do not solve the OpenClaw problem**. OpenClaw is now both pay-per-use *and* flaky. Swapping the model backend inside OpenClaw gets us off the Anthropic metered bill but leaves us paying OpenClaw's fee on top of a fragile harness, and adds a new source of failures (local inference). If we're going to invest in local models, we should do it *outside* OpenClaw — see [claude-tools-only.md](claude-tools-only.md) for the harness replacement, where a local-model backend is a trivial add-on via LiteLLM.

**Recommendation: do not switch to local models as a standalone move. If local models are worth doing, do them as phase 2 of the OpenClaw replacement, routing selectively via LiteLLM.**

---

## 2. Top Local Models for Agentic Tool-Calling (April 2026)

Ranked by tool-calling reliability on schemas Cleo cares about.

| Model | Params / Active | Context | Tool-calling | License | Notes |
|---|---|---|---|---|---|
| **GLM-4.6** | ~355B MoE | 200K | **Best open schema adherence**; BFCL v3 ~77.8% | MIT-style | Refuses unknown tools, minimal argument hallucination. Cleanest fit for Cleo's hardened admin/untrusted split. |
| **Qwen3-Coder-480B-A35B** | 480B / 35B MoE | 256K (1M extrap) | SOTA open on agentic coding | Apache 2.0 | Dedicated `qwen3_coder` parser in vLLM/SGLang. Use for `.lobster` pipelines with code/structured ops. |
| **DeepSeek V3.2** | 671B / 37B MoE | 128K | Strong; 85K synthetic agentic trajectories in training | MIT | First DeepSeek with thinking-integrated tool calls. Big but active params modest. |
| **Llama 3.1 405B** | 405B dense | 128K | BFCL 0.885 (leaderboard top) | Llama 3 | Highest BFCL, but dense 405B is painful on a single Mac. |
| **Llama 4 Scout** | 109B / 17B MoE | **10M** | Weak on agentic tool-use | Llama 4 | Only realistic 10M NIH model. Use as RAG backbone for vault-wide sweeps, not as primary agent. |
| **GPT-OSS-120B** | 117B / 5.1B MoE | 128K | ~67% BFCL v3 | Apache 2.0 | Easy to serve; behind GLM/Qwen on tool-use. |

Reference point: Claude Sonnet 4.6 scores **87.5% on tau-bench retail**; the best open models sit 5–15 points lower on multi-turn agentic tasks. That gap is where Cleo's harder pipelines live.

**Practical picks:**
- **GLM-4.6** as primary (chat, tool-calling, safety boundary)
- **Qwen3-Coder-480B** as fallback for code-heavy pipelines
- **Llama 4 Scout** as a RAG-only long-context model for `vault-health` sweeps

---

## 3. Hardware

### Mac Studio M3 Ultra (the realistic ceiling in April 2026)

- M4 Ultra was **cancelled** — Apple skipped it. M5 Ultra is rumored for WWDC 2026.
- Apple pulled the 512GB SKU in March 2026 (DRAM squeeze). Current cap is 256GB unless you find used/B-stock.
- 819 GB/s unified memory bandwidth, ~$7–9K configured.
- Realistic tok/s under MLX, 4-bit quant:
  - DeepSeek V3 671B: ~20 tok/s gen, 69 tok/s prompt
  - Qwen3 32B: 30+ tok/s gen
  - Llama 70B: 10–15 tok/s gen
  - Llama 4 Scout (109B MoE, 17B active): comfortably >30 tok/s
- **TTFT on a 15–20K prompt: 10–20 seconds.** That's the bottleneck for voice and Discord latency.

### GPU alternative

- 4× RTX 4090 (96GB total): ~$11K all-in. Runs Llama 70B Q4 at 40–60 tok/s under vLLM tensor parallel. **Cannot fit Qwen3-Coder-480B or DeepSeek V3** even at Q4.
- 2× H100 80GB: ~$60K. Overkill; 1.4 kW sustained.
- **Verdict:** Mac Studio is the only sane 24/7 household box. GPU rigs only win if we need concurrent multi-user throughput, which Cleo does not.

### Quantization for tool-calling

- **Q5_K_M or Q8_0 minimum** for Cleo's tool-calling. Below Q5, JSON schema adherence degrades measurably — that directly breaks the admin-vs-untrusted safety boundary.
- Q4 is fine for chat, risky for structured output.

---

## 4. Serving Stack

| Stack | Mac? | OpenAI-compatible | Tool-calling | Verdict |
|---|---|---|---|---|
| **MLX / mlx-lm** | Best on Mac | via wrappers | Good | Fastest prompt processing on Apple Silicon (4–5× llama.cpp) |
| **Ollama** (MLX backend since Mar 2026) | Yes | Yes (base URL; `/v1` has tool-calling bugs) | Native tool-calling | Easiest. **Use base URL, not `/v1`, for reliable tool calls.** |
| **vLLM** | Via `vllm-mlx` | Yes, richest | **Best: guided decoding, Qwen tool parser** | Use on GPU rigs |
| **llama.cpp** | Yes | Yes | Added MCP client Mar 2026 | Solid fallback; slower than MLX on Apple |
| **LM Studio** | Yes | Yes | OK | GUI-first; not for 24/7 |

**Pick: MLX-backed Ollama on Mac Studio. vLLM if we ever go GPU.**

---

## 5. What Breaks, What Works

### Works at roughly Sonnet parity
- Single-turn tool calls against well-defined schemas (`brain_search`, Todoist CRUD)
- Short/medium context reasoning (<32K)
- Morning-brief assembly, Discord chit-chat
- Voice handoff to ElevenLabs

### Degrades noticeably
- **Long multi-turn agent loops (10–20 steps):** tau-bench gap shows up as "lost the plot" failures on knowledge-graph discovery
- **128K+ context:** only Llama 4 Scout genuinely does 1M+ NIH; GLM-4.6 caps at 200K, Qwen3-Coder at 256K native. Claude Sonnet 4.6 has strong 1M retrieval.
- **Safety boundary robustness:** Anthropic has done more RL against prompt injection than any open lab. More false positives/negatives at the Discord/iMessage trust boundary.
- **TTFT on long prompts:** 10–20s vs Claude's 1–3s. Voice and interactive Discord will feel laggy.

### Functional gaps
- **No prompt caching.** Anthropic caches are essentially free; local has none. Makes large system prompts more expensive per turn in wall-clock terms.
- **Serialization under concurrency.** Two users hitting Cleo at once on a Mac Studio queues; Claude API parallelizes for free.

---

## 6. Total Cost of Ownership

Assume household volume: 5–10M input + 0.5–1M output tokens/month.

| Scenario | Upfront | Monthly | 3-yr total |
|---|---|---|---|
| **Status quo (OpenClaw + Sonnet 4.6)** | $0 | ~$50–120 API + OpenClaw fee | ~$2–5K |
| **Pure local (M3 Ultra + GLM-4.6 + Ollama)** | $9,500 | ~$25 electricity | ~$10.4K |
| **GPU rig (4×4090 + vLLM)** | $11,000 | ~$90 electricity | ~$14.2K |
| **Hybrid (M3 Ultra + Claude for top 15% via LiteLLM)** | $9,500 | ~$35 | ~$10.8K |

Break-even against Claude-only is **~5–7 years** at household volume. The hardware case only pays off if:
1. Privacy/sovereignty is the actual driver, or
2. OpenClaw's new pay-per-use fee is the dominant cost, or
3. The Mac Studio is wanted for other reasons anyway.

**If it's pure token cost, Claude API stays cheaper through 2028–2029.**

---

## 7. Hybrid Routing (the honest recommendation)

LiteLLM is the canonical router. Pattern: 85–95% local, 5–15% Claude.

**Route to local (GLM-4.6):**
- `brain_search` / `brain_capture`
- Todoist CRUD
- Discord replies, iMessage chit-chat
- `vault-health` scans
- Morning-brief assembly

**Route to Claude Sonnet 4.6:**
- Planner-detected >5-step tool-call depth
- Safety-boundary elevations (admin flips)
- `knowledge-graph` link discovery
- Long-context vault-wide reasoning
- Kid/nanny-facing content

**Fallback chain:**
- Local TTFT > 10s → cloud
- Local returns malformed tool JSON twice → cloud

LiteLLM sits as an OpenAI-compatible proxy in front of whatever harness we run. It routes cleanly under OpenClaw (Ollama as first-class provider via `#2838`), Claude Agent SDK (configure `baseURL`), or a custom loop.

---

## 8. How This Interacts with the OpenClaw Decision

This research was scoped as "switch Cleo to local models" on the assumption we'd stay on OpenClaw. Given OpenClaw is *also* fragile, that framing is wrong. The real matrix:

|  | **Claude API** | **Local models** |
|---|---|---|
| **Keep OpenClaw** | Current pain (paid + flaky) | Paid + flaky + inference complexity ❌ |
| **Claude-native harness** | ⭐ Recommended next step | Agent SDK + LiteLLM → Ollama |
| **Custom harness** | Possible, more work | Most work; only if privacy-driven |

**The standalone "just swap the model" move is the weakest quadrant.** It keeps the worst component (the flaky harness) and adds the most operational complexity (local inference).

**Correct sequencing:**
1. Replace OpenClaw with a Claude-native stack first (see [claude-tools-only.md](claude-tools-only.md)).
2. If privacy, cost, or sovereignty then becomes the dominant concern, add LiteLLM + Ollama as a routed backend — a small incremental change once the harness is clean.

---

## 9. Concrete Setup (if we do local, later)

1. **Hardware:** Mac Studio M3 Ultra, 256GB RAM (or wait for M5 Ultra at WWDC 2026 for 512GB)
2. **Server:** Ollama with MLX backend, launchd service
3. **Primary model:** `glm-4.6` at Q5_K_M or Q8
4. **Fallbacks:** `qwen3-coder:480b` Q4 for code pipelines; `llama4-scout` for long-context RAG
5. **Router:** LiteLLM proxy with depth/content/safety-boundary rules
6. **Cloud fallback:** Anthropic via LiteLLM; budget ~$20–40/mo for escalations

---

## 10. Sources

- [Berkeley Function Calling Leaderboard V4](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [GLM-4.6 on Hugging Face](https://huggingface.co/zai-org/GLM-4.6)
- [GLM-4.6 Tool Calling & MCP Analysis (Cirra)](https://cirra.ai/articles/glm-4-6-tool-calling-mcp-analysis)
- [Qwen3-Coder blog](https://qwenlm.github.io/blog/qwen3-coder/)
- [Qwen3-Coder-480B on Hugging Face](https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct)
- [DeepSeek V3.2 paper](https://arxiv.org/pdf/2512.02556)
- [Llama 4 release](https://huggingface.co/blog/llama4-release)
- [GPT-OSS benchmarks (Clarifai)](https://www.clarifai.com/blog/openai-gpt-oss-benchmarks-how-it-compares-to-glm-4.5-qwen3-deepseek-and-kimi-k2)
- [tau-bench](https://github.com/sierra-research/tau-bench)
- [Mac Studio M3 Ultra AI review (Creative Strategies)](https://creativestrategies.com/mac-studio-m3-ultra-ai-workstation-review/)
- [Apple pulls 512GB Mac Studio (Tom's Hardware)](https://www.tomshardware.com/tech-industry/apple-pulls-512-mac-studio-upgrade-option)
- [llama.cpp vs MLX vs Ollama vs vLLM on Apple Silicon](https://contracollective.com/blog/llama-cpp-vs-mlx-ollama-vllm-apple-silicon-2026)
- [Ollama vs vLLM benchmark 2026 (SitePoint)](https://www.sitepoint.com/ollama-vs-vllm-performance-benchmark-2026/)
- [LLM Quantization Guide](https://www.knightli.com/en/2026/04/05/llm-quantization-guide-fp16-q4-q2/)
- [OpenClaw Ollama provider docs](https://docs.openclaw.ai/providers/ollama)
- [OpenClaw first-class Ollama/vLLM issue #2838](https://github.com/openclaw/openclaw/issues/2838)
- [LiteLLM Claude Code with non-Anthropic models](https://docs.litellm.ai/docs/tutorials/claude_non_anthropic_models)
- [LiteLLM auto-routing docs](https://docs.litellm.ai/docs/proxy/auto_routing)
- [Running Claude Code with local LLMs via vLLM+LiteLLM](https://dev.to/dcruver/running-claude-code-with-local-llms-via-vllm-and-litellm-599b)

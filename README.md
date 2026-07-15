# FIP Enterprise — Module 06.2

## Working Capital 2.0 + Global ElevenLabs Voice Agent

### Working Capital corrections

- DSO uses AR invoice activity from the same ledger population.
- DPO uses AP invoice activity from the same ledger population.
- Uses trailing 12 months when sufficient history exists.
- Uses YTD activity and elapsed days for partial-year histories.
- Eliminates the selected-period denominator mismatch.
- Adds risk levels: Low, Medium, High and Critical.
- Adds Top 5 AR/AP concentration.
- Uses a balanced risk score that does not automatically saturate at 100.

### Voice Controller

- ElevenLabs widget is mounted from the Enterprise Shell.
- It remains available across all workspaces.
- It retries while the web component loads.
- AI Center includes a reload control and operating guidance.
- Agent ID can be configured through `ELEVENLABS_AGENT_ID`.
- No ElevenLabs Python package or API key is required for the public widget.

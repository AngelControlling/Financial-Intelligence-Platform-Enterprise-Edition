# Installation

Copy `backend/` over the current V2 backend.

## Add

```text
backend/ui/elevenlabs_agent.py
backend/tests/test_working_capital_intelligence_v2.py
backend/tests/test_elevenlabs_global_agent.py
```

## Replace

```text
backend/models/working_capital_intelligence.py
backend/engines/working_capital_intelligence_engine.py
backend/services/working_capital_intelligence_service.py
backend/ui/working_capital_intelligence.py
backend/core/enterprise_shell.py
backend/workspaces/ai_center.py
```

## Optional agent configuration

PowerShell:

```powershell
$env:ELEVENLABS_AGENT_ID="agent_your_id"
```

The current configured agent remains the default when this variable is absent.

## Restart

```powershell
Ctrl + C
Remove-Item backend\engines\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item backend\models\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item backend\services\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item backend\ui\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item backend\core\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item backend\workspaces\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
streamlit run backend/enterprise_v2.py --server.port 8504
```

## Browser requirements

- Allow microphone permission.
- Allow network access to `unpkg.com` and ElevenLabs.
- The agent appears in the lower-right corner on every workspace.

from __future__ import annotations

import os

import streamlit.components.v1 as components


DEFAULT_AGENT_ID = "agent_8201kxf93n0eegj898dksdwwpwfv"


def render_global_elevenlabs_agent() -> None:
    """
    Mount the ElevenLabs conversational widget in the Streamlit parent page.

    The mount is idempotent, survives workspace navigation and retries while
    the custom element script is loading.
    """
    agent_id = os.getenv("ELEVENLABS_AGENT_ID", DEFAULT_AGENT_ID).strip()
    if not agent_id:
        return

    components.html(
        f"""
        <script>
        (() => {{
            const parentWindow = window.parent;
            const doc = parentWindow.document;
            const scriptId = "fip-elevenlabs-widget-script";
            const containerId = "fip-elevenlabs-global-agent";
            const agentId = {agent_id!r};

            function ensureScript() {{
                let script = doc.getElementById(scriptId);
                if (script) return script;

                script = doc.createElement("script");
                script.id = scriptId;
                script.src = "https://unpkg.com/@elevenlabs/convai-widget-embed";
                script.async = true;
                script.type = "text/javascript";
                doc.head.appendChild(script);
                return script;
            }}

            function mountWidget() {{
                let container = doc.getElementById(containerId);

                if (!container) {{
                    container = doc.createElement("div");
                    container.id = containerId;
                    Object.assign(container.style, {{
                        position: "fixed",
                        right: "22px",
                        bottom: "22px",
                        zIndex: "2147483646",
                        pointerEvents: "auto"
                    }});
                    doc.body.appendChild(container);
                }}

                const current = container.querySelector("elevenlabs-convai");
                if (current && current.getAttribute("agent-id") === agentId) {{
                    return true;
                }}

                container.innerHTML = "";
                const widget = doc.createElement("elevenlabs-convai");
                widget.setAttribute("agent-id", agentId);
                container.appendChild(widget);
                return true;
            }}

            ensureScript();

            let attempts = 0;
            const timer = parentWindow.setInterval(() => {{
                attempts += 1;
                mountWidget();

                if (
                    parentWindow.customElements
                    && parentWindow.customElements.get("elevenlabs-convai")
                ) {{
                    parentWindow.clearInterval(timer);
                }}

                if (attempts >= 40) {{
                    parentWindow.clearInterval(timer);
                }}
            }}, 250);

            mountWidget();
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def render_voice_agent_control_panel() -> None:
    """Render an agent health/reload control inside AI Center."""
    agent_id = os.getenv("ELEVENLABS_AGENT_ID", DEFAULT_AGENT_ID).strip()

    components.html(
        f"""
        <style>
        body {{
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background: transparent;
        }}
        .panel {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border: 1px solid #1d3a5f;
            border-radius: 12px;
            background: linear-gradient(145deg,#10243d,#081727);
            color: white;
        }}
        .status {{
            color: #22c55e;
            font-weight: 800;
        }}
        .meta {{
            color: #8fa5bd;
            font-size: 12px;
            margin-top: 4px;
        }}
        button {{
            border: 0;
            border-radius: 9px;
            padding: 10px 14px;
            background: linear-gradient(90deg,#2f80ed,#7457e8);
            color: white;
            font-weight: 800;
            cursor: pointer;
        }}
        </style>
        <div class="panel">
            <div>
                <div><span class="status">● Available globally</span></div>
                <div class="meta">
                    Voice Controller remains mounted while navigating FIP.
                </div>
            </div>
            <button id="reload-agent">Reload Voice Agent</button>
        </div>
        <script>
        document.getElementById("reload-agent").onclick = () => {{
            const doc = window.parent.document;
            const old = doc.getElementById("fip-elevenlabs-global-agent");
            if (old) old.remove();

            const widget = doc.createElement("elevenlabs-convai");
            widget.setAttribute("agent-id", {agent_id!r});

            const container = doc.createElement("div");
            container.id = "fip-elevenlabs-global-agent";
            Object.assign(container.style, {{
                position: "fixed",
                right: "22px",
                bottom: "22px",
                zIndex: "2147483646",
                pointerEvents: "auto"
            }});
            container.appendChild(widget);
            doc.body.appendChild(container);
        }};
        </script>
        """,
        height=82,
        scrolling=False,
    )

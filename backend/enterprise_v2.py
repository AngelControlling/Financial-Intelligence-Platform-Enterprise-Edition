from core.enterprise_shell import (
    EnterpriseShell,
)
from core.registry import (
    register_enterprise_workspaces,
)


EnterpriseShell(
    register_workspaces=(
        register_enterprise_workspaces
    )
).run()

#!/usr/bin/env python3
"""
Sync Airtable data for this specific MCP server
Pulls configuration, metadata, and deployment info from Airtable
"""

import os
import json
from datetime import datetime
from pathlib import Path
from pyairtable import Api

# Configuration
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appHbSB7WhT1TxEQb")
SERVER_NAME = os.getenv("SERVER_NAME", "unknown-server")

# Output directory
AIRTABLE_DIR = Path("airtable-data")

def setup_directories():
    """Create output directory"""
    AIRTABLE_DIR.mkdir(exist_ok=True)

def find_server_record(api):
    """Find this server's record in Airtable"""
    table = api.table(AIRTABLE_BASE_ID, "MCP Servers")
    all_records = table.all()

    # Normalize server name (remove common prefixes/suffixes)
    def normalize_name(name):
        """Normalize server name for matching"""
        name = name.lower()
        # Remove common prefixes
        name = name.replace("mcp__", "").replace("mcp-", "")
        # Remove common suffixes
        name = name.replace("-mcp", "").replace("_mcp", "")
        # Normalize separators
        name = name.replace("-", " ").replace("_", " ")
        return name.strip()

    normalized_search = normalize_name(SERVER_NAME)

    print(f"Searching for: {SERVER_NAME} (normalized: {normalized_search})")

    # Try exact match on normalized names
    for record in all_records:
        server_name_field = record["fields"].get("MCP Server Name", "")
        normalized_field = normalize_name(server_name_field)

        if normalized_search == normalized_field:
            print(f"✅ Found exact match: {server_name_field}")
            return record

    # Try partial match
    for record in all_records:
        server_name_field = record["fields"].get("MCP Server Name", "")
        normalized_field = normalize_name(server_name_field)

        if normalized_search in normalized_field or normalized_field in normalized_search:
            print(f"✅ Found partial match: {server_name_field}")
            return record

    # Try package/source match
    for record in all_records:
        package = record["fields"].get("Package/Source", "")
        if SERVER_NAME in package or package in SERVER_NAME:
            print(f"✅ Found package match: {package}")
            return record

    # Try connection command match
    for record in all_records:
        connection = record["fields"].get("Connection URL/Command", "")
        if SERVER_NAME in connection:
            print(f"✅ Found connection match")
            return record

    return None

def sync_server_metadata(api, server_record):
    """Sync server metadata to JSON"""
    if not server_record:
        print(f"⚠️  No Airtable record found for server: {SERVER_NAME}")
        return None

    fields = server_record["fields"]

    metadata = {
        "airtable_record_id": server_record["id"],
        "server_name": fields.get("MCP Server Name"),
        "description": fields.get("Description"),
        "purpose": fields.get("Purpose"),
        "server_type": fields.get("Server Type"),
        "deployment_method": fields.get("Deployment Method"),
        "fastmcp_cloud_status": fields.get("FastMCP Cloud Status"),
        "fastmcp_cloud_url": fields.get("FastMCP Cloud URL"),
        "local_port": fields.get("Local Server Port"),
        "package_source": fields.get("Package/Source"),
        "connection": fields.get("Connection URL/Command"),
        "config_path": fields.get("Configuration Path"),
        "environment_variables": fields.get("Environment Variables"),
        "available_tools": fields.get("Available Tools"),
        "security_notes": fields.get("Security Notes"),
        "agent_count": fields.get("Agent Count", 0),
        "last_synced": datetime.utcnow().isoformat() + "Z"
    }

    # Write metadata
    with open(AIRTABLE_DIR / "server-metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Synced metadata for: {metadata['server_name']}")
    return metadata

def generate_deployment_config(metadata):
    """Generate deployment configuration files"""
    if not metadata:
        return

    deployment_method = metadata.get("deployment_method", "Unknown")
    server_type = metadata.get("server_type", "Unknown")

    # Generate .mcp.json entry
    mcp_config = {
        "mcpServers": {
            SERVER_NAME: {}
        }
    }

    server_config = mcp_config["mcpServers"][SERVER_NAME]

    if deployment_method in ["npx", "Python Script"]:
        # STDIO configuration
        command_str = metadata.get("connection", "")
        parts = command_str.split() if command_str else []

        server_config["command"] = parts[0] if parts else "npx"
        server_config["args"] = parts[1:] if len(parts) > 1 else []

    elif "HTTP" in server_type:
        # HTTP configuration
        server_config["type"] = "http"
        server_config["url"] = metadata.get("connection", "http://localhost:8000")

    # Add environment variables
    env_str = metadata.get("environment_variables", "")
    if env_str:
        env_vars = {}
        for line in env_str.strip().split('\n'):
            if '=' in line:
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()
        if env_vars:
            server_config["env"] = env_vars

    # Write config
    with open(AIRTABLE_DIR / "mcp-config.json", 'w') as f:
        json.dump(mcp_config, f, indent=2)

    print(f"✅ Generated deployment config ({deployment_method})")

def generate_readme_section(metadata):
    """Generate README section with Airtable data"""
    if not metadata:
        return

    readme_content = f"""## Airtable Configuration

This server's configuration is synced from Airtable.

### Server Information

- **Name**: {metadata.get('server_name')}
- **Type**: {metadata.get('server_type')}
- **Deployment**: {metadata.get('deployment_method')}
- **Cloud Status**: {metadata.get('fastmcp_cloud_status')}
- **Agent Count**: {metadata.get('agent_count', 0)}

### Description

{metadata.get('description', 'No description')}

### Purpose

{metadata.get('purpose', 'No purpose specified')}

"""

    # Add cloud URL if deployed
    if metadata.get('fastmcp_cloud_status') == 'Deployed':
        cloud_url = metadata.get('fastmcp_cloud_url')
        if cloud_url:
            readme_content += f"""### FastMCP Cloud

**Deployment URL**: {cloud_url}

"""

    # Add available tools
    tools = metadata.get('available_tools')
    if tools:
        readme_content += f"""### Available Tools

{tools}

"""

    # Add environment variables
    env_vars = metadata.get('environment_variables')
    if env_vars:
        readme_content += f"""### Environment Variables

```bash
{env_vars}
```

"""

    readme_content += f"""---
*Last synced from Airtable: {metadata.get('last_synced')}*
*Airtable Record: {metadata.get('airtable_record_id')}*
"""

    with open(AIRTABLE_DIR / "README-AIRTABLE.md", 'w') as f:
        f.write(readme_content)

    print("✅ Generated README section")

def generate_env_template(metadata):
    """Generate .env.example from environment variables"""
    if not metadata:
        return

    env_str = metadata.get('environment_variables', '')
    if not env_str:
        return

    env_lines = []
    for line in env_str.strip().split('\n'):
        if '=' in line:
            key, _ = line.split('=', 1)
            # Create placeholder
            env_lines.append(f"{key.strip()}=your_{key.strip().lower()}_here")

    if env_lines:
        with open(AIRTABLE_DIR / ".env.example", 'w') as f:
            f.write('\n'.join(env_lines))
            f.write('\n')

        print("✅ Generated .env.example")

def main():
    """Main sync function"""
    print(f"🚀 Starting Airtable sync for: {SERVER_NAME}")

    if not AIRTABLE_TOKEN:
        print("❌ Error: AIRTABLE_TOKEN environment variable not set")
        return 1

    # Initialize Airtable API
    api = Api(AIRTABLE_TOKEN)

    # Setup directories
    setup_directories()

    # Find and sync server record
    print("\n📥 Finding server in Airtable...")
    server_record = find_server_record(api)

    if not server_record:
        print(f"⚠️  Server '{SERVER_NAME}' not found in Airtable")
        print("Creating placeholder metadata...")

        # Create minimal metadata
        metadata = {
            "server_name": SERVER_NAME,
            "description": "No Airtable record found",
            "last_synced": datetime.utcnow().isoformat() + "Z"
        }

        with open(AIRTABLE_DIR / "server-metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        return 0

    # Sync metadata
    print("\n📝 Syncing server metadata...")
    metadata = sync_server_metadata(api, server_record)

    # Generate deployment config
    print("\n⚙️  Generating deployment configuration...")
    generate_deployment_config(metadata)

    # Generate README section
    print("\n📄 Generating README section...")
    generate_readme_section(metadata)

    # Generate env template
    print("\n🔑 Generating environment template...")
    generate_env_template(metadata)

    print(f"\n✅ Sync completed for {SERVER_NAME}!")
    print(f"📁 Output directory: {AIRTABLE_DIR}/")

    return 0

if __name__ == "__main__":
    exit(main())

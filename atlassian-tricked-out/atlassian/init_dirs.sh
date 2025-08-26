#!/bin/bash

# System Direct Novas parent directory
mkdir -p /data-nova/00/novas-sysdirect

# Helix working directory under NovaOps
mkdir -p /data-nova/ax/novaops/helix/{logs,builds,scripts,doctrine,diagnostics}

# Vaeris and Helix Nova runtime directories
mkdir -p /data-nova/00/novas-sysdirect/vaeris
mkdir -p /data-nova/00/novas-sysdirect/helix

# Optional: Registry location for Phase 1
mkdir -p /data-nova/00/novas-sysdirect/registry/phase1

<!--
  Copyright (c) 2025 Vinicius Tadeu Zein

  See the NOTICE file(s) distributed with this work for additional
  information regarding copyright ownership.

  This program and the accompanying materials are made available under the
  terms of the Apache License Version 2.0 which is available at
  https://www.apache.org/licenses/LICENSE-2.0

  SPDX-License-Identifier: Apache-2.0
-->

# Setting up Open SOME/IP Specification Submodule

## Overview

The Open SOME/IP Specification is included as a git submodule to ensure the implementation stays synchronized with the official specification.

## Setup Instructions

1. **Remove the current directory** (if it exists):
   ```bash
   rm -rf open-someip-spec/
   ```

2. **Add the submodule**:
   ```bash
   git submodule add https://github.com/some-ip-com/open-someip-spec.git open-someip-spec
   ```

3. **Initialize and update**:
   ```bash
   git submodule update --init --recursive
   ```

4. **Verify**:
   ```bash
   ls -la open-someip-spec/
   ```

## Usage

The specification documents are now available at `open-someip-spec/src/` and can be referenced in:

- Traceability matrices
- Documentation
- Compliance verification
- Implementation validation

## Updating the Submodule

To update to the latest specification version:

```bash
git submodule update --remote
```

## Repository Structure

```
open-someip-spec/
├── src/                    # Specification documents (RST format)
│   ├── someip-rpc.rst     # Core SOME/IP RPC specification
│   ├── someip-sd.rst      # Service Discovery specification
│   ├── someip-tp.rst      # Transport Protocol specification
│   └── someip-compat.rst  # Compatibility requirements
├── tools/                  # Build tools for documentation
├── scripts/               # Utility scripts
└── README.md             # Specification repository documentation
```

## Integration with Build System

The submodule is automatically included in the build process for:

- Documentation generation
- Requirement traceability
- Compliance checking
- Specification validation

## Maintenance

- **Regular Updates**: Update the submodule quarterly to stay current
- **Breaking Changes**: Monitor for specification changes that affect implementation
- **Contributions**: Specification contributions should be made upstream

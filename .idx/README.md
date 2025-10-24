# Firebase Studio Configuration

This directory contains the Firebase Studio (Project IDX) workspace configuration for SeatSync.

## Files in this Directory

### `dev.nix`
The main Nix configuration file that defines the development environment. It includes:

- **Packages**: All system packages needed for development (Python, Node.js, databases, etc.)
- **Environment Variables**: Default environment settings
- **IDE Extensions**: VS Code extensions to install
- **Workspace Hooks**: Automated setup and startup tasks
- **Preview Configuration**: Multi-service preview setup
- **Services**: Database and cache services configuration

**Key Features:**
- Python 3.11+ with comprehensive ML/AI dependencies
- Node.js 20 with modern frontend tooling
- PostgreSQL 15 and SQLite databases
- Firebase Tools and Google Cloud SDK
- 40+ development tools and utilities
- 30+ VS Code extensions
- Automated dependency installation
- Multi-service preview (backend, frontend, streamlit)

### `icon.png`
Project icon displayed in Firebase Studio workspace list. Replace this placeholder with an actual PNG image (32x32 or 64x64 pixels) representing your project.

### `validate-config.sh`
Automated validation script that checks:
- All configuration files are present
- Required tools are installed
- Correct versions of Python and Node.js
- Project structure is intact
- dev.nix syntax is valid
- Firebase configuration is set up

**Usage:**
```bash
./.idx/validate-config.sh
```

## How It Works

When you open this repository in Firebase Studio:

1. **Nix Evaluation**: Firebase Studio reads `dev.nix` and evaluates the Nix expression
2. **Package Installation**: All packages listed are downloaded and installed in an isolated environment
3. **Environment Setup**: Environment variables are set according to the configuration
4. **IDE Configuration**: VS Code extensions are installed automatically
5. **Workspace Hooks**: `onCreate` hooks run to set up Python venv, install dependencies, etc.
6. **Services Start**: Configured services (PostgreSQL) start automatically
7. **Preview Launch**: Preview servers start for backend, frontend, and streamlit

## Customization

### Adding Packages

To add new system packages, edit the `packages` list in `dev.nix`:

```nix
packages = [
  # ... existing packages ...
  pkgs.yourPackageName
];
```

Find packages at: [search.nixos.org](https://search.nixos.org/packages)

### Adding Environment Variables

Edit the `env` section in `dev.nix`:

```nix
env = {
  # ... existing variables ...
  YOUR_VAR_NAME = "your-value";
};
```

### Adding IDE Extensions

Edit the `idx.extensions` list in `dev.nix`:

```nix
idx.extensions = [
  # ... existing extensions ...
  "publisher.extension-name"
];
```

Find extensions at: [marketplace.visualstudio.com](https://marketplace.visualstudio.com/)

### Modifying Preview Commands

Edit the `idx.previews.previews` section in `dev.nix`:

```nix
idx.previews.previews = {
  myservice = {
    command = ["command", "args"];
    manager = "web";
    env = { PORT = "8080"; };
  };
};
```

### Adding Services

Edit the `services` section in `dev.nix`:

```nix
services = {
  # ... existing services ...
  myservice = {
    enable = true;
    # service-specific options
  };
};
```

## Workspace Lifecycle

### onCreate Hooks
Run once when workspace is first created:
- `setup-python-env`: Creates Python virtual environment and installs dependencies
- `setup-node-env`: Installs Node.js dependencies
- `setup-database`: Runs database migrations
- `setup-scrapling`: Installs browser automation tools

### onStart Hooks
Run every time the workspace starts:
- `start-postgres`: Ensures PostgreSQL service is running

## Previews

Three preview environments are configured:

1. **Backend** (Port 8000): FastAPI server with hot reload
2. **Frontend** (Port 3000): React development server
3. **Streamlit** (Port 8501): Data visualization dashboard

Access previews by clicking the port number in the terminal or using the "Ports" panel.

## Troubleshooting

### Workspace Won't Load
- Check `dev.nix` syntax with the validation script
- Review Firebase Studio console for error messages
- Try closing and reopening the workspace

### Packages Not Installing
- Verify package names at search.nixos.org
- Check for typos in package names
- Ensure Nix channel is compatible (stable-24.05)

### Services Not Starting
- Check service configuration in `dev.nix`
- Review service logs in the terminal
- Verify port conflicts

### Extensions Not Installing
- Verify extension IDs are correct
- Check Firebase Studio extensions marketplace
- Some extensions may not be compatible with web-based IDE

## Best Practices

1. **Keep dev.nix Updated**: Regularly update package versions and channel
2. **Document Changes**: Add comments for custom configurations
3. **Test Locally**: Use the validation script before committing
4. **Minimal Configuration**: Only include necessary packages and extensions
5. **Environment Variables**: Use .env for secrets, not dev.nix
6. **Version Control**: Commit dev.nix but not generated files

## Performance Optimization

1. **Package Selection**: Only include packages you actually use
2. **Extension Management**: Disable unused extensions in VS Code
3. **Preview Management**: Close previews when not needed
4. **Service Configuration**: Set appropriate resource limits
5. **Cache Utilization**: Nix caches builds for faster restarts

## Security Considerations

1. **Never commit secrets** in dev.nix
2. **Use environment variables** for sensitive data
3. **Review extension permissions** before adding
4. **Keep packages updated** for security patches
5. **Use Secret Manager** for production secrets

## Additional Resources

- [Firebase Studio Documentation](https://firebase.google.com/docs/studio)
- [dev.nix Reference](https://firebase.google.com/docs/studio/devnix-reference)
- [Nix Package Search](https://search.nixos.org/packages)
- [NixOS Manual](https://nixos.org/manual/nixpkgs/stable/)

## Support

For issues with:
- **Firebase Studio**: [firebase.google.com/support](https://firebase.google.com/support)
- **Nix Configuration**: [NixOS Discourse](https://discourse.nixos.org/)
- **SeatSync Application**: [GitHub Issues](https://github.com/elliotttmiller/SeatSync/issues)

---

**Configuration Version**: 1.0  
**Last Updated**: October 2024  
**Nix Channel**: stable-24.05

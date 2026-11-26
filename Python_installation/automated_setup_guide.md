# Automated Setup Script Guide (Windows & macOS)

> **Note:** Make sure both script files (`setup_windows.ps1` and `setup_macos.sh`) have been downloaded into your **Downloads** folder. Once completed, your terminal window will automatically navigate to the `code-practice` project directory with the `(code-practice)` virtual environment activated.

## 1. Windows (PowerShell)

Open **PowerShell** and run one of the following commands:

* **Recommended Command (Bypasses ExecutionPolicy restrictions & keeps the virtual environment active):**

  ```powershell
  powershell -ExecutionPolicy Bypass -NoExit -Command "& '$HOME\Downloads\setup_windows.ps1'"
  ```

* **Fallback Command (Use if running `.ps1` files directly from Downloads is blocked):**

  ```powershell
  Get-Content "$HOME\Downloads\setup_windows.ps1" -Raw | Invoke-Expression
  ```

## 2. macOS (Terminal)

Open **Terminal** and run one of the following commands:

* **Recommended Command (Removes Gatekeeper quarantine flag, grants execute permissions & keeps the virtual environment active):**

  ```bash
  xattr -d com.apple.quarantine ~/Downloads/setup_macos.sh 2>/dev/null; chmod +x ~/Downloads/setup_macos.sh && source ~/Downloads/setup_macos.sh
  ```

* **Fallback Command (Use if corporate/system policies block executing `.sh` files):**

  ```bash
  eval "$(cat ~/Downloads/setup_macos.sh)"
  ```
# Automated Setup Script Guide (Windows & macOS)

> **Note:** Make sure both script files (`setup_windows.ps1` and `setup_macos.sh`) have been downloaded into your **Downloads** folder. Once completed, your terminal window will automatically navigate to the `code-practice` project directory with the `(code-practice)` virtual environment activated.

## 1. Windows (PowerShell)

### Initial setup (one time)

Open **PowerShell** and run one of the following commands:

* **Recommended Command (Bypasses ExecutionPolicy restrictions & keeps the virtual environment active):**

  ```powershell
  powershell -ExecutionPolicy Bypass -NoExit -Command "& '$HOME\Downloads\setup_windows.ps1'"
  ```

* **Fallback Command (Use if running `.ps1` files directly from Downloads is blocked):**

  ```powershell
  Get-Content "$HOME\Downloads\setup_windows.ps1" -Raw | Invoke-Expression
  ```

### Daily use

#### Reopen the dashboard

Each time you return, open **PowerShell** and paste these **two commands** together:

```powershell
cd $HOME\Downloads\code-practice
.\.venv\Scripts\Activate.ps1
```

Then run your project's Streamlit launch command to start the dashboard.

#### Stop the dashboard

| Goal | Action |
| --- | --- |
| Stop Streamlit | In the PowerShell window running it, press **Ctrl + C**. |
| Leave the virtual environment | Type `deactivate`. |
| Close everything | Close the PowerShell window. |

Closing the **browser tab does not stop** Streamlit; use **Ctrl + C** in PowerShell.

---

## 2. macOS (Terminal)

### Initial setup (one time)

Open **Terminal** and run one of the following commands:

* **Recommended Command (Removes Gatekeeper quarantine flag, grants execute permissions & keeps the virtual environment active):**

  ```bash
  xattr -d com.apple.quarantine ~/Downloads/setup_macos.sh 2>/dev/null; chmod +x ~/Downloads/setup_macos.sh && source ~/Downloads/setup_macos.sh
  ```

* **Fallback Command (Use if corporate/system policies block executing `.sh` files):**

  ```bash
  eval "$(cat ~/Downloads/setup_macos.sh)"
  ```

### Daily use

#### Reopen the dashboard

Each time, open **Terminal**. If you are in a Conda `(base)` environment, run `conda deactivate` first. Then paste these **two commands** together:

```bash
cd ~/Downloads/code-practice
source .venv/bin/activate
```

Then run your project's Streamlit launch command to start the dashboard.

#### Stop the dashboard

| Goal | Action |
| --- | --- |
| Stop Streamlit | In the Terminal window running it, press **Control + C**. |
| Leave the virtual environment | Type `deactivate`. |
| Stop everything | Press **Cmd + Q** and select **Terminate** if asked. |

**Control + C** stops the dashboard; **Cmd + C** copies text. Closing only the browser tab does not stop Streamlit.

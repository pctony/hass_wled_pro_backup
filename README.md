
***

# WLED Pro Auto-Backup for Home Assistant

![WLED Logo](https://raw.githubusercontent.com/Aircoookie/WLED/master/images/wled_logo_akemi.png)

**WLED Pro Auto-Backup** is a robust Home Assistant add-on designed to protect your elaborate lighting designs. It automatically discovers all WLED instances in your network, captures their full configuration and presets, and organizes them into a clean, time-stamped directory hierarchy.

Whether you are running on a Raspberry Pi SD card or a high-capacity NAS, this add-on ensures your `cfg.json` and `presets.json` files are safe and easy to find.

## ✨ Features

*   **Zero-Config Discovery**: Automatically finds all WLED instances integrated into your Home Assistant. No manual IP list management required.
*   **Active Verification**: Safely "knocks on the door" of candidate devices to verify they are genuine WLED hardware before attempting a backup.
*   **Pro-Grade Storage**: Support for local storage or mapped Network Storage (Samba/NFS) to keep backups off your primary Home Assistant drive.
*   **ISO Directory Hierarchy**: Organizes files by `Device Name > YYYY > MM > DD > [Timestamp]`.
*   **Smart Retention**: Automatically prunes old backups based on a user-defined day limit to save space.
*   **Maximum Reliability**: Uses direct file access (`/presets.json`) to bypass API serialization errors on large preset files or older hardware.
*   **Flexible Intervals**: Set your backup frequency in increments of Minutes, Hours, or Days.

---

## 🚀 Installation

### Method 1: Local Add-on (Recommended for custom tweaks)
1.  Using the **Samba Share** or **VS Code** add-on, navigate to your Home Assistant root directory.
2.  Create a folder  `/addons` (if it doesn't already exist).
3.  Inside `addons`, create a folder named `wled_pro_backup`.
4.  Upload the `config.json`, `Dockerfile`, and `backup.py` files from this repository into that folder.
5.  In Home Assistant, go to **Settings** > **Add-ons** > **Add-on Store**.
6.  Click the **three dots (⋮)** in the top right and select **Check for updates**.
7.  The **"Local Add-ons"** section will appear at the top. Select **WLED Pro Auto-Backup** and click **Install**.

---

## ⚙️ Configuration

Once installed, navigate to the **Configuration** tab in the add-on UI.

| Setting | Description | Default |
| :--- | :--- | :--- |
| `storage_root` | Select the base mount point (`share`, `media`, or `backup`). | `share` |
| `storage_subfolder` | The path within the root (e.g., `nas_mount/wled_backups`). | `wled_backups` |
| `interval_value` | The numerical frequency of the backup. | `24` |
| `interval_unit` | The unit of time for the frequency (`minutes`, `hours`, `days`). | `hours` |
| `retention_days` | Number of days to keep historical backups. | `30` |
| `include_presets` | Whether to include the `presets.json` file in backups. | `true` |

---

## 📂 Understanding the Storage Hierarchy

The add-on builds a deep-nested structure to ensure you can run multiple backups per day without overwriting data. 

**Example Path:**
`/share/wled_backups/Kitchen_Island/2024/05/21/143005/cfg.json`

1.  **Device Level**: Uses the "Friendly Name" from your HA integration.
2.  **Date Level**: ISO Standard `YYYY/MM/DD`.
3.  **Capture Level**: A unique `HHMMSS` folder for every run.

---

## 🛠️ Requirements & Troubleshooting

### 1. Enable the IP Sensor
For discovery to work, the **"IP Address" sensor** must be enabled for your WLED devices:
*   Go to **Settings** > **Devices & Services** > **WLED**.
*   Select your device.
*   Under **Sensors**, ensure the **IP Address** sensor is not disabled. If it is, click it and select **Enable**.

### 2. Network Storage Setup
If using a NAS:
*   Mount your drive in Home Assistant via **Settings** > **System** > **Storage** > **Add Network Storage**.
*   If you name your mount `backup_nas`, your `storage_root` should be `share` and your `storage_subfolder` should be `backup_nas/wled`.

### 3. Error 501 (Not Implemented)
If you see a `501` error in the logs, it means that specific WLED device does not have any presets saved yet. Create at least one preset in the WLED Web UI to resolve this.

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the Apache License 2.0 . See the `LICENSE` file for details.

# <img src="./imgs/icon.png" style="float" width="80" align="center"> &nbsp; APEXMOD

#### :exclamation: ***Note:*** `APEXMOD is compatible with QGIS3.`

APEXMOD is a QGIS-based graphical user interface that facilitates linking [APEX](https://epicapex.tamu.edu/apex//) and [MODFLOW](https://www.usgs.gov/mission-areas/water-resources/science/modflow-and-related-programs?qt-science_center_objects=0#qt-science_center_objects), running APEX-MODFLOW simulations, and viewing results.  

This repository contains the source code of APEXMOD, the example dataset and the tools to build and install it. Releases (plugin ZIPs for Windows and Linux, install scripts, QGIS plugin repository files) are on the Releases page.
- **[Releases](https://github.com/spark-hydro/APEXMOD-plugin/releases):** plugin ZIPs, `install.sh` (Linux), `install.ps1` (Windows), `plugins.xml`
- __[Installer](https://github.com/spark-brc/APEXMOD-plugin/raw/main/Installer/APEXMOD.exe):__ APEXMOD 1.5.exe
- **[Inputs](https://github.com/spark-brc/APEXMOD/releases/download/v1.4.3/apexmod_data.zip):** Animas Dataset zip file
- **[Salt_Test_Dataset](https://github.com/spark-brc/APEXMOD/releases/download/v1.3.1/APEXMOD_salt_test.zip):** Price Dataset zip file
- **[Source Code](https://github.com/spark-brc/APEXMOD/tree/master/APEXMOD)**
- **[Tutorial Document (example)]()** will be provided soon!

-----
# <img src="./imgs/icon2.png" style="float" width="80" align="center"> &nbsp; Installation
The QGIS3 software must be installed on the system prior to the installation of APEXMOD. We've tested APEXMOD with the “long term release (LTR)” (3.28.14) and "latest release (RC)" (3.34.0) versions of QGIS3 (long term release version recommended). Download the [QGIS](https://www.qgis.org/en/site/forusers/download.html)

- Install one of the versions of QGIS. It can be downloaded from https://qgis.org/en/site/forusers/download.html.
- Download [the APEXMOD installer](https://github.com/spark-brc/APEXMOD-plugin/raw/main/Installer/APEXMOD.exe) and install it by running APEXMOD 1.0.exe or a later version. The APEXMOD is installed into the user's home directory *(~\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\APEXMOD)*, which we will refer to as the APEXMOD plugin directory.

<p align="center">
    <img src="./imgs/fig_01.png" width="200" align="center">
</p>
<p align="center">
    <img src="./imgs/fig_02.png" width="500">
</p>

APEXMOD includes all dependencies ([FloPy](https://www.usgs.gov/software/flopy-python-package-creating-running-and-post-processing-modflow-based-models) ([Bakker et al., 2016](https://onlinelibrary.wiley.com/doi/abs/10.1002/hyp.10933)) and [PyShp](https://pypi.org/project/pyshp/)) directly in the plugin to avoid user-installation.  
- Open QGIS3 after the installation of APEXMOD is finished.

If you don't see APEXMOD icon on the toolbar,
- Go to Plugins menu and open Manage and Install Plugins
<p align="center">
    <img src="./imgs/fig_03.png" width="700">
</p>

- Click the installed tab and check APEXMOD box to activate the plugin.
<p align="center">
    <img src="./imgs/fig_04.png" width="450">

Now, you will see the APEXMOD icon on the toolbar.
<p align="center">
    <img src="./imgs/fig_05.png" width="300">
</p>
<br>

# Installation on Linux

APEXMOD needs **QGIS 3** (Qt5). QGIS 4 (Qt6) is not supported yet, and most rolling distributions (Arch, for example) now ship QGIS 4 or a Qt6 build of QGIS 3.x. The easiest way to get QGIS 3.44 LTR on any distribution is conda-forge:

```bash
conda create -n qgis-ltr -c conda-forge --override-channels qgis=3.44 python=3.12 pandas matplotlib scipy pillow
conda activate qgis-ltr
qgis
```

Other QGIS 3 installs (the [Ubuntu/Debian QGIS repositories](https://qgis.org/resources/installation-guide/#debian--ubuntu), the Flatpak) should work too if they provide Python with pandas, matplotlib, scipy and Pillow, but they are **not tested**. Only the conda install above was tested.

The Linux version of the APEX-MODFLOW program (AMRS, from [spark-hydro/AMRS](https://github.com/spark-hydro/AMRS)) is inside the plugin; the **Run** button uses it and writes its screen output to `amrs_run.log` in the `APEX-MODFLOW` folder. There is nothing else to install, and the linking step needs no Windows program.

Pick one way to install the plugin:

**1. Script** (installs into the default QGIS profile)

```bash
curl -fsSL https://raw.githubusercontent.com/spark-hydro/APEXMOD-plugin/main/install.sh | bash
```

Options: `--version v1.6.0`, `--flatpak` (installs into the Flatpak profile folder; untested), `--profile NAME`, `--plugins-dir DIR`, `--uninstall`. Run `./install.sh --help` after downloading it. Restart QGIS, then tick APEXMOD in *Plugins > Manage and Install Plugins > Installed*.

**2. ZIP file.** Download `APEXMOD.<version>-linux.zip` from the [Releases page](https://github.com/spark-hydro/APEXMOD-plugin/releases), then in QGIS: *Plugins > Manage and Install Plugins > Install from ZIP*. (`APEXMOD.<version>.zip` also contains the Windows program and is larger; it installs on every system.)

**3. Plugin repository** (QGIS then offers updates): *Plugins > Manage and Install Plugins > Settings > Add...*, and enter

```
https://github.com/spark-hydro/APEXMOD-plugin/releases/latest/download/plugins-linux.xml
```

Building the ZIP yourself and running the tests: [BUILD.md](BUILD.md).

# Installation on Windows

Close QGIS first. Pick one way to install the plugin (QGIS 3, tested with 3.44 LTR; the plugin goes into `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\APEXMOD`):

**1. Script** (PowerShell, no administrator rights)

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/spark-hydro/APEXMOD-plugin/main/install.ps1 | iex"
```

To choose a release, another profile, or to uninstall, download [install.ps1](install.ps1) and run `.\install.ps1 -Version v1.6.0`, `.\install.ps1 -Profile NAME` or `.\install.ps1 -Uninstall` (`Get-Help .\install.ps1` lists all options). It checks the download against the `SHA256SUMS` of the release. Then start QGIS and tick APEXMOD in *Plugins > Manage and Install Plugins > Installed*.

**2. ZIP file.** Download `APEXMOD.<version>.zip` from the [Releases page](https://github.com/spark-hydro/APEXMOD-plugin/releases), then in QGIS: *Plugins > Manage and Install Plugins > Install from ZIP*.

**3. Plugin repository** (QGIS then offers updates): *Plugins > Manage and Install Plugins > Settings > Add...*, and enter

```
https://github.com/spark-hydro/APEXMOD-plugin/releases/latest/download/plugins.xml
```

The Run button uses `amrs.exe`, the Windows (gfortran) build of [AMRS](https://github.com/spark-hydro/AMRS). Projects made with older versions keep their own `amrs_rel24-002.exe`, which is still found if there is no `amrs.exe`. Two things to know about the gfortran Windows build: its RT3D (nitrate) concentrations differ from those of the Linux and the older Intel builds on the Animas example (the authors are still looking into which is right), and Windows Defender has flagged the *download* of the AMRS Windows zip once as a false positive (a cloud-based guess; compare the `SHA256SUMS` of the release if in doubt).

# References
[Park, S., Jeong, J., Motter, E., and Bailey, R (2023). Introducing APEXMOD, A QGIS plugin for application and evaluation for the Enhanced APEX model, Environmental modelling & software. 165, 105723. 10.1016/j.envsoft.2023.105723](https://doi.org/10.1016/j.envsoft.2023.105723)

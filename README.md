# Grid Tools

## Overview

**Grid-Based Numbering** is a pyRevit add-in that automates the assignment of two parameters to selected Revit elements:

- **Grid Square**: Determined based on the closest grid intersection (formatted as `{Vertical Grid}-{Horizontal Grid}`).
- **Number**: Sequentially assigned based on the spatial proximity of each element relative to a user-selected starting element.

This tool is designed to work with Revit versions **2019 through 2024**.

---

## Setup Instructions

### Clone the Repository
Clone this repository to your local machine:

```bash
git clone https://github.com/jcesarpolo/grid-tools.git
```
or use the *"Download Zip"* button on Github.

### Install pyRevit
If you have not already installed pyRevit, follow the [pyRevit installation guide](https://github.com/eirannejad/pyRevit) to get started.

### Installing the Extension into pyRevit

**Option 1: Using the pyRevit CLI**
1. *Open PowerShell or Command Prompt*

    Ensure pyRevit CLI is installed by running:
    ```bash
    pyrevit env
    ```

2. *Install the Extension*

    Run the following command:
    ```bash
    pyrevit extend ui grid-tools "https://github.com/jcesarpolo/grid-tools.git" --dest "C:\pyRevit\Extensions"
    ```

3. *Reload pyRevit*

    Apply changes by reloading pyRevit:
    ```bash
    pyrevit reload
    ```

4. *Verify Installation*

    Check if the extension is installed:

    ```bash
    pyrevit extensions list
    ```

The Grid Tools extension should now be available in Revit.


**Option 2: Adding the extension manually**

1. Open pyRevit Settings*

    Go to pyRevit settings and locate the Custom Extensions Directory option.

2. *Select the Parent Folder*

    When using this option, ensure you select the parent folder that contains the *.extension* folder.

3. *Apply Changes*

    Save the settings, pyRevit will reload automatically.

For more details, check the *"Adding Extensions Manually"* section on the [documentation](https://pyrevitlabs.notion.site/Install-Extensions-0753ab78c0ce46149f962acc50892491).

---

## How to Use

### 1. Select Elements
In your Revit project, select the elements you want to number.

### 2. Launch the Tool
From the **Grid Tools** tab, click on the **Grid-Based Numbering** button.

### 3. Pick a Starting Element
When prompted, pick one element (from the initially selected set) as the starting element for numbering.

### 4. Automatic Processing
The script will:

- Verify (and, if necessary, create) the shared parameters **Grid Square** and **Number**.
- Calculate grid intersections from the model’s grids.
- Assign the **Grid Square** parameter to each selected element based on the nearest grid intersection.
- Assign a sequential **Number** to each element based on proximity to the starting element.

### 5. Confirmation
A message will confirm whether all selected elements were successfully numbered.

---

## Demo

![Demo](https://github.com/user-attachments/assets/ab5b7d5e-6020-4e9f-9fe1-df3828a17b87)

---

## Requirements

- **Revit**: 2019–2024
- **pyRevit**: Latest version
- **Python**: IronPython (as provided with pyRevit)



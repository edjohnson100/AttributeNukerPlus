# Attribute Nuker Plus

**Version:** 1.0.0  
**Author:** Ed Johnson (Making With An EdJ)

**The essential cleanup utility for Autodesk Fusion developers and power users.**

<img src="AttributesNuker2.png" width="50%" alt="AttributeNuker Logo">

## Introduction: The "Why" and "What"

We’ve all been there: you are developing a new Fusion add-in or testing a script. You run it a dozen times. Now your design file is stuffed with hidden data: `test_data_v1`, `debug_log_entry`, `temp_config_backup`, or leftover attributes from an add-in you uninstalled months ago.

Fusion doesn't provide a native way to see or delete these invisible "Named Values" (Attributes) that get attached to your design. 

**Attribute Nuker Plus** is a lightweight Python script designed to solve this problem. It acts as a "Deep Clean" utility for your Fusion files, and is the perfect companion tool for users of the **LiveUtilities** suite.

* **Total Transparency:** Scans the entire active design to find *every* hidden attribute.
* **Surgical Precision:** View attributes in a table and select exactly which ones to delete.
* **JSON X-Ray:** Unique "X-Ray" tech detects if an attribute contains JSON data (like the payloads used in **LiveUtilities**) and lets you expand it to delete *individual keys* or *list items* without destroying the entire attribute.
* **Developer Companion:** Written specifically to assist in the development and troubleshooting of data-heavy tools like *LiveConfig* and *Changelog Sidecar*, allowing you to reset specific states without nuking your entire setup.

## Installation

Unlike *LiveUtilities* (which is an Add-In), **Attribute Nuker Plus** is a **Script**. This means it only runs when you tell it to and doesn't run in the background.

### Manual Installation

1. **Download:** Download the `AttributeNukerPlus` folder.
2. **Locate Scripts Folder:**
   * **Windows:** `%AppData%\Autodesk\Autodesk Fusion 360\API\Scripts\`
   * **Mac:** `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts/`
3. **Install:** Copy the entire `AttributeNukerPlus` folder into that directory.
4. **Run:**
   * Open Autodesk Fusion.
   * Press `Shift+S` to open **Scripts and Add-Ins**.
   * Click the **Scripts** tab (not Add-Ins).
   * Select **AttributeNukerPlus**.
   * Click **Run**.

## Using Attribute Nuker Plus

### The Nuke Dashboard

When you run the script, a modal dialog appears listing every attribute found in the design.

* **The List:** Attributes are listed with their Group, Name, Value, and the Parent Object they are attached to.
* **Smart Truncation:** Long text values are shortened for readability, but hovering over any value reveals the full text in a tooltip.

### JSON X-Ray (The "Killer" Feature)

If the script detects that an attribute contains a valid JSON string (Dictionary or List):

1. **Expansion:** It automatically creates "Child Rows" underneath the main attribute.
   * **Dictionaries:** Shows every Key/Value pair.
   * **Lists:** Shows every Item by index.
2. **Selective Nuking:**
   * **Nuke the Root:** Check the main "Container" row to delete the attribute entirely.
   * **Nuke a Key:** Check a specific child row (e.g., `timestamp` or `settings_backup`) to remove *just that piece of data* while keeping the rest of the attribute intact.

This is critical for tools like the **LiveUtilities Config tab**, where you might want to delete a single "Snapshot" from the JSON storage without wiping out all your other saved configurations.

## Tech Stack

For the fellow coders and makers out there, here is how Attribute Nuker Plus was built:

* **Language:** Python (Fusion API)
* **Interface:** Native Fusion Command Inputs (TableCommandInput)
* **Logic:** Recursive JSON parsing to handle both Dictionaries (`{}`) and Lists (`[]`) with safe index management (deleting from bottom-up to preserve indices).
* **Lifecycle:** Uses `adsk.autoTerminate(False)` to maintain a persistent dialog window despite being a single-run script.

## Acknowledgements & Credits

* **Developer:** Ed Johnson ([Making With An EdJ](https://www.youtube.com/@makingwithanedj))
* **AI Assistance:** Co-authored with Google's Gemini 3.1 Pro model.
* **Lucy (The Cavachon Puppy):**
  ***Chief Wellness Officer & Director of Mandatory Breaks***
  * Still preventing Repetitive Strain Injury one fetch session at a time.
* **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

---

## Support the Maker (and Lucy!)

I develop these tools to improve my own parametric workflows and love sharing them with the community. If you find LiveUtilities useful and want to say thanks, feel free to **[buy Lucy a dog treat on Ko-fi](https://ko-fi.com/makingwithanedj)**! This is completely optional and supports my Chief Wellness Officer in maintaining mandatory play breaks. Your appreciation and feedback are more than enough.

***

*Happy Making!*
*— EdJ*
# Physician scheduling

1. Use a Python environment with the packages in `requirements.txt`.
2. Run all cells in `scheduling.ipynb`.
3. Open `output/dashboard.html`.

Run all notebook cells once to create the switches. Rerunning cells or Run All preserves selections in the current kernel; restarting the kernel restores defaults. Change any switch, then rerun the **Solve** cell to rebuild the model and update the HTML. **Allow seniors to work weekends** is on by default; turn it off to prohibit their weekend assignments.

Update `scheduling_dataset.xlsx` and rerun the notebook to replan. The notebook has three sections: Setup, Constraints and Solve. It solves the binary linear program and writes `output/schedule.json`; `dashboard.py` renders the offline HTML. The dashboard displays a seven-column weekly calendar. Its menu provides CSV export, printing and source details. The Add to calendar button shows a paid-feature prompt.

Regenerate only the HTML from an existing result:

```sh
python dashboard.py output/schedule.json -o output/dashboard.html
```

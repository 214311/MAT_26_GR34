#def analyse(model):
 #   """Return a starter window count, not a compliance assessment."""
  #  windows = model.by_type("IfcWindow")
   # return {"window_count": len(windows)}
    
"""Extract glazing from an IFC model and calculate EPD-based GWP totals.

The runner opens the IFC once and passes the model to analyse(model).
Geometry returned by IfcOpenShell is already in metres. IFC property
width/height values are converted using the IFC project unit scale.
"""

from collections import defaultdict
from pathlib import Path
import re

import numpy as np
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.unit
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# Edit these project-level assumptions when you run the analysis.
HEATED_FLOOR_AREA_M2 = 10000.0
REFERENCE_PERIOD_YEARS = 50.0


def _material_name(element):
    """Return a readable material name where the IFC provides one."""
    try:
        material = ifcopenshell.util.element.get_material(element)
        if material is None:
            return "Unknown"
        if material.is_a("IfcMaterial"):
            return material.Name or "Unknown"
        names = []
        for item in getattr(material, "Materials", []) or []:
            if getattr(item, "Name", None):
                names.append(item.Name)
        if names:
            return ", ".join(names)
        layer_set = getattr(material, "ForLayerSet", None)
        if layer_set:
            for layer in getattr(layer_set, "MaterialLayers", []) or []:
                mat = getattr(layer, "Material", None)
                if mat and getattr(mat, "Name", None):
                    names.append(mat.Name)
        return ", ".join(names) if names else (getattr(material, "Name", None) or "Unknown")
    except Exception:
        return "Unknown"


def _element_type(element):
    value = getattr(element, "ObjectType", None) or getattr(element, "Name", None) or "Unknown"
    return re.sub(r":\d+$", "", str(value)).strip()


def _is_glass(element):
    fields = [getattr(element, attr, None) or "" for attr in ("Name", "ObjectType", "Description", "Tag")]
    searchable = " ".join(str(value) for value in fields) + " " + _material_name(element)
    searchable = searchable.lower()
    keywords = ("glass", "glazing", "glazed", "double glazing", "triple glazing", "window", "suncool", "planitherm")
    return any(keyword in searchable for keyword in keywords)


def _get_geometry_dimensions(element, settings):
    """Return approximate bbox dimensions and plan area in metres."""
    try:
        shape = ifcopenshell.geom.create_shape(settings, element)
        vertices = np.asarray(shape.geometry.verts, dtype=float).reshape(-1, 3)
        if vertices.size == 0:
            return None
        dimensions = np.sort(vertices.max(axis=0) - vertices.min(axis=0))[::-1]
        width, height, depth = (float(value) for value in dimensions)
        if width <= 0 or height <= 0:
            return None
        return width, height, depth, width * height
    except Exception:
        return None


def _get_window_property_dimensions(element, unit_scale):
    """Fallback for IfcWindow instances without usable representation geometry."""
    try:
        width = getattr(element, "OverallWidth", None)
        height = getattr(element, "OverallHeight", None)
        if width is not None and height is not None:
            width, height = float(width) * unit_scale, float(height) * unit_scale
            if width > 0 and height > 0:
                return width, height, 0.0, width * height
    except (TypeError, ValueError):
        pass
    return None


def _get_descendants(element):
    """Recursively return decomposed children without repeating GlobalIds."""
    descendants, visited = [], set()

    def collect(parent):
        try:
            children = ifcopenshell.util.element.get_decomposition(parent) or []
        except Exception:
            children = []
        for child in children:
            global_id = getattr(child, "GlobalId", None)
            if global_id and global_id in visited:
                continue
            if global_id:
                visited.add(global_id)
            descendants.append(child)
            collect(child)

    collect(element)
    return descendants


def _style_header(sheet, row, column_count):
    fill = PatternFill("solid", fgColor="1F4E78")
    font = Font(color="FFFFFF", bold=True)
    for column in range(1, column_count + 1):
        cell = sheet.cell(row, column)
        cell.fill, cell.font = fill, font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _export_excel(elements, grouped_data, output_path):
    """Create the editable EPD input workbook. A4 and A5 are intentionally omitted."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "GWP Analysis"
    detail_sheet = workbook.create_sheet("IFC Elements")

    sheet["A1"] = "WINDOW AND GLAZING - GWP ANALYSIS"
    sheet["A1"].font = Font(bold=True, size=16, color="1F4E78")
    sheet["A3"] = "Project inputs"
    sheet["A3"].font = Font(bold=True)
    sheet["A4"], sheet["B4"] = "Heated floor area (m²)", HEATED_FLOOR_AREA_M2
    sheet["A5"], sheet["B5"] = "Reference period (years)", REFERENCE_PERIOD_YEARS
    input_fill = PatternFill("solid", fgColor="FFF2CC")
    for address in ("B4", "B5"):
        sheet[address].fill = input_fill
    sheet["A7"] = "EPD inputs - enter values in kg CO₂-eq/m²"
    sheet["A7"].font = Font(bold=True)

    headers = ["Category", "Type", "Material", "Width (m)", "Height (m)", "Depth (m)", "Count", "Area (m²)", "A1-A3", "C3", "C4", "Total GWP (kg CO₂-eq)"]
    header_row, start_row = 9, 10
    for column, value in enumerate(headers, 1):
        sheet.cell(header_row, column, value)
    _style_header(sheet, header_row, len(headers))

    for row, item in enumerate(grouped_data, start_row):
        values = [item["Category"], item["Type"], item["Material"], item["Width"], item["Height"], item["Depth"], item["Count"], item["Area"], 0, 0, 0]
        for column, value in enumerate(values, 1):
            cell = sheet.cell(row, column, value)
            cell.border = Border(bottom=Side(style="thin", color="D9E1F2"))
            if column in (9, 10, 11):
                cell.fill = input_fill
        sheet.cell(row, 12, f"=H{row}*SUM(I{row}:K{row})")

    end_row = start_row + len(grouped_data) - 1
    total_row = max(end_row + 2, start_row + 1)
    sheet.cell(total_row, 1, "TOTAL")
    sheet.cell(total_row, 7, f"=SUM(G{start_row}:G{end_row})" if grouped_data else "=0")
    sheet.cell(total_row, 8, f"=SUM(H{start_row}:H{end_row})" if grouped_data else "=0")
    sheet.cell(total_row, 12, f"=SUM(L{start_row}:L{end_row})" if grouped_data else "=0")
    total_fill = PatternFill("solid", fgColor="D9EAD3")
    for column in range(1, 13):
        sheet.cell(total_row, column).fill = total_fill
        sheet.cell(total_row, column).font = Font(bold=True)

    summary_row = total_row + 3
    summary = [
        ("Total GWP (kg CO₂-eq)", f"=L{total_row}"),
        ("GWP per heated floor area (kg CO₂-eq/m²)", f"=B{summary_row}/B4"),
        ("GWP per m² per year (kg CO₂-eq/m²/year)", f"=B{summary_row}/B4/B5"),
    ]
    for offset, (label, formula) in enumerate(summary):
        sheet.cell(summary_row + offset, 1, label).font = Font(bold=True)
        sheet.cell(summary_row + offset, 2, formula).number_format = "0.000"

    detail_headers = ["GlobalId", "Category", "Name", "Type", "Material", "Width (m)", "Height (m)", "Depth (m)", "Area (m²)"]
    for column, value in enumerate(detail_headers, 1):
        detail_sheet.cell(1, column, value)
    _style_header(detail_sheet, 1, len(detail_headers))
    for row, item in enumerate(elements, 2):
        values = [item["GlobalId"], item["Category"], item["Name"], item["Type"], item["Material"], item["Width"], item["Height"], item["Depth"], item["Area"]]
        for column, value in enumerate(values, 1):
            detail_sheet.cell(row, column, value)

    for current_sheet in (sheet, detail_sheet):
        current_sheet.freeze_panes = "A10" if current_sheet is sheet else "A2"
        current_sheet.auto_filter.ref = current_sheet.dimensions
        for column_cells in current_sheet.columns:
            max_length = max((len(str(cell.value or "")) for cell in column_cells), default=10)
            current_sheet.column_dimensions[get_column_letter(column_cells[0].column)].width = min(max(max_length + 2, 12), 38)
    sheet.row_dimensions[header_row].height = 34
    for row in range(start_row, end_row + 1):
        for column in (4, 5, 6, 8, 9, 10, 11, 12):
            sheet.cell(row, column).number_format = "0.000"
    for row in range(2, len(elements) + 2):
        for column in range(6, 10):
            detail_sheet.cell(row, column).number_format = "0.000"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    return output_path


def analyse(model):
    """Analyse glazing in an already-open IFC model and return JSON-safe results."""
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    elements, processed_ids = [], set()
    geometry_errors = 0

    def add_element(element, category):
        nonlocal geometry_errors
        global_id = getattr(element, "GlobalId", None)
        if not global_id or global_id in processed_ids:
            return
        dimensions = _get_geometry_dimensions(element, settings)
        if dimensions is None and element.is_a("IfcWindow"):
            dimensions = _get_window_property_dimensions(element, unit_scale)
        if dimensions is None:
            geometry_errors += 1
            return
        width, height, depth, area = dimensions
        if area <= 0:
            return
        processed_ids.add(global_id)
        elements.append({
            "GlobalId": str(global_id), "Category": category,
            "Name": str(getattr(element, "Name", None) or "Unnamed"),
            "Type": _element_type(element), "Material": _material_name(element),
            "Width": float(width), "Height": float(height), "Depth": float(depth), "Area": float(area),
        })

    print("Extracting windows...")
    for window in model.by_type("IfcWindow"):
        add_element(window, "Window")

    print("Extracting curtain-wall glazing...")
    for curtain_wall in model.by_type("IfcCurtainWall"):
        for child in _get_descendants(curtain_wall):
            if child.is_a("IfcPlate") and _is_glass(child):
                add_element(child, "Curtain Wall Glazing")
            elif child.is_a("IfcWindow") and _is_glass(child):
                add_element(child, "Curtain Wall Glazing")

    print("Extracting roof glazing...")
    for roof in model.by_type("IfcRoof"):
        for child in _get_descendants(roof):
            if child.is_a("IfcPlate") and _is_glass(child):
                add_element(child, "Roof Glazing")
            elif child.is_a("IfcWindow") and _is_glass(child):
                add_element(child, "Roof Glazing")

    grouped = defaultdict(list)
    for item in elements:
        key = (item["Category"], item["Type"], item["Material"], round(item["Width"], 3), round(item["Height"], 3), round(item["Depth"], 3))
        grouped[key].append(item)

    grouped_data = []
    for key, items in grouped.items():
        category, element_type, material, width, height, depth = key
        grouped_data.append({
            "Category": category, "Type": element_type, "Material": material,
            "Width": width, "Height": height, "Depth": depth,
            "Count": len(items), "Area": float(sum(item["Area"] for item in items)),
        })
    grouped_data.sort(key=lambda item: (item["Category"], item["Type"], item["Material"]))

    project_root = Path(__file__).resolve().parents[2]
    excel_path = project_root / "glazing_gwp" / "results" / "Windows_GWP_Analysis.xlsx"
    _export_excel(elements, grouped_data, excel_path)

    total_area = float(sum(item["Area"] for item in elements))
    print(f"Extraction complete: {len(elements)} elements, {len(grouped_data)} groups, {geometry_errors} geometry errors.")
    print(f"Total extracted glazing area: {total_area:.3f} m²")
    print(f"Excel workbook created: {excel_path}")

    return {
        "analysis": "glazing_gwp",
        "element_count": len(elements),
        "group_count": len(grouped_data),
        "geometry_errors": geometry_errors,
        "total_glazing_area_m2": total_area,
        "heated_floor_area_m2": float(HEATED_FLOOR_AREA_M2),
        "reference_period_years": float(REFERENCE_PERIOD_YEARS),
        "epd_phases": ["A1-A3", "C3", "C4"],
        "excel_workbook": str(excel_path),
        "groups": grouped_data,
        "elements": elements,
        "limitations": [
            "Areas are based on axis-aligned geometry bounding boxes, not exact glass surface areas.",
            "GlobalId deduplication does not detect different IFC elements representing the same physical pane.",
            "Check the IFC model for overlapping IfcWindow and IfcPlate representations before using totals.",
            "Enter EPD values in the yellow Excel cells using a functional unit consistent with the extracted area.",
        ],
    }



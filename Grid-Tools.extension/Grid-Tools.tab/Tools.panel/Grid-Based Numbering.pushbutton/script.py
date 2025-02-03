__title__ = "Grid-Based\nNumbering"
__doc__ = """Version = 1.0
Date    = 02.01.2025
__________________________________________________________________
Description:
    This script assigns the following parameters to selected elements:
      - "Grid Square": based on the names of the closest grid intersection
        in the format {Vertical Grid}-{Horizontal Grid}.
      - "Number": sequential numbering based on spatial proximity from a
        user-selected starting element.
__________________________________________________________________
Author: Julio Polo"""

# IMPORTS
import os
import tempfile
import clr
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ISelectionFilter, ObjectType
from pyrevit import forms, HOST_APP

# VARIABLES
doc   = __revit__.ActiveUIDocument.Document #type: ignore
uidoc = __revit__.ActiveUIDocument #type: ignore
app   = __revit__.Application #type: ignore
revitVersion = int(HOST_APP.version)

# MAIN
def ensure_text_parameter(doc, param_name, categories, group=BuiltInParameterGroup.PG_DATA):
    """
    Ensures that a text parameter with the given name exists and is bound to the provided categories.
    
    If the parameter already exists, its binding is updated to include any missing categories.
    Otherwise, it is created as a shared parameter (using a temporary shared parameter file).
    
    :param doc: The current Revit document.
    :param param_name: The name of the parameter to ensure.
    :param categories: A list of Category objects to bind the parameter to.
    :param group: The built-in parameter group under which the parameter will be categorized.
    """
    bindingMap = doc.ParameterBindings
    # Build a CategorySet from the selected categories.
    cat_set = app.Create.NewCategorySet()
    for cat in categories:
        if cat.AllowsBoundParameters:
            cat_set.Insert(cat)

    # Check if the parameter already exists and update its binding if needed.
    iterator = bindingMap.ForwardIterator()
    iterator.Reset()
    parameterExists = False
    while iterator.MoveNext():
        definition = iterator.Key
        binding = iterator.Current
        if definition.Name == param_name:
            parameterExists = True
            existingCats = binding.Categories
            missingCats = app.Create.NewCategorySet()
            catIter = cat_set.ForwardIterator()
            catIter.Reset()
            while catIter.MoveNext():
                cat = catIter.Current
                if not existingCats.Contains(cat):
                    missingCats.Insert(cat)
            # If some categories are missing, update the binding.
            if missingCats.Size > 0:
                t = Transaction(doc, "Update binding for " + param_name)
                t.Start()
                missingIter = missingCats.ForwardIterator()
                missingIter.Reset()
                while missingIter.MoveNext():
                    missingCat = missingIter.Current
                    if (missingCat.AllowsBoundParameters):
                        existingCats.Insert(missingCat)
                binding.Categories = existingCats
                bindingMap.ReInsert(definition, binding)
                t.Commit()
            break
    # If the parameter doesn't exist, create it bound to the selected categories.
    if not parameterExists:
        t = Transaction(doc, "Add Project Parameter: " + param_name)
        t.Start()
        try:
            shared_param_file = app.OpenSharedParameterFile()
            if shared_param_file is None:
                    temp_folder = tempfile.gettempdir()
                    shared_param_file_path = os.path.join(temp_folder, "TempSharedParameters.txt")
                    with open(shared_param_file_path, "w") as file:
                        file.write("")
                    app.SharedParametersFilename = shared_param_file_path
                    shared_param_file = app.OpenSharedParameterFile()
            # Create (or get) a separate shared parameter group.
            group_name = "Grid Tools"
            shared_group = None
            for g in shared_param_file.Groups:
                if g.Name == group_name:
                    shared_group = g
                    break
            if shared_group is None:
                shared_group = shared_param_file.Groups.Create(group_name)
            # Use the appropriate options based on the Revit version.
            options = None
            if revitVersion < 2023:
                options = ExternalDefinitionCreationOptions(param_name, ParameterType.Text)
            else:
                options = ExternalDefinitionCreationOptions(param_name, SpecTypeId.String.Text)
            if options:
                # Check if the parameter already exists on the shared group.
                existing_def = None
                for d in shared_group.Definitions:
                    if d.Name == param_name:
                        existing_def = d
                        break

                binding = app.Create.NewInstanceBinding(cat_set)
                if existing_def:
                    bindingMap.Insert(existing_def, binding, group)
                else:
                    if options:
                        new_def = shared_group.Definitions.Create(options)
                        bindingMap.Insert(new_def, binding, group)
                t.Commit()
        except Exception as e:
            t.RollBack()
            forms.alert("Failed to create parameter: " + param_name + "\n" + repr(e), exitscript=True)

def get_element_location(elem):
    """
    Returns the location of the element as an XYZ point.
    
    :param elem: The element whose location is being determined.
    :return: An XYZ point or None.
    """
    loc = elem.Location
    try:
        return loc.Point
    except:
        try:
            return loc.Curve.Evaluate(0.5, True)
        except:
            return None

def get_grid_intersections(v_grids, h_grids):
    """
    Calculates and returns intersections between vertical and horizontal grids.
    
    Each intersection is returned as a tuple of (intersection_point, vertical_grid, horizontal_grid).
    
    Note: The Intersect method requires an 'out' parameter, which is handled using clr.Reference.
    
    :param v_grids: List of vertical grid elements.
    :param h_grids: List of horizontal grid elements.
    :return: A list of tuples with intersection information.
    """
    intersections = []
    for v in v_grids:
        for h in h_grids:
            results = clr.Reference[IntersectionResultArray](IntersectionResultArray()) 
            res = v.Curve.Intersect(h.Curve, results)
            if res == SetComparisonResult.Overlap and results.Size > 0:
                ip = results.get_Item(0).XYZPoint
                intersections.append((ip, v, h))
    return intersections

class InitialSelectionFilter(ISelectionFilter):
    """
    A selection filter that allows only elements whose Ids are in the allowed_ids set.
    """
    def __init__(self, allowed_ids):
        self.allowed_ids = allowed_ids
    def AllowElement(self, element):
        return element.Id in self.allowed_ids
    def AllowReference(self, ref, point):
        return False

# Retrieve selected elements and collect their categories.
initial_sel_ids = uidoc.Selection.GetElementIds()
if not initial_sel_ids:
    forms.alert("Please select one or more elements.", exitscript=True)

selected_categories = set()
for eid in initial_sel_ids:
    elem = doc.GetElement(eid)
    if elem.Category:
        selected_categories.add(elem.Category)
selected_categories = list(selected_categories)

# Create a selection filter to restrict picking the starting element to the initial selection.
selection_filter = InitialSelectionFilter(initial_sel_ids)

# Ensure the required parameters are created and bound.
ensure_text_parameter(doc, "Grid Square", selected_categories)
ensure_text_parameter(doc, "Number", selected_categories)

# Prompt user to pick the starting element for numbering.
start_elem = None
try:
    forms.alert("Select the starting element for numbering.", exitscript=False)
    start_ref = uidoc.Selection.PickObject(ObjectType.Element, selection_filter, "Select the starting element for numbering")
    start_elem = doc.GetElement(start_ref)
except Exception as e:
    forms.alert("No starting element selected", exitscript=True)

start_point = get_element_location(start_elem)
if not start_point:
    forms.alert("The starting element does not have a valid location.", exitscript=True)

# Collect grid elements and separate them by orientation.
grids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
vertical_grids = []
horizontal_grids = []
for grid in grids:
    curve = grid.Curve
    direction = curve.Direction
    if abs(direction.X) > abs(direction.Y):
        horizontal_grids.append(grid)
    else:
        vertical_grids.append(grid)

intersections = get_grid_intersections(vertical_grids, horizontal_grids)
if not intersections:
    forms.alert("No grid intersections found. Ensure the model has both vertical and horizontal grids.", exitscript=True)

# Begin a transaction to assign parameters.
t = Transaction(doc, "Assign Grid Square and Number")
t.Start()
modified_elem_ids = set()

# Assign "Grid Square" based on the closest grid intersection.
for eid in initial_sel_ids:
    elem = doc.GetElement(eid)
    pt = get_element_location(elem)
    if pt:
        min_dist = float("inf")
        closest = None
        for (ip, v_grid, h_grid) in intersections:
            dist = pt.DistanceTo(ip)
            if dist < min_dist:
                min_dist = dist
                closest = (v_grid, h_grid)
        if closest:
            grid_square = "{}-{}".format(closest[0].Name, closest[1].Name)
            param = elem.LookupParameter("Grid Square")
            if param and not param.IsReadOnly:
                param.Set(grid_square)
                modified_elem_ids.add(elem.Id)

# Prepare elements for numbering by computing distance from the starting element.
elements_with_distance = []
for id in initial_sel_ids:
    elem = doc.GetElement(id)
    pt = get_element_location(elem)
    if pt:
        distance = pt.DistanceTo(start_point)
        elements_with_distance.append((elem, distance))

elements_with_distance.sort(key=lambda x: x[1])

# Assign sequential "Number" parameter starting at 1.
num = 1
for (elem, dist) in elements_with_distance:
    param = elem.LookupParameter("Number")
    if param and not param.IsReadOnly:
        param.Set(str(num))
        modified_elem_ids.add(elem.Id)
        num += 1

t.Commit()

if (len(modified_elem_ids) ==  len(initial_sel_ids)):
    forms.alert("Selected elements were successfully numbered.")
else:
    forms.alert("Not all elements were numbered.")

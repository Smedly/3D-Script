import adsk.core, adsk.fusion, adsk.cam, traceback

# Fusion 360 script to create Estonian Swearing Machine case only (no lid)
# Includes: case walls, speaker hole, button hole, potentiometer hole, and vent slots

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent

        # Clear old stuff if re-running
        for body in rootComp.bRepBodies:
            body.deleteMe()

        # Parameters (all mm)
        width = 90
        height = 59
        depth = 50
        thickness = 3

        # Component objects
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane

        # Sketch main rectangle
        sketch = sketches.add(xyPlane)
        lines = sketch.sketchCurves.sketchLines
        rect = lines.addCenterPointRectangle(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(width/2, height/2,0))

        # Extrude to depth
        prof = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        caseExtrude = extrudes.addSimple(prof, adsk.core.ValueInput.createByReal(depth), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        caseBody = caseExtrude.bodies.item(0)
        caseBody.name = "ESM_Case"

        # Shell inside (open top)
        shellFeats = rootComp.features.shellFeatures
        allFaces = adsk.core.ObjectCollection.create()
        for f in caseBody.faces:
            if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType and abs(f.geometry.normal.z) > 0.9:
                allFaces.add(f)
        shellInput = shellFeats.createInput(allFaces)
        shellInput.insideThickness = adsk.core.ValueInput.createByReal(thickness)
        shellFeats.add(shellInput)

        # --- Speaker hole (40 mm diameter) ---
        yzPlane = rootComp.yZConstructionPlane
        spSketch = sketches.add(yzPlane)
        spSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(depth/2-2, 0, 2), 20)
        spProf = spSketch.profiles.item(0)
        cutExtrude = extrudes.addSimple(spProf, adsk.core.ValueInput.createByReal(5), adsk.fusion.FeatureOperations.CutFeatureOperation)

        # --- Button hole (22 mm diameter, opposite wall) ---
        spSketch2 = sketches.add(yzPlane)
        spSketch2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(-depth/2+2, 0, 0), 11)
        btnProf = spSketch2.profiles.item(0)
        extrudes.addSimple(btnProf, adsk.core.ValueInput.createByReal(5), adsk.fusion.FeatureOperations.CutFeatureOperation)

        # --- Potentiometer hole (8 mm, above button) ---
        potSketch = sketches.add(yzPlane)
        potSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(-depth/2+2, 0, 10), 4)
        potProf = potSketch.profiles.item(0)
        extrudes.addSimple(potProf, adsk.core.ValueInput.createByReal(5), adsk.fusion.FeatureOperations.CutFeatureOperation)

        # --- Vent slots (bottom, 1x30 mm, 10 slots) ---
        xzPlane = rootComp.xZConstructionPlane
        ventSketch = sketches.add(xzPlane)
        for i in range(-45, 46, 9):
            ventSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(i, -depth/2, -15),
                adsk.core.Point3D.create(i+1, -depth/2+30, -14)
            )
        for prof in ventSketch.profiles:
            extrudes.addSimple(prof, adsk.core.ValueInput.createByReal(5), adsk.fusion.FeatureOperations.CutFeatureOperation)

        ui.messageBox('ESM Case with holes created.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

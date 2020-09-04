def Main():
	rigids = []
	selected = scene.getSelectedNodes()
	for obj in selected:
		if obj.getType() == TYPE_OBJECT and obj.getParameter("Dynamics") == "Active rigid body":
			rigids.append(obj)
	if rigids:
		form = GUIFormDialog.new()
		form.addListField("Axis", ["X", "Y", "Z"], 1)
		form.addVectorField("Offset", 0, 0, 0)
		form.addBoolField("Rel. offset rotation", True)
		form.addBoolField("Rel. offset scale", True)
		form.addObjectField("Parent object", TYPE_OBJECT, SELECTION_UNIQUE)
		form.setTitle("Hinge creator")
		if form.show() == GUI_DIALOG_ACCEPTED:
			for rigid in rigids:
				axis = "XYZ"[form.getFieldValue("Axis")]
				offset = form.getFieldValue("Offset")
				relRot = form.getFieldValue("Rel. offset rotation")
				relScale = form.getFieldValue("Rel. offset scale")
				fixObj = form.getFieldValue("Parent object")
				CreateHinge(rigid, axis, offset, relRot, relScale, fixObj)
			scene.message(str(len(rigids)) + " " + axis + " hinge" + ("s were" if len(rigids)>1 else " was") + " created.")
	else:
		 GUIMessageDialog.new().show(ALERT_TYPE_INFORMATION, "No rigids were selected! Please first select rigids you wish to create hinges for.")
		
def GetAxisVector(ax):
	return V(ax == "X", ax == "Y", ax == "Z")
def X(v):
	return v.getX()
def Y(v):
	return v.getY()
def Z(v):
	return v.getZ()
def V(x, y, z):
	return Vector.new(x, y, z)
def Mul(a, b):
	return V(X(a)*X(b), Y(a)*Y(b), Z(a)*Z(b))
def Div(a, b):
	return V(X(a)/X(b), Y(a)/Y(b), Z(a)/Z(b))

def SaveSetName(obj, name):
	currName = name
	i = 2
	while scene.getNode(currName):
		currName = name + "_" + str(i)
		i += 1
	obj.setName(currName)

def GetObjectSize(obj):
	min, max = obj.getBoundingBox()
	return max - min

def Scale(v, q):
	return V(X(v) * q, Y(v) * q, Z(v) * q)

def CreateHinge(obj, axis, offset, relRot, relScale, fixObj):
	axisV = GetAxisVector(axis)
	pos = obj.getParameter("Position")
	scale = GetObjectSize(obj)
	scaleD = axisV * scale
	name = obj.getName()	
	
	hinge = scene.addCube()
	hinge.setParameter("Scale", Scale(axisV, scaleD * 1.2) + Scale(V(1, 1, 1) - axisV, scaleD/10))
	SaveSetName(hinge, "Hinge_locator_B_of_" + name)
	hinge.setParameter("Color", V(0,0,0))
	hinge.setParameter("Texture", "Object")	
	if relRot:
		hinge.setParameter("Parent to", name)
		hinge.setParameter("Position", offset.scale(0.5) if relScale else Div(offset, scale))
		hinge.setParameter("Parent to", "")
	else:
		hinge.setParameter("Position", Mul(offset, scale).scale(0.5) if relScale else offset)
	obj.setParameter("Parent to", hinge.getName())
	if fixObj:
		hinge.setParameter("Parent to", fixObj[0])
	
	null = scene.addNull()
	null.setParameter("Parent to", hinge.getName())
	null.setParameter("Position", axisV.scale(0.25))
	null.setParameter("Visible", False)
	SaveSetName(null, "Hinge_locator_A_of_" + name)
	
	joint = scene.addMultiJoint()
	SaveSetName(joint, "Joint_of_" + name + "_hinge")
	joint.setParameter("Objects A", name)
	if fixObj:
		joint.setParameter("Objects B", fixObj[0])
	joint.setParameter("Creation mode", "At locators positions")
	joint.setParameter("@ Locators", hinge.getName() + " " + null.getName())
	joint.create()
	
	group = scene.addGroup()
	SaveSetName(group, axis + "_Hinge_of_" + name)
	group.add(joint.getName())
	group.add(hinge.getName())
	group.add(null.getName())

Main()
bl_info = {
    "category": "Camera",
    "name": "Multicamera Rendering Plugin",
    "author": "TRAK",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Camera > Properties Panel > Multicamera",
    "description": "Utils for setting up multiple camera matrices.",
}

import bpy


class OBJECT_PT_multicam_panel(bpy.types.Panel):

    # panel location
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    bl_category = "Multicamera"
    bl_label = "Multicamera properties"

    @classmethod
    def poll(self, context):
        return context.active_object.type  == 'CAMERA'
    
    bpy.types.Object.camera_type = bpy.props.EnumProperty(
        attr="camera_type",
        items=( ("SINGLE", "Single", "Default single camera"),
                ("STEREO", "Stereo", "Stereo camera"),
                ("MATRIX", "Matrix", "Matrix of cameras (light-field)"),
                ("MESH", "Mesh", "Mesh of cameras around object")),
        name="camera_type", 
        description="Camera type (single camera / multiple cameras in different configurations)", 
        default="SINGLE")

    bpy.types.Object.stereo_focal_distance = bpy.props.FloatProperty(
        attr="stereo_focal_distance",
        name='stereo_focal_distance', 
        description='Distance to the Stereo-Window (Zero Parallax) in Blender Units',
        min=0.0, soft_min=0.0, max=1000, soft_max=1000, default=20)

    # user interface
    def draw(self, context):
        layout = self.layout

        camera = context.scene.camera
        tmp_cam = context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            camera = bpy.data.objects[camera.name[2:]]

        row = layout.row()
        row.prop(camera, "camera_type", text="Stereo Camera Type", expand=True)

        row = layout.row()
        row.prop(camera, "stereo_focal_distance", text="Zero Parallax")

        row = layout.row()
        row.operator('multicam.set_cameras')


class OBJECT_OT_set_cameras(bpy.types.Operator):
    bl_label = 'Set Stereo Camera'
    bl_idname = 'multicam.set_cameras'
    bl_description = 'Setup the Cameras'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.set_camera(context)
        return {'FINISHED'}

    def set_camera(self, context):
        tmp_camera = context.scene.camera 
        if(tmp_camera.name[:2]=="L_" or tmp_camera.name[:2]=="R_"):
            center_cam = bpy.data.objects[tmp_camera.name[2:]]
        else:
            center_cam = tmp_camera
        active_cam = bpy.data.objects[center_cam.name]
        context.scene.camera = active_cam
        camera = bpy.context.scene.camera

        # check for existing stereocamera objects
        left_cam_exists = 0
        right_cam_exists = 0
        zero_plane_exists = 0
        near_plane_exists = 0
        far_plane_exists = 0
        scn = bpy.context.scene
        for ob in scn.collection.objects:
            if(ob.name == "L_"+center_cam.name):
                left_cam_exists = 1
            if(ob.name == "R_"+center_cam.name):
                right_cam_exists = 1
            if(ob.name == "SW_"+center_cam.name):
                zero_plane_exists = 1
            if(ob.name == "NP_"+center_cam.name):
                near_plane_exists = 1
            if(ob.name == "FP_"+center_cam.name):
                far_plane_exists = 1
    
        # add a new or (if exists) get the left camera
        if(left_cam_exists==0):
            left_cam = bpy.data.cameras.new('L_'+center_cam.name)
            left_cam_obj = bpy.data.objects.new('L_'+center_cam.name, left_cam)
            scn.collection.objects.link(left_cam_obj)
        else:
            left_cam_obj = bpy.data.objects['L_'+center_cam.name]  
            left_cam = left_cam_obj.data 
    
        # add a new or (if exists) get the right camera
        if(right_cam_exists==0):
            right_cam = bpy.data.cameras.new('R_'+center_cam.name)
            right_cam_obj = bpy.data.objects.new('R_'+center_cam.name, right_cam)
            scn.collection.objects.link(right_cam_obj)    
        else:
            right_cam_obj = bpy.data.objects['R_'+center_cam.name]
            right_cam = right_cam_obj.data

        # temp location
        # set the left camera
        left_cam.angle = center_cam.data.angle
        left_cam.clip_start = center_cam.data.clip_start
        left_cam.clip_end = center_cam.data.clip_end
        # left_cam.dof_distance = center_cam.data.dof_distance
        # left_cam.dof_object = center_cam.data.dof_object
        left_cam.shift_y = center_cam.data.shift_y
        left_cam.shift_x = (1/2)+center_cam.data.shift_x
        left_cam_obj.location = -(100/1000)/2,0,0
        left_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset

        # set the right camera
        right_cam.angle = center_cam.data.angle
        right_cam.clip_start = center_cam.data.clip_start
        right_cam.clip_end = center_cam.data.clip_end
        # right_cam.dof_distance = center_cam.data.dof_distance
        # right_cam.dof_object = center_cam.data.dof_object
        right_cam.shift_y = center_cam.data.shift_y
        right_cam.shift_x = -(1/2)+center_cam.data.shift_x
        right_cam_obj.location = (100/1000)/2,0,0
        right_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset

        left_cam_obj.parent = center_cam
        right_cam_obj.parent = center_cam

        # select the center camera (object mode)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.camera = tmp_camera
        # bpy.context.scene.objects.active = tmp_camera
        # tmp_camera.select = True

        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_PT_multicam_panel)
    bpy.utils.register_class(OBJECT_OT_set_cameras)


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_multicam_panel)
    bpy.utils.unregister_class(OBJECT_OT_set_cameras)


if __name__ == "__main__":
    register()

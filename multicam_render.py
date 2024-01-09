import bpy
import os
import json

bl_info = {
    "category": "Camera",
    "name": "Multi camera Rendering Plugin",
    "author": "TRAK",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Camera > Properties Panel > Multi camera",
    "description": "Utils for setting up multiple camera matrices.",
}


DEFAULT_CAMERA_NAME = "Camera"

class CameraUtils():
    @staticmethod
    def reset_multicamera(context):
        # reset multicamera by deleting all children
        base_camera = context.scene.camera
        if base_camera.multicam_child and base_camera.parent is not None and base_camera.parent.type == 'CAMERA':
            base_camera = base_camera.parent
            context.scene.camera = base_camera

        del_names = [obj.name for obj in base_camera.children]

        with context.temp_override(selected_objects=base_camera.children):
            bpy.ops.object.delete()

        for name in del_names:
            bpy.data.cameras.remove(bpy.data.cameras[name], do_unlink=True)

    @staticmethod
    def create_child_camera(suffix, parent):
        cam_data = bpy.data.cameras.new(DEFAULT_CAMERA_NAME + suffix)
        cam_obj = bpy.data.objects.new(DEFAULT_CAMERA_NAME + suffix, cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        cam_obj.multicam_child = True
        cam_obj.parent = parent
        return cam_data, cam_obj


class OBJECT_PT_multicam_panel(bpy.types.Panel):
    # panel location
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    bl_category = "Multi camera"
    bl_label = "Multi camera properties"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'CAMERA'
    
    def update_camera_type(self, context):
        match self.camera_type:
            case "SINGLE":
                bpy.ops.multicam.set_single_camera('INVOKE_DEFAULT')
            case "STEREO":
                bpy.ops.multicam.set_stereo_cameras('INVOKE_DEFAULT')
            case "MATRIX":
                bpy.ops.multicam.set_matrix_cameras('INVOKE_DEFAULT')
            case "MESH":
                bpy.ops.multicam.set_mesh_cameras('INVOKE_DEFAULT')

    bpy.types.Object.camera_type = bpy.props.EnumProperty(
        attr="camera_type",
        items=(("SINGLE", "Single", "Default single camera"),
               ("STEREO", "Stereo", "Stereo camera"),
               ("MATRIX", "Matrix", "Matrix of cameras (light-field)"),
               ("MESH", "Mesh", "Mesh of cameras around object")),
        name="camera_type",
        description="Camera type (single camera / multiple cameras in different configurations)",
        default="SINGLE",
        update=update_camera_type
    )

    bpy.types.Object.multicam_child = bpy.props.BoolProperty(
        attr="multicam_child",
        name="multicam_child",
        description="Camera is a multicam child",
        default=False
    )

    bpy.types.Object.stereo_focal_distance = bpy.props.FloatProperty(
        attr="stereo_focal_distance",
        name="stereo_focal_distance",
        description="Distance to the Stereo-Window (Zero Parallax) in Blender Units",
        min=0.0, soft_min=0.0, max=1000, soft_max=1000, default=20,
        update=update_camera_type
    )

    bpy.types.Object.matrix_vertical_distance = bpy.props.IntProperty(
        attr="matrix_vertical_distance",
        name="matrix_vertical_distance",
        description="Distance between cameras in vertical direction",
        min=0, soft_min=0, max=10000, soft_max=1000, default=100,
        update=update_camera_type
    )

    bpy.types.Object.matrix_horizontal_distance = bpy.props.IntProperty(
        attr="matrix_horizontal_distance",
        name="matrix_horizontal_distance",
        description="Distance between cameras in horizontal direction",
        min=0, soft_min=0, max=10000, soft_max=1000, default=100,
        update=update_camera_type
    )

    bpy.types.Object.matrix_vertical_amount = bpy.props.IntProperty(
        attr="matrix_vertical_amount",
        name="matrix_vertical_amount",
        description="Amount of cameras in vertical axis",
        min=2, soft_min=0, max=15, soft_max=15, default=3,
        update=update_camera_type
    )

    bpy.types.Object.matrix_horizontal_amount = bpy.props.IntProperty(
        attr="matrix_horizontal_amount",
        name="matrix_horizontal_amount",
        description="Amount of cameras in horizontal axis",
        min=2, soft_min=0, max=15, soft_max=15, default=3,
        update=update_camera_type
    )

    # user interface
    def draw(self, context):
        layout = self.layout

        camera = context.active_object
        if camera.parent is not None and camera.parent.type == 'CAMERA':
            camera = camera.parent

        row = layout.row()
        row.prop(camera, "camera_type", text="Stereo Camera Type", expand=True)

        match camera.camera_type:
            case "SINGLE":
                self.draw_single_camera_sub_layout(context)
            case "STEREO":
                self.draw_stereo_camera_sub_layout(context)
            case "MATRIX":
                self.draw_matrix_camera_sub_layout(context)
            case "MESH":
                self.draw_mesh_camera_sub_layout(context)

    def draw_single_camera_sub_layout(self, context):
        row = self.layout.row()

    def draw_stereo_camera_sub_layout(self, context):
        camera = context.scene.camera
        row1 = self.layout.grid_flow(columns=2, even_columns=False, even_rows=False, align=True)
        column1 = row1.column()
        column1.alignment = "RIGHT"
        column1.label(text="Zero Parallax")
        column2 = row1.column()
        column2.prop(camera, "stereo_focal_distance", text="", slider=True)

        row2 = self.layout.row()

    def draw_matrix_camera_sub_layout(self, context):
        camera = context.scene.camera
        row1 = self.layout.grid_flow(columns=2, even_columns=False, even_rows=False, align=True)

        column1 = row1.column()
        column1.alignment = "RIGHT"
        column1.label(text="Vertical amount")
        column1.label(text="Horizontal amount")
        column1.label(text="Vertical distance")
        column1.label(text="Horizontal distance")
        column2 = row1.column()
        column2.prop(camera, "matrix_vertical_amount", text="", slider=True)
        column2.prop(camera, "matrix_horizontal_amount", text="", slider=True)
        column2.prop(camera, "matrix_vertical_distance", text="", slider=True)
        column2.prop(camera, "matrix_horizontal_distance", text="", slider=True)

        row2 = self.layout.row()

    def draw_mesh_camera_sub_layout(self, context):
        row = self.layout.row()


class OUTPUT_PT_multicam_panel(bpy.types.Panel):
    # panel location
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    bl_category = "Multi camera"
    bl_label = "Multi camera output"

    bpy.types.Scene.renderQueue = bpy.props.StringProperty(
        attr="renderQueue",
        name="renderQueue",
        description="Queue of cameras to render",
        default="[]"
    )
    bpy.types.Scene.rendering = bpy.props.BoolProperty(
        attr="rendering",
        name="rendering",
        description="Render in progress",
        default=False
    )
    bpy.types.Scene.cancelRender = bpy.props.BoolProperty(
        attr="cancelRender",
        name="cancelRender",
        description="Render canceled",
        default=False
    )
    bpy.types.Scene.baseOutputPath = bpy.props.StringProperty(
        attr="baseOutputPath",
        name="baseOutputPath",
        description="Base output path",
        default=""
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'CAMERA' and context.active_object.camera_type != 'SINGLE'

    def draw(self, context):
        row = self.layout.row()
        column1 = row.column()
        column1.operator('multicam.render_multi_cameras')
        column2 = row.column()
        column2.operator('multicam.cancel_rendering')


class OutputOTRenderMultiCameras(bpy.types.Operator):
    bl_label = 'Render Multi Cameras'
    bl_idname = 'multicam.render_multi_cameras'
    bl_description = 'Render all cameras'
    bl_options = {'REGISTER'}

    timerEvent = None

    # Rendering callback functions
    @staticmethod
    def pre_render(scene, *args):
        scene.rendering = True

    @staticmethod
    def post_render(scene, *args):
        print("post render")
        renderQueue = json.loads(scene.renderQueue)
        renderQueue.pop(0) # remove finished item from render queue
        scene.renderQueue = json.dumps(renderQueue)
        print('remaining queue: ' + scene.renderQueue)
        scene.rendering = False
        scene.camera = scene.camera.parent # restore base camera
        bpy.context.view_layer.update() 

    @staticmethod
    def on_render_cancel(scene, *args):
        scene.cancelRender = True
        scene.render.filepath = scene.baseOutputPath # restore base output path
        scene.camera = scene.camera.parent # restore base camera

    def execute(self, context):
        context.scene.cancelRender = False
        context.scene.rendering = False
        
        # fill renderQueue with all cameras
        renderQueue = []
        base_camera = context.scene.camera
        cameras = [obj for obj in base_camera.children if obj.type == 'CAMERA']

        for camera in cameras:
            renderQueue.append(camera.name)

        print(renderQueue)

        context.scene.renderQueue = json.dumps(renderQueue)
        context.scene.baseOutputPath = context.scene.render.filepath
        
        # Register callback functions
        bpy.app.handlers.render_init.append(self.pre_render)
        bpy.app.handlers.render_complete.append(self.post_render)
        bpy.app.handlers.render_cancel.append(self.on_render_cancel)
        # Create timer event that runs every second to check if render renderQueue needs to be updated
        self.timerEvent = context.window_manager.event_timer_add(1.0, window=context.window)

        # register this as running in background 
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        bpy.context.view_layer.update()
        renderQueue = json.loads(context.scene.renderQueue)
        rendering = context.scene.rendering
        cancelRender = context.scene.cancelRender

        if event.type == 'TIMER':                                 
            # If cancelled or no items in queue to render, finish.
            if not renderQueue or cancelRender is True:
                # remove all render callbacks and cancel timer event
                bpy.app.handlers.render_init.remove(self.pre_render)
                bpy.app.handlers.render_complete.remove(self.post_render)
                bpy.app.handlers.render_cancel.remove(self.on_render_cancel)
                context.window_manager.event_timer_remove(self.timerEvent)

                context.scene.renderQueue = json.dumps([])
                context.scene.render.filepath = context.scene.baseOutputPath # restore base output path
                context.scene.baseOutputPath = ""
                
                self.report({"INFO"},"RENDER QUEUE FINISHED")
                return {"FINISHED"} 
            # nothing is rendering and there are items in queue
            elif rendering is False:
                bpy.context.view_layer.update()

                sc = context.scene
                cameraName = renderQueue[0]

                if sc.baseOutputPath:
                    sc.render.filepath = sc.baseOutputPath # restore base output path
                
                # change scene active camera
                if cameraName in sc.objects:
                    sc.camera = bpy.data.objects[cameraName]
                else:
                    self.report({'ERROR_INVALID_INPUT'}, message="Can not find camera " + cameraName + " in scene!")
                    return {'CANCELLED'}
                    
                self.report({"INFO"}, "Rendering camera: " + cameraName)
                # set output file path as base path + camera name
                original_output_dir = bpy.context.scene.render.filepath
                output_dir = bpy.context.scene.render.filepath
                if not os.path.exists(os.path.join(output_dir, cameraName)):
                    os.makedirs(os.path.join(output_dir, cameraName))
                bpy.context.scene.render.filepath = os.path.join(output_dir, cameraName, '')

                sc.baseOutputPath = original_output_dir
                bpy.context.view_layer.update()
                # start new render
                bpy.ops.render.render("INVOKE_DEFAULT", animation=True)
        return {"PASS_THROUGH"}


class OutputOTCancelRendering(bpy.types.Operator):
    bl_label = 'Cancel'
    bl_idname = 'multicam.cancel_rendering'
    bl_description = 'Cancel rendering queue'
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.scene.cancelRender = True
        return {'FINISHED'}


class ObjectOTSetSingleCamera(bpy.types.Operator):
    bl_label = 'Set Single Camera'
    bl_idname = 'multicam.set_single_camera'
    bl_description = 'Setup the Camera'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.set_camera(context)
        return {'FINISHED'}

    def set_camera(self, context):
        CameraUtils.reset_multicamera(context)

        return {'FINISHED'}


class ObjectOTSetStereoCameras(bpy.types.Operator):
    bl_label = 'Set Stereo Cameras'
    bl_idname = 'multicam.set_stereo_cameras'
    bl_description = 'Setup the Cameras'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.set_camera(context)
        return {'FINISHED'}

    def set_camera(self, context):
        CameraUtils.reset_multicamera(context)
        scene = context.scene
        base_camera = scene.camera

        # add a new left camera
        left_cam_data, left_cam_obj = CameraUtils.create_child_camera('_L', base_camera)

        # add a new right camera
        right_cam_data, right_cam_obj = CameraUtils.create_child_camera('_R', base_camera)

        # temp location
        # set the left camera
        right_cam_data.angle = base_camera.data.angle
        right_cam_data.clip_start = base_camera.data.clip_start
        right_cam_data.clip_end = base_camera.data.clip_end
        # left_cam.dof_distance = center_cam.data.dof_distance
        # left_cam.dof_object = center_cam.data.dof_object
        right_cam_data.shift_y = base_camera.data.shift_y
        right_cam_data.shift_x = (1 / 2) + base_camera.data.shift_x
        right_cam_obj.location = -(100 / 1000) / 2, 0, 0
        right_cam_obj.rotation_euler = (0.0, 0.0, 0.0)  # reset

        # set the right camera
        right_cam_data.angle = base_camera.data.angle
        right_cam_data.clip_start = base_camera.data.clip_start
        right_cam_data.clip_end = base_camera.data.clip_end
        # right_cam.dof_distance = center_cam.data.dof_distance
        # right_cam.dof_object = center_cam.data.dof_object
        right_cam_data.shift_y = base_camera.data.shift_y
        right_cam_data.shift_x = -(1 / 2) + base_camera.data.shift_x
        right_cam_obj.location = (100 / 1000) / 2, 0, 0
        right_cam_obj.rotation_euler = (0.0, 0.0, 0.0)  # reset

        right_cam_obj.parent = base_camera
        right_cam_obj.parent = base_camera

        # select the center camera (object mode)
        bpy.ops.object.select_all(action='DESELECT')
        base_camera.select_set(True)
        bpy.context.scene.objects.active = base_camera
        # tmp_camera.select = True

        return {'FINISHED'}


class ObjectOTSetMatrixCameras(bpy.types.Operator):
    bl_label = 'Set Matrix Cameras'
    bl_idname = 'multicam.set_matrix_cameras'
    bl_description = 'Setup the Cameras'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.set_camera(context)
        return {'FINISHED'}

    def set_camera(self, context):
        CameraUtils.reset_multicamera(context)
        scene = context.scene
        base_camera = scene.camera

        w_amount = base_camera.matrix_horizontal_amount
        h_amount = base_camera.matrix_vertical_amount

        for y_idx in range(h_amount):
            for x_idx in range(w_amount):
                suffix = '_Y' + str(y_idx) + '_X' + str(x_idx)
                cam_data, cam_obj = CameraUtils.create_child_camera(suffix, base_camera)

                cam_data.angle = base_camera.data.angle
                cam_data.clip_start = base_camera.data.clip_start
                cam_data.clip_end = base_camera.data.clip_end
                # cam.dof_distance = center_cam.data.dof_distance
                # cam.dof_object = center_cam.data.dof_object
                cam_data.shift_y = base_camera.data.shift_y
                cam_data.shift_x = base_camera.data.shift_x
                cam_obj.location = (x_idx * base_camera.matrix_horizontal_distance) / 100, (y_idx * base_camera.matrix_vertical_distance) / 100, 0
                cam_obj.rotation_euler = (0.0, 0.0, 0.0)

        return {'FINISHED'}


class ObjectOTSetMeshCameras(bpy.types.Operator):
    bl_label = 'Set Mesh Cameras'
    bl_idname = 'multicam.set_mesh_cameras'
    bl_description = 'Setup the Cameras'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.set_camera(context)
        return {'FINISHED'}

    def set_camera(self, context):
        return {'FINISHED'}


classes = (
    OBJECT_PT_multicam_panel,
    ObjectOTSetSingleCamera,
    ObjectOTSetStereoCameras,
    ObjectOTSetMatrixCameras,
    ObjectOTSetMeshCameras,
    OutputOTRenderMultiCameras,
    OutputOTCancelRendering,
    OUTPUT_PT_multicam_panel
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()

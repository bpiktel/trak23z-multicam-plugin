import bpy
import os
import json
import math

bl_info = {
    "category": "Camera",
    "name": "Multi camera Rendering Plugin",
    "author": "TRAK",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
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

        for constraint in base_camera.constraints:
            base_camera.constraints.remove(constraint)

    @staticmethod
    def create_child_camera(suffix, parent):
        master_collection = bpy.context.scene.collection
        current_collection = parent.users_collection[0]
        cam_data = bpy.data.cameras.new(DEFAULT_CAMERA_NAME + suffix)
        cam_obj = bpy.data.objects.new(DEFAULT_CAMERA_NAME + suffix, cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        cam_obj.multicam_child = True
        cam_obj.parent = parent

        current_collection.objects.link(cam_obj)
        master_collection.objects.unlink(cam_obj)

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

    # Stereo camera properties
    bpy.types.Object.stereo_focal_distance = bpy.props.FloatProperty(
        attr="stereo_focal_distance",
        name="stereo_focal_distance",
        description="Distance to the Stereo-Window (Zero Parallax) in Blender Units",
        min=0.0, soft_min=0.0, max=1000, soft_max=1000, default=20,
        update=update_camera_type
    )

    # Matrix camera properties
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

    # Mesh camera properties
    bpy.types.Object.pattern_type = bpy.props.EnumProperty(
        attr="pattern_type",
        items=(("ORBIT", "Orbit", "Orbit around object"),
               ("SPHERE", "Sphere", "Sphere of cameras around object")),
        name="pattern_type",
        description="Pattern type (orbit / sphere) for mesh camera",
        default="ORBIT",
        update=update_camera_type
    )

    bpy.types.Object.target_object = bpy.props.StringProperty(
        attr="target_object",
        name="target_object",
        description="Target object for mesh camera",
        default="",
        update=update_camera_type
    )

    bpy.types.Object.radius = bpy.props.FloatProperty(
        attr="radius",
        name="radius",
        description="Radius of mesh camera",
        min=0.0, soft_min=0.0, max=1000, soft_max=1000, default=5,
        update=update_camera_type
    )

    bpy.types.Object.mesh_horizontal_amount = bpy.props.IntProperty(
        attr="mesh_horizontal_amount",
        name="mesh_horizontal_amount",
        description="Amount of cameras in horizontal axis",
        min=2, soft_min=0, max=100, soft_max=30, default=4,
        update=update_camera_type
    )

    bpy.types.Object.mesh_vertical_amount = bpy.props.IntProperty(
        attr="mesh_vertical_amount",
        name="mesh_vertical_amount",
        description="Amount of cameras in vertical axis",
        min=2, soft_min=0, max=100, soft_max=30, default=4,
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
        row1 = self.layout.grid_flow(
            columns=2, even_columns=False, even_rows=False, align=True)
        column1 = row1.column()
        column1.alignment = "RIGHT"
        column1.label(text="Zero Parallax")
        column2 = row1.column()
        column2.prop(camera, "stereo_focal_distance", text="", slider=True)

        row2 = self.layout.row()

    def draw_matrix_camera_sub_layout(self, context):
        camera = context.scene.camera
        row1 = self.layout.grid_flow(
            columns=2, even_columns=False, even_rows=False, align=True)

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
        column2.prop(camera, "matrix_horizontal_distance",
                     text="", slider=True)

        row2 = self.layout.row()

    def draw_mesh_camera_sub_layout(self, context):
        column = self.layout.column()

        row1 = column.row()
        row1.prop(context.scene.camera, "pattern_type",
                  text="Pattern Type", expand=True)

        row2 = column.row()
        row2.prop_search(context.scene.camera, "target_object",
                         context.scene, "objects", text="Target Object")

        row3 = column.row()
        row3.prop(context.scene.camera, "radius", text="Radius")

        row4 = column.row()
        row4.prop(context.scene.camera, "mesh_horizontal_amount",
                  text="Horizontal amount", slider=True)


class OUTPUT_PT_multicam_panel(bpy.types.Panel):
    # panel location
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    bl_category = "Multi camera"
    bl_label = "Multi camera output"

    # Options
    bpy.types.Scene.frameByFrame = bpy.props.BoolProperty(
        attr="frameByFrame",
        name="frameByFrame",
        description="Frame by frame rendering mode",
        default=False
    )
    bpy.types.Scene.copyMainCameraProperties = bpy.props.BoolProperty(
        attr="copyMainCameraProperties",
        name="copyMainCameraProperties",
        description="Copy main camera properties to all cameras",
        default=True
    )

    # Current render queue state
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
    bpy.types.Scene.baseStartFrame = bpy.props.IntProperty(
        attr="baseStartFrame",
        name="baseStartFrame",
        description="Saved start frame of scene",
        default=0
    )
    bpy.types.Scene.baseEndFrame = bpy.props.IntProperty(
        attr="baseEndFrame",
        name="baseEndFrame",
        description="Saved end frame of scene",
        default=0
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'CAMERA' and context.active_object.camera_type != 'SINGLE'

    @staticmethod
    def isVideoRender(format):
        videoFormats = [
            'AVI_JPEG',
            'AVI_RAW',
            'FFMPEG'
        ]
        return format in videoFormats

    def draw(self, context):
        scene = context.scene
        column = self.layout.column()
        row1 = column.row()
        if scene.rendering is True:
            row1.operator('multicam.cancel_rendering')
        else:
            row1.operator('multicam.render_multi_cameras')
        row2 = column.row()
        if self.isVideoRender(
                scene.render.image_settings.file_format):
            row2.label(
                text="Frame by frame rendering unavailable")
        else:
            row2.prop(context.scene, "frameByFrame",
                      text="Frame by frame rendering")
        row3 = column.row()
        row3.prop(context.scene, "copyMainCameraProperties",
                  text="Copy main camera properties to all cameras")


class OutputOTRenderMultiCameras(bpy.types.Operator):
    bl_label = 'Render Multi Cameras'
    bl_idname = 'multicam.render_multi_cameras'
    bl_description = 'Render selected multicamera'
    bl_options = {'REGISTER'}

    timerEvent = None

    # Rendering callback functions
    @staticmethod
    def pre_render(scene, *args):
        scene.rendering = True

    @staticmethod
    def post_render(scene, *args):
        renderQueue = json.loads(scene.renderQueue)
        renderQueue.pop(0)  # remove finished item from render queue
        scene.renderQueue = json.dumps(renderQueue)
        print('remaining queue: ' + scene.renderQueue)
        scene.rendering = False
        scene.camera = scene.camera.parent  # restore base camera
        bpy.context.view_layer.update()

    @staticmethod
    def on_render_cancel(scene, *args):
        scene.cancelRender = True
        scene.render.filepath = scene.baseOutputPath  # restore base output path
        scene.camera = scene.camera.parent  # restore base camera
        # restore selected frame range
        scene.frame_start = scene.baseStartFrame
        scene.frame_end = scene.baseEndFrame

    def execute(self, context):
        scene = context.scene
        scene.cancelRender = False
        scene.rendering = False

        if OUTPUT_PT_multicam_panel.isVideoRender(scene.render.image_settings.file_format):
            scene.frameByFrame = False

        # fill renderQueue with all cameras
        renderQueue = []
        base_camera = scene.camera
        cameras = [obj for obj in base_camera.children if obj.type == 'CAMERA']

        if scene.frameByFrame is True:
            for i in range(scene.frame_start, scene.frame_end + 1, scene.frame_step):
                for camera in cameras:
                    renderQueue.append(
                        {'camera': camera.name, 'frameStart': i, 'frameEnd': i}
                    )
        else:
            for camera in cameras:
                renderQueue.append(
                    {'camera': camera.name, 'frameStart': scene.frame_start, 'frameEnd': scene.frame_end})

        scene.renderQueue = json.dumps(renderQueue)
        scene.baseOutputPath = scene.render.filepath
        scene.baseStartFrame = scene.frame_start
        scene.baseEndFrame = scene.frame_end

        # Register callback functions
        bpy.app.handlers.render_init.append(self.pre_render)
        bpy.app.handlers.render_complete.append(self.post_render)
        bpy.app.handlers.render_cancel.append(self.on_render_cancel)
        # Create timer event that runs every second to check if render renderQueue needs to be updated
        self.timerEvent = context.window_manager.event_timer_add(
            1.0, window=context.window)

        # register this as running in background
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        bpy.context.view_layer.update()
        scene = context.scene
        renderQueue = json.loads(scene.renderQueue)
        rendering = scene.rendering
        cancelRender = scene.cancelRender

        if event.type == 'TIMER':
            # If cancelled or no items in queue to render, finish.
            if not renderQueue or cancelRender is True:
                # remove all render callbacks and cancel timer event
                bpy.app.handlers.render_init.remove(self.pre_render)
                bpy.app.handlers.render_complete.remove(self.post_render)
                bpy.app.handlers.render_cancel.remove(self.on_render_cancel)
                context.window_manager.event_timer_remove(self.timerEvent)

                scene.renderQueue = json.dumps([])
                # restore base output path
                scene.render.filepath = scene.baseOutputPath
                scene.baseOutputPath = ""
                # restore selected frame range
                scene.frame_start = scene.baseStartFrame
                scene.frame_end = scene.baseEndFrame

                self.report({"INFO"}, "RENDER QUEUE FINISHED")
                return {"FINISHED"}
            # nothing is rendering and there are items in queue
            elif rendering is False:
                bpy.context.view_layer.update()

                scene = context.scene
                queueItem = renderQueue[0]
                cameraName = queueItem['camera']
                frameStart = queueItem['frameStart']
                frameEnd = queueItem['frameEnd']

                if scene.baseOutputPath:
                    scene.render.filepath = scene.baseOutputPath  # restore base output path

                # change scene active camera
                if cameraName in scene.objects:
                    scene.camera = bpy.data.objects[cameraName]
                    if scene.copyMainCameraProperties is True:
                        # copy camera properties from base camera
                        scene.camera.data = scene.camera.parent.data.copy()
                else:
                    self.report(
                        {'ERROR_INVALID_INPUT'}, message="Can not find camera " + cameraName + " in scene!")
                    return {'CANCELLED'}

                self.report({"INFO"}, "Rendering camera: " + cameraName)
                # set output file path as base path + camera name
                original_output_dir = scene.render.filepath
                output_dir = scene.render.filepath
                if not os.path.exists(os.path.join(output_dir, cameraName)):
                    os.makedirs(os.path.join(output_dir, cameraName))
                scene.render.filepath = os.path.join(
                    output_dir, cameraName, '')
                scene.frame_start = frameStart
                scene.frame_end = frameEnd

                scene.baseOutputPath = original_output_dir
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
        left_cam_data, left_cam_obj = CameraUtils.create_child_camera(
            '_L', base_camera)

        # add a new right camera
        right_cam_data, right_cam_obj = CameraUtils.create_child_camera(
            '_R', base_camera)

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
                cam_data, cam_obj = CameraUtils.create_child_camera(
                    suffix, base_camera)

                cam_data.angle = base_camera.data.angle
                cam_data.clip_start = base_camera.data.clip_start
                cam_data.clip_end = base_camera.data.clip_end
                # cam.dof_distance = center_cam.data.dof_distance
                # cam.dof_object = center_cam.data.dof_object
                cam_data.shift_y = base_camera.data.shift_y
                cam_data.shift_x = base_camera.data.shift_x
                cam_obj.location = (x_idx * base_camera.matrix_horizontal_distance) / \
                    100, (y_idx * base_camera.matrix_vertical_distance) / 100, 0
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
        CameraUtils.reset_multicamera(context)
        scene = context.scene
        base_camera = scene.camera

        target = bpy.data.objects[base_camera.target_object]
        radius = base_camera.radius

        target_pos = target.matrix_world.translation

        for i in range(base_camera.mesh_horizontal_amount):
            angle = (i / base_camera.mesh_horizontal_amount) * 2 * math.pi
            new_camera_pos = (radius * math.cos(angle) + target_pos[0],
                              radius * math.sin(angle) + target_pos[1], target_pos[2])
            suffix = '_R' + str(i)
            cam_data, cam_obj = CameraUtils.create_child_camera(
                suffix, base_camera)

            cam_obj.matrix_world.translation = new_camera_pos

            track_to = cam_obj.constraints.new('TRACK_TO')
            track_to.target = target
            track_to.track_axis = 'TRACK_NEGATIVE_Z'
            track_to.up_axis = 'UP_Y'

        # select the center camera (object mode)
        bpy.ops.object.select_all(action='DESELECT')
        base_camera.select_set(True)

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

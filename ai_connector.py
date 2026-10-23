# Bforartists 2 / Blender 2.93 Add-on: AI Connector
# File: ai_connector.py

bl_info = {
    "name": "AI Connector",
    "author": "Expert Developer",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > AI Tool",
    "description": "Connects Bforartists/Blender to an external AI API to generate and execute Python code",
    "warning": "",
    "doc_url": "",
    "category": "Development",
}

import bpy
import urllib.request
import urllib.error
import json

class AI_OT_Generate(bpy.types.Operator):
    """Send prompt to external AI API and execute the returned Python code"""
    bl_idname = "ai.generate"
    bl_label = "Generate & Execute"
    bl_description = "Send the text prompt to the specified API, retrieve Python code, and execute it"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        prompt = scene.ai_prompt
        api_url = scene.ai_api_url

        if not prompt.strip():
            self.report({'WARNING'}, "Prompt cannot be empty!")
            scene.ai_status = "Error: Prompt is empty"
            return {'CANCELLED'}

        if not api_url.strip():
            self.report({'WARNING'}, "API URL cannot be empty!")
            scene.ai_status = "Error: API URL is empty"
            return {'CANCELLED'}

        scene.ai_status = "Contacting AI... (Blender will freeze briefly)"
        
        # Force redraw of the viewport sidebar to display status update immediately
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        # Prepare JSON payload
        payload = {
            "prompt": prompt
        }
        data = json.dumps(payload).encode('utf-8')

        # Create HTTP request
        req = urllib.request.Request(
            api_url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Bforartists-AI-Connector/1.0'
            },
            method='POST'
        )

        try:
            # Send POST request with a 15-second timeout to prevent Blender from hanging indefinitely
            with urllib.request.urlopen(req, timeout=15) as response:
                status_code = response.getcode()
                if status_code != 200:
                    err_msg = f"API returned HTTP status {status_code}"
                    self.report({'ERROR'}, err_msg)
                    scene.ai_status = f"Error: {err_msg}"
                    return {'CANCELLED'}

                res_body = response.read().decode('utf-8')
                
                # Attempt to parse as JSON first
                try:
                    res_json = json.loads(res_body)
                    if isinstance(res_json, dict):
                        # Support standard response patterns (e.g., {"code": "..."} or {"script": "..."})
                        if 'code' in res_json:
                            code_to_run = res_json['code']
                        elif 'script' in res_json:
                            code_to_run = res_json['script']
                        else:
                            # If JSON is returned but lacks a 'code' key, try to use the raw body or warn
                            code_to_run = res_body
                    else:
                        code_to_run = res_body
                except json.JSONDecodeError:
                    # If response is not JSON, treat the raw response body as the Python code string
                    code_to_run = res_body

                if not code_to_run.strip():
                    self.report({'WARNING'}, "API returned empty code string")
                    scene.ai_status = "Error: Empty response code"
                    return {'CANCELLED'}

                scene.ai_status = "Executing generated code..."
                print("\n--- AI Connector: Executing Generated Code ---")
                print(code_to_run)
                print("----------------------------------------------\n")

                # Define global/local execution contexts containing bpy and context safely
                global_dict = {
                    '__builtins__': __import__('builtins'),
                    'bpy': bpy,
                    'context': context,
                }
                local_dict = {}

                # Safely execute the returned Python code string
                try:
                    exec(code_to_run, global_dict, local_dict)
                except Exception as exec_err:
                    err_msg = f"Execution Error: {str(exec_err)}"
                    self.report({'ERROR'}, exec_err)
                    scene.ai_status = "Script runtime error!"
                    print(f"Code execution failed: {exec_err}")
                    return {'CANCELLED'}

                scene.ai_status = "Success!"
                self.report({'INFO'}, "Successfully generated and executed AI code")
                return {'FINISHED'}

        except urllib.error.HTTPError as e:
            err_msg = f"HTTP Error {e.code}: {e.reason}"
            self.report({'ERROR'}, err_msg)
            scene.ai_status = f"HTTP Error: {e.code}"
            return {'CANCELLED'}
        except urllib.error.URLError as e:
            err_msg = f"Connection Failed: {e.reason}"
            self.report({'ERROR'}, err_msg)
            scene.ai_status = "Error: Connection failed"
            return {'CANCELLED'}
        except Exception as e:
            err_msg = f"Unexpected Error: {str(e)}"
            self.report({'ERROR'}, err_msg)
            scene.ai_status = "Error: Unexpected issue"
            return {'CANCELLED'}

class AI_PT_Panel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport Sidebar for Bforartists / Blender"""
    bl_label = "AI Connector"
    bl_idname = "VIEW3D_PT_ai_connector"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Header info
        layout.label(text="AI Assistant Panel", icon='LIGHT')
        
        # Prompt text box section
        box = layout.box()
        box.label(text="AI Text Prompt:", icon='TEXT')
        # Custom StringProperty for prompt (displays properly inside panel)
        box.prop(scene, "ai_prompt", text="")
        
        # Configuration section
        box = layout.box()
        box.label(text="Server Target Settings", icon='PREFERENCES')
        box.prop(scene, "ai_api_url", text="URL")
        
        # Status/Feedback section
        box = layout.box()
        box.label(text="Status Monitor", icon='INFO')
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text=scene.ai_status)
        
        # Prominent Generate button
        layout.separator()
        row = layout.row()
        row.scale_y = 2.0  # Make the button visually prominent
        row.operator("ai.generate", text="Ask AI & Run", icon='PLAY')

# Registration
classes = (
    AI_OT_Generate,
    AI_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Custom properties attached to the active scene
    bpy.types.Scene.ai_prompt = bpy.props.StringProperty(
        name="Prompt",
        description="Describe what you want the AI to create or do",
        default="Create a step setup of 5 cubes stacked cleanly layout style."
    )
    
    bpy.types.Scene.ai_api_url = bpy.props.StringProperty(
        name="API URL",
        description="URL of the external AI API endpoint server setup",
        default="http://localhost:5000/generate"
    )
    
    bpy.types.Scene.ai_status = bpy.props.StringProperty(
        name="Status",
        description="Status of the AI Connection pipeline",
        default="Ready"
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.ai_prompt
    del bpy.types.Scene.ai_api_url
    del bpy.types.Scene.ai_status

if __name__ == "__main__":
    register()

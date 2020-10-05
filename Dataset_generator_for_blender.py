import bpy
from bpy_extras.object_utils import world_to_camera_view
import xml.etree.cElementTree as ET
import random
import os, shutil
scene = bpy.context.scene


render = scene.render
res_x = render.resolution_x
res_y = render.resolution_y



index = 0

def my_handler(scene):
    obj = bpy.data.objects['boundBox']
    cam = bpy.data.objects['Camera']

    global index
    bpy.context.scene.frame_set(index)
    
    render_scale = scene.render.resolution_percentage / 100
    render_size = (
        int(scene.render.resolution_x * render_scale),
        int(scene.render.resolution_y * render_scale),
    )
    flag = True
    global global_location
    global global_rotation
    global global_scale
    obj.location = global_location
    obj.rotation_euler = global_rotation
    obj.scale = global_scale
    while flag:
        move_obj_random(obj)
        verts = ((obj.matrix_world @ vert.co) for vert in obj.data.vertices)

        co_2d = [world_to_camera_view(scene, cam, coord) for coord in verts]
        flag = False
        for v in co_2d:
            if v.x <0 or v.y <0 or v.x >1 or v.y >1:
                flag = True
                obj.location = global_location
                obj.rotation_euler = global_rotation
                obj.scale = global_scale
                break
    
    
    

    c_x = [p.x for p in co_2d]
    c_y = [p.y for p in co_2d]

    max_x = max(c_x)
    min_x = min(c_x)
    max_y = max(c_y)
    min_y = min(c_y)

    #width = (max_x- min_x)*render_size[0]
    #height = (max_y - min_y)*render_size[1]

    #x_center = (max_x + min_x)*0.5*render_size[0]
    #y_center = (max_y + min_y)*0.5*render_size[1]


    max_x = max_x*render_size[0]
    min_x = min_x*render_size[0]
    max_y = render_size[1] - (max_y*render_size[1])
    min_y = render_size[1] -(min_y*render_size[1])

    #print(width*render_size[0],height* render_size[1])
    #print(x_center*render_size[0],y_center* render_size[1])

    save_xml(index,max_x,min_x,max_y,min_y,render_size)
    index = index+1

def register():
    bpy.app.handlers.frame_change_post.append(my_handler)

def unregister():
    bpy.app.handlers.frame_change_post.remove(my_handler)
    

def move_sun():    
    sun = bpy.data.objects['Sun']

    x_min =71.4429
    x_max =109.743
    

    y_min =-61.6581
    y_max = 62.8419

    z_min =-80.6817
    z_max =46.6183
    
    rad = 0.0174532925
    r1 = random.uniform(x_min,x_max)*rad
    r2 = random.uniform(y_min,y_max)*rad
    r3 = random.uniform(z_min,z_max)*rad
    
    sun.rotation_euler = (r1,r2,r3)

def move_earth():
    earth = bpy.data.objects['Earth']
    
    r1 = random.uniform(0,6.2831853072)
    r2 = random.uniform(0,6.2831853072)
    r3 = random.uniform(0,6.2831853072)
    
    z_loc_max =-0.183857    
    z_loc_min =-1.37386
    x_loc_min =-0.201492
    x_loc_max = 0.538508
    
    x = random.uniform(x_loc_min, x_loc_max)
    z = random.uniform(z_loc_min, z_loc_max)
    
    earth.rotation_euler = (r1,r2,r3)
    earth.location = (x,earth.location.y,z)
      
def move_obj_random(obj):
    x_max = -1.27917
    x_min = -3.20983
    z_max = 0.919755
    z_min = -0.536651
    y_min = -3.95811
    y_max = -2.8427
    
    scale_min=0.022621
    scale_max=0.34904
    
    scale = random.uniform(scale_min, scale_max)
    p = (scale -scale_min)/(scale_max - scale_min)
    qx = p*(x_max - x_min)*0.5
    qy = p*(y_max - y_min)*0.5
    qz = p*(z_max - z_min)*0.5
    
    x = random.uniform(x_min + qx, x_max -qx)
    y = random.uniform(y_min+qy, y_max-qy)
    z = random.uniform(z_min+qz, z_max-qz)

    
    r1 = random.uniform(0,6.2831853072)
    r2 = random.uniform(0,6.2831853072)
    r3 = random.uniform(0,6.2831853072)
    
    obj.rotation_euler = (r1,r2,r3)
    obj.scale = (scale,scale,scale)
    obj.location = (x,y,z)

def del_f(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            
            
obj2 = bpy.data.objects['boundBox']
global_location = obj2.location
global_rotation = obj2.rotation_euler
global_scale = obj2.scale
anns = 'cubesat_dataset/anns'
tmp = 'cubesat_dataset/tmp'
del_f(anns)
del_f(tmp)
register()


def save_xml(index,x_max,x_min,y_max,y_min,render_size):
    if index ==0:
        return
    
    root = ET.Element("annotation", verified = "yes")
    
    ET.SubElement(root, "folder").text = "imgs"
    ET.SubElement(root, "filename").text = "{:04d}.jpg".format(index)
    ET.SubElement(root, "path").text = "cubesat_detector/imgs"
    source = ET.SubElement(root, "source")
    ET.SubElement(source,"database").text = "rendered"
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(int(render_size[0]))
    ET.SubElement(size, "height").text = str(int(render_size[1]))
    ET.SubElement(size, "deph").text = '3'
    ET.SubElement(root, "segmented").text = "0"
    object = ET.SubElement(root, "object")
    ET.SubElement(object, "name").text = "sat"
    ET.SubElement(object, "pose").text = "Unspecified"
    ET.SubElement(object, "truncated").text = "0"
    ET.SubElement(object, "difficult").text = "0"
    bndbox = ET.SubElement(object, "bndbox")
    ET.SubElement(bndbox, "xmin").text = str(round(x_min))
    ET.SubElement(bndbox, "ymin").text = str(round(y_max))
    ET.SubElement(bndbox, "xmax").text = str(round(x_max))
    ET.SubElement(bndbox, "ymax").text = str(round(y_min))

    
    #ET.SubElement(doc, "field2", name="asdfasd").text = "some vlaue2"

    tree = ET.ElementTree(root)
    #tree.write("test.xml")
    path = "cubesat_dataset/anns/{:04d}.xml".format(index)
    print(path)
    tree.write(path)

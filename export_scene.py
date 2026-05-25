import bpy
import bpy_extras
import math

class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーンを出力します"
    filename_ext = ".scene"

    def write_and_export(self, file, str):
        print(str)
        file.write(str)
        file.write('\n')
    
    def export(self, context):
        """ファイルに出力"""

        print("シーン情報出力開始...%r" % self.filepath)
    
        with open(self.filepath, "wt") as file:
            file.write("Scene\n")
            
            for object in bpy.context.scene.objects:
                if(object.parent):
                    continue

                self.parse_scene_recursive(file, object, 0)

    
    def parse_scene_recursive(self, file, object, level):
        """シーン解析用再起関数"""

        indent = "  " * level

        #オブジェクト名書き込み
        self.write_and_export(file, indent + object.type + " - " + object.name)
        #ローカルトランスフォーム行列から平行移動、回転、スケーリングを抽出
        #型はVector, Quaternion, Vector
        trans, rot, scale = object.matrix_local.decompose()
        #回転をQuaternionからEulerに変換
        rot = rot.to_euler()
        #ラジアンから度数法に変換
        rot.x = math.degrees(rot.x)
        rot.y = math.degrees(rot.y)
        rot.z = math.degrees(rot.z)
        
        self.write_and_export(file, indent + "T (%f,%f,%f)" % (trans.x, trans.y, trans.z))
        self.write_and_export(file, indent + "R (%f,%f,%f)" % (rot.x, rot.y, rot.z))
        self.write_and_export(file, indent + "S (%f,%f,%f)" % (scale.x, scale.y, scale.z))

        if "file_name" in object:
            self.write_and_export(file, indent + "N %s" % object["file_name"])

        if "collider" in object:
            self.write_and_export(file, indent + "C %s" % object["collider"])
            self.write_and_export(file, indent + "CC (%f,%f,%f)" % (object["collider_center"][0], object["collider_center"][1], object["collider_center"][2]))
            self.write_and_export(file, indent + "CS (%f,%f,%f)" % (object["collider_size"][0], object["collider_size"][1], object["collider_size"][2]))

        self.write_and_export(file, '')

        #子オブジェクトも同様に解析
        for child in object.children:
            self.parse_scene_recursive(file, child, level + 1)

    def execute(self, context):
        
        print("シーン情報をExportします")

        self.export(context)

        print("シーン情報をExportしました")
        self.report({'INFO'}, "シーン情報をExportしました")

        return {'FINISHED'}

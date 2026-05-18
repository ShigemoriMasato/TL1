import bpy
import bpy_extras
import math

#ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Taro Kamata",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description":"レベルエディタ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "頂点座標を引っ張って伸ばします"
    #Redo, UnDo可能オプション
    bl_option = {'REGISTER', 'UNDO'}

    #メニューを実行したときの呼ばれるコールバック関数
    def execute(self, context):
        bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
        print("頂点を伸ばしました")

        #オペレーターの命令終了を通知
        return {'FINISHED'}

class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_ico_sphere"
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    #Redo, UnDo可能オプション
    bl_option = {'REGISTER', 'UNDO'}

    #メニューを実行したときの呼ばれるコールバック関数
    def execute(self, context):
        bpy.ops.mesh.primitive_ico_sphere_add()
        print("ICO球を作成しました")

        #オペレーターの命令終了を通知
        return {'FINISHED'}
    

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

class OBJECT_PT_file_name(bpy.types.Panel):
    """オブジェクトのファイルネームパネル"""
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "ファイルネーム"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        #パネルに項目を追加
        if "file_name" in context.object:
            self.layout.prop(context.object, '["file_name"]', text=self.bl_label)

        else:
            self.layout.operator(MYADDON_OT_add_filename.bl_idname, text="FileName追加", icon='ADD')

#トップバーの拡張メニュー
class TOPBAR_MT_my_menu(bpy.types.Menu):
    #Blenderがクラスを識別するための固有の文字列
    bl_idname = "TOPBAR_MT_my_menu"
    #メニューのラベルとして表示される文字列
    bl_label = "MyMenu"
    #著者表示用の文字列
    bl_description = "拡張メニュー by " + bl_info["author"]

    #サブメニューの描画
    def draw(self, context):
        #トップバーの「エディターメニュー」に項目(オペレーター)を追加
        self.layout.operator(MYADDON_OT_stretch_vertex.bl_idname, text=MYADDON_OT_stretch_vertex.bl_label)
        self.layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text=MYADDON_OT_create_ico_sphere.bl_label)
        self.layout.operator(MYADDON_OT_export_scene.bl_idname, text=MYADDON_OT_export_scene.bl_label)

    #既存のメニューにサブメニューを追加
    def submenu(self, context):
        #ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

#オペレーター　カスタムプロパティ[filename]を追加
class MYADDON_OT_add_filename(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_filename"
    bl_label = "FileName追加"
    bl_description = "['file_name']カスタムプロパティを追加します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object["file_name"] = ""
        return {'FINISHED'}



#自作クラスまとめ
classes = (MYADDON_OT_stretch_vertex, MYADDON_OT_create_ico_sphere, MYADDON_OT_export_scene, MYADDON_OT_add_filename, TOPBAR_MT_my_menu, OBJECT_PT_file_name)

#Menu描画関数
def draw_menu_manual(self, context):
    #self : 呼び出し元のクラスインスタンス。C++でいうthis
    #context : カーソルを合わせたときのポップアップのカスタマイズなどに使用
    self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

#アドオン有効化時コールバック
def register():
    # Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)
        
    #メニューに項目を追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)

    print("レベルエディタが有効化されました。")

#アドオン無効化時コールバック
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)

    for cls in classes:
        bpy.utils.unregister_class(cls)

    print("レベルエディタが無効化されました。")

if __name__ == "__main__":
    register()

from ext import extructer

if __name__ == "__main__":
    # 使用例：Employee構造体だけを対象にする
    output = extructer.extract_struct_definition("example.h", "Employee")
    print(output)
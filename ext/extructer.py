
from clang.cindex import Index, CursorKind

def extract_struct_definition(filename, target_struct_name, output_filename=None):
    index = Index.create()
    tu = index.parse(filename, args=["-x", "c"])

    for cursor in tu.cursor.get_children():
        if cursor.kind == CursorKind.STRUCT_DECL and cursor.is_definition():
            struct_name = cursor.spelling or "anonymous"
            if struct_name == target_struct_name:
                extent = cursor.extent
                start_line = extent.start.line
                end_line = extent.end.line

                with open(filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                extracted_lines = lines[start_line - 1:end_line]

                return "".join(extracted_lines)

    print(f"構造体 '{target_struct_name}' は見つかりませんでした。")
    
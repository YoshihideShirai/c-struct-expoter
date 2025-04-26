import argparse
import re
from clang.cindex import Index, CursorKind, TypeKind, Config

Config.set_library_file("/usr/lib/llvm-19/lib/libclang-19.so.1")

TYPE_REPLACEMENTS = {
    TypeKind.UINT: ('int32_t', [r'\bint\b']),
    TypeKind.UINT: ('uint32_t', [r'\bulong\b']),
    TypeKind.LONG: ('int64_t', [r'\blong\b', r'\blong int\b']),
    TypeKind.ULONG: ('uint64_t', [r'\bunsigned long\b', r'\bunsigned long int\b']),
}

def read_struct_names_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def collect_target_lines(cursor, target_lines):
    for child in cursor.get_children():
        if child.kind == CursorKind.FIELD_DECL:
            canonical = child.type.get_canonical()  # ← typedef展開後の型
            kind = canonical.kind
            if kind in TYPE_REPLACEMENTS:
                target_lines.append((child.location.line, kind))
        elif child.kind in [CursorKind.UNION_DECL, CursorKind.STRUCT_DECL, CursorKind.ENUM_DECL]:
            if child.is_definition():
                collect_target_lines(child, target_lines)

def extract_struct_text(filename, struct_cursor):
    extent = struct_cursor.extent
    start_line = extent.start.line
    end_line = extent.end.line

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    struct_lines = lines[start_line - 1:end_line]
    target_line_info = []
    collect_target_lines(struct_cursor, target_line_info)

    for rel_line_num in range(len(struct_lines)):
        abs_line_num = start_line + rel_line_num
        matches = [kind for line, kind in target_line_info if line == abs_line_num]
        if matches:
            for kind in matches:
                replacement, patterns = TYPE_REPLACEMENTS[kind]
                for pattern in patterns:
                    struct_lines[rel_line_num] = re.sub(pattern, replacement, struct_lines[rel_line_num])
    return ''.join(struct_lines)

def extract_and_combine_structs(filename, struct_names, output_filename):
    index = Index.create()
    tu = index.parse(filename, args=["-x", "c"])

    found = set()
    combined_texts = []

    for cursor in tu.cursor.get_children():
        if cursor.kind == CursorKind.STRUCT_DECL and cursor.is_definition():
            if cursor.spelling in struct_names:
                struct_code = extract_struct_text(filename, cursor)
                combined_texts.append(f"// === {cursor.spelling} ===\n{struct_code}\n")
                found.add(cursor.spelling)

    not_found = set(struct_names) - found
    if not_found:
        print(f"⚠️ 見つからなかった構造体: {', '.join(not_found)}")

    if combined_texts:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("#ifndef COMBINED_STRUCTS_H\n#define COMBINED_STRUCTS_H\n\n")
            f.write("#include <stdint.h>\n\n")
            f.writelines(combined_texts)
            f.write("\n#endif // COMBINED_STRUCTS_H\n")
        print(f"✅ 出力ファイル: {output_filename}")
    else:
        print("⚠️ 対象の構造体は見つかりませんでした。")

def main():
    parser = argparse.ArgumentParser(description="C構造体を抽出＆long→int64_t変換")
    parser.add_argument("-i", "--input", required=True, help="入力ヘッダファイル")
    parser.add_argument("-f", "--struct-file", required=True, help="構造体名リストファイル（1行ずつ構造体名）")
    parser.add_argument("-o", "--output", default="combined_structs.h", help="出力ファイル名（省略時は combined_structs.h）")
    args = parser.parse_args()

    struct_names = read_struct_names_from_file(args.struct_file)
    extract_and_combine_structs(args.input, struct_names, args.output)

if __name__ == "__main__":
    main()

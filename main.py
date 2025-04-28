import argparse
import re
from clang.cindex import Index, CursorKind, TypeKind, Config, TokenKind

Config.set_library_file("/usr/lib/llvm-19/lib/libclang-19.so.1")

TYPE_REPLACEMENTS = {
    TypeKind.UINT: ('int32_t', [r'\bint\b']),
    TypeKind.UINT: ('uint32_t', [r'\bulong\b']),
    TypeKind.LONG: ('int64_t', [r'\blong\b', r'\blong int\b']),
    TypeKind.ULONG: ('uint64_t', [r'\bunsigned long\b', r'\bunsigned long int\b']),
}

import re

def extract_used_macros(struct_code):
    # マクロっぽい単語（定数・名前）を収集（大文字とアンダースコアで構成されるもの）
    return set(re.findall(r'\b[A-Z_][A-Z0-9_]*\b', struct_code))

def extract_macro_definitions(filename, macro_names):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    macro_lines = []
    for line in lines:
        if line.strip().startswith("#define"):
            for macro in macro_names:
                if re.match(rf'#define\s+{macro}\b', line):
                    macro_lines.append(line)
                    break
    return macro_lines

def extract_macro_definitions_from_files(file_list, macro_names):
    macro_lines = []
    seen = set()
    for path in file_list:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("#define"):
                        for macro in macro_names:
                            if re.match(rf'#define\s+{macro}\b', line) and macro not in seen:
                                macro_lines.append(line)
                                seen.add(macro)
        except FileNotFoundError:
            continue
    return macro_lines

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
    filename = extent.start.file.name
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

def extract_and_combine_structs(filename,include_paths, struct_names, output_filename):
    index = Index.create()
    tu = index.parse(filename, args=["-x", "c"] + [f"-I{path}" for path in include_paths])

    found = set()
    combined_texts = []
    used_macros = set()

    for cursor in tu.cursor.get_children():
        if cursor.kind == CursorKind.STRUCT_DECL and cursor.is_definition():
            if cursor.spelling in struct_names:
                struct_code = extract_text_from_cursor(cursor)
                combined_texts.append(
                    f"// === {cursor.spelling} ===\ntypedef {struct_code} {cursor.spelling};\n"
                )
                used_macros.update(extract_used_macros(struct_code))
                found.add(cursor.spelling)

    file_list = [filename]
    tu.get_includes()
    for include in tu.get_includes():
        file_list.append(include.include.name)
    macro_defs = extract_macro_definitions_from_files(file_list, used_macros)

    not_found = set(struct_names) - found
    if not_found:
        print(f"⚠️ 見つからなかった構造体: {', '.join(not_found)}")

    if combined_texts:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("#ifndef COMBINED_STRUCTS_H\n#define COMBINED_STRUCTS_H\n\n")
            f.write("#include <stdint.h>\n\n")
            if macro_defs:
                f.write("// === Used Defines ===\n")
                f.writelines(macro_defs)
                f.write("\n")
            f.writelines(combined_texts)
            f.write("\n#endif // COMBINED_STRUCTS_H\n")
        print(f"✅ 出力ファイル: {output_filename}")
    else:
        print("⚠️ 対象の構造体は見つかりませんでした。")

def extract_text_from_cursor(cursor):
    tu = cursor.translation_unit
    extent = cursor.extent

    tokens = list(tu.get_tokens(extent=extent))

    output = []
    for token in tokens:
        if token.kind in [TokenKind.KEYWORD, TokenKind.IDENTIFIER, TokenKind.LITERAL, TokenKind.PUNCTUATION]:
            output.append(token.spelling)
        elif token.kind == TokenKind.COMMENT:
            pass  # コメントはスキップする

    # トークンをうまく並べ直して Cコードっぽくする
    # ここはシンプルにスペース区切りでまず繋げる
    return ' '.join(output)

def main():
    parser = argparse.ArgumentParser(description="C構造体を抽出＆bit長指定型変換")
    parser.add_argument("-i", "--input", default="examples/basic/example.h", help="入力ヘッダファイル")
    parser.add_argument("-f", "--struct-file", default="structs.txt", help="構造体名リストファイル（1行ずつ構造体名）")
    parser.add_argument("-o", "--output", default="combined_structs.h", help="出力ファイル名（省略時は combined_structs.h）")
    parser.add_argument("-I", "--include", action="append", default=["examples/basic"], help="インクルードパス（複数指定可能）")
    args = parser.parse_args()

    struct_names = read_struct_names_from_file(args.struct_file)
    extract_and_combine_structs(args.input,args.include, struct_names, args.output)

if __name__ == "__main__":
    main()

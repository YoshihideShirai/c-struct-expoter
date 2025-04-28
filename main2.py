import argparse
import os
from clang.cindex import Index, CursorKind, TokenKind, Config

# 必要ならlibclangのパスを設定
# Config.set_library_path('/path/to/clang/library')
Config.set_library_file("/usr/lib/llvm-19/lib/libclang-19.so.1")


def load_target_structs(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def reconstruct_macro(cursor):
    tu = cursor.translation_unit
    tokens = list(tu.get_tokens(extent=cursor.extent))
    parts = []
    for token in tokens:
        parts.append(token.spelling)
    return ' '.join(parts)


def collect_all_macros(cursor, macro_map):
    if cursor.kind == CursorKind.MACRO_DEFINITION:
        macro_map[cursor.spelling] = reconstruct_macro(cursor)
    for child in cursor.get_children():
        collect_all_macros(child, macro_map)


def extract_text_from_cursor(cursor, used_macros, macro_names):
    tu = cursor.translation_unit
    tokens = list(tu.get_tokens(extent=cursor.extent))

    output = []
    skip_next = False
    for i, token in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue

        if token.kind == TokenKind.COMMENT:
            continue

        word = token.spelling

        # 型変換対応
        if word == "long":
            word = "int64_t"
        elif word == "unsigned":
            if (i + 1) < len(tokens) and tokens[i + 1].spelling == "long":
                word = "uint64_t"
                skip_next = True

        # マクロ利用チェック
        if word in macro_names:
            used_macros.add(word)

        output.append(word)

    return ' '.join(output)


def find_target_structs(cursor, targets, collected):
    if cursor.kind in (CursorKind.STRUCT_DECL, CursorKind.UNION_DECL, CursorKind.ENUM_DECL):
        if cursor.spelling in targets and cursor.is_definition():
            collected.append(cursor)
    for child in cursor.get_children():
        find_target_structs(child, targets, collected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True,
                        help="Input header file")
    parser.add_argument("-f", "--structs", required=True,
                        help="Text file listing struct names")
    parser.add_argument("-o", "--output", required=True,
                        help="Output file name")
    parser.add_argument("-I", "--include", action="append",
                        default=[], help="Include dirs")
    parser.add_argument("-D", "--define", action="append",
                        default=[], help="Macro defines")

    args = parser.parse_args()

    index = Index.create()
    parse_args = ["-x", "c", "-std=c11", "-Xclang", "-detailed-preprocessing-record"] \
        + [f"-I{inc}" for inc in args.include] \
        + [f"-D{d}" for d in args.define]
    tu = index.parse(args.input, args=parse_args)

    target_structs = load_target_structs(args.structs)

    macro_map = {}
    collect_all_macros(tu.cursor, macro_map)

    structs = []
    find_target_structs(tu.cursor, target_structs, structs)

    used_macros = set()
    output_structs = {}

    for cursor in structs:
        struct_text = extract_text_from_cursor(
            cursor, used_macros, set(macro_map.keys()))
        filename = cursor.location.file.name
        struct_name = cursor.spelling
        output_structs[struct_name] = {
            "filename": filename,
            "text": f"typedef {struct_text} {struct_name};"
        }

    # 出力
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    INCLUDE_GUARD_NAME = f"__{os.path.basename(args.output).upper().replace('.', '_')}"
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"#ifndef {INCLUDE_GUARD_NAME}\n")
        f.write(f"#define {INCLUDE_GUARD_NAME}\n\n")
        f.write("#include <stdint.h>\n\n")

        f.write("// Used defines\n")
        for name in sorted(used_macros):
            f.write(f"#define {macro_map[name]}\n")
        f.write("\n")

        for struct_name, struct_val in output_structs.items():
            f.write(f"// {struct_val["filename"]} : {struct_name}\n")
            f.write(struct_val["text"])
            f.write("\n\n")

        f.write(f"#endif // {INCLUDE_GUARD_NAME}\n")


if __name__ == "__main__":
    main()

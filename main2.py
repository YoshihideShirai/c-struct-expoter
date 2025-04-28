import argparse
import os
from clang.cindex import Index, CursorKind, TokenKind, Config

# 必要ならlibclangのパスを設定
# Config.set_library_path('/path/to/clang/library')
Config.set_library_file("/usr/lib/llvm-19/lib/libclang-19.so.1")

def load_target_structs(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def extract_text_from_cursor(cursor):
    tu = cursor.translation_unit
    tokens = list(tu.get_tokens(extent=cursor.extent))

    output = []
    for token in tokens:
        if token.kind == TokenKind.COMMENT:
            continue
        word = token.spelling
        if word == "long":
            word = "int64_t"
        elif word == "unsigned":
            # unsigned long など対応
            next_idx = tokens.index(token) + 1
            if next_idx < len(tokens) and tokens[next_idx].spelling == "long":
                word = "uint64_t"
                tokens[next_idx] = token  # nextの"long"を無視する
        output.append(word)

    return ' '.join(output)

def find_defines(cursor, defines):
    if cursor.kind == CursorKind.MACRO_DEFINITION:
        define_text = reconstruct_macro(cursor)
        defines.append(define_text)
    for child in cursor.get_children():
        find_defines(child, defines)

def reconstruct_macro(cursor):
    tu = cursor.translation_unit
    tokens = list(tu.get_tokens(extent=cursor.extent))
    parts = []
    for token in tokens:
        parts.append(token.spelling)
    return ' '.join(parts)

def find_target_structs(cursor, targets, collected):
    if cursor.kind in (CursorKind.STRUCT_DECL, CursorKind.UNION_DECL, CursorKind.ENUM_DECL):
        if cursor.spelling in targets:
            collected.append(cursor)
    for child in cursor.get_children():
        find_target_structs(child, targets, collected)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Input header file")
    parser.add_argument("-f", "--structs", required=True, help="Text file listing struct names")
    parser.add_argument("-o", "--output", required=True, help="Output file name")
    parser.add_argument("-I", "--include", action="append", default=[], help="Include dirs")
    parser.add_argument("-D", "--define", action="append", default=[], help="Macro defines")

    args = parser.parse_args()

    # パース準備
    index = Index.create()
    parse_args = ["-x", "c", "-std=c11"] + [f"-I{inc}" for inc in args.include] + [f"-D{d}" for d in args.define]
    tu = index.parse(args.input, args=parse_args)

    # ターゲットのstruct名をロード
    target_structs = load_target_structs(args.structs)

    # 抽出
    structs = []
    find_target_structs(tu.cursor, target_structs, structs)

    defines = set()
    find_defines(tu.cursor, defines)

    # 出力
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("#ifndef EXTRACTED_STRUCTS_H\n")
        f.write("#define EXTRACTED_STRUCTS_H\n\n")
        f.write("#include <stdint.h>\n\n")

        f.write("// Used defines\n")
        for define in sorted(defines):
            f.write(f"#define {define}\n")
        f.write("\n")

        for cursor in structs:
            filename = cursor.location.file.name
            struct_text = extract_text_from_cursor(cursor)
            f.write(f"// From: {filename}\n")
            f.write(struct_text)
            f.write("\n\n")

        f.write("#endif // EXTRACTED_STRUCTS_H\n")

if __name__ == "__main__":
    main()

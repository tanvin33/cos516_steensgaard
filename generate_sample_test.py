def main():
    z = int(input("Enter a number z: ").strip())

    z *= 2000

    filename = f"tests/{z * 5}_sample_test.sil"

    with open(filename, "w") as f:
        for i in range(1, z + 1):
            f.write(f"p{i} := &x{i};\n")
            f.write(f"r{i} := &p{i};\n")
            f.write(f"q{i} := &y{i};\n")
            f.write(f"s{i} := &q{i};\n")
            f.write(f"r{i} := s{i};\n")
            f.write("\n")

    print(f"Wrote {filename}")

if __name__ == "__main__":
    main()

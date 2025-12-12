def main():
    z = int(input("Enter a number z: ").strip())

    filename = f"tests/{z}_assign_test.sil"

    with open(filename, "w") as f:
        for i in range(1, z + 1):
            f.write(f"x{i} := y{i};\n")

    print(f"Wrote {filename}")

if __name__ == "__main__":
    main()

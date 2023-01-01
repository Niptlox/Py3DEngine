def open_file_obj(path, scale=1, _convert_faces_to_lines=False, ):
    with open(path, "r") as f:
        lines = f.readlines()

    vertexes = []
    faces = []
    vertex_index_offset = 0
    for line in lines:
        if not line.replace(" ", "") or line[0] == "#":
            continue
        b = line.split()[0]
        if b == "o":
            # object
            vertex_index_offset = len(vertexes)
        if b == "v":
            vertex = list(map(lambda x: float(x)*scale, line.split()[1:4]))
            vertexes.append(vertex)
        if b == "f":
            face = [int(st.split("/")[0]) - 1 for st in line.split(" ")[1:]]
            faces.append(face)
    if _convert_faces_to_lines:
        return vertexes, convert_faces_to_lines(faces)
    return vertexes, faces


def convert_faces_to_lines(faces):
    lines = set()
    for face in faces:
        lines.add(tuple(sorted((face[0], face[-1]))))
        lines |= {tuple(sorted((face[i], face[i + 1]))) for i in range(len(face) - 1)}

    return lines

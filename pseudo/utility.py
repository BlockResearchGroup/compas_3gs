def oriented_normal_polygon(points, unitized=True):
    p = len(points)
    assert p > 2, "At least three points required"
    w          = centroid_points(points)
    normal_sum = (0, 0, 0)
    for i in range(-1, len(points) - 1):
        u          = points[i]
        v          = points[i + 1]
        uv         = subtract_vectors(v, u)
        vw         = subtract_vectors(w, v)
        normal     = scale_vector(cross_vectors(uv, vw), 0.5)
        normal_sum = add_vectors(normal_sum, normal)
    if unitized:
        return normaalize_vector(normal_sum)
    return normal_sum


def oriented_area_polygon(points):
    oriented_normal = oriented_normal_polygons(points, unitized=False)
    return length_vector(oriented_normal)
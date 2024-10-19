class DisjointSet:
    def __init__(self, vertexes_len) -> None:
        self._representatives = [-1] * vertexes_len
    
    def make_set(self, vertex) -> None:
            self._representatives[vertex] = vertex

    def union(self, vertex1, vertex2) -> None:
        representative1 = self.find(vertex1)
        representative2 = self.find(vertex2)

        if representative1 != representative2:
            self._representatives[representative2] = representative1

    def find(self, vertex) -> int:
        if self._representatives[vertex] == vertex:
            return vertex
        else:
            representetive = self.find(self._representatives[vertex])
            self._representatives[vertex] = representetive
            return representetive
from __future__ import annotations
import copy


"""
TODO:
- __setitem__ 구현하기
- __pow__ 구현하기 (__matmul__을 활용해봅시다)
- __repr__ 구현하기
"""


class Matrix:
    MOD = 1000

    def __init__(self, matrix: list[list[int]]) -> None:
        self.matrix = matrix

    @staticmethod
    def full(n: int, shape: tuple[int, int]) -> Matrix:
        return Matrix([[n] * shape[1] for _ in range(shape[0])])

    @staticmethod
    def zeros(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(0, shape)

    @staticmethod
    def ones(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(1, shape)

    @staticmethod
    def eye(n: int) -> Matrix:
        matrix = Matrix.zeros((n, n))
        for i in range(n):
            matrix[i, i] = 1
        return matrix

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.matrix), len(self.matrix[0]))

    def clone(self) -> Matrix:
        return Matrix(copy.deepcopy(self.matrix))

    def __getitem__(self, key: tuple[int, int]) -> int:
        return self.matrix[key[0]][key[1]]

    def __setitem__(self, key: tuple[int, int], value: int) -> None:
        """
        key를 i와 j로 분해하고 self.matrix에 값을 집어넣고자 함
        누적 값이 커지기 전에 MOD 1000을 적용하여 행렬곱의 크기가 일정 수준 이하로 유지되게 하고자 했다
        따라서 행렬 안에 저장되는 원소들은 0~999의 값을 가지게 되며 행렬의 거듭제곱을 여러번 해도 안정적으로 계산이 가능하게 했다.
        """
        i, j = key
        self.matrix[i][j] = value % self.MOD
    

    def __matmul__(self, matrix: Matrix) -> Matrix:
        x, m = self.shape
        m1, y = matrix.shape
        assert m == m1

        result = self.zeros((x, y))

        for i in range(x):
            for j in range(y):
                for k in range(m):
                    result[i, j] += self[i, k] * matrix[k, j]

        return result

    def __pow__(self, n: int) -> Matrix:
        """
        1629의 예시와 유사한 방식으로 곱셈을 분할하여 계산하고자 했음. 아이디어는 1629번 문제와 동일함
        result는 항등행렬 I로 설정하고 시작하며 원본 행렬 base로 시작함.
        지수가 남아있을 동안 반복문을 실행한다.
            n이 홀수 일 때 result에 base를 곱하여 업데이트 해주고 base는 제곱, n은 2로 나눈 몫으로 업데이트 해준다.
            이후 반복문을 반복하며 n이 0보다 크지 않을 때 반복문을 종료하고 result를 리턴한다.
        """
        x,y = self.shape
        assert x == y
        
        result = Matrix.eye(x)
        base = self.clone()
        
        while n > 0:
            if n % 2 == 1:
                result = result @ base
            base = base @ base
            n = n // 2
            
        return result
    

    def __repr__(self) -> str:
        return "\n".join(" ".join(map(str, row)) for row in self.matrix)
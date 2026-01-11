from __future__ import annotations
from collections import deque


"""
TODO:
- rotate_and_remove 구현하기 
"""


def create_circular_queue(n: int) -> deque[int]:
    """1부터 n까지의 숫자로 deque를 생성합니다."""
    return deque(range(1, n + 1))

def rotate_and_remove(queue: deque[int], k: int) -> int:
    """
    queue.rotate(t): 
        t > 0: 오른쪽으로 t칸 회전
        t < 0: 왼쪽으로 t칸 회전
    queue.rotate(-(k-1)): 왼쪽으로 k-1칸 회전하여 k번째 원소가 가장 먼저 오게 만듦
    return queue.popleft: 가장 먼저 위치하고 있는 k번째 원소를 return 해줌
    """
    queue.rotate(-(k-1))
    return queue.popleft()
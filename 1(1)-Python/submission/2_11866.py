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




"""
TODO:
- josephus_problem 구현하기
    # 요세푸스 문제 구현
        # 1. 큐 생성
        # 2. 큐가 빌 때까지 반복
        # 3. 제거 순서 리스트 반환
"""


def josephus_problem(n: int, k: int) -> list[int]:
    """
    create_circular_queue(n)을 통해 q를 생성하고 리턴을 위한 빈 리스트를 만듦
    q에 원소가 존재하지 않을 때까지, rotate_and_remove(q,k)를 통해 q에서 k번째 원소를 제거해 k_th에 저장함
    제거된 k_th를 result 리스트에 넣고 q에 원소가 존재하지 않을 때까지 반복함
    q에 원소가 존재하지 않는다면 반복문을 종료하고 result를 리턴함
    """
    q = create_circular_queue(n)
    result: list[int] = []
    
    while q:
        k_th = rotate_and_remove(q, k)
        result.append(k_th)
        
    return result
        

def solve_josephus() -> None:
    """입, 출력 format"""
    n: int
    k: int
    n, k = map(int, input().split())
    result: list[int] = josephus_problem(n, k)
    
    # 출력 형식: <3, 6, 2, 7, 5, 1, 4>
    print("<" + ", ".join(map(str, result)) + ">")

if __name__ == "__main__":
    solve_josephus()
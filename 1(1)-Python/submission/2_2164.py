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
- simulate_card_game 구현하기
    # 카드 게임 시뮬레이션 구현
        # 1. 큐 생성
        # 2. 카드가 1장 남을 때까지 반복
        # 3. 마지막 남은 카드 반환
"""


def simulate_card_game(n: int) -> int:
    """
    create_circular_queue의 함수를 이용하여 q를 생성
    q의 길이가 1보다 큰 상태에서 popleft로 가장 위에 있는 카드를 제거하고, 그 다음 위에 있는 카드를 뽑아 q에 append함으로써 가장 뒤로 보냄
    다음의 과정을 반복하여 q가 하나의 카드만을 남길 때까지 반복하고 q[0]을 리턴함
    """
    q = create_circular_queue(n)
    while len(q) > 1:
        q.popleft()
        q.append(q.popleft())
        
    return q[0]

def solve_card2() -> None:
    """입, 출력 format"""
    n: int = int(input())
    result: int = simulate_card_game(n)
    print(result)

if __name__ == "__main__":
    solve_card2()
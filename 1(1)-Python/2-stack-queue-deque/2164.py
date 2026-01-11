from lib import create_circular_queue


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
# lib.py의 Matrix 클래스를 참조하지 않음
import sys


"""
TODO:
- fast_power 구현하기 
"""


def fast_power(base: int, exp: int, mod: int) -> int:
    """
    거듭제곱 계산에 걸리는 시간을 줄이기 위해서 각각의 단계에서 곱셈을 분해해 mod를 적용할 수 있다는 성질을 이용하여 흐름을 구성하였음
    초기 결과값을 1로 두고, 초기 base 값을 mod로 나눈 나머지 값을 base로 준비하고 반복문에 들어감
        exp가 0보다 큰 동안, 만약에 지수가 홀수라면, 절반으로 나누고 하나의 base가 추가로 곱해져야 하므로 result에 base를 곱하고 mod의 성질을 적용하여 나머지를 구한뒤 result에 다시 대입함
        이후 mod의 성질을 적용하여 제곱한 base를 나누어주고, 지수도 절반으로 나눈 몫으로 업데이트 해준다.
    이 반복문은 지수가 0보다 클 때에만 동작하며 이후에는 도출된 result를 리턴한다.
        """
    result = 1
    base = base % mod
    
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        
        base = (base * base) % mod
        exp = exp // 2
        
    return result 

def main() -> None:
    A: int
    B: int
    C: int
    A, B, C = map(int, input().split()) # 입력 고정
    
    result: int = fast_power(A, B, C) # 출력 형식
    print(result) 

if __name__ == "__main__":
    main()

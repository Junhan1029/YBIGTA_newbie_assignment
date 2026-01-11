from __future__ import annotations
import copy
from collections import deque
from collections import defaultdict
from typing import DefaultDict, List


"""
TODO:
- __init__ 구현하기
- add_edge 구현하기
- dfs 구현하기 (재귀 또는 스택 방식 선택)
- bfs 구현하기
"""


class Graph:
    def __init__(self, n: int) -> None:
        """
        그래프 초기화
        n: 정점의 개수 (1번부터 n번까지)
        
        DefaultDict[int, List[int]]: 타입 힌트
            key가 int이고 value가 List[int]인 DefaultDict 형태의 딕셔너리
            정점 번호(int), 정점의 adjacency list(int로 이루어진 리스트)
            
        defaultdict(list):
            일반 딕셔너리는 없는 key에 접근하면 에러가 발생
            defaultdict(list)는 없는 key에 접근하면 자동으로 기본값을 생성해줌
            (list): 기본값 생성 함수, 어떤 key를 처음 사용하면 list()를 호출해서 빈 리스트를 만들어줌
        """
        self.n = n
        self.adj: DefaultDict[int, List[int]] = defaultdict(list)
    
    def add_edge(self, u: int, v: int) -> None:
        """
        양방향 간선 추가
        양방향 간선이므로 u의 이웃에 v를 추가하고, v의 이웃에 u를 추가
        """
        self.adj[u].append(v)
        self.adj[v].append(u)
        
    
    def dfs(self, start: int) -> list[int]:
        """
        깊이 우선 탐색 (DFS) - 재귀 방식: 함수 내부에서 재귀 함수 정의하여 구현  
            총 n+1 개의 False를 가진 visited 리스트를 생성하여 0번째 인덱스를 제외하고 <1번 정점 - 1번 정점의 방문 여부> 형태로 확인하고자 함
            결과를 담을 result 리스트를 만듦
            DFS 함수를 정의
                x 정점을 방문했으므로 visited 리스트에 x번 인덱스의 값을 True로 바꿈
                x 정점을 방문했으므로 result 리스트에 x를 추가
                x의 이웃들 중에서, 아직 방문하지 않은 정점들에 대해(visited에 False로 되어 있는 정점들에 대해) DFS 함수를 다시 실행
            DFS 함수를 실행하고 result 리스트를 반환
        """
        visited = [False] * (self.n + 1)  
        result: list[int] = []
        
        def DFS(x: int) -> None:
            visited[x] = True
            result.append(x)

            for vertex in sorted(self.adj[x]):
                if not visited[vertex]:
                    DFS(vertex)
                    
        DFS(start)
        return result            
    
    def bfs(self, start: int) -> list[int]:
        """
        너비 우선 탐색 (BFS)
            총 n+1 개의 False를 가진 visited 리스트를 생성하여 0번째 인덱스를 제외하고 <1번 정점 - 1번 정점의 방문 여부> 형태로 확인하고자 함
            visited: 정점을 발견하였고 큐에 들어갔거나, 들어갈 예정이므로 다시 큐에 넣을 필요가 없음을 알려주는 리스트
            결과를 담을 result 리스트를 만듦
            q: 처리해야할 정점들의 대기열(이미 발견한 정점 목록)
            q = deque([start]): start 정점에서 시작, 처음 처리할 정점을 q에 넣어둠
            start 정점을 방문했다고 처리함
            q에서 왼쪽에서부터 하나씩 뽑아서 x에 넣고 x를 result에 추가함
            x의 이웃들에 대해, visited = False라면 True로 바꿔주고 q에 추가함
                True로 바꾸고 q에 추가해야 같은 정점이 q에 두 번 들어가는 것을 방지할 수 있음
            result 리턴      
        """
        visited = [False] * (self.n + 1)  
        result: list[int] = []
        
        q = deque([start])
        visited[start] = True
        
        while q:
            x = q.popleft()
            result.append(x)
            
            for vertex in sorted(self.adj[x]):
                if not visited[vertex]:
                    visited[vertex] = True
                    q.append(vertex)
                    
        return result        
    
    
    
    def search_and_print(self, start: int) -> None:
        """
        DFS와 BFS 결과를 출력
        """
        dfs_result = self.dfs(start)
        bfs_result = self.bfs(start)
        
        print(' '.join(map(str, dfs_result)))
        print(' '.join(map(str, bfs_result)))



from typing import Callable
import sys


"""
-아무것도 수정하지 마세요!
"""


def main() -> None:
    intify: Callable[[str], list[int]] = lambda l: [*map(int, l.split())]

    lines: list[str] = sys.stdin.readlines()

    N, M, V = intify(lines[0])
    
    graph = Graph(N)  # 그래프 생성
    
    for i in range(1, M + 1): # 간선 정보 입력
        u, v = intify(lines[i])
        graph.add_edge(u, v)
    
    graph.search_and_print(V) # DFS와 BFS 수행 및 출력


if __name__ == "__main__":
    main()
